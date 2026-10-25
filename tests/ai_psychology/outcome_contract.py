"""Inert reference oracle for the missing AI-psychology outcome feedback seam.

This module deliberately has no imports from MESO, Volition, or Pre-Active. It
does not authenticate observers, persist data, or execute an effect. An adapter
cannot pass cross-repo conformance merely by passing these local unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from threading import RLock
from typing import Callable


RUNTIME_INTEGRATION_STATUS = "UNWIRED_SOURCE_CONTRACT_ONLY"


def _finite_float(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{field} must be numeric")
    try:
        normalized = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not math.isfinite(normalized):
        raise ValueError(f"{field} must be finite")
    return normalized


def _unit(value: float, field: str) -> float:
    normalized = _finite_float(value, field)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field} must be finite and in [0, 1]")
    return normalized


def _time(value: float, field: str) -> float:
    normalized = _finite_float(value, field)
    if normalized < 0:
        raise ValueError(f"{field} must be finite and nonnegative")
    return normalized


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value


@dataclass(frozen=True)
class NeedSnapshot:
    need_id: str
    goal_id: str
    revision: int
    current_level: float
    setpoint: float

    def __post_init__(self) -> None:
        _text(self.need_id, "need_id")
        _text(self.goal_id, "goal_id")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer")
        _unit(self.current_level, "current_level")
        _unit(self.setpoint, "setpoint")


@dataclass(frozen=True)
class OutcomeClaim:
    event_id: str
    attempt_id: str
    need_id: str
    goal_id: str
    expected_revision: int
    asserted_status: str
    evidence_ref: str
    observed_at: float
    expires_at: float

    def __post_init__(self) -> None:
        for field in ("event_id", "attempt_id", "need_id", "goal_id", "evidence_ref"):
            _text(getattr(self, field), field)
        if isinstance(self.expected_revision, bool) or not isinstance(self.expected_revision, int) or self.expected_revision < 0:
            raise ValueError("expected_revision must be a nonnegative integer")
        if self.asserted_status not in {"SUCCESS", "NO_OP", "FAILED", "UNKNOWN"}:
            raise ValueError("invalid asserted_status")
        _time(self.observed_at, "observed_at")
        _time(self.expires_at, "expires_at")
        if self.expires_at < self.observed_at:
            raise ValueError("expires_at precedes observed_at")

    def digest(self) -> str:
        data = {field: getattr(self, field) for field in self.__dataclass_fields__}
        return sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class WitnessedMeasurement:
    """Evidence returned by a separately governed verifier, never the claim."""

    event_id: str
    attempt_id: str
    need_id: str
    goal_id: str
    evidence_ref: str
    measured_level: float
    observer_id: str
    measured_at: float

    def __post_init__(self) -> None:
        for field in ("event_id", "attempt_id", "need_id", "goal_id", "evidence_ref", "observer_id"):
            _text(getattr(self, field), field)
        _unit(self.measured_level, "measured_level")
        _time(self.measured_at, "measured_at")


@dataclass(frozen=True)
class AdmissionResult:
    status: str  # APPLIED | REPLAY | HOLD
    reason: str
    snapshot: NeedSnapshot
    measured_improvement: float = 0.0


class InMemoryContractOracle:
    """Single-process, thread-serialized test oracle; NOT a durable outcome ledger.

    The caller supplies an independently administered verifier callback.
    Authenticity of that callback and durability of its evidence are OUTSIDE
    this oracle. Without the callback, every new claim is held.
    """

    def __init__(
        self,
        initial: NeedSnapshot,
        *,
        verifier: Callable[[OutcomeClaim], WitnessedMeasurement | None] | None = None,
        trusted_observers: frozenset[str] = frozenset(),
    ) -> None:
        self.snapshot = initial
        self.verifier = verifier
        self.trusted_observers = trusted_observers
        self._lock = RLock()
        self._seen: dict[str, tuple[str, AdmissionResult]] = {}
        self._applied_attempts: set[str] = set()
        self._applied_evidence: set[str] = set()

    def admit(self, claim: OutcomeClaim, *, now: float) -> AdmissionResult:
        # Keep the snapshot/replay/causal-effect test oracle linearizable inside
        # this process. This does NOT constitute durable cross-repository CAS.
        with self._lock:
            return self._admit_locked(claim, now=now)

    def _admit_locked(self, claim: OutcomeClaim, *, now: float) -> AdmissionResult:
        _time(now, "now")
        digest = claim.digest()
        existing = self._seen.get(claim.event_id)
        if existing is not None:
            original_digest, original = existing
            if original_digest != digest:
                return AdmissionResult("HOLD", "CONFLICTING_EVENT_ID", self.snapshot)
            if original.status == "HOLD":
                # Idempotent rejection must not be presented as a successful
                # replay of an accepted, measured effect.
                return AdmissionResult("HOLD", original.reason, self.snapshot)
            return AdmissionResult("REPLAY", original.reason, self.snapshot)

        def hold(reason: str) -> AdmissionResult:
            result = AdmissionResult("HOLD", reason, self.snapshot)
            self._seen[claim.event_id] = digest, result
            return result

        if claim.need_id != self.snapshot.need_id or claim.goal_id != self.snapshot.goal_id:
            return hold("CROSS_NEED_OR_GOAL")
        # Event IDs alone do not uniquely name a physical effect. Two distinct
        # events claiming the same attempt or observer evidence cannot both
        # create a measured need update.
        if claim.attempt_id in self._applied_attempts or claim.evidence_ref in self._applied_evidence:
            return hold("DUPLICATE_ATTEMPT_OR_EVIDENCE")
        if claim.expected_revision != self.snapshot.revision:
            return hold("STALE_NEED_REVISION")
        if now < claim.observed_at or now > claim.expires_at:
            return hold("OUTSIDE_OBSERVATION_WINDOW")
        if claim.asserted_status != "SUCCESS":
            return hold("NO_VERIFIED_EFFECT")
        if self.verifier is None:
            return hold("NO_INDEPENDENT_VERIFIER")
        observation = self.verifier(claim)
        if observation is None:
            return hold("UNVERIFIED_OUTCOME")
        if observation.observer_id not in self.trusted_observers:
            return hold("UNTRUSTED_OBSERVER")
        for field in ("event_id", "attempt_id", "need_id", "goal_id", "evidence_ref"):
            if getattr(observation, field) != getattr(claim, field):
                return hold("WITNESS_BINDING_MISMATCH")
        if not claim.observed_at <= observation.measured_at <= now:
            return hold("WITNESS_TIME_MISMATCH")
        deficit_before = max(0.0, self.snapshot.setpoint - self.snapshot.current_level)
        deficit_after = max(0.0, self.snapshot.setpoint - observation.measured_level)
        improvement = deficit_before - deficit_after
        if improvement <= 0:
            return hold("NO_MEASURED_NEED_IMPROVEMENT")

        current = self.snapshot
        self.snapshot = NeedSnapshot(
            need_id=current.need_id,
            goal_id=current.goal_id,
            revision=current.revision + 1,
            current_level=observation.measured_level,
            setpoint=current.setpoint,
        )
        result = AdmissionResult("APPLIED", "INDEPENDENT_WITNESS_ACCEPTED", self.snapshot, improvement)
        self._seen[claim.event_id] = digest, result
        self._applied_attempts.add(claim.attempt_id)
        self._applied_evidence.add(claim.evidence_ref)
        return result
