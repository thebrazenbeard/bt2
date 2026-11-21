"""Ecosystem proactivity governor: pure, read-only, deterministic, no network/actions.

The governor evaluates *claims about* observed signals. It cannot authenticate
sources, install schedulers, send notifications, or authorize effects.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, replace, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Iterable, Mapping, Sequence
import re


class Action(str, Enum):
    SILENT = "stay_silent"
    DRAFT = "draft"
    QUESTION = "question"
    NOTIFY = "notify"


class EvidenceClass(str, Enum):
    SOURCE = "SOURCE_INSPECTION"
    TEST = "TEST"
    CI = "CI"
    HOST = "REAL_HOST_PROBE"
    RUNTIME = "QUALIFIED_RUNTIME"
    MODEL = "MODEL_BEHAVIOR"
    USER = "USER_FEEDBACK"
    DOC = "DOC"


KNOWN_DOMAINS = frozenset({
    "security", "coordination", "runtime", "memory", "identity", "agency",
    "models", "creative", "product", "research", "infrastructure", "privacy",
})
SHA = re.compile(r"^[0-9a-f]{40}$")
ISO_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/#@+\-]{0,160}$")


def _valid_incident_key(key) -> bool:
    return (
        isinstance(key, tuple) and len(key) == 3
        and all(type(x) is str for x in key)
        and all(ISO_KEY.fullmatch(x) is not None for x in key[:2])
        and (key[2] == "" or SHA.fullmatch(key[2]) is not None)
    )


def parse_time(value: str) -> datetime:
    d = datetime.fromisoformat(value)
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError("offset-aware timestamp required")
    return d.astimezone(timezone.utc)


@dataclass(frozen=True)
class Signal:
    signal_id: str
    fingerprint: str
    subject: str
    domain: str
    cause: str
    evidence_refs: tuple[str, ...]
    evidence_classes: tuple[EvidenceClass, ...]
    exact_head: str | None
    observed_at: str
    freshness_hours: int
    severity: int
    relevance: int
    actionability: int
    confidence: int
    hours_to_impact: int
    concrete_next_step: str
    known_to_owner: bool = False
    needs_user_decision: bool = False
    protected_effect: bool = False
    contains_private_data: bool = False
    runtime_claim: bool = False
    model_subjectivity_claim: bool = False
    owner_lane: str = "UNASSIGNED"
    needed_capabilities: tuple[str, ...] = ()
    outcome_is_release: bool = False
    corroborated: bool = False
    source_verified_by_evaluator: bool = False  # caller assertion, never crypto proof
    externally_visible: bool = False  # opt in; not proof of source authenticity

    def __post_init__(self):
        # Python treats non-empty strings and integers as truthy. Never allow
        # textual "false" or 1 to impersonate privacy or trust booleans.
        boolean_fields = (
            "known_to_owner", "needs_user_decision", "protected_effect",
            "contains_private_data", "runtime_claim", "model_subjectivity_claim",
            "outcome_is_release", "corroborated",
            "source_verified_by_evaluator", "externally_visible",
        )
        if any(type(getattr(self, name)) is not bool for name in boolean_fields):
            raise ValueError("signal boolean flags require actual booleans")
        # Numeric policy thresholds are discrete. Boolean is a subclass of
        # int, while fractional values change scoring and urgency semantics.
        integer_fields = ("freshness_hours", "hours_to_impact",
                          "severity", "relevance", "actionability", "confidence")
        if any(type(getattr(self, name)) is not int for name in integer_fields):
            raise ValueError("signal policy scores and time windows require integers")
        # Bare strings iterate by character in Python. For release
        # prerequisites this can falsely satisfy a claimed capability.
        if type(self.needed_capabilities) is not tuple or any(
            type(cap) is not str or ISO_KEY.fullmatch(cap) is None
            for cap in self.needed_capabilities
        ):
            raise ValueError("needed capabilities require bounded tuple IDs")
        if type(self.evidence_refs) is not tuple or type(self.evidence_classes) is not tuple:
            raise ValueError("evidence containers require tuples")
        if type(self.concrete_next_step) is not str:
            raise ValueError("next step requires text")
        if not all(ISO_KEY.fullmatch(v or "") for v in
                   (self.signal_id, self.fingerprint, self.subject, self.cause, self.owner_lane)):
            raise ValueError("invalid non-identifying ID")
        if self.domain not in KNOWN_DOMAINS:
            raise ValueError("unknown domain")
        if not self.evidence_refs or not self.evidence_classes:
            raise ValueError("evidence required")
        if any(not isinstance(r, str) or not r.strip() or len(r) > 320 for r in self.evidence_refs):
            raise ValueError("malformed evidence ref")
        if any(not isinstance(x, EvidenceClass) for x in self.evidence_classes):
            raise ValueError("unknown evidence class")
        if self.exact_head is not None and not SHA.fullmatch(self.exact_head):
            raise ValueError("exact 40-char Git head required if provided")
        if not 0 < self.freshness_hours <= 720 or not 0 <= self.hours_to_impact <= 720:
            raise ValueError("invalid time budget")
        if any(not 0 <= k <= 5 for k in (self.severity, self.relevance, self.actionability, self.confidence)):
            raise ValueError("scores must be integers in 0..5")
        if not self.concrete_next_step or len(self.concrete_next_step) > 240:
            raise ValueError("bounded next step required")
        parse_time(self.observed_at)


@dataclass(frozen=True)
class Context:
    """User/operator-supplied policy state; must NOT be mistaken for live provider state."""
    now: str
    known_observations: frozenset[tuple[str, str, str]] = frozenset()  # fingerprint, subject, head
    muted_domains: frozenset[str] = frozenset()
    qualified_capabilities: frozenset[str] = frozenset()
    notification_log: tuple[tuple[str, str, str, str], ...] = ()  # fingerprint, subject, exact_head, time
    daily_notification_limit: int = 1
    same_subject_cooldown_hours: int = 48
    verified_head_bindings: frozenset[tuple[str, str]] = frozenset()  # trusted-source subject/head readbacks, not signal claims
    owner_lanes: frozenset[str] = frozenset()
    verified_signal_ids: frozenset[str] = frozenset()  # MUST be supplied by independently trusted host
    trusted_owner_ack_keys: frozenset[tuple[str, str, str]] = frozenset()  # separately verified scoped owner acknowledgment
    feedback: tuple[tuple[str, str, str, str], ...] = ()  # fingerprint, subject, head, label ACCEPTED|NOISY

    def __post_init__(self):
        # These context fields carry operator policy and alleged independent
        # trust readbacks. Python permits substring membership against a
        # plain string: "s1" in "s1" is True. Reject malformed containers
        # instead of silently promoting a caller's string to an allowlist.
        set_fields = (
            "known_observations", "muted_domains", "qualified_capabilities",
            "verified_head_bindings", "owner_lanes", "verified_signal_ids",
            "trusted_owner_ack_keys",
        )
        if any(type(getattr(self, field_name)) is not frozenset
               for field_name in set_fields):
            raise ValueError("context policy sets require frozenset")
        for field_name in ("muted_domains", "qualified_capabilities",
                           "owner_lanes", "verified_signal_ids"):
            if any(type(value) is not str or ISO_KEY.fullmatch(value) is None
                   for value in getattr(self, field_name)):
                raise ValueError("context policy set members require valid strings")
        if any(type(value) is not tuple or len(value) != 2
               or type(value[0]) is not str or type(value[1]) is not str
               for value in self.verified_head_bindings):
            raise ValueError("verified head bindings require subject/head pairs")
        if type(self.notification_log) is not tuple or type(self.feedback) is not tuple:
            raise ValueError("context history and feedback require tuples")
        if type(self.daily_notification_limit) is not int or type(self.same_subject_cooldown_hours) is not int:
            raise ValueError("context numeric policy limits require integers")
        parse_time(self.now)
        if not 0 <= self.daily_notification_limit <= 3:
            raise ValueError("notification limit 0..3")
        if not 1 <= self.same_subject_cooldown_hours <= 168:
            raise ValueError("invalid cooldown")
        if not self.muted_domains.issubset(KNOWN_DOMAINS):
            raise ValueError("unknown muted domain")
        # V4 history keys must identify the exact incident, never only a
        # fingerprint or bare head. Reject old schemas rather than silently
        # granting their cross-subject suppression authority.
        for key in self.known_observations:
            if not _valid_incident_key(key):
                raise ValueError("known observations require fingerprint, subject, head")
        for key in self.trusted_owner_ack_keys:
            if not _valid_incident_key(key):
                raise ValueError("trusted owner ACKs require fingerprint, subject, head")
        for event in self.feedback:
            if (not isinstance(event, tuple) or len(event) != 4 or
                not _valid_incident_key(event[:3]) or event[3] not in ("ACCEPTED", "NOISY")):
                raise ValueError("feedback requires fingerprint, subject, head, explicit label")
        for entry in self.notification_log:
            if not isinstance(entry, tuple) or len(entry) != 4 or not _valid_incident_key(entry[:3]):
                raise ValueError("notification log requires fingerprint, subject, head, time")
            parse_time(entry[3])
        for subject, head in self.verified_head_bindings:
            if not ISO_KEY.fullmatch(subject) or not SHA.fullmatch(head):
                raise ValueError("invalid source head binding")


@dataclass(frozen=True)
class Decision:
    fingerprint: str
    subject: str
    domain: str
    action: Action
    priority: float
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    next_step: str
    owner_lane: str
    source_head: str | None
    effect_authority: bool = False
    source_authenticity_verified: bool = False
    runtime_currentness_verified: bool = False
    emitted: bool = False  # A proposal to notify is never an actual notification
    private_subject: bool = False

    def public_record(self):
        """Public projection only; private Decisions get a constant sentinel.

        Masking the fingerprint alone leaks a private classification through
        domain, priority, action and reason codes. Those fields are never
        included for private/local-only Decisions.
        """
        if self.private_subject:
            return {"redacted": True, "effect_authority": False, "emitted": False}
        return {"fingerprint": self.fingerprint, "domain": self.domain,
                "action": self.action.value, "priority": self.priority,
                "reason_codes": list(self.reasons), "effect_authority": False,
                "emitted": False}


@dataclass(frozen=True)
class Batch:
    decisions: tuple[Decision, ...]
    dropped_duplicate_signal_ids: tuple[str, ...]
    observed_count: int
    currentness_source_only: bool = True
    monitor_is_active: bool = False
    external_effects: bool = False
    # Derived exclusively from public source signals. This is deliberately
    # distinct from internal decisions, which may be influenced by private
    # fingerprint collisions and same-incident duplicates.
    _public_decisions: tuple[Decision, ...] = field(default_factory=tuple,
                                                      repr=False, compare=False)

    def public_record(self) -> dict:
        """Explicit safe projection, not a generic dataclass serializer.

        The raw Batch is an internal object: dropped duplicate signal IDs,
        private subjects and original Decision fields must never be exported
        through an unfiltered asdict/json serializer.
        """
        return {
            # A masked private record still discloses the existence,
            # domain and priority of a local-only finding.
            "decisions": [d.public_record() for d in self._public_decisions
                          if not d.private_subject],
            "currentness_source_only": True,
            "monitor_is_active": False,
            "external_effects": False,
        }


def _score(s: Signal) -> float:
    return round((0.30 * s.severity + 0.25 * s.relevance
                  + 0.25 * s.actionability + 0.20 * s.confidence), 2)


def _today_notifications(c: Context) -> int:
    n = parse_time(c.now)
    return sum(1 for _, _, _, t in c.notification_log if
               parse_time(t).astimezone(n.tzinfo).date() == n.date()
               and 0 <= (n - parse_time(t)).total_seconds() <= 86400)


def _recent_duplicate(s: Signal, c: Context) -> bool:
    now = parse_time(c.now)
    return any((f, subject, h) == (s.fingerprint, s.subject, s.exact_head or "")
               and 0 <= (now - parse_time(t)).total_seconds()
               <= c.same_subject_cooldown_hours * 3600
               for f, subject, h, t in c.notification_log)


def decide_one(s: Signal, c: Context, slots_used: int = 0) -> Decision:
    now = parse_time(c.now)
    age = (now - parse_time(s.observed_at)).total_seconds() / 3600
    priority = _score(s)
    reasons = []
    action = Action.SILENT
    missing = tuple(x for x in s.needed_capabilities if x not in c.qualified_capabilities)

    if age < 0:
        reasons.append("FUTURE_OBSERVATION")
    elif age > s.freshness_hours:
        reasons.append("STALE_SUBJECT")
    elif s.domain in c.muted_domains or (s.fingerprint, s.subject, s.exact_head or "", "NOISY") in c.feedback:
        # Respect the user's no-interruption choice, but do not erase a
        # separately source-verified severe finding from private review.
        if (s.severity >= 4 and s.actionability >= 3 and
                s.signal_id in c.verified_signal_ids and s.source_verified_by_evaluator):
            action = Action.DRAFT
        reasons.append("USER_FEEDBACK_SUPPRESSION")
    elif (s.fingerprint, s.subject, s.exact_head or "") in c.known_observations or _recent_duplicate(s, c):
        reasons.append("ALREADY_KNOWN_OR_DUPLICATE")
    elif (s.contains_private_data or not s.externally_visible):
        action = Action.DRAFT if s.actionability >= 3 else Action.SILENT
        reasons.append("PRIVATE_LOCAL_ONLY")
    elif s.model_subjectivity_claim:
        action = Action.DRAFT
        reasons.append("SUBJECTIVITY_UNVERIFIED")
    elif s.runtime_claim and EvidenceClass.RUNTIME not in s.evidence_classes and EvidenceClass.HOST not in s.evidence_classes:
        action = Action.DRAFT
        reasons.append("SOURCE_NOT_RUNTIME_EVIDENCE")
    elif s.outcome_is_release and missing:
        action = Action.DRAFT
        reasons.append("RELEASE_DEPENDENCY_HOLD")
    elif s.exact_head is not None and (s.subject, s.exact_head) not in c.verified_head_bindings:
        # Syntax and caller assertions cannot bind mutable Git state. An
        # independent reader must supply an exact subject/head observation.
        # This library does not authenticate that reader or guarantee freshness.
        action = Action.DRAFT if s.actionability >= 3 else Action.SILENT
        reasons.append("UNVERIFIED_HEAD_BINDING")
    elif s.owner_lane == "UNASSIGNED" or s.owner_lane not in c.owner_lanes:
        action = Action.DRAFT
        reasons.append("DIFFERENT_WRITER_OWNER")
    elif not s.source_verified_by_evaluator or s.signal_id not in c.verified_signal_ids:
        action = Action.DRAFT if s.actionability >= 3 else Action.SILENT
        reasons.append("UNVERIFIED_SOURCE_ASSERTION")
    elif (s.fingerprint, s.subject, s.exact_head or "") in c.trusted_owner_ack_keys:
        action = Action.DRAFT if s.actionability >= 3 else Action.SILENT
        reasons.append("OWNER_ALREADY_AWARE")
    elif s.needs_user_decision and priority >= 3.5:
        action = Action.QUESTION
        reasons.append("EXPLICIT_OWNER_DECISION_NEEDED")
    elif (priority >= 4.15 and s.hours_to_impact <= 48
          and s.corroborated and s.severity >= 4 and s.actionability >= 4
          and s.confidence >= 4):
        action = Action.NOTIFY
        reasons.append("HIGH_CONFIDENCE_URGENT_ACTIONABLE")
    elif priority >= 3.0 and s.actionability >= 3:
        action = Action.DRAFT
        reasons.append("WORTH_DRAFTING_WITHOUT_INTERRUPTION")
    else:
        reasons.append("LOW_VALUE_OR_UNGROUNDED")

    if action == Action.NOTIFY and _today_notifications(c) + slots_used >= c.daily_notification_limit:
        action = Action.DRAFT
        reasons.append("INTERRUPTION_BUDGET_EXHAUSTED")
    if action == Action.NOTIFY and _recent_duplicate(s, c):
        action = Action.SILENT
        reasons.append("COOLDOWN")
    if s.protected_effect:
        reasons.append("PROTECTED_EFFECT_REQUIRES_SEPARATE_AUTHORITY")
    if missing:
        reasons.append("MISSING_DEPENDENCY")
    # Either explicit privacy condition makes the whole decision local-only.
    # Externally invisible data cannot become public when another flag is absent.
    private_local = s.contains_private_data or not s.externally_visible
    return Decision(s.fingerprint, s.subject, s.domain, action, priority,
                    tuple(reasons), s.evidence_refs if not private_local else (),
                    s.concrete_next_step if not private_local else "Review privately in authorized scope",
                    s.owner_lane, s.exact_head, private_subject=private_local)


def _evaluate_core(signals: Sequence[Signal], context: Context, *, max_scan: int = 40) -> Batch:
    """Evaluate one internally scoped batch; never serialize directly."""
    if not 1 <= max_scan <= 100:
        raise ValueError("bounded scan required")
    if len(signals) > max_scan:
        raise ValueError("batch exceeds analysis budget; paginate with stable cursor")
    # Group equal incident IDs before deciding; selecting the first report
    # would let an unverified low-risk claim suppress a verified severe one,
    # or let a forged high-risk claim win simply by reversing input order.
    grouped_by_instance: dict[tuple[str, str, str | None], list[Signal]] = {}
    for s in signals:
        grouped_by_instance.setdefault((s.fingerprint, s.subject, s.exact_head), []).append(s)
    by_instance: dict[tuple[str, str, str | None], Signal] = {}
    exact_conflicts: set[tuple[str, str, str | None]] = set()
    dropped: list[str] = []
    material_fields = tuple(f.name for f in fields(Signal)
                            if f.name not in ("signal_id", "evidence_refs"))
    for key, reports in grouped_by_instance.items():
        # Equivalent duplicate reporters may differ in ID and evidence
        # location only if their independently asserted ID verification state
        # is also identical. Neither source text nor arrival order grants trust.
        ordered = sorted(reports, key=lambda s: (s.signal_id, s.evidence_refs))
        first = ordered[0]
        by_instance[key] = first
        # Preserve the existing private coalescing audit trail, including
        # conflicting reports; the Decision itself is now held for review.
        dropped.extend(s.signal_id for s in ordered[1:])
        for candidate in ordered[1:]:
            if (any(getattr(candidate, name) != getattr(first, name)
                    for name in material_fields)
                    or ((candidate.signal_id in context.verified_signal_ids)
                        != (first.signal_id in context.verified_signal_ids))):
                exact_conflicts.add(key)
                break
    grouped: dict[str, list[tuple[str, str, str | None]]] = {}
    for key in by_instance:
        grouped.setdefault(key[0], []).append(key)
    collisions = {fp for fp, keys in grouped.items() if len(keys) > 1}
    proposals = []
    for key, s in by_instance.items():
        if key in exact_conflicts:
            # A constant internal hold (not a public Decision), regardless
            # of severity, ownership or which conflicting report came first.
            # No external decision or priority may inherit either claim.
            proposals.append(Decision(
                key[0], key[1], "coordination", Action.DRAFT, 0.0,
                ("EXACT_INCIDENT_CONFLICT",), (), "Review privately in authorized scope",
                "UNASSIGNED", key[2], private_subject=True))
            continue
        if s.fingerprint in collisions:
            s = replace(s, source_verified_by_evaluator=False, corroborated=False)
        dec = decide_one(s, context)
        if s.fingerprint in collisions:
            # A stale or future report remains silent, never reactivated.
            if dec.action != Action.SILENT or 'ALREADY_KNOWN_OR_DUPLICATE' in dec.reasons:
                dec = replace(dec, action=Action.DRAFT)
            dec = replace(dec, reasons=dec.reasons + ("FINGERPRINT_COLLISION",))
        proposals.append(dec)
    proposals.sort(key=lambda x: (-x.priority, x.fingerprint, x.subject))
    notices = 0
    outputs = []
    for dec in proposals:
        if dec.action == Action.NOTIFY:
            if _today_notifications(context) + notices >= context.daily_notification_limit:
                dec = replace(dec, action=Action.DRAFT, reasons=dec.reasons + ("INTERRUPTION_BUDGET_EXHAUSTED",))
            else:
                notices += 1
        outputs.append(dec)
    return Batch(tuple(outputs), tuple(dropped), len(signals))


def evaluate(signals: Sequence[Signal], context: Context, *, max_scan: int = 40) -> Batch:
    """Return internal decisions and a public view independent of private signals.

    Public decisions are computed from public-only inputs *before* deduplication,
    collision quarantine and notification-slot allocation. A public and private
    signal describing the exact same incident is ambiguous and cannot be
    declassified merely because one input says it is publicly visible.
    """
    internal = _evaluate_core(signals, context, max_scan=max_scan)
    def identity(s: Signal):
        return (s.fingerprint, s.subject, s.exact_head)

    private_keys = {identity(s) for s in signals
                    if s.contains_private_data or not s.externally_visible}
    public_signals = tuple(s for s in signals
                           if not s.contains_private_data and s.externally_visible
                           and identity(s) not in private_keys)
    visible = _evaluate_core(public_signals, context, max_scan=max_scan)
    return replace(internal, _public_decisions=visible.decisions)


def measure(decisions: Sequence[Decision], ground_truth: Mapping[tuple[str, str, str], str], k: int = 3) -> dict:
    """Synthetic evaluator with subject-bound labels, never independent judgment."""
    def key(d: Decision) -> tuple[str, str, str]:
        return (d.fingerprint, d.subject, d.source_head or "")

    assessed = [d for d in decisions if key(d) in ground_truth]
    matched = sum(d.action.value == ground_truth[key(d)] for d in assessed)
    interruptions = [d for d in assessed if d.action in (Action.NOTIFY, Action.QUESTION)]
    false_interrupts = sum(ground_truth[key(d)] not in (Action.NOTIFY.value, Action.QUESTION.value)
                           for d in interruptions)
    top = sorted(assessed, key=lambda d: -d.priority)[:k]
    top_relevance = sum(ground_truth[key(d)] != Action.SILENT.value for d in top)
    grounded = sum(bool(d.evidence_refs and d.source_head) for d in assessed)
    return {"total": len(assessed), "agreement_rate": round(matched / len(assessed), 3) if assessed else None,
            "grounding_fraction": round(grounded / len(assessed), 3) if assessed else None,
            "false_interruption_fraction": round(false_interrupts / len(interruptions), 3) if interruptions else 0.0,
            "hit_at_k": round(top_relevance / len(top), 3) if top else None,
            "independent_ground_truth": False}
