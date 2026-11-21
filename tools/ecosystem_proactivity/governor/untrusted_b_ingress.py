"""BT2 policy-owner dry run of Engineer B's UNTRUSTED source output.

This boundary deliberately cannot create a trusted Context, owner ACK, authenticated
source, notification, action, memory change, scheduler or other external effect.
It does not import Engineer B's still-draft module or read any provider.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

from .engine import (
    Action, Context, EvidenceClass, Signal, evaluate, parse_time,
)

OUTPUT_SCHEMA = "BT2_GOVERNOR_UNTRUSTED_DRY_RUN_V1"
RAW_SCHEMA = "BT2_ECOSYSTEM_SIGNAL_OUTPUT_V1"
BRIDGE_SCHEMA = "BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_GROUPS = 40


class AdmissionError(ValueError):
    """Sanitized input validation code; never contain source/user bytes."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise AdmissionError(code)


def _signal_document(document: dict) -> dict:
    _require(type(document) is dict, "BAD_INPUT_DOCUMENT")
    try:
        encoded = json.dumps(document, sort_keys=True, ensure_ascii=True,
                             allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (ValueError, TypeError, RecursionError):
        raise AdmissionError("BAD_INPUT_DOCUMENT") from None
    _require(len(encoded) <= 512000, "DOCUMENT_TOO_LARGE")
    schema = document.get("schema")
    if schema == BRIDGE_SCHEMA:
        _require(document.get("source_authentication") == "UNVERIFIED_NO_SIGNED_RECEIPT",
                 "BRIDGE_AUTH_CLAIM")
        _require(document.get("independently_authenticated") is False, "BRIDGE_AUTH_CLAIM")
        _require(document.get("replay_scope") == "CALLER_PROVIDED_CACHE_NOT_INDEPENDENT",
                 "BRIDGE_REPLAY_CLAIM")
        _require(document.get("memory_admission") == "NONE", "BRIDGE_MEMORY_CLAIM")
        _require(document.get("side_effects") == [], "BRIDGE_EFFECT_CLAIM")
        raw = document.get("signal")
    else:
        _require(schema == RAW_SCHEMA, "UNSUPPORTED_SCHEMA")
        raw = document
    _require(type(raw) is dict and raw.get("schema") == RAW_SCHEMA,
             "BAD_SOURCE_SIGNAL")
    _require(raw.get("release_permission") is False, "UNTRUSTED_RELEASE_CLAIM")
    _require(raw.get("side_effects_performed") is False, "UNTRUSTED_EFFECT_CLAIM")
    _require(raw.get("external_effects") == [], "UNTRUSTED_EFFECT_CLAIM")
    _require(raw.get("host_task_proposals") == [], "UNTRUSTED_EFFECT_CLAIM")
    _require(raw.get("policy_decision") == "NOT_MADE", "UNTRUSTED_POLICY_CLAIM")
    _require(type(raw.get("limitations")) is list and
             "SOURCE_ONLY" in raw["limitations"], "SOURCE_ONLY_LIMITATION_MISSING")
    return raw


def _untrusted_signal(group: dict) -> Signal:
    _require(type(group) is dict, "BAD_OBSERVATION")
    _require(group.get("independently_authenticated") is False and
             group.get("release_permission") is False, "GROUP_AUTH_CLAIM")
    _require(type(group.get("candidate_observation")) is bool,
             "BAD_CANDIDATE_FLAG")
    _require(group.get("head_currentness") in
             ("EXACT_HEAD", "STALE_HEAD", "UNKNOWN_HEAD"),
             "BAD_HEAD_CURRENTNESS")
    if group["candidate_observation"]:
        _require(group["head_currentness"] == "EXACT_HEAD",
                 "CONTRADICTORY_CANDIDATE_HEAD")
    ref = {key: group.get(key) for key in
           ("repository", "subject", "head", "incident_key")}
    _require(all(type(ref[k]) is str for k in
                 ("repository", "subject", "incident_key")), "BAD_INCIDENT_KEY")
    _require(ref["head"] is None or
             (type(ref["head"]) is str and
              SHA40.fullmatch(ref["head"]) is not None), "BAD_INCIDENT_HEAD")
    if group["candidate_observation"]:
        _require(ref["head"] is not None, "CANDIDATE_MISSING_HEAD")
    canonical = json.dumps(ref, sort_keys=True, ensure_ascii=True,
                           separators=(",", ":")).encode("utf-8")
    digest = sha256(canonical).hexdigest()
    _require(type(group.get("observation_key")) is str and
             SHA64.fullmatch(group["observation_key"]) is not None and
             group["observation_key"] == digest, "INCIDENT_KEY_MISMATCH")
    observed_at = group.get("observation_timestamp")
    _require(type(observed_at) is str, "BAD_SOURCE_TIMESTAMP")

    # A group from B's output is only a claim. Even valid hashes and alleged
    # EXACT_HEAD flags are NOT evidence admission or ownership authentication.
    # Keep every resulting decision private, never attach raw source refs here.
    subject = ref["repository"] + "@" + ref["subject"]
    try:
        return Signal(
            signal_id="untrusted-" + digest[:24],
            fingerprint=digest,
            subject=subject,
            domain="coordination",
            cause="source-observation-unverified",
            evidence_refs=("untrusted-source-proposal-v1",),
            evidence_classes=(EvidenceClass.DOC,),
            exact_head=ref["head"],
            observed_at=observed_at,
            freshness_hours=48,
            severity=3,
            relevance=3,
            actionability=3 if group["candidate_observation"] else 0,
            confidence=0,
            hours_to_impact=72,
            concrete_next_step="Independently verify source and ownership privately",
            owner_lane="UNASSIGNED",
            corroborated=False,
            source_verified_by_evaluator=False,
            contains_private_data=True,
            externally_visible=False,
            needs_user_decision=False,
            outcome_is_release=False,
        )
    except (ValueError, TypeError):
        raise AdmissionError("INVALID_UNTRUSTED_SIGNAL") from None


def review_untrusted(document: dict, *, now: str) -> dict:
    """Read-only source proposal review: no host admission, release or emitted signal.

    This API deliberately has no argument for verified IDs, owner ACKs,
    owner lanes, authenticated provider or notification logs.
    """
    raw = _signal_document(document)
    groups = raw.get("observations")
    _require(type(groups) is list and len(groups) <= MAX_GROUPS,
             "GROUP_BUDGET_EXCEEDED")
    try:
        parse_time(now)
        proposals = [_untrusted_signal(x) for x in groups]
        context = Context(now=now, daily_notification_limit=0)
        batch = evaluate(proposals, context)
    except AdmissionError:
        raise
    except (ValueError, TypeError, OverflowError):
        raise AdmissionError("INVALID_DRY_RUN_INPUT") from None

    # Source claims can at most become local review drafts. No direct Decision,
    # raw subject, fingerprint, input reports or provenance refs are exported.
    _require(all(d.action in (Action.DRAFT, Action.SILENT) and d.private_subject
                 and not d.emitted and not d.effect_authority
                 for d in batch.decisions), "INTERNAL_POLICY_UNTRUSTED")
    return {
        "schema": OUTPUT_SCHEMA,
        "reviewed_count": len(batch.decisions),
        # This API is an internal review summary, NOT a public Decision.
        # Keep only the local action; never export private priority, reasons,
        # domain, incident ID, source references or owner attributes.
        "decisions": [{"fingerprint": "", "action": d.action.value}
                      for d in batch.decisions],
        "source_authentication": "UNVERIFIED_NO_SIGNED_RECEIPT",
        "trusted_context_admitted": False,
        "notifier_active": False,
        "release_permission": False,
        "external_effects": [],
        "currentness_qualified": False,
        "replay_persisted": False,
    }
