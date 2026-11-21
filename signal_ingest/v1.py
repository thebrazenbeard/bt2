"""BT2_ECOSYSTEM_SIGNAL_V1: deterministic observations only, no provider or effects.

Input is untrusted even if it claims a GitHub/Bus/host authentication label.
This module has no network, credentials, clocks, persistence, scheduling or
external-effect capability. It cannot independently verify source identities.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit

INPUT_SCHEMA = "BT2_ECOSYSTEM_SIGNAL_INPUT_V1"
OUTPUT_SCHEMA = "BT2_ECOSYSTEM_SIGNAL_OUTPUT_V1"
KINDS = {
    "PR_HEAD_CHANGE": {"CHANGED", "UNCHANGED"},
    "CI_RESULT": {"FAILED", "PASSED"},
    "SECURITY_DEPENDENCY_CHANGE": {"INVALIDATED", "UNCHANGED"},
    "COORDINATION": {"CONFLICT", "DUPLICATE_ALERT", "REVIEW_PENDING", "RESOLVED"},
    "RUNTIME_GAP": {"MISSING", "UNQUALIFIED", "REPORTED_QUALIFIED"},
}
EVIDENCE_CLASSES = {"SOURCE", "CI", "BUS_REPORT", "DEPENDENCY_REPORT", "HOST_REPORT"}
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
MAX_OBSERVATIONS = 256
MAX_SUBJECTS = 128
MAX_BYTES = 512_000


class SignalError(ValueError):
    """A bounded public-safe validation code (never embeds attacker payload)."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise SignalError(code)


def _mapping(raw: Any, required: set[str], optional: set[str], code: str) -> dict:
    _require(type(raw) is dict, code)
    _require(required <= raw.keys() and raw.keys() <= required | optional, code)
    return raw


def _text(raw: Any, code: str, pattern: re.Pattern[str] = IDENT) -> str:
    _require(type(raw) is str and bool(pattern.fullmatch(raw)), code)
    return raw


def _head(raw: Any) -> str | None:
    _require(raw is None or (type(raw) is str and SHA.fullmatch(raw) is not None), "INVALID_HEAD")
    return raw


def _utc(raw: Any) -> str:
    _require(type(raw) is str and UTC.fullmatch(raw) is not None, "INVALID_UTC")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SignalError("INVALID_UTC") from None
    _require(value.tzinfo is not None and value.utcoffset().total_seconds() == 0,
             "INVALID_UTC")
    return raw


def _source(raw: Any) -> str:
    _require(type(raw) is str and len(raw) <= 512, "INVALID_SOURCE_REF")
    try:
        url = urlsplit(raw)
    except ValueError:
        raise SignalError("INVALID_SOURCE_REF") from None
    try:
        qualified = (url.scheme == "https" and url.hostname in ("github.com", "api.github.com")
                     and url.username is None and url.password is None
                     and not url.query and url.port is None and bool(url.path.strip("/"))
                     and (not url.fragment or re.fullmatch(r"(?:issuecomment-|discussion_r)\d+", url.fragment) is not None))
    except ValueError:
        raise SignalError("INVALID_SOURCE_REF") from None
    _require(qualified, "INVALID_SOURCE_REF")
    return raw


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def _observed_status(kind: str, status: str, subject: dict, obs: dict) -> tuple[str, bool]:
    """Return observed source currentness and candidate (not action) suitability."""
    current = subject["head"]
    seen = obs["head"]
    if current is None or seen is None:
        currentness = "UNKNOWN_HEAD"
    elif current != seen:
        currentness = "STALE_HEAD"
    else:
        currentness = "EXACT_HEAD"
    negative = status in {"CHANGED", "FAILED", "INVALIDATED", "CONFLICT",
                          "DUPLICATE_ALERT", "REVIEW_PENDING", "MISSING", "UNQUALIFIED"}
    if kind == "PR_HEAD_CHANGE" and status == "CHANGED":
        negative = obs["previous_head"] is not None and obs["previous_head"] != obs["head"]
    if kind == "RUNTIME_GAP":
        negative = subject["runtime_required"] and status in ("MISSING", "UNQUALIFIED")
        # Missing runtime evidence is an observation even if the runtime has no
        # known source HEAD. It cannot imply runtime availability or permission.
        if current is None and seen is None:
            return currentness, bool(negative)
    return currentness, bool(negative and currentness == "EXACT_HEAD")


