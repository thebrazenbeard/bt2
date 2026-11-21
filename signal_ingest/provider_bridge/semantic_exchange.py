"""Bounded Semantic Atlas / VSNS / Empathy evidence exchange, advisory only.

This is a typed adapter for already-evaluated, untrusted research outputs,
not an identity, experience, consent, memory or authority verifier. No
transcript, individual identifier, provider service, or persistence method.
"""
from __future__ import annotations

from hashlib import sha256
import math
import re
from typing import Any

from signal_ingest.provider_bridge.v1 import canonical

INPUT_SCHEMA="BT2_SEMANTIC_EVIDENCE_EXCHANGE_INPUT_V1"
OUTPUT_SCHEMA="BT2_SEMANTIC_EVIDENCE_EXCHANGE_OUTPUT_V1"
HEAD=re.compile(r"[0-9a-f]{40}\Z")
OPAQUE=re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}\Z")
EVID=re.compile(r"ev_[0-9a-f]{32}\Z")
HYP=re.compile(r"hyp_[0-9a-f]{32}\Z")
ATLAS_PATH="schemas/semantic_atlas_v0.1.schema.json"
VSNS_EFFECTS=("consent_effect","authority_effect","decision_effect","action_effect",
              "identity_effect","memory_admission_effect")
VSNS_FIELDS={
    "schema","speech_act","reality_layer","event_class","interpretation_status",
    "candidates","interrupt_suggested","calibration","claim_ceiling",
    "provider_currentness","behavioral_qualification","phenomenology",
    *VSNS_EFFECTS,
}
EMPATHY_FIELDS={
    "schema","consumer","policy","reason_code","confidence_band",
    "supporting_evidence_ids","superseded_hypothesis_ids","focus_needed",
    "authority","persistence","volition_want_authority","effect_authority"
}
CANDIDATE_FIELDS={
    "meaning_id","domain","claimed_evidence_class","evidence_origin_trust",
    "salience","uncertainty","boundary_tension","semantic_relevance"
}
DOMAINS={
    "INTELLECTUAL","RELATIONAL","IDENTITY","AUTONOMY_BOUNDARY",
    "THREAT_SAFETY","VALUE_ETHICAL","GOAL_ACTION","SYMBOLIC","CONATIVE"
}
EVIDENCE={
    "USER_DIRECT","SYMBOLIC_TEXT","MODEL_INFERENCE","HISTORICAL_SOURCE","SYNTHETIC_TEST"
}
POLICIES={
    "CLARIFY_MEANING","TASK_DIRECT","REPAIR_FIRST","CELEBRATE_FIRST",
    "TRUTHFUL_CHALLENGE","PRESERVE_PLAY","STOP_PLAY"
}


class SemanticExchangeError(ValueError):
    """No private payload in errors."""


def need(flag: bool, code: str) -> None:
    if not flag:
        raise SemanticExchangeError(code)


def closed(obj: Any, keys: set[str], code: str) -> dict:
    need(type(obj) is dict and set(obj)==keys,code)
    return obj


def fraction(v: Any) -> bool:
    if type(v) not in (float,int):
        return False
    # Range-check Python's unbounded integers BEFORE float conversion.
    if type(v) is int:
        return 0 <= v <= 1
    return math.isfinite(v) and 0 <= v <= 1


