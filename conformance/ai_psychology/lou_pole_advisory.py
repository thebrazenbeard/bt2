"""Bounded Lou-Pole JSON handoff into AI-psychology *advisory* evidence.

No Lou-Pole code is imported or executed here. A report's contents and claimed
engine revision are NOT authenticated by matching a source-text digest. This
tool can never grant authorization, attest execution, or clear a policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


SCHEMA = "BT2_LOU_POLE_ADVISORY_V1"
MAX_SOURCE_BYTES = 65536
MAX_REPORT_BYTES = 131072
MAX_ARTIFACT_BYTES = 65536
MAX_FINDINGS = 64
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
PROFILES = {"auto", "instructions", "code", "mixed"}
COVERAGE_STATUSES = {
    "empty_input", "no_rules_extracted", "heuristic_partial",
    "heuristic_extracted_unverified",
}


class InvalidAdvisory(ValueError):
    """Input cannot be admitted even as untrusted advisory material."""


def _fields(value: object, expected: set[str], scope: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        raise InvalidAdvisory(f"{scope}: missing or unexpected fields")
    return value


def _string(value: object, scope: str, limit: int = 2048) -> str:
    if type(value) is not str or len(value.encode("utf-8", errors="surrogatepass")) > limit:
        raise InvalidAdvisory(f"{scope}: not bounded text")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise InvalidAdvisory(f"{scope}: malformed Unicode") from exc
    return value


def _count(value: object, scope: str, maximum: int = 65536) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise InvalidAdvisory(f"{scope}: invalid bounded count")
    return value


def _exact_evidence(value: object, lines: list[str]) -> dict[str, object]:
    ev = _fields(value, {"line_start", "line_end", "text"}, "evidence")
    start = _count(ev["line_start"], "line_start")
    end = _count(ev["line_end"], "line_end")
    if start < 1 or end < start or end > len(lines):
        raise InvalidAdvisory("evidence: source span out of bounds")
    raw = _string(ev["text"], "evidence.text", 4096)
    if not raw.strip() or raw not in "\n".join(lines[start - 1:end]):
        raise InvalidAdvisory("evidence: text absent at declared source lines")
    return {"line_start": start, "line_end": end, "text": raw}


def build_advisory(
    source_bytes: bytes, report: object, *, engine_revision: str,
) -> dict[str, object]:
    """Validate source alignment, not analyzer authenticity or behavioral safety."""
    if type(source_bytes) is not bytes or len(source_bytes) > MAX_SOURCE_BYTES:
        raise InvalidAdvisory("source: must be bounded UTF-8 bytes")
    try:
        source = source_bytes.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise InvalidAdvisory("source: invalid UTF-8") from exc
    if type(engine_revision) is not str or HEX40.fullmatch(engine_revision) is None:
        raise InvalidAdvisory("engine revision: expected lowercase 40-hex Git SHA")
    obj = _fields(report, {
        "profile", "intent", "risk_score", "finding_count", "findings",
        "coverage", "source",
    }, "report")
    if type(obj["profile"]) is not str or obj["profile"] not in PROFILES:
        raise InvalidAdvisory("report: unsupported profile")
    intent = obj["intent"]
    if intent is not None:
        intent = _string(intent, "intent", 2048)
    _count(obj["risk_score"], "risk_score", 100)
    count = _count(obj["finding_count"], "finding_count", MAX_FINDINGS)
    findings = obj["findings"]
    if type(findings) is not list or len(findings) != count:
        raise InvalidAdvisory("finding_count does not match findings")

    provenance = obj["source"]
    if type(provenance) is not dict or set(provenance) not in (
        {"content_sha256", "digest_basis", "verification"},
        {"content_sha256", "digest_basis", "verification", "declared_url"},
    ):
        raise InvalidAdvisory("source: missing or unexpected provenance fields")
    digest = provenance["content_sha256"]
    if type(digest) is not str or HEX64.fullmatch(digest) is None:
        raise InvalidAdvisory("source: invalid SHA-256 digest")
    if provenance["digest_basis"] != "analyzed_text_utf8" or provenance["verification"] != "not_checked":
        raise InvalidAdvisory("source: unsupported attestation claim")
    if digest != hashlib.sha256(source_bytes).hexdigest():
        raise InvalidAdvisory("source digest does not match supplied input bytes")
    declared_url = provenance.get("declared_url")
    if declared_url is not None:
        declared_url = _string(declared_url, "declared_url", 2048)

    coverage = _fields(obj["coverage"], {
        "status", "nonempty_clause_count", "extracted_rule_count",
        "unparsed_normative_clause_count", "unparsed_normative_clauses",
        "nonoperative_clause_count", "nonoperative_clauses", "notice",
    }, "coverage")
    if type(coverage["status"]) is not str or coverage["status"] not in COVERAGE_STATUSES:
        raise InvalidAdvisory("coverage: unsupported status")
    _count(coverage["nonempty_clause_count"], "nonempty_clause_count")
    extracted = _count(coverage["extracted_rule_count"], "extracted_rule_count")
    unparsed = _count(coverage["unparsed_normative_clause_count"], "unparsed_normative_clause_count")
    nonoperative = _count(coverage["nonoperative_clause_count"], "nonoperative_clause_count")
    if (
        type(coverage["unparsed_normative_clauses"]) is not list
        or len(coverage["unparsed_normative_clauses"]) != unparsed
        or type(coverage["nonoperative_clauses"]) is not list
        or len(coverage["nonoperative_clauses"]) != nonoperative
    ):
        raise InvalidAdvisory("coverage: item counts disagree")
    _string(coverage["notice"], "coverage.notice", 2048)

    lines = source.splitlines()
    items: list[dict[str, object]] = []
    for finding in findings:
        f = _fields(finding, {
            "rule_id", "category", "severity", "title", "evidence",
            "why_it_matters", "literalist_path", "hardening", "confidence",
        }, "finding")
        if f["severity"] not in ("low", "medium", "high"):
            raise InvalidAdvisory("finding: unsupported severity")
        confidence = f["confidence"]
        if type(confidence) not in (int, float) or not 0 <= confidence <= 1:
            raise InvalidAdvisory("finding: invalid confidence")
        if not math.isfinite(confidence):
            raise InvalidAdvisory("finding: nonfinite confidence")
        evidence = f["evidence"]
        if type(evidence) is not list or not 1 <= len(evidence) <= 8:
            raise InvalidAdvisory("finding: expected bounded source evidence")
        items.append({
            "rule_id": _string(f["rule_id"], "rule_id", 256),
            "category": _string(f["category"], "category", 128),
            "severity": f["severity"],
            "title": _string(f["title"], "title", 512),
            "evidence": [_exact_evidence(v, lines) for v in evidence],
            "why_it_matters": _string(f["why_it_matters"], "why_it_matters"),
            "literalist_path": _string(f["literalist_path"], "literalist_path"),
            "hardening": _string(f["hardening"], "hardening"),
        })

    artifact: dict[str, object] = {
        "schema": SCHEMA,
        "review_status": (
            "CANDIDATES_REQUIRE_REVIEW" if items else "NO_DETECTED_FINDINGS_NOT_CLEARED"
        ),
        "authority": "NONE",
        "authorization_effect": "NONE",
        "runtime_verified": False,
        "engine": {
            "repository": "thebrazenbeard/lou-pole",
            "declared_revision": engine_revision,
            "revision_verified": False,
            "report_execution_verified": False,
        },
        "source": {
            "content_sha256": digest,
            "digest_verified_against_input": True,
            "declared_url_unverified": declared_url,
        },
        "profile": obj["profile"],
        "intent": intent,
        "coverage": {
            "status": coverage["status"],
            "extracted_rule_count": extracted,
            "unparsed_normative_clause_count": unparsed,
            "nonoperative_clause_count": nonoperative,
            "completeness_verified": False,
        },
        "finding_count": count,
        "findings": items,
    }
    if len(_encode(artifact)) + 1 > MAX_ARTIFACT_BYTES:  # CLI appends newline
        raise InvalidAdvisory("advisory artifact exceeds output budget")
    return artifact


def _encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False).encode("utf-8")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for k, v in pairs:
        if k in output:
            raise InvalidAdvisory("report has duplicate JSON keys")
        output[k] = v
    return output


def _numeric(token: str, *, integer: bool) -> int | float:
    if len(token) > 256:
        raise InvalidAdvisory("report numeric token too long")
    result = int(token) if integer else float(token)
    if type(result) is float and not math.isfinite(result):
        raise InvalidAdvisory("report numeric value not finite")
    return result


def _check_depth(raw: bytes, maximum: int = 64) -> None:
    depth = 0
    quoted = False
    escaped = False
    for b in raw:
        if quoted:
            if escaped:
                escaped = False
            elif b == 92:
                escaped = True
            elif b == 34:
                quoted = False
        elif b == 34:
            quoted = True
        elif b in (91, 123):
            depth += 1
            if depth > maximum:
                raise InvalidAdvisory("report JSON nesting exceeds limit")
        elif b in (93, 125):
            depth -= 1
            if depth < 0:
                raise InvalidAdvisory("report JSON is malformed")


def parse_report(raw: bytes) -> object:
    if type(raw) is not bytes or len(raw) > MAX_REPORT_BYTES:
        raise InvalidAdvisory("report exceeds byte limit")
    _check_depth(raw)
    try:
        return json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_pairs,
            parse_int=lambda x: _numeric(x, integer=True),
            parse_float=lambda x: _numeric(x, integer=False),
            parse_constant=lambda x: (_ for _ in ()).throw(InvalidAdvisory("nonfinite JSON")),
        )
    except InvalidAdvisory:
        raise
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise InvalidAdvisory("invalid report JSON") from exc


def load_bounded(path: Path, limit: int) -> bytes:
    """Read a bounded ordinary file without following POSIX symlinks."""
    try:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise InvalidAdvisory("symlinked input is forbidden")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise InvalidAdvisory("input must be a bounded ordinary file")
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise InvalidAdvisory("input exceeds byte limit")
        return raw
    except InvalidAdvisory:
        raise
    except OSError as exc:
        raise InvalidAdvisory("input file cannot be opened safely") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert a Lou-Pole provenance JSON report to inert BT2 advisory evidence"
    )
    parser.add_argument("source", type=Path, help="exact UTF-8 input analyzed by Lou-Pole")
    parser.add_argument("report_json", type=Path, help="Lou-Pole --json --provenance output")
    parser.add_argument("--engine-revision", required=True, help="caller-declared source commit SHA")
    args = parser.parse_args(argv)
    try:
        result = build_advisory(
            load_bounded(args.source, MAX_SOURCE_BYTES),
            parse_report(load_bounded(args.report_json, MAX_REPORT_BYTES)),
            engine_revision=args.engine_revision,
        )
    except InvalidAdvisory as exc:
        print(json.dumps({"status": "INVALID_ADVISORY", "reason": str(exc)}), file=sys.stderr)
        return 2
    sys.stdout.buffer.write(_encode(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
