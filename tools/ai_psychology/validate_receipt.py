"""Research-only AI psychology receipt format validation.

Valid formatting is NOT independent evaluator proof, learned model behavior,
current identity, trusted label custody, or permission to promote/deploy.
This standard-library module imports no sibling AI repositories.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import stat
import re
import sys
from typing import Any

SCHEMA = "BT2_AI_PSYCHOLOGY_EVAL_RECEIPT_V1"
VALIDATION = "FORMAT_VALID_EVIDENCE_UNVERIFIED"
SOURCES = frozenset({"meta", "humility", "driftguard", "vera_mono"})
METRIC_FIELDS = frozenset({"brier", "coverage", "abstention_rate", "n"})
METRIC_SETS = frozenset({"baseline", "candidate", "shift_baseline", "shift_candidate"})
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
MAX_BYTES = 131072


class InvalidReceipt(ValueError):
    """The supplied material fails a strict local *format* requirement."""


def _shape(value: object, fields: set[str] | frozenset[str], scope: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != fields:
        raise InvalidReceipt(f"{scope}: missing or unknown fields")
    return value


def _identifier(value: object, scope: str) -> str:
    if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
        raise InvalidReceipt(f"{scope}: expected bounded opaque identifier")
    return value


def _hex(value: object, pattern: re.Pattern[str], scope: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise InvalidReceipt(f"{scope}: expected exact lowercase digest")
    return value


def _items(value: object, scope: str) -> list[str]:
    if type(value) is not list or not value or len(value) > 4096:
        raise InvalidReceipt(f"{scope}: expected nonempty bounded list")
    ids = [_identifier(v, scope) for v in value]
    if len(set(ids)) != len(ids):
        raise InvalidReceipt(f"{scope}: duplicate identities")
    return ids


def _metric(value: object, scope: str) -> dict[str, object]:
    obj = _shape(value, METRIC_FIELDS, scope)
    n = obj["n"]
    if type(n) is not int or not 1 <= n <= 1_000_000:
        raise InvalidReceipt(f"{scope}.n: expected bounded positive integer")
    for name in ("brier", "coverage", "abstention_rate"):
        v = obj[name]
        # Range check first: math.isfinite(10**500) can raise OverflowError.
        if type(v) not in (int, float) or not 0.0 <= v <= 1.0:
            raise InvalidReceipt(f"{scope}.{name}: expected finite fraction")
        if not math.isfinite(v):
            raise InvalidReceipt(f"{scope}.{name}: expected finite fraction")
    if abs(obj["coverage"] + obj["abstention_rate"] - 1.0) > 1e-8:
        raise InvalidReceipt(f"{scope}: coverage and abstention must sum to one")
    return obj


def validate_receipt(receipt: object) -> dict[str, object]:
    """Validate only strict structure; do not authenticate any claim."""
    obj = _shape(receipt, {
        "schema", "subject_id", "source_heads", "roles", "splits", "evidence",
        "metrics", "independent_label_custody_verified", "authorization_effect",
    }, "receipt")
    if obj["schema"] != SCHEMA:
        raise InvalidReceipt("unsupported receipt schema")
    _identifier(obj["subject_id"], "subject_id")
    sources = _shape(obj["source_heads"], SOURCES, "source_heads")
    for name in sorted(SOURCES):
        _hex(sources[name], HEX40, f"source_heads.{name}")
    roles = _shape(obj["roles"], {"proposer_id", "evaluator_id"}, "roles")
    proposer = _identifier(roles["proposer_id"], "roles.proposer_id")
    evaluator = _identifier(roles["evaluator_id"], "roles.evaluator_id")
    if proposer == evaluator:
        raise InvalidReceipt("proposer and evaluator must have distinct identities")
    splits = _shape(obj["splits"], {
        "training_sha256", "heldout_sha256", "shift_sha256",
    }, "splits")
    values = [_hex(splits[k], HEX64, f"splits.{k}") for k in sorted(splits)]
    if len(set(values)) != len(values):
        raise InvalidReceipt("train, heldout and shift partitions must differ")
    evidence = _shape(obj["evidence"], {
        "event_ids", "dependence_group_ids",
        "method_execution_claim_refs", "observation_order",
    }, "evidence")
    _items(evidence["event_ids"], "evidence.event_ids")
    _items(evidence["dependence_group_ids"], "evidence.dependence_group_ids")
    _items(evidence["method_execution_claim_refs"], "evidence.method_execution_claim_refs")
    if evidence["observation_order"] != "PREQUENTIAL":
        raise InvalidReceipt("only prequential observation ordering can be claimed")
    metrics = _shape(obj["metrics"], METRIC_SETS, "metrics")
    checked = {key: _metric(metrics[key], f"metrics.{key}") for key in METRIC_SETS}
    if checked["baseline"]["n"] != checked["candidate"]["n"]:
        raise InvalidReceipt("heldout comparison counts must agree")
    if checked["shift_baseline"]["n"] != checked["shift_candidate"]["n"]:
        raise InvalidReceipt("shift comparison counts must agree")
    if obj["independent_label_custody_verified"] is not False:
        raise InvalidReceipt("this source-only validator cannot verify label custody")
    if obj["authorization_effect"] != "NONE":
        raise InvalidReceipt("evaluation is not an effect authorization")
    return {
        "schema": SCHEMA,
        "validation": VALIDATION,
        "subject_id": obj["subject_id"],
        "candidate_brier_delta": checked["candidate"]["brier"] - checked["baseline"]["brier"],
        "shift_brier_delta": checked["shift_candidate"]["brier"] - checked["shift_baseline"]["brier"],
        "independent_label_custody_verified": False,
        "authorization_effect": "NONE",
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            # Keys are untrusted input and may contain secrets; never echo them.
            raise InvalidReceipt("duplicate JSON key")
        result[key] = value
    return result


def _parse_number(token: str, *, integer: bool) -> int | float:
    if len(token) > 256:
        raise InvalidReceipt("numeric JSON token exceeds limit")
    v = int(token) if integer else float(token)
    if type(v) is float and not math.isfinite(v):
        raise InvalidReceipt("nonfinite JSON number")
    return v


def _check_nesting(raw: bytes, *, max_depth: int = 64) -> None:
    # A lexical upper bound before the JSON parser allocates nested arrays/objects.
    depth = 0
    quoted = False
    escaped = False
    for code in raw:
        if quoted:
            if escaped:
                escaped = False
            elif code == 92:  # backslash
                escaped = True
            elif code == 34:  # quote
                quoted = False
        elif code == 34:
            quoted = True
        elif code in (91, 123):  # [ {
            depth += 1
            if depth > max_depth:
                raise InvalidReceipt("JSON nesting exceeds limit")
        elif code in (93, 125):  # ] }
            depth -= 1
            if depth < 0:
                raise InvalidReceipt("malformed JSON structure")


def load_receipt(path: Path) -> object:
    # Best-effort path checks; secure opening also checks descriptor type/size.
    # Windows path reparse races cannot be ruled out by this source-only helper.
    try:
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise InvalidReceipt("symlinked receipt path is not accepted")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                raise InvalidReceipt("receipt must be a bounded ordinary file")
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InvalidReceipt("receipt exceeds byte limit")
        _check_nesting(raw)
        return json.loads(
            raw.decode("utf-8"),
            parse_int=lambda v: _parse_number(v, integer=True),
            parse_float=lambda v: _parse_number(v, integer=False),
            parse_constant=lambda v: (_ for _ in ()).throw(InvalidReceipt(f"nonfinite JSON: {v}")),
            object_pairs_hook=_unique_object,
        )
    except InvalidReceipt:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError, OverflowError) as exc:
        raise InvalidReceipt("invalid or excessively nested JSON receipt") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate untrusted research receipt format")
    parser.add_argument("receipt_json", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_receipt(load_receipt(args.receipt_json))
    except InvalidReceipt as exc:
        print(json.dumps({"validation": "INVALID_RECEIPT", "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
