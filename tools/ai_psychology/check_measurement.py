"""Strict source-only coherence check of forecast rows versus aggregate receipts.

The independent custody of labels, event timestamps, source Git commits, and
witness identities is NOT established. Coherence never implies authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

from tools.ai_psychology.score_forecasts import ScoreError, score_events
from tools.ai_psychology.validate_receipt import (
    InvalidReceipt,
    load_receipt,
    validate_receipt,
)

STATUS = "MEASUREMENT_COHERENT_EVIDENCE_UNVERIFIED"
ARMS = (
    ("baseline", "heldout", "baseline"),
    ("candidate", "heldout", "candidate"),
    ("shift_baseline", "shift", "baseline"),
    ("shift_candidate", "shift", "candidate"),
)


class MeasurementError(ValueError):
    """The claim envelopes fail format or mutual measurement consistency."""


def _same_numbers(a: object, b: object, path: str) -> None:
    if type(a) not in (int, float) or type(b) not in (int, float):
        raise MeasurementError(path + ": nonnumeric aggregate")
    if not (math.isfinite(a) and math.isfinite(b)):
        raise MeasurementError(path + ": nonfinite aggregate")
    if not math.isclose(a, b, abs_tol=1e-12, rel_tol=0.0):
        raise MeasurementError(path + ": disagrees with recomputed events")


def _same_ids(a: object, b: object, scope: str) -> None:
    if type(a) is not list or type(b) is not list or set(a) != set(b):
        raise MeasurementError(scope + ": inconsistent event/source membership")


def check_measurement(document: object) -> dict[str, Any]:
    """Check bounded claim structure against independent arithmetic recomputation.

    This checks *only* consistency across two caller-controlled views.
    Real prequential execution, label custody, and source truth remain UNKNOWN.
    """
    if type(document) is not dict or set(document) != {
        "score_claims", "evaluation_receipt"
    }:
        raise MeasurementError("expected only score_claims and evaluation_receipt")

    try:
        claims = document["score_claims"]
        receipt = document["evaluation_receipt"]
        outcome = score_events(claims)
        validated = validate_receipt(receipt)
    except (ScoreError, InvalidReceipt, OverflowError, ValueError, TypeError) as exc:
        raise MeasurementError("one or both claim envelopes are invalid") from exc

    if receipt["subject_id"] != claims["run_id"]:
        raise MeasurementError("run/subject identity mismatch")
    for key in ("source_heads", "splits"):
        if receipt[key] != claims[key]:
            raise MeasurementError(key + " claim mismatch")
    for key in ("proposer_id", "evaluator_id"):
        if receipt["roles"][key] != claims["roles"][key]:
            raise MeasurementError("role identity mismatch")

    events = claims["events"]
    _same_ids(receipt["evidence"]["event_ids"],
              [event["event_id"] for event in events], "event_ids")
    _same_ids(receipt["evidence"]["dependence_group_ids"],
              sorted({event["dependence_group_id"] for event in events}),
              "dependence_group_ids")

    for name, split, arm in ARMS:
        advertised = receipt["metrics"][name]
        actual = outcome["splits"][split][arm]
        if actual["mean_brier_answered_only"] is None:
            raise MeasurementError(
                name + ": answered-only Brier undefined when all abstain"
            )
        if advertised["n"] != actual["n"]:
            raise MeasurementError(name + ": case count mismatch")
        for claim_key, score_key in (
            ("brier", "mean_brier_answered_only"),
            ("coverage", "coverage"),
            ("abstention_rate", "abstention_rate"),
        ):
            _same_numbers(advertised[claim_key], actual[score_key],
                          name + "." + claim_key)

    # Validated aggregate matches arithmetic; it still cannot authenticate labels.
    digest = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode("utf-8")
    ).hexdigest()
    return {
        "status": STATUS,
        "subject_id": receipt["subject_id"],
        "score_claim_sha256": outcome["input_claim_sha256"],
        "receipt_claim_sha256": digest,
        "results": outcome,
        "source_claims_shape_valid": True,
        "measured_consistency_pass": True,
        "independent_custody_verified": False,
        "admission_eligible": False,
        "authorization_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check unverified score claims against unverified aggregate receipt"
    )
    parser.add_argument("claims_json", type=Path)
    args = parser.parse_args(argv)
    try:
        result = check_measurement(load_receipt(args.claims_json))
    except (MeasurementError, InvalidReceipt) as exc:
        print(json.dumps({"status": "INVALID_MEASUREMENT_CLAIMS",
                          "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