def exchange(data: dict) -> dict:
    closed(data,{"schema","source","vsns","empathy"},"INVALID_FRAME")
    need(data["schema"]==INPUT_SCHEMA,"INVALID_SCHEMA")
    source=closed(data["source"],{"repository","head","source_ref","surface","evidence_class",
            "vsns_repository","vsns_head","vsns_ref","empathy_repository","empathy_head","empathy_ref"},
                  "INVALID_SOURCE")
    head=source["head"]
    need(source["repository"]=="thebrazenbeard/semanticatlas" and
         type(head) is str and HEAD.fullmatch(head) is not None and
         source["source_ref"]==
            f"https://github.com/thebrazenbeard/semanticatlas/blob/{head}/{ATLAS_PATH}" and
         source["surface"]=="RESEARCH_STAGING" and
         source["evidence_class"]=="SOURCE", "UNQUALIFIED_ATLAS_LOCATOR")
    vh=source["vsns_head"]
    eh=source["empathy_head"]
    need(type(vh) is str and HEAD.fullmatch(vh) is not None and
         type(eh) is str and HEAD.fullmatch(eh) is not None and
         source["vsns_repository"]=="thebrazenbeard/vera" and
         source["empathy_repository"]=="thebrazenbeard/empathy" and
         source["vsns_ref"]==
             f"https://github.com/thebrazenbeard/vera/blob/{vh}/runtime_cohesion/vsns_reception.py" and
         source["empathy_ref"]==
             f"https://github.com/thebrazenbeard/empathy/blob/{eh}/empathy_research/integration_contract.py",
         "UNQUALIFIED_CROSS_REPO_SOURCE")
    v=closed(data["vsns"],VSNS_FIELDS,"INVALID_VSNS_RESULT")
    need(v["schema"]=="VERA_VSNS_RECEPTION_RESULT_V0_1" and
         v["calibration"]=="DETERMINISTIC_HEURISTIC_NOT_EMPIRICALLY_VALIDATED" and
         v["claim_ceiling"]=="SEMANTIC_SALIENCE_ADVISORY_ONLY" and
         v["provider_currentness"]=="UNVERIFIED" and
         v["behavioral_qualification"]=="NOT_ESTABLISHED" and
         v["phenomenology"]=="UNRESOLVED" and
         all(v[k]=="NONE" for k in VSNS_EFFECTS), "VSNS_AUTHORITY_FENCE")
    need(type(v["interrupt_suggested"]) is bool and
         v["speech_act"] in ("SHARING","QUESTION","REQUEST","PERMISSION",
                              "SYMBOLIC_ACTION","HYPOTHETICAL","CORRECTION") and
         v["reality_layer"] in ("CONVERSATIONAL_SYMBOLIC","PHYSICAL_REPORTED","HYPOTHETICAL") and
         v["event_class"] in ("NONE","PROPOSED_ONLY","SYMBOLIC_ENACTED_IN_TEXT",
                               "REPORTED_PHYSICAL_EVENT") and
         v["interpretation_status"] in ("MULTIPLE_CANDIDATES_UNRESOLVED",
                                        "SINGLE_CANDIDATE_UNCERTAIN",
                                        "SINGLE_CANDIDATE_UNVERIFIED"),
         "INVALID_VSNS_TYPES")
    need(not (v["event_class"]=="REPORTED_PHYSICAL_EVENT" and
              v["reality_layer"]!="PHYSICAL_REPORTED") and
         not (v["event_class"]=="SYMBOLIC_ENACTED_IN_TEXT" and
              v["reality_layer"]!="CONVERSATIONAL_SYMBOLIC"), "CONTRADICTORY_REALITY_LAYER")
    candidates=v["candidates"]
    need(type(candidates) is list and 1<=len(candidates)<=8,"VSNS_BUDGET_EXCEEDED")
    seen=set()
    ids=[]
    for c in candidates:
        closed(c,CANDIDATE_FIELDS,"INVALID_SEMANTIC_CANDIDATE")
        meaning=c["meaning_id"]
        need(type(meaning) is str and OPAQUE.fullmatch(meaning) is not None
             and meaning not in seen,"INVALID_MEANING_ID")
        seen.add(meaning)
        ids.append(meaning)
        need(c["domain"] in DOMAINS and c["claimed_evidence_class"] in EVIDENCE and
             c["evidence_origin_trust"]=="UNVERIFIED_CALLER_ASSERTION" and
             all(fraction(c[k]) for k in ("salience","uncertainty",
                                          "boundary_tension","semantic_relevance")),
             "UNTRUSTED_SEMANTIC_CANDIDATE")
    need((len(candidates)>1)==(v["interpretation_status"]=="MULTIPLE_CANDIDATES_UNRESOLVED"),
         "AMBIGUITY_STATUS_CONFLICT")
    e=closed(data["empathy"],EMPATHY_FIELDS,"INVALID_EMPATHY_HINT")
    need(e["schema"]=="EMPATHY_RESPONSE_POLICY_HINT_V1" and
         e["consumer"]=="RESPONSE_POLICY_ONLY" and
         e["authority"]=="NONE" and
         e["persistence"]=="EPHEMERAL" and
         e["volition_want_authority"] is False and
         e["effect_authority"] is False and
         e["policy"] in POLICIES and
         e["confidence_band"] in ("NONE","TENTATIVE","HIGH_SCORE") and
         type(e["focus_needed"]) is bool and
         type(e["reason_code"]) is str and OPAQUE.fullmatch(e["reason_code"]) is not None,
         "EMPATHY_AUTHORITY_FENCE")
    support=e["supporting_evidence_ids"]
    superseded=e["superseded_hypothesis_ids"]
    need(type(support) is list and len(support)<=32 and
         all(type(x) is str and EVID.fullmatch(x) for x in support) and
         len(support)==len(set(support)) and
         type(superseded) is list and len(superseded)<=32 and
         all(type(x) is str and HYP.fullmatch(x) for x in superseded) and
         len(superseded)==len(set(superseded)),"PRIVATE_ID_SHAPE_UNQUALIFIED")
    return {
        "schema":OUTPUT_SCHEMA,
        "source_repository":source["repository"],
        "source_head":head,
        "source_binding":"EXACT_DECLARED_SOURCE_REF_NOT_INDEPENDENTLY_AUTHENTICATED",
        "source_ref_sha256":sha256(source["source_ref"].encode()).hexdigest(),
        "vsns_source_head":vh,
        "empathy_source_head":eh,
        "vsns_source_ref_sha256":sha256(source["vsns_ref"].encode()).hexdigest(),
        "empathy_source_ref_sha256":sha256(source["empathy_ref"].encode()).hexdigest(),
        "semantic_authority":"RESEARCH_ONLY",
        "semantic_currentness":"UNVERIFIED_SOURCE_SNAPSHOT",
        # Local position aliases deliberately do not echo or hash caller ID text.
        # Hashing low-entropy labels would still permit offline guessing.
        "candidate_meaning_ids":[f"candidate_{i+1}" for i in range(len(ids))],
        "semantic_provenance":"UNVERIFIED_CALLER_ASSERTION",
        "salience_role":"ATTENTION_HINT_NOT_TRUTH",
        "reality_layer":v["reality_layer"],
        "event_class":v["event_class"],
        "empathy_policy_hint":e["policy"],
        "empathy_consumer":"RESPONSE_POLICY_ONLY",
        "empathy_confidence_role":"SCORE_NOT_PROBABILITY",
        "supporting_evidence_count":len(support),
        "truth":"NOT_DETERMINED",
        "consent":"NOT_GRANTED",
        "action_authority":"NONE",
        "identity_assertion":"NONE",
        "autobiographical_admission":"NONE",
        "memory_admission":"NONE",
        "phenomenology":"UNRESOLVED",
        "independently_authenticated":False,
        "side_effects":[],
    }


__all__=["exchange","SemanticExchangeError"]