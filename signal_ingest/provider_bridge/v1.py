"""BT2 GitHub provider receipts -> Engineer B V1 signal normalizer (source only).

A successful GitHub CLI/API observation is useful source evidence, not
independent identity authentication. Replay filtering depends on a
CALLER-PROVIDED previous digest set; no durable trusted replay ledger here.
No GitHub calls, network, database, clock, notifications or protected effects.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit

from signal_ingest.v1 import normalize, SignalError, _canonical, _utc, _head

INPUT_SCHEMA = "BT2_GITHUB_PROVIDER_BRIDGE_INPUT_V1"
OUTPUT_SCHEMA = "BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
REPO = re.compile(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\Z")
PR_SUBJECT = re.compile(r"pr:([1-9]\d{0,8})\Z")
INCIDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
MAX_RECEIPTS = 256
MAX_BYTES = 512000
MAX_SEEN = 512


class BridgeError(ValueError):
    """Sanitized error codes, never source payloads."""


def require(test: bool, error_code: str) -> None:
    if not test:
        raise BridgeError(error_code)


def fields(obj: Any, required: set[str], optional: set[str], code: str) -> dict:
    require(type(obj) is dict and required <= obj.keys() <= required | optional, code)
    return obj


def canonical(value: Any) -> bytes:
    try:
        result = _canonical(value)
    except (ValueError, TypeError, RecursionError) as exc:
        raise BridgeError("BAD_DOCUMENT") from None
    return result


def origin_matches(raw_url: str, repo: str, kind: str, subject: str) -> bool:
    if type(raw_url) is not str or len(raw_url) > 512:
        return False
    try:
        url = urlsplit(raw_url)
    except ValueError:
        return False
    if url.scheme != "https" or url.netloc != "github.com" or url.query or url.fragment:
        return False
    parts = url.path.strip("/").split("/")
    if len(parts) not in (4,5) or "/".join(parts[:2]) != repo:
        return False
    if kind == "CI_RESULT":
        return len(parts) == 5 and parts[2:4] == ["actions", "runs"] and bool(re.fullmatch(r"[1-9]\d{0,12}", parts[4]))
    if kind == "PR_HEAD_CHANGE":
        match = PR_SUBJECT.fullmatch(subject)
        return (bool(match) and parts[2] == "pull" and len(parts) == 4 and parts[3] == match.group(1))
    return False


def bridge(document: dict) -> dict:
    require(type(document) is dict, "INVALID_DOCUMENT")
    require(len(canonical(document)) <= MAX_BYTES, "DOCUMENT_TOO_LARGE")
    fields(document, {"schema", "snapshot", "receipts", "seen_receipt_digests"}, set(),
           "INVALID_INPUT_FIELDS")
    require(document["schema"] == INPUT_SCHEMA, "WRONG_SCHEMA")
    snapshot = document["snapshot"]
    fields(snapshot, {"observed_at","host_access_cutoff","subjects"}, set(),
           "INVALID_SNAPSHOT")
    _utc(snapshot["observed_at"])
    _utc(snapshot["host_access_cutoff"])
    require(type(snapshot["subjects"]) is list and 0 < len(snapshot["subjects"]) <= 128,
            "INVALID_SUBJECTS")
    subjects = set()
    for item in snapshot["subjects"]:
        fields(item, {"repository","subject","head","runtime_required",
                      "reported_runtime_status"}, set(), "BAD_SUBJECT")
        require(type(item["repository"]) is str and REPO.fullmatch(item["repository"]) is not None,
                "BAD_SUBJECT_REPO")
        require(type(item["subject"]) is str and INCIDENT.fullmatch(item["subject"]) is not None,
                "BAD_SUBJECT_ID")
        _head(item["head"])
        require(type(item["runtime_required"]) is bool and
                item["reported_runtime_status"] in ("UNKNOWN","REPORTED_QUALIFIED","REPORTED_UNQUALIFIED"),
                "BAD_SUBJECT_RUNTIME")
        key = (item["repository"],item["subject"])
        require(key not in subjects, "DUPLICATE_SUBJECT")
        subjects.add(key)

    seen = document["seen_receipt_digests"]
    require(type(seen) is list and len(seen) <= MAX_SEEN, "BAD_REPLAY_CACHE")
    require(all(type(s) is str and HEX64.fullmatch(s) is not None for s in seen),
            "BAD_REPLAY_HASH")
    require(len(set(seen)) == len(seen), "DUPLICATE_REPLAY_HASH")
    receipts = document["receipts"]
    require(type(receipts) is list and len(receipts) <= MAX_RECEIPTS, "BAD_RECEIPTS")
    consumed = set(seen)
    ids = {}
    accepted = []
    suppressed = []
    reports = []
    for report in receipts:
        fields(report, {"event_id","repository","subject","kind","status","head",
                        "incident_key","observed_at","source_ref","provider_response_sha256",
                        "claimed_owner","claimed_reviewer","claims_authenticated","transport"},
               {"previous_head"}, "BAD_RECEIPT")
        require(type(report["event_id"]) is str and INCIDENT.fullmatch(report["event_id"]) is not None,
                "BAD_EVENT_ID")
        require(type(report["repository"]) is str and REPO.fullmatch(report["repository"]) is not None,
                "BAD_RECEIPT_REPO")
        require(type(report["subject"]) is str and PR_SUBJECT.fullmatch(report["subject"]) is not None,
                "BAD_RECEIPT_SUBJECT")
        require((report["repository"],report["subject"]) in subjects, "UNKNOWN_SUBJECT")
        require(report["kind"] in ("PR_HEAD_CHANGE","CI_RESULT"),"BAD_KIND")
        require(report["transport"] == "GITHUB_API_SESSION_READONLY","UNSUPPORTED_PROVENANCE")
        require(report["status"] in (("CHANGED","UNCHANGED") if report["kind"] == "PR_HEAD_CHANGE"
                      else ("FAILED","PASSED")), "BAD_STATUS")
        _head(report["head"])
        _utc(report["observed_at"])
        require(report["observed_at"] <= snapshot["observed_at"],"FUTURE_RECEIPT")
        require(origin_matches(report["source_ref"],report["repository"],
                               report["kind"],report["subject"]), "SOURCE_REPO_MISMATCH")
        require(type(report["provider_response_sha256"]) is str and
                HEX64.fullmatch(report["provider_response_sha256"]) is not None,
                "INVALID_PROVIDER_DIGEST")
        require(type(report["incident_key"]) is str and
                INCIDENT.fullmatch(report["incident_key"]) is not None, "BAD_INCIDENT")
        require(type(report["claimed_owner"]) is str and
                INCIDENT.fullmatch(report["claimed_owner"]) is not None,"BAD_OWNER")
        require(report["claimed_reviewer"] is None or
                (type(report["claimed_reviewer"]) is str and
                 INCIDENT.fullmatch(report["claimed_reviewer"]) is not None),
                "BAD_REVIEWER")
        require(type(report["claims_authenticated"]) is bool,"BAD_AUTH_CLAIM")
        if report["kind"] == "PR_HEAD_CHANGE":
            require("previous_head" in report, "MISSING_PREVIOUS_HEAD")
            _head(report["previous_head"])
            require((report["status"] == "CHANGED") ==
                    (report["previous_head"] != report["head"]), "CONFLICTING_HEAD_EVENT")
        else:
            require("previous_head" not in report, "UNEXPECTED_PREVIOUS_HEAD")
        # Dedupe identity and refuse equivocation before applying supplied cache.
        digest = sha256(canonical(report)).hexdigest()
        old = ids.get(report["event_id"])
        require(old is None or old == digest, "CONFLICTING_EVENT_ID")
        ids[report["event_id"]] = digest
        if digest in consumed:
            suppressed.append(digest)
            continue
        consumed.add(digest)
        accepted.append(digest)
        result = {key:report[key] for key in (
            "repository","subject","kind","status","head","incident_key",
            "observed_at","source_ref","claimed_owner","claimed_reviewer",
            "claims_authenticated")}
        result["id"] = report["event_id"]
        result["evidence_class"] = "CI" if report["kind"]=="CI_RESULT" else "SOURCE"
        if "previous_head" in report:
            result["previous_head"] = report["previous_head"]
        reports.append(result)
    try:
        require(len(consumed) <= MAX_SEEN, "REPLAY_CACHE_CAPACITY_REQUIRES_EXTERNAL_CHECKPOINT")
        signal = normalize({"schema":"BT2_ECOSYSTEM_SIGNAL_INPUT_V1",
                            "snapshot":snapshot, "observations":reports})
    except SignalError as exc:
        raise BridgeError(str(exc)) from None
    return {
        "schema":OUTPUT_SCHEMA,
        "signal":signal,
        "accepted_receipt_digests":accepted,
        "replay_suppressed":sorted(set(suppressed)),
        "next_seen_receipt_digests":sorted(consumed),
        "replay_scope":"CALLER_PROVIDED_CACHE_NOT_INDEPENDENT",
        "source_authentication":"UNVERIFIED_NO_SIGNED_RECEIPT",
        "provider_transport_claim":"GITHUB_API_SESSION_READONLY_UNATTESTED",
        "independently_authenticated":False,
        "memory_admission":"NONE",
        "semantic_truth":"NOT_EVALUATED",
        "side_effects":[],
    }


def bridge_with_predecessor(previous: dict, current: dict) -> dict:
    """Opt-in source-only adjacent-batch replay reconciliation.

    The ordinary V1 bridge has no independent replay storage and retains
    its exact input/output schema. When a caller explicitly supplies both
    consecutive documents, verify that its new cache retains the whole
    previous digest frontier and that an event ID never changes content
    between those two documents. Both documents remain caller-provided,
    so this checks consistency, NOT authenticity, durable history, or
    memory-admission authority. The caller can still omit or forge the
    predecessor entirely.
    """
    prior = bridge(previous)
    following = bridge(current)
    # Both timestamps passed _utc's canonical fixed-width YYYY-MM-DDTHH:MM:SSZ
    # validation during bridge(). Their lexical order is chronological.
    # This is consistency of *reported* observation order, not a trusted clock.
    require(current["snapshot"]["observed_at"] >=
            previous["snapshot"]["observed_at"],
            "CROSS_BATCH_SNAPSHOT_CLOCK_ROLLBACK")
    prior_seen = set(prior["next_seen_receipt_digests"])
    current_seen = set(current["seen_receipt_digests"])
    require(prior_seen <= current_seen,
            "CROSS_BATCH_REPLAY_HISTORY_DROPPED")
    ids = {}
    for record in previous["receipts"]:
        digest = sha256(canonical(record)).hexdigest()
        prior_digest = ids.get(record["event_id"])
        require(prior_digest is None or prior_digest == digest,
                "CROSS_BATCH_EVENT_ID_CONFLICT")
        ids[record["event_id"]] = digest
    for record in current["receipts"]:
        digest = sha256(canonical(record)).hexdigest()
        known = ids.get(record["event_id"])
        require(known is None or known == digest,
                "CROSS_BATCH_EVENT_ID_CONFLICT")
    return following


def bridge_with_history(history: list[dict], current: dict) -> dict:
    """Opt-in bounded consistency check across ALL supplied prior documents.

    These documents and their event IDs remain caller-controlled. This
    is neither an authenticated history provider nor a persistent ledger:
    replacing the whole supplied chain can still pass. Existing V1 source
    output and authority limits are preserved without side effects.
    """
    require(type(history) is list and bool(history),
            "MULTIBATCH_HISTORY_REQUIRED")
    require(len(history) <= 8, "MULTIBATCH_HISTORY_BOUNDS")
    # Check every adjacency, not just last->current. The original bridge
    # validates each document's canonical timestamps, subjects and receipts.
    for previous, successor in zip(history, history[1:]):
        bridge_with_predecessor(previous, successor)
    output = bridge_with_predecessor(history[-1], current)
    # Digests alone do not preserve event-ID attribution across an empty
    # middle batch. Check each original event ID against ALL supplied steps.
    all_ids = {}
    for document in [*history, current]:
        for receipt in document["receipts"]:
            digest = sha256(canonical(receipt)).hexdigest()
            old = all_ids.get(receipt["event_id"])
            require(old is None or old == digest,
                    "MULTIBATCH_EVENT_ID_CONFLICT")
            all_ids[receipt["event_id"]] = digest
    return output


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    out = {}
    for key,value in pairs:
        if key in out:
            raise BridgeError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description="Offline GitHub report -> BT2 signals")
    ap.add_argument("input",type=Path)
    args=ap.parse_args(argv)
    try:
        if args.input.stat().st_size>MAX_BYTES:
            raise BridgeError("DOCUMENT_TOO_LARGE")
        doc=json.loads(args.input.read_text(encoding="utf-8"),
                       object_pairs_hook=reject_duplicate_keys,
                       parse_constant=lambda _: (_ for _ in ()).throw(BridgeError("NONFINITE_JSON")))
        out=bridge(doc)
    except (BridgeError,SignalError,OSError,UnicodeError,ValueError) as exc:
        print("BRIDGE_ERROR:"+str(exc) if isinstance(exc,BridgeError) else
              "BRIDGE_ERROR:INVALID_INPUT",file=sys.stderr)
        return 2
    print(canonical(out).decode("utf-8"))
    return 0


if __name__=="__main__":
    raise SystemExit(main())