def normalize(document: dict) -> dict:
    """Normalize untrusted source reports into provisional deduped observations.

    No caller-supplied authentication, claimed owner, CI status, runtime status
    or cutoff grants operational authority. Every output action set is empty.
    """
    _require(type(document) is dict, "INVALID_DOCUMENT")
    try:
        size = len(_canonical(document))
    except (ValueError, TypeError, RecursionError):
        raise SignalError("INVALID_DOCUMENT") from None
    _require(size <= MAX_BYTES, "DOCUMENT_TOO_LARGE")
    _mapping(document, {"schema", "snapshot", "observations"}, set(), "INVALID_DOCUMENT")
    _require(document["schema"] == INPUT_SCHEMA, "UNSUPPORTED_SCHEMA")
    snap = _mapping(document["snapshot"],
                    {"observed_at", "subjects", "host_access_cutoff"}, set(), "INVALID_SNAPSHOT")
    observed_at = _utc(snap["observed_at"])
    cutoff = _utc(snap["host_access_cutoff"])
    _require(type(snap["subjects"]) is list and 0 < len(snap["subjects"]) <= MAX_SUBJECTS,
             "INVALID_SUBJECTS")
    subjects: dict[tuple[str, str], dict] = {}
    for item in snap["subjects"]:
        item = _mapping(item, {"repository", "subject", "head", "runtime_required",
                               "reported_runtime_status"}, set(), "INVALID_SUBJECT")
        repository = _text(item["repository"], "INVALID_REPOSITORY", REPO)
        subject = _text(item["subject"], "INVALID_SUBJECT_ID")
        _head(item["head"])
        _require(type(item["runtime_required"]) is bool, "INVALID_RUNTIME_FLAG")
        _require(item["reported_runtime_status"] in ("UNKNOWN", "REPORTED_QUALIFIED",
                                                      "REPORTED_UNQUALIFIED"), "INVALID_RUNTIME_STATUS")
        key = (repository, subject)
        _require(key not in subjects, "DUPLICATE_SUBJECT")
        subjects[key] = item
    raw_observations = document["observations"]
    _require(type(raw_observations) is list and len(raw_observations) <= MAX_OBSERVATIONS,
             "INVALID_OBSERVATIONS")
    entries = []
    ids: dict[str, bytes] = {}
    for raw in raw_observations:
        raw = _mapping(raw, {"id", "kind", "status", "repository", "subject", "head",
                             "incident_key", "observed_at", "source_ref", "evidence_class",
                             "claimed_owner", "claimed_reviewer", "claims_authenticated"},
                       {"previous_head"}, "INVALID_OBSERVATION")
        ident = _text(raw["id"], "INVALID_OBSERVATION_ID")
        kind = _text(raw["kind"], "INVALID_KIND")
        _require(kind in KINDS, "INVALID_KIND")
        status = _text(raw["status"], "INVALID_STATUS")
        _require(status in KINDS[kind], "INVALID_STATUS")
        repo = _text(raw["repository"], "INVALID_REPOSITORY", REPO)
        subject = _text(raw["subject"], "INVALID_SUBJECT_ID")
        _require((repo, subject) in subjects, "UNKNOWN_SUBJECT")
        _head(raw["head"])
        incident = _text(raw["incident_key"], "INVALID_INCIDENT_KEY")
        timestamp = _utc(raw["observed_at"])
        _require(timestamp <= observed_at, "OBSERVATION_FROM_FUTURE")
        source_ref = _source(raw["source_ref"])
        _require(type(raw["evidence_class"]) is str and
                 raw["evidence_class"] in EVIDENCE_CLASSES, "INVALID_EVIDENCE_CLASS")
        owner = _text(raw["claimed_owner"], "INVALID_OWNER")
        reviewer = raw["claimed_reviewer"]
        _require(reviewer is None or (type(reviewer) is str and IDENT.fullmatch(reviewer)),
                 "INVALID_REVIEWER")
        _require(type(raw["claims_authenticated"]) is bool, "INVALID_AUTH_CLAIM")
        previous = raw.get("previous_head")
        _head(previous)
        if kind == "PR_HEAD_CHANGE":
            _require("previous_head" in raw, "MISSING_PREVIOUS_HEAD")
            _require((status == "CHANGED") == (previous != raw["head"]),
                     "HEAD_CHANGE_CONTRADICTION")
        else:
            _require("previous_head" not in raw, "UNEXPECTED_PREVIOUS_HEAD")
        identity = _canonical(raw)
        if ident in ids:
            _require(ids[ident] == identity, "CONFLICTING_OBSERVATION_ID")
            continue
        ids[ident] = identity
        currentness, candidate = _observed_status(kind, status, subjects[(repo, subject)], raw)
        entries.append({
            "id": ident, "kind": kind, "status": status,
            "repository": repo, "subject": subject, "head": raw["head"],
            "incident_key": incident, "observed_at": timestamp,
            "source_ref": source_ref, "evidence_class": raw["evidence_class"],
            "claimed_owner": owner, "claimed_reviewer": reviewer,
            "authentication": "UNVERIFIED", "claimed_authenticated": raw["claims_authenticated"],
            "owner_verified": False, "reviewer_verified": False,
            "head_currentness": currentness,
            "candidate_observation": candidate,
        })
    # Initial experimental grouping was source-ref-specific; see RED -> GREEN
    # receipt in tests. Final grouping uses the *provisional incident key*,
    # with exact repo, subject and head to prevent cross-head contamination.
    grouped: dict[tuple, list[dict]] = {}
    for entry in entries:
        key = (entry["repository"], entry["subject"], entry["head"], entry["incident_key"])
        grouped.setdefault(key, []).append(entry)
    groups = []
    for key, members in sorted(grouped.items(), key=lambda x: tuple(str(z) for z in x[0])):
        members.sort(key=lambda x: (x["observed_at"], x["source_ref"], x["id"]))
        currentnesses = {x["head_currentness"] for x in members}
        _require(len(currentnesses) == 1, "INCONSISTENT_HEAD_STATUS")
        currentness = next(iter(currentnesses))
        eligible = any(x["candidate_observation"] for x in members)
        kinds = sorted(set(x["kind"] for x in members))
        limitations = ["SOURCE_AUTHENTICATION_UNVERIFIED", "OWNER_AND_REVIEWER_UNVERIFIED",
                       "INCIDENT_EQUIVALENCE_REPORTED_NOT_PROVEN", "OBSERVATION_NOT_AUTHORITY"]
        if currentness != "EXACT_HEAD":
            limitations.append("SOURCE_HEAD_" + currentness)
        if "CI_RESULT" in kinds:
            limitations.append("CI_STATUS_NOT_RELEASE_PERMISSION")
        if "RUNTIME_GAP" in kinds:
            limitations.append("RUNTIME_AUTHENTICATION_AND_CURRENTNESS_UNKNOWN")
        if any(x["claimed_authenticated"] for x in members):
            limitations.append("SELF_ASSERTED_AUTHENTICATION_IGNORED")
        reference = {"repository": members[0]["repository"],
                     "subject": members[0]["subject"], "head": members[0]["head"],
                     "incident_key": members[0]["incident_key"]}
        groups.append({
            "observation_key": sha256(_canonical(reference)).hexdigest(),
            "repository": reference["repository"], "subject": reference["subject"],
            "head": reference["head"], "incident_key": reference["incident_key"],
            "categories": kinds, "statuses": sorted(set(x["status"] for x in members)),
            "head_currentness": currentness, "candidate_observation": eligible,
            "observation_timestamp": max(x["observed_at"] for x in members),
            "reports": members, "source_refs": sorted(set(x["source_ref"] for x in members)),
            "claimed_owners": sorted(set(x["claimed_owner"] for x in members)),
            "confidence_limitations": limitations,
            "independently_authenticated": False,
            "release_permission": False,
        })
    runtime = []
    for (repo, subject), item in sorted(subjects.items()):
        if item["runtime_required"]:
            runtime.append({"repository": repo, "subject": subject, "head": item["head"],
                            "currentness": "UNKNOWN", "availability": "UNKNOWN",
                            "independently_authenticated": False,
                            "limitation": "NO_TRUSTED_RUNTIME_ATTESTATION_VERIFIER_INSTALLED"})
    cutoff_reached = observed_at >= cutoff
    return {
        "schema": OUTPUT_SCHEMA, "snapshot_observed_at": observed_at,
        "observations": sorted(groups, key=lambda g:(g["repository"],g["subject"],str(g["head"]),g["incident_key"])),
        "runtime": runtime,
        "host_access_cutoff": cutoff,
        "host_task_start_permitted": "NO_EXPIRED_CUTOFF" if cutoff_reached else "UNKNOWN_UNVERIFIED_AUTHORITY",
        "host_task_proposals": [], "external_effects": [], "release_permission": False,
        "policy_decision": "NOT_MADE", "side_effects_performed": False,
        "limitations": ["SOURCE_ONLY", "NO_AUTHENTICATED_PROVIDER", "NO_HOST_RUNTIME_PROBE",
                        "NO_ACTION_OR_DECISION_ENGINE"],
    }


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SignalError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def main() -> int:
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Offline source-only signal normalizer")
    parser.add_argument("input", help="Local UTF-8 JSON input; no network")
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        parser.error("INVALID_INPUT_FILE")
    try:
        document = json.loads(path.read_text(encoding="utf-8"),
                              object_pairs_hook=_reject_duplicate_json_keys,
                              parse_constant=lambda _: (_ for _ in ()).throw(SignalError("NONFINITE_JSON")))
        result = normalize(document)
    except (SignalError, ValueError, OSError, UnicodeError) as exc:
        parser.error(exc.args[0] if isinstance(exc, SignalError) else "INVALID_JSON_INPUT")
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
