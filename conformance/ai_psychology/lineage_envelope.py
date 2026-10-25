"""Pure source-only forward/outcome correlation advisory for AI psychology.

This does not verify observers, install a runtime, grant effect authority, or
apply MESO/Volition state. All records supplied to this module are untrusted
test fixtures or caller assertions. Even a structural match is NOT admission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
import re


RUNTIME_INTEGRATION_STATUS = "UNWIRED_CORRELATION_ADVISORY_ONLY"
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_SOURCE_KINDS = frozenset(
    {"observer", "tool_result", "operator_statement", "model_generated"}
)
_CLAIMED_OUTCOMES = frozenset({"SUCCESS", "FAILURE", "NO_EFFECT", "UNKNOWN"})


def _name(value: str, field: str) -> str:
    if (
        type(value) is not str
        or not value.strip()
        or len(value) > 2048
        or any(ord(char) < 32 for char in value)
    ):
        raise ValueError(f"{field}: expected bounded opaque identifier")
    return value


def _timestamp(value: float, field: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{field}: expected finite nonnegative timestamp")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{field}: expected finite nonnegative timestamp") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{field}: expected finite nonnegative timestamp")
    return value


@dataclass(frozen=True, slots=True)
class ForwardTrace:
    """Caller-supplied MESO ingress -> signal -> goal receipt relationship."""

    meso_source_event_id: str
    signal_event_id: str
    goal_id: str
    choice_id: str
    target_id: str

    def __post_init__(self) -> None:
        for field in self.__dataclass_fields__:
            _name(getattr(self, field), field)


@dataclass(frozen=True, slots=True)
class CurrentGoalBinding:
    """Claim about the current goal receipt, NOT authenticated by this module."""

    goal_id: str
    choice_id: str
    target_id: str
    signal_event_id: str

    def __post_init__(self) -> None:
        for field in self.__dataclass_fields__:
            _name(getattr(self, field), field)


@dataclass(frozen=True, slots=True)
class CandidateTrace:
    """The V1 outcome candidate's useful correlation fields, still unverified.

    Notably, V1 candidates lack choice_id and MESO source/signal IDs; these
    are looked up separately from forward and goal receipt assertions. need_id
    is claimant-supplied and cannot be derived from MESO's current intent path.
    """

    candidate_event_id: str  # Pre-Active OutcomeCandidate.event_id
    need_id: str
    goal_id: str
    action_request_id: str | None
    claimed_outcome: str
    claimed_need_change: float
    state: str
    source_kind: str
    source_actor_id: str
    source_revision: str
    evidence_ref: str
    evidence_sha256: str
    observed_at: float
    expires_at: float
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("unsupported Pre-Active V1 claim schema")
        for field in (
            "candidate_event_id", "need_id", "goal_id", "source_actor_id",
            "source_revision", "evidence_ref",
        ):
            _name(getattr(self, field), field)
        if self.action_request_id is not None:
            _name(self.action_request_id, "action_request_id")
        if self.claimed_outcome not in _CLAIMED_OUTCOMES:
            raise ValueError("unsupported claimed_outcome")
        if self.state not in {"CANDIDATE", "REJECTED"}:
            raise ValueError("unsupported candidate state")
        if self.source_kind not in _SOURCE_KINDS:
            raise ValueError("unsupported source_kind claim")
        if type(self.evidence_sha256) is not str or _DIGEST.fullmatch(self.evidence_sha256) is None:
            raise ValueError("evidence_sha256: expected lowercase SHA-256 hex")
        claimed_delta = self.claimed_need_change
        if type(claimed_delta) not in (float, int):
            raise ValueError("claimed_need_change: expected normalized finite delta")
        try:
            claimed_delta = float(claimed_delta)
        except (OverflowError, ValueError) as exc:
            raise ValueError("claimed_need_change: expected normalized finite delta") from exc
        if not math.isfinite(claimed_delta) or not -1.0 <= claimed_delta <= 1.0:
            raise ValueError("claimed_need_change: expected normalized finite delta")
        if self.claimed_outcome in {"NO_EFFECT", "UNKNOWN"} and claimed_delta != 0:
            raise ValueError("no-effect or unknown claim cannot assert need change")
        if self.claimed_outcome == "FAILURE" and claimed_delta > 0:
            raise ValueError("failure cannot assert positive need change")
        if self.claimed_outcome == "SUCCESS" and claimed_delta < 0:
            raise ValueError("success cannot assert negative need change")
        object.__setattr__(self, "claimed_need_change", claimed_delta)
        first = _timestamp(self.observed_at, "observed_at")
        last = _timestamp(self.expires_at, "expires_at")
        if last <= first:
            raise ValueError("expires_at must follow observed_at")
        object.__setattr__(self, "observed_at", first)
        object.__setattr__(self, "expires_at", last)


@dataclass(frozen=True, slots=True)
class CorrelationAdvisory:
    status: str  # CORRELATED_UNVERIFIED | DUPLICATE_UNVERIFIED | HOLD
    reason: str
    candidate_event_id: str
    need_id_claim: str
    correlation_sha256: str

    @property
    def authorization_effect(self) -> str:
        return "NONE"

    @property
    def may_complete_goal(self) -> bool:
        return False

    @property
    def may_update_need(self) -> bool:
        return False

    @property
    def need_id_is_attested(self) -> bool:
        return False

    @property
    def candidate_choice_link_verified(self) -> bool:
        """V1 candidates contain no choice ID and cannot prove causality."""
        return False

    @property
    def source_receipts_authenticated(self) -> bool:
        return False

    @property
    def evidence_admitted(self) -> bool:
        return False

    @property
    def action_effect_verified(self) -> bool:
        return False

    @property
    def absolute_need_observation_admitted(self) -> bool:
        """A signed absolute need observation is absent, regardless of delta."""
        return False


def correlate_candidate(
    forward: ForwardTrace,
    candidate: CandidateTrace,
    current: CurrentGoalBinding,
    *,
    now: float,
) -> CorrelationAdvisory:
    """Check lexical/referential consistency; NEVER authenticate or satisfy."""
    if not isinstance(forward, ForwardTrace) or not isinstance(candidate, CandidateTrace):
        raise TypeError("typed forward and outcome candidate required")
    if not isinstance(current, CurrentGoalBinding):
        raise TypeError("typed current-goal receipt required")
    now = _timestamp(now, "now")
    payload = {"forward": asdict(forward), "candidate": asdict(candidate), "current": asdict(current)}
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

    def advisory(status: str, reason: str) -> CorrelationAdvisory:
        return CorrelationAdvisory(status, reason, candidate.candidate_event_id, candidate.need_id, digest)

    if (forward.goal_id, forward.choice_id) != (current.goal_id, current.choice_id):
        return advisory("HOLD", "STALE_GOAL_INSTANCE")
    if forward.signal_event_id != current.signal_event_id:
        return advisory("HOLD", "SIGNAL_RECEIPT_MISMATCH")
    if forward.target_id != current.target_id:
        return advisory("HOLD", "TARGET_MISMATCH")
    if candidate.goal_id != forward.goal_id:
        return advisory("HOLD", "CANDIDATE_GOAL_MISMATCH")
    if candidate.state != "CANDIDATE":
        return advisory("HOLD", "CANDIDATE_NOT_ACTIVE")
    if now < candidate.observed_at or now >= candidate.expires_at:
        return advisory("HOLD", "CANDIDATE_OUTSIDE_WINDOW")
    if candidate.source_kind == "model_generated":
        return advisory("HOLD", "MODEL_SELF_REPORT")
    return advisory("CORRELATED_UNVERIFIED", "CLAIMED_LINEAGE_ONLY")


class InertLineageIndex:
    """Volatile duplicate detector; cannot be used as durable replay custody."""

    is_durable = False

    def __init__(self) -> None:
        self._seen: dict[str, tuple[str, CorrelationAdvisory]] = {}

    def record(self, advisory: CorrelationAdvisory) -> CorrelationAdvisory:
        if not isinstance(advisory, CorrelationAdvisory):
            raise TypeError("typed correlation advisory required")
        original = self._seen.get(advisory.candidate_event_id)
        if original is not None:
            digest, first = original
            if digest == advisory.correlation_sha256:
                if first.status == "HOLD":
                    return first
                return CorrelationAdvisory(
                    "DUPLICATE_UNVERIFIED", "REPLAY_OF_UNVERIFIED_CANDIDATE",
                    advisory.candidate_event_id, advisory.need_id_claim, advisory.correlation_sha256,
                )
            return CorrelationAdvisory(
                "HOLD", "CONFLICTING_CANDIDATE_ID",
                advisory.candidate_event_id, advisory.need_id_claim, advisory.correlation_sha256,
            )
        # Even local rejections reserve an event ID so a modified claim cannot
        # be retried under the same identity. No disk persistence is implied.
        self._seen[advisory.candidate_event_id] = advisory.correlation_sha256, advisory
        return advisory

    def count(self) -> int:
        return len(self._seen)
