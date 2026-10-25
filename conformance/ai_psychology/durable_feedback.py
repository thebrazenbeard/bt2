"""Qualification-only SQLite feedback journal, not a trusted runtime."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sqlite3
from contextlib import closing
from typing import Callable

from outcome_contract import NeedSnapshot


RUNTIME_INTEGRATION_STATUS = "UNWIRED_LOCAL_SQLITE_QUALIFICATION_ONLY"


def _id(value: str, label: str) -> None:
    if (type(value) is not str or not value or len(value) > 256
            or value != value.strip() or any(ord(c) < 32 for c in value)):
        raise ValueError(f"{label} requires a bounded opaque identifier")


def _revision(value: int, label: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")


def _finite(value: float, label: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be finite nonnegative numeric")
    try:
        value = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be finite nonnegative numeric") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be finite nonnegative numeric")
    return value


@dataclass(frozen=True)
class GoalBinding:
    goal_id: str
    choice_id: str
    target_id: str
    revision: int = 0
    protection_veto: bool = False
    completed: bool = False

    def __post_init__(self) -> None:
        for field in ("goal_id", "choice_id", "target_id"):
            _id(getattr(self, field), field)
        _revision(self.revision, "revision")
        if type(self.protection_veto) is not bool or type(self.completed) is not bool:
            raise ValueError("goal flags must be boolean")


@dataclass(frozen=True)
class FeedbackClaim:
    event_id: str
    attempt_id: str
    need_id: str
    goal_id: str
    choice_id: str
    target_id: str
    expected_need_revision: int
    expected_goal_revision: int
    claimed_status: str
    claimant_kind: str
    evidence_ref: str
    observed_at: float
    expires_at: float

    def __post_init__(self) -> None:
        for field in ("event_id", "attempt_id", "need_id", "goal_id", "choice_id",
                      "target_id", "evidence_ref"):
            _id(getattr(self, field), field)
        _revision(self.expected_need_revision, "expected_need_revision")
        _revision(self.expected_goal_revision, "expected_goal_revision")
        if self.claimed_status not in {"SUCCESS", "NO_OP", "FAILED", "UNKNOWN"}:
            raise ValueError("unsupported claimed_status")
        if self.claimant_kind not in {"observer", "model_generated", "tool_result", "operator_statement"}:
            raise ValueError("unsupported claimant_kind")
        observed = _finite(self.observed_at, "observed_at")
        expires = _finite(self.expires_at, "expires_at")
        if expires <= observed:
            raise ValueError("expires_at must follow observed_at")


@dataclass(frozen=True)
class MeasuredEffect:
    physical_effect_id: str
    event_id: str
    attempt_id: str
    need_id: str
    goal_id: str
    choice_id: str
    target_id: str
    evidence_ref: str
    observer_id: str
    measured_level: float
    measured_at: float

    def __post_init__(self) -> None:
        for field in ("physical_effect_id", "event_id", "attempt_id", "need_id", "goal_id",
                      "choice_id", "target_id", "evidence_ref", "observer_id"):
            _id(getattr(self, field), field)
        level = _finite(self.measured_level, "measured_level")
        if level > 1:
            raise ValueError("measured_level must be at most 1")
        _finite(self.measured_at, "measured_at")


@dataclass(frozen=True)
class DurableFeedbackReceipt:
    status: str
    reason: str
    need: NeedSnapshot
    goal: GoalBinding

    @property
    def effect_authority(self) -> bool:
        return False


class DurableFeedbackFixture:
    def __init__(self, path: Path, initial_need: NeedSnapshot, initial_goal: GoalBinding, *,
                 verifier: Callable[[FeedbackClaim], MeasuredEffect | None] | None = None,
                 trusted_observers: frozenset[str] = frozenset()) -> None:
        if (initial_need.goal_id != initial_goal.goal_id
                or initial_goal.target_id != initial_need.need_id):
            raise ValueError("initial goal/target must bind the single need axis")
        self.path = Path(path)
        self.verifier = verifier
        self.trusted_observers = trusted_observers
        with closing(self._connect()) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS needs (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    need_id TEXT NOT NULL, goal_id TEXT NOT NULL,
                    revision INTEGER NOT NULL, current_level REAL NOT NULL,
                    setpoint REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS goals (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    goal_id TEXT NOT NULL, choice_id TEXT NOT NULL, target_id TEXT NOT NULL,
                    revision INTEGER NOT NULL, protection_veto INTEGER NOT NULL,
                    completed INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS receipts (
                    event_id TEXT PRIMARY KEY, claim_digest TEXT NOT NULL,
                    status TEXT NOT NULL, reason TEXT NOT NULL,
                    physical_effect_id TEXT UNIQUE, attempt_id TEXT UNIQUE,
                    evidence_ref TEXT UNIQUE
                );
            """)
            db.execute(
                "INSERT OR IGNORE INTO needs VALUES (1, ?, ?, ?, ?, ?)",
                (initial_need.need_id, initial_need.goal_id, initial_need.revision,
                 initial_need.current_level, initial_need.setpoint),
            )
            db.execute(
                "INSERT OR IGNORE INTO goals VALUES (1, ?, ?, ?, ?, ?, ?)",
                (initial_goal.goal_id, initial_goal.choice_id, initial_goal.target_id,
                 initial_goal.revision, int(initial_goal.protection_veto),
                 int(initial_goal.completed)),
            )
            db.commit()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA synchronous = FULL")
        return db

    @staticmethod
    def _state(db: sqlite3.Connection) -> tuple[NeedSnapshot, GoalBinding]:
        need_row = db.execute("SELECT * FROM needs WHERE singleton=1").fetchone()
        goal_row = db.execute("SELECT * FROM goals WHERE singleton=1").fetchone()
        assert need_row is not None and goal_row is not None
        need = NeedSnapshot(need_row["need_id"], need_row["goal_id"],
                            need_row["revision"], need_row["current_level"], need_row["setpoint"])
        goal = GoalBinding(goal_row["goal_id"], goal_row["choice_id"],
                           goal_row["target_id"], goal_row["revision"],
                           bool(goal_row["protection_veto"]), bool(goal_row["completed"]))
        if need.goal_id != goal.goal_id or goal.target_id != need.need_id:
            raise ValueError("fixture need/goal target binding is inconsistent")
        return need, goal

    def state(self) -> tuple[NeedSnapshot, GoalBinding]:
        with closing(self._connect()) as db:
            return self._state(db)

    def replace_goal(self, new: GoalBinding) -> DurableFeedbackReceipt:
        """Test fixture setup: simulate a new choice, NOT authorize real adoption.

        This is intentionally a local harness state transition, not a Volition
        API; the caller controls it and no external effects are available.
        """
        if not isinstance(new, GoalBinding):
            raise TypeError("typed GoalBinding required")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                need, old = self._state(db)
                if (new.goal_id, new.choice_id) == (old.goal_id, old.choice_id):
                    raise ValueError("a replacement must be a new goal/choice instance")
                if new.target_id != need.need_id:
                    raise ValueError("replacement goal cannot target another need axis")
                if new.revision != old.revision + 1 or new.completed:
                    raise ValueError("goal replacement revision must advance once")
                db.execute("UPDATE needs SET goal_id=?, revision=revision+1 WHERE singleton=1",
                           (new.goal_id,))
                db.execute("UPDATE goals SET goal_id=?, choice_id=?, target_id=?, revision=?, "
                           "protection_veto=?, completed=0 WHERE singleton=1",
                           (new.goal_id, new.choice_id, new.target_id, new.revision,
                            int(new.protection_veto)))
                updated_need, updated_goal = self._state(db)
                db.commit()
                return DurableFeedbackReceipt("ROTATED", "SIMULATED_GOAL_REPLACEMENT",
                                              updated_need, updated_goal)
            except Exception:
                db.rollback()
                raise
    def admit(self, claim: FeedbackClaim, *, now: float) -> DurableFeedbackReceipt:
        if not isinstance(claim, FeedbackClaim):
            raise TypeError("typed FeedbackClaim required")
        now = _finite(now, "now")
        digest = sha256(json.dumps(asdict(claim), sort_keys=True, separators=(",", ":"),
                                   allow_nan=False).encode()).hexdigest()
        # Callback runs without a database transaction. It is external to this
        # qualification fixture and must never be a model self-approval API.
        observation = None
        verifier_failed = False
        if self.verifier is not None:
            try:
                observation = self.verifier(claim)
            except Exception:
                verifier_failed = True
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                need, goal = self._state(db)
                previous = db.execute(
                    "SELECT claim_digest, status, reason FROM receipts WHERE event_id=?",
                    (claim.event_id,),
                ).fetchone()
                if previous is not None:
                    if previous["claim_digest"] != digest:
                        result = DurableFeedbackReceipt("HOLD", "CONFLICTING_EVENT_ID", need, goal)
                    elif previous["status"] == "APPLIED":
                        result = DurableFeedbackReceipt("REPLAY", "ALREADY_APPLIED", need, goal)
                    else:
                        result = DurableFeedbackReceipt("HOLD", previous["reason"], need, goal)
                    db.commit()
                    return result

                def hold(reason: str) -> DurableFeedbackReceipt:
                    db.execute("INSERT INTO receipts(event_id,claim_digest,status,reason) "
                               "VALUES(?, ?, 'HOLD', ?)", (claim.event_id, digest, reason))
                    db.commit()
                    return DurableFeedbackReceipt("HOLD", reason, need, goal)

                if (claim.need_id != need.need_id or claim.goal_id != goal.goal_id
                        or claim.choice_id != goal.choice_id or claim.target_id != goal.target_id):
                    return hold("STALE_OR_CROSS_GOAL")
                if (claim.expected_need_revision != need.revision
                        or claim.expected_goal_revision != goal.revision):
                    return hold("STALE_REVISION")
                if goal.protection_veto:
                    return hold("PROTECTION_VETO")
                if goal.completed:
                    return hold("GOAL_ALREADY_COMPLETED")
                if not claim.observed_at <= now < claim.expires_at:
                    return hold("OUTSIDE_OBSERVATION_WINDOW")
                if claim.claimed_status != "SUCCESS":
                    return hold("NO_VERIFIED_EFFECT")
                if self.verifier is None:
                    return hold("NO_INDEPENDENT_VERIFIER")
                if verifier_failed:
                    return hold("VERIFIER_UNAVAILABLE")
                if not isinstance(observation, MeasuredEffect):
                    return hold("UNVERIFIED_OUTCOME")
                if observation.observer_id not in self.trusted_observers:
                    return hold("UNTRUSTED_OBSERVER")
                fields = ("event_id", "attempt_id", "need_id", "goal_id", "choice_id",
                          "target_id", "evidence_ref")
                if any(getattr(claim, f) != getattr(observation, f) for f in fields):
                    return hold("WITNESS_BINDING_MISMATCH")
                if not claim.observed_at <= observation.measured_at <= now:
                    return hold("WITNESS_TIME_MISMATCH")
                level = observation.measured_level
                if type(level) not in (float, int) or not math.isfinite(float(level)) or not 0 <= level <= 1:
                    return hold("INVALID_MEASUREMENT")
                if db.execute("SELECT 1 FROM receipts WHERE status='APPLIED' AND "
                              "(physical_effect_id=? OR attempt_id=? OR evidence_ref=?)",
                              (observation.physical_effect_id, claim.attempt_id,
                               claim.evidence_ref)).fetchone():
                    return hold("DUPLICATE_PHYSICAL_EFFECT")
                if (max(0.0, need.setpoint - level)
                        >= max(0.0, need.setpoint - need.current_level)):
                    return hold("NO_MEASURED_IMPROVEMENT")

                # Both updates and the idempotency journal are one SQLite
                # transaction. Failure anywhere rolls back the entire group.
                db.execute("UPDATE needs SET current_level=?, revision=revision+1 WHERE singleton=1",
                           (level,))
                db.execute("UPDATE goals SET completed=1, revision=revision+1 WHERE singleton=1")
                db.execute(
                    "INSERT INTO receipts VALUES(?, ?, 'APPLIED', 'INJECTED_TEST_WITNESS_ACCEPTED', ?, ?, ?)",
                    (claim.event_id, digest, observation.physical_effect_id,
                     claim.attempt_id, claim.evidence_ref),
                )
                updated_need, updated_goal = self._state(db)
                db.commit()
                return DurableFeedbackReceipt("APPLIED", "INJECTED_TEST_WITNESS_ACCEPTED",
                                              updated_need, updated_goal)
            except Exception:
                db.rollback()
                raise
