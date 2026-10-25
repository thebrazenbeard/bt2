"""Deterministic research-only scoring of *claimed* paired binary forecasts.

Recomputes descriptive losses from the submitted rows. This never verifies
outcomes, timestamps, reviewer identities, source hashes, or split custody.
It emits no DriftGuard CI report, training result, trusted PASS, or effect.
"""
from __future__ import annotations

import math
import re
from typing import Any

SCHEMA = "BT2_PAIRED_FORECAST_SCORE_V1"
STATUS = "RECOMPUTED_FROM_UNVERIFIED_CLAIMS"
ABSTENTION_LOSS = 0.25
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
HEADS = frozenset({"meta", "humility", "driftguard", "vera_mono"})
SPLITS = ("heldout", "shift")
MAX_EVENTS = 1000

class ScoreError(ValueError):
    """Malformed, inconsistent, or over-authorizing input."""


def _shape(value: object, keys: set[str] | frozenset[str], name: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise ScoreError(f"{name}: unexpected or missing field")
    return value


def _id(value: object, name: str) -> str:
    if type(value) is not str or IDENT.fullmatch(value) is None:
        raise ScoreError(f"{name}: invalid opaque identifier")
    return value


def _digest(value: object, pattern: re.Pattern[str], name: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ScoreError(f"{name}: malformed unverified digest claim")
    return value


def _time(value: object, name: str) -> int:
    if type(value) is not int or not 0 < value < 2**63:
        raise ScoreError(f"{name}: must be positive bounded integer")
    return value


def _prob(value: object, name: str) -> float | None:
    if value is None:
        return None
    if type(value) not in (int, float) or not 0 <= value <= 1:
        raise ScoreError(f"{name}: invalid probability")
    if not math.isfinite(value):
        raise ScoreError(f"{name}: nonfinite probability")
    return float(value)


def _identifiers(value: object, name: str) -> set[str]:
    if type(value) is not list or not value or len(value) > MAX_EVENTS:
        raise ScoreError(f"{name}: nonempty bounded list required")
    ids = [_id(v, name) for v in value]
    if len(ids) != len(set(ids)):
        raise ScoreError(f"{name}: duplicate value")
    return set(ids)


def _measure(values: list[float | None], outcomes: list[int]) -> dict[str, object]:
    losses = [
        ABSTENTION_LOSS if p is None else (p - outcome) ** 2
        for p, outcome in zip(values, outcomes, strict=True)
    ]
    predicted = [p for p in values if p is not None]
    return {
        "n": len(values),
        "coverage": len(predicted) / len(values),
        "abstention_rate": (len(values) - len(predicted)) / len(values),
        "mean_fixed_loss": math.fsum(losses) / len(losses),
        "abstention_fixed_loss": ABSTENTION_LOSS,
    }


def score_events(raw: object) -> dict[str, object]:
    """Score caller-supplied rows only, with no authority or evidence admission."""
    doc = _shape(raw, {
        "schema", "run_id", "source_heads", "roles", "splits",
        "training_cutoff_epoch_ms", "train_group_ids", "events",
        "authorization_effect",
    }, "score_input")
    if doc["schema"] != SCHEMA:
        raise ScoreError("unsupported score schema")
    run_id = _id(doc["run_id"], "run_id")
    if doc["authorization_effect"] != "NONE":
        raise ScoreError("research scoring cannot authorize effects")
    heads = _shape(doc["source_heads"], HEADS, "source_heads")
    for key in sorted(HEADS):
        _digest(heads[key], HEX40, "source_heads." + key)
    roles = _shape(doc["roles"], {
        "proposer_id", "evaluator_id", "outcome_releaser_id",
    }, "roles")
    if len(set(_id(roles[k], k) for k in roles)) != 3:
        raise ScoreError("claimed role labels must be different")
    splits = _shape(doc["splits"], {
        "training_sha256", "heldout_sha256", "shift_sha256",
    }, "splits")
    digests = [_digest(splits[k], HEX64, k) for k in sorted(splits)]
    if len(set(digests)) != 3:
        raise ScoreError("split digest claims must differ")
    cutoff = _time(doc["training_cutoff_epoch_ms"], "training_cutoff_epoch_ms")
    train_groups = _identifiers(doc["train_group_ids"], "train_group_ids")
    events = doc["events"]
    if type(events) is not list or not 2 <= len(events) <= MAX_EVENTS:
        raise ScoreError("bounded heldout and shift events required")
    seen_events: set[str] = set()
    seen_forecasts: set[str] = set()
    family_split: dict[str, str] = {}
    rows: dict[str, list[tuple[float | None, float | None, int]]] = {
        split: [] for split in SPLITS
    }
    for index, event in enumerate(events):
        name = f"events[{index}]"
        obj = _shape(event, {
            "event_id", "split", "dependence_group_id", "outcome",
            "label_release_epoch_ms", "baseline", "candidate",
        }, name)
        event_id = _id(obj["event_id"], name + ".event_id")
        if event_id in seen_events:
            raise ScoreError("duplicate event identity")
        seen_events.add(event_id)
        split = obj["split"]
        if type(split) is not str or split not in SPLITS:
            raise ScoreError("training events cannot be scored")
        group = _id(obj["dependence_group_id"], name + ".dependence_group_id")
        if group in train_groups:
            raise ScoreError("group overlaps declared training partition")
        old = family_split.setdefault(group, split)
        if old != split:
            raise ScoreError("dependence group crosses heldout and shift")
        outcome = obj["outcome"]
        if type(outcome) is not int or outcome not in (0, 1):
            raise ScoreError("outcome must be exactly binary")
        release = _time(obj["label_release_epoch_ms"], name + ".label_release_epoch_ms")
        probs: list[float | None] = []
        for arm in ("baseline", "candidate"):
            claim = _shape(obj[arm], {
                "forecast_id", "issued_epoch_ms", "p_true",
            }, name + "." + arm)
            forecast_id = _id(claim["forecast_id"], name + "." + arm + ".forecast_id")
            if forecast_id in seen_forecasts:
                raise ScoreError("duplicate forecast identity")
            seen_forecasts.add(forecast_id)
            issued = _time(claim["issued_epoch_ms"], name + "." + arm + ".issued")
            if not cutoff < issued < release:
                raise ScoreError("claimed forecast/release order is not prequential")
            probs.append(_prob(claim["p_true"], name + "." + arm + ".p_true"))
        rows[split].append((probs[0], probs[1], outcome))
    if not rows["heldout"] or not rows["shift"]:
        raise ScoreError("both heldout and shift cohorts required")
    results: dict[str, dict[str, object]] = {}
    for split in SPLITS:
        values = rows[split]
        actual = [r[2] for r in values]
        baseline = _measure([r[0] for r in values], actual)
        candidate = _measure([r[1] for r in values], actual)
        results[split] = {
            "n": len(values),
            "claimed_distinct_dependence_groups": len(
                {group for group, belonging in family_split.items() if belonging == split}
            ),
            "baseline": baseline,
            "candidate": candidate,
            "delta_candidate_minus_baseline": (
                candidate["mean_fixed_loss"] - baseline["mean_fixed_loss"]
            ),
        }
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "status": STATUS,
        "preview_only": True,
        "independent_custody_verified": False,
        "authorization_effect": "NONE",
        "splits": results,
        "driftguard_preview": {
            "schema": "BT2_DRIFTGUARD_UNTRUSTED_PREVIEW_V1",
            "admission_eligible": False,
            "authorization_effect": "NONE",
            "candidate_loss_claimed_heldout": results["heldout"]["candidate"]["mean_fixed_loss"],
            "candidate_loss_claimed_shift": results["shift"]["candidate"]["mean_fixed_loss"],
        },
    }
