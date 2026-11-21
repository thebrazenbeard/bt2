"""Pure, read-only portfolio impact / diverse briefing helpers.

Graph edges are hypotheses owned by a source inventory: a dependency relation
never establishes runtime installation, technical permission, or causality.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from .engine import Action, Batch, Context, Decision, _valid_incident_key


@dataclass(frozen=True)
class DependencyEdge:
    consumer: str
    requires: str
    reason: str
    source_ref: str

    def __post_init__(self):
        if not all((self.consumer, self.requires, self.reason, self.source_ref)):
            raise ValueError("explicit source-linked dependency required")


def blocked_consumers(edges: Sequence[DependencyEdge], qualified: frozenset[str]):
    """Declared dependency reachability only; never installation/currentness proof."""
    result: dict[str, list[str]] = {}
    for edge in edges:
        if edge.requires not in qualified:
            result.setdefault(edge.consumer, []).append(edge.requires)
    return {consumer: tuple(sorted(set(missing))) for consumer, missing in sorted(result.items())}


def diverse_briefing(batch: Batch, limit: int = 6, max_per_domain: int = 2):
    """Prevents one noisy domain from occupying the whole cross-ecosystem review."""
    if not 1 <= limit <= 20 or not 1 <= max_per_domain <= limit:
        raise ValueError("bounded diversity budget required")
    counts: dict[str, int] = {}
    selected = []
    for decision in batch.decisions:
        if decision.action == Action.SILENT:
            continue
        if counts.get(decision.domain, 0) >= max_per_domain:
            continue
        selected.append(decision)
        counts[decision.domain] = counts.get(decision.domain, 0) + 1
        if len(selected) >= limit:
            break
    return tuple(selected)


def explicit_feedback(context: Context, fingerprint: str, subject: str,
                      exact_head: str, label: str) -> Context:
    """Apply explicitly scoped feedback to a single incident only.

    Caller must establish real principal/consent; this helper does not.
    Legacy fingerprint-only calls are deliberately incompatible with V4.
    """
    from dataclasses import replace
    key = (fingerprint, subject, exact_head)
    if not _valid_incident_key(key):
        raise ValueError("feedback requires a typed subject and exact head")
    if label not in ("ACCEPTED", "NOISY"):
        raise ValueError("only explicit labels")
    existing = [entry for entry in context.feedback if entry[:3] != key]
    return replace(context, feedback=tuple(existing + [(*key, label)]))
