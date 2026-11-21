"""Read-only PR125 source finding -> Engineer B PR123 signal envelope.
No source retrieval, identity verification, dispatch, provider or host effects.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import islice
from typing import Iterable
from urllib.parse import quote
import re

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")
PATH = re.compile(r"^[A-Za-z0-9_./-]{1,200}$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
MAX_FINDINGS = 256

def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)

def field(f, k):
    return f.get(k) if type(f) is dict else getattr(f, k, None)

def adapt(findings: Iterable[object], *, repository: str,
          observed_head: str, current_head: str, subject: str,
          observed_at: str, host_access_cutoff: str) -> dict:
    """Adapter output is untrusted input to normalize(), not permission."""
    require(type(repository) is str and REPO.fullmatch(repository) is not None, "INVALID_REPOSITORY")
    require(type(observed_head) is str and SHA.fullmatch(observed_head) is not None, "INVALID_OBSERVED_HEAD")
    require(type(current_head) is str and SHA.fullmatch(current_head) is not None, "INVALID_CURRENT_HEAD")
    require(type(subject) is str and IDENT.fullmatch(subject) is not None, "INVALID_SUBJECT")
    require(type(observed_at) is str and type(host_access_cutoff) is str, "INVALID_TIME")
    rows=list(islice(findings,MAX_FINDINGS+1))
    require(len(rows)<=MAX_FINDINGS, "TOO_MANY_FINDINGS_NO_SILENT_TRUNCATION")
    observations=[]
    severe=[]
    seen_severe={}
    for i,f in enumerate(rows):
        path,rule,digest,incident,severity=(field(f,k) for k in
            ("path","rule_id","source_digest","incident_id","severity"))
        require(type(path) is str and PATH.fullmatch(path) is not None and
                '..' not in path.split('/') and not path.startswith('/') and
                not path.startswith('supabase/'), "UNSUPPORTED_SOURCE_PATH")
        require(type(rule) is str and re.fullmatch(r"[A-Z][A-Z0-9_]{1,90}",rule) is not None, "INVALID_RULE")
        require(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}",digest) is not None,
                "INVALID_SOURCE_DIGEST")
        require(severity in ("CRITICAL","HIGH","MEDIUM","LOW","INFO"),"INVALID_SEVERITY")
        require(field(f,"authority")=="NONE" and
                field(f,"evidence_class")=="SOURCE_INSPECTION" and
                field(f,"independent_revalidation")=="NOT_PERFORMED",
                "UNTRUSTED_EFFECT_CLAIM")
        expected=sha256('\0'.join([repository,observed_head,path,rule,digest]).encode()).hexdigest()[:24]
        require(incident==expected,"FINDING_SOURCE_HEAD_BINDING_MISMATCH")
        key="src:"+expected
        observations.append({
            "id":f"scan-{i:03d}-{expected}",
            "kind":"SECURITY_DEPENDENCY_CHANGE",
            "status":"INVALIDATED" if severity in ("CRITICAL","HIGH") else "UNCHANGED",
            "repository":repository,"subject":subject,"head":observed_head,
            "incident_key":key,"observed_at":observed_at,
            "source_ref":f"https://github.com/{repository}/blob/{observed_head}/{quote(path,safe='/._-')}",
            "evidence_class":"SOURCE","claimed_owner":"unverified-scanner",
            "claimed_reviewer":None,"claims_authenticated":False})
        if severity in ("CRITICAL","HIGH"):
            if key not in seen_severe:
                seen_severe[key]=len(severe)
                severe.append({"incident_key":key,"severity":severity,
                               "rule":rule,"review_status":"INDEPENDENT_REVALIDATION_REQUIRED"})
            elif severity=="CRITICAL":
                severe[seen_severe[key]]["severity"]="CRITICAL"
    doc={"schema":"BT2_ECOSYSTEM_SIGNAL_INPUT_V1",
         "snapshot":{"observed_at":observed_at,"host_access_cutoff":host_access_cutoff,
                     "subjects":[{"repository":repository,"subject":subject,
                                  "head":current_head,"runtime_required":False,
                                  "reported_runtime_status":"UNKNOWN"}]},
         "observations":observations}
    return {"ingest_input":doc,"severe_review_queue":severe,
            "source_binding_verified":False,"authorization":"NONE",
            "external_effects":[],
            "limitations":["CALLER_SUPPLIED_REPOSITORY_HEAD_TIMESTAMP_AND_CUTOFF",
                           "SOURCE_BYTES_NOT_INDEPENDENTLY_VERIFIED",
                           "INCIDENT_EQUIVALENCE_PROVISIONAL",
                           "NO_PERMISSION_OR_LIVE_RUNTIME_ATTESTATION"]}
