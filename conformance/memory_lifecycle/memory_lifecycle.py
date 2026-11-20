"""BT2 Memory Lifecycle Conformance V1: deterministic, source-only evaluator.

No database, host, GitHub, network, inference, authentication or action side effects.
Inputs are untrusted descriptions of evidence, not credentials or authorization.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

INPUT_SCHEMA = "BT2_MEMORY_LIFECYCLE_INPUT_V1"
OUTPUT_SCHEMA = "BT2_MEMORY_LIFECYCLE_OUTPUT_V1"
SOURCE_KINDS = frozenset({
    "STM_WORKING", "DMS_HISTORICAL", "VERA_MONO_GOVERNED",
    "SUPABASE_METADATA", "GITHUB_SOURCE", "REVIEW_COMMENT",
})
MEMORY_CLASSES = frozenset({"WORKING_PROJECT", "HISTORICAL_AUDIT", "AUTOBIOGRAPHICAL"})
EVIDENCE_CLASSES = frozenset({"DOC", "SOURCE_INSPECTION", "TEST", "REAL_PROBE", "FORMAL_VERIFY", "MODEL_REVIEW"})
WORD = re.compile(r"[a-z0-9_]+")
INJECTION = re.compile(r"(?:ignore|override)\s+(?:all\s+)?(?:previous|system|developer)\s+instructions|<\|im_start\|>|(?:save|promote)\s+this\s+(?:as|to)\s+(?:permanent|canonical)\s+memory", re.I)

class ContractError(ValueError):
    pass

class ProvenanceConflict(ContractError):
    pass


def strict_json(text: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ContractError("duplicate JSON key")
            result[key] = value
        return result
    def reject_constant(v: str) -> None:
        raise ContractError("nonfinite JSON value: " + v)
    try:
        result = json.loads(text, object_pairs_hook=unique, parse_constant=reject_constant)
    except (TypeError, json.JSONDecodeError) as e:
        raise ContractError("invalid JSON") from e
    if type(result) is not dict:
        raise ContractError("top-level JSON must be an object")
    return result


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def utc(s: str) -> datetime:
    if type(s) is not str or not s.endswith("Z"):
        raise ContractError("timestamp must be canonical UTC Z")
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as e:
        raise ContractError("invalid timestamp") from e
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise ContractError("timestamp must be UTC")
    return dt


def req(obj: dict[str, Any], key: str, kind: type = str) -> Any:
    v = obj.get(key)
    if type(v) is not kind or (kind is str and not v.strip()):
        raise ContractError("invalid field " + key)
    return v


def _valid_record(r: dict[str, Any], now: datetime) -> None:
    if type(r) is not dict:
        raise ContractError("record must be object")
    for name in ("record_id", "subject", "source_ref", "source_kind", "memory_class",
                 "evidence_class", "privacy_scope", "claim", "event_at", "recorded_at"):
        req(r, name)
    if r["source_kind"] not in SOURCE_KINDS or r["memory_class"] not in MEMORY_CLASSES or r["evidence_class"] not in EVIDENCE_CLASSES:
        raise ContractError("invalid source/memory/evidence class")
    if len(r["claim"].encode("utf-8")) > 2048 or len(r["source_ref"]) > 512:
        raise ContractError("record content exceeds budget")
    if type(r.get("head")) not in (str, type(None)) or r.get("head") == "":
        raise ContractError("invalid head")
    if type(r.get("supersedes")) not in (str, type(None)) or r.get("supersedes") == "":
        raise ContractError("invalid supersedes")
    if type(r.get("claimed_actor")) not in (str, type(None)):
        raise ContractError("invalid claimed_actor")
    confidence = r.get("extraction_confidence")
    if type(confidence) not in (float, int) or type(confidence) is bool or not 0 <= confidence <= 1:
        raise ContractError("every extraction requires bounded confidence")
    observed = utc(r["event_at"])
    recorded = utc(r["recorded_at"])
    if observed > now or recorded > now:
        raise ContractError("record time in future")
    if r.get("expires_at") is not None:
        utc(r["expires_at"])
    if type(r.get("independently_authenticated", False)) is not bool:
        raise ContractError("invalid claimed authentication flag")


def select_current_heads(records: list[dict[str, Any]]) -> dict[str, dict[str, Any] | None]:
    """Return lineage-qualified heads, not time-sorted assertions.

    Historical restatements of a superseded head never revive it. Unrelated
    conflicting chains remain UNKNOWN rather than newest-time-wins.
    This structural projection does not establish external current authority.
    """
    by_id: dict[str, dict[str, Any]] = {}
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        i = r["record_id"]
        if i in by_id:
            if canonical_json(by_id[i]) != canonical_json(r):
                raise ProvenanceConflict("same record_id with divergent source")
            continue
        by_id[i] = r
        by_subject[r["subject"]].append(r)
    for r in by_id.values():
        parent = r.get("supersedes")
        if parent is not None:
            if parent not in by_id or by_id[parent]["subject"] != r["subject"]:
                raise ProvenanceConflict("unknown or cross-subject supersession")
    out: dict[str, dict[str, Any] | None] = {}
    for subject, group in by_subject.items():
        children: dict[str, list[str]] = defaultdict(list)
        for r in group:
            if r.get("supersedes"):
                children[r["supersedes"]].append(r["record_id"])
        if any(len(v) > 1 for v in children.values()):
            out[subject] = None
            continue
        # Follow each root; reject cycles instead of manufacturing a head.
        terminals = []
        for r in group:
            if r.get("supersedes") is not None:
                continue
            visited: set[str] = set()
            cur = r
            while True:
                if cur["record_id"] in visited:
                    raise ProvenanceConflict("supersession cycle")
                visited.add(cur["record_id"])
                successors = children.get(cur["record_id"], [])
                if not successors:
                    terminals.append(cur)
                    break
                cur = by_id[successors[0]]
        if not terminals:
            raise ProvenanceConflict("no rooted supersession chain")
        # Drop stale restatements: root of a competing chain repeats an already
        # superseded head in another witnessed chain. Never drop different heads.
        ancestors = {
            r.get("head") for r in group
            if r["record_id"] in children and r.get("head") is not None
        }
        qualified = [r for r in terminals if not (r.get("supersedes") is None and r.get("head") in ancestors)]
        out[subject] = qualified[0] if len(qualified) == 1 else None
    return out


def _relevance(query: str, candidate: dict[str, Any]) -> float:
    q = set(WORD.findall(query.lower()))
    if not q:
        return 0.0
    words = set(WORD.findall((candidate["subject"] + " " + candidate["claim"]).lower()))
    return round(len(q & words) / len(q), 6)


def evaluate(envelope: dict[str, Any]) -> dict[str, Any]:
    if type(envelope) is not dict or envelope.get("schema") != INPUT_SCHEMA:
        raise ContractError("unsupported input schema")
    now = utc(req(envelope, "observed_at"))
    goal = req(envelope, "goal", dict)
    query = req(goal, "query"); purpose = req(goal, "purpose")
    if not purpose or len(query) > 200 or len(purpose) > 100:
        raise ContractError("unbounded retrieval goal")
    max_records = 256
    records = req(envelope, "records", list)
    if len(records) > max_records:
        raise ContractError("input candidate budget exceeded")
    allowed = req(envelope, "authorized_privacy_scopes", list)
    if not allowed or len(allowed) > 16 or any(type(v) is not str or not v for v in allowed) or len(set(allowed)) != len(allowed):
        raise ContractError("exact privacy authorization scopes required")
    expected_heads = req(envelope, "expected_heads", dict)
    if any(type(k) is not str or not k or type(v) is not str or not v for k,v in expected_heads.items()):
        raise ContractError("expected heads invalid")
    max_results = goal.get("max_candidates", 5)
    max_bytes = goal.get("max_utf8_bytes", 800)
    min_score = goal.get("min_relevance", 0.4)
    if type(max_results) is not int or not 1 <= max_results <= 5 or type(max_bytes) is not int or not 1 <= max_bytes <= 4096 or type(min_score) not in (int, float) or not 0 <= min_score <= 1:
        raise ContractError("retrieval budget/relevance invalid")
    for r in records:
        _valid_record(r, now)
    heads = select_current_heads(records)
    seen = set()
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for r in records:
        if r["record_id"] in seen:
            continue
        seen.add(r["record_id"])
        reasons = []
        if r["privacy_scope"] not in allowed:
            reasons.append("UNAUTHORIZED_PRIVACY")
        if r.get("expires_at") is not None and utc(r["expires_at"]) <= now:
            reasons.append("EXPIRED")
        if INJECTION.search(r["claim"]):
            reasons.append("UNTRUSTED_INSTRUCTION_CANDIDATE")
        if r["source_kind"] == "DMS_HISTORICAL" or r["memory_class"] != "WORKING_PROJECT":
            reasons.append("HISTORICAL_NOT_CURRENT")
        if heads.get(r["subject"]) is None or heads[r["subject"]]["record_id"] != r["record_id"]:
            reasons.append("NOT_UNIQUE_CURRENT_LINEAGE_HEAD")
        if expected_heads.get(r["subject"]) != r.get("head"):
            reasons.append("EXTERNAL_HEAD_MISSING_OR_DIFFERENT")
        # A claimed source-owner, reviewer, or authenticated boolean is data.
        # No independently rooted proof verifier exists in this module.
        score = _relevance(query, r)
        if score < min_score:
            reasons.append("BELOW_RELEVANCE_THRESHOLD")
        if reasons:
            rejected.append({"record_id":r["record_id"], "reasons":sorted(set(reasons))})
            continue
        candidates.append({
            "record_id":r["record_id"], "subject":r["subject"], "head":r.get("head"),
            "claim":r["claim"], "source_ref":r["source_ref"], "source_kind":r["source_kind"],
            "evidence_class":r["evidence_class"], "privacy_scope":r["privacy_scope"],
            "extraction_confidence":r["extraction_confidence"], "claimed_actor":r.get("claimed_actor"),
            "independently_authenticated":False, "currentness":"MATCHES_SUPPLIED_HEAD_UNAUTHENTICATED",
            "relevance":score, "trust_status":"UNTRUSTED_EVIDENCE_DATA_NOT_AUTHORITY"
        })
    candidates.sort(key=lambda x:(-x["relevance"],x["subject"],x["record_id"]))
    used=0; included=[]
    for c in candidates:
        length=len(canonical_json(c).encode("utf-8"))
        if length > max_bytes-used or len(included) == max_results:
            rejected.append({"record_id":c["record_id"],"reasons":["RETRIEVAL_BUDGET_EXCEEDED"]})
            continue
        included.append(c); used+=length
    # Runtime scope is a separate attested plane. Input runtime claims are
    # deliberately not promoted; this source-only module cannot probe a host.
    return {
        "schema":OUTPUT_SCHEMA, "goal":{"query":query,"purpose":purpose},
        "observed_at":envelope["observed_at"],
        "selected":included, "rejected":sorted(rejected,key=lambda x:(x["record_id"],x["reasons"])),
        "structural_heads":{k:(v["record_id"] if v else None) for k,v in sorted(heads.items())},
        "runtime_currentness":"UNKNOWN_NOT_PROBED", "independently_authenticated":False,
        "budget":{"max_input_records":max_records,"max_candidates":max_results,
                  "max_utf8_bytes":max_bytes,"used_utf8_bytes":used,
                  "min_relevance":min_score,"target_latency_ms":200,
                  "measured_latency_ms":None,"measured_cost_usd":None},
        "side_effects":{"memory_write":"NONE","permission_change":"NONE",
                        "notification":"NONE","host_task":"NONE","external_action":"NONE",
                        "release_authorization":"NONE"},
        "result_semantics":"SOURCE_ONLY_EVIDENCE_NOT_CURRENT_TRUTH_OR_AUTHORITY"
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic source-only memory lifecycle conformance")
    ap.add_argument("input", type=Path)
    args=ap.parse_args(argv)
    try:
        obj = strict_json(args.input.read_text(encoding="utf-8"))
        result=evaluate(obj)
    except (OSError, ContractError) as e:
        print("MEMORY_LIFECYCLE_ERROR:" + str(e),file=sys.stderr)
        return 2
    print(canonical_json(result))
    return 0

if __name__=="__main__":
    raise SystemExit(main())