"""Source-only WeKnora-to-SPM activation decision; NOT memory admission.

WeKnora provides untrusted search evidence; SPM's memory specialist activates
only in the presence of retrieval. This boundary passes a *count*, never
untrusted document instructions, and cannot attest the retrieval index epoch.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from spm_bench.memory_specialist import memory_adapter_active
from weknora_adapter import RetrievalBatch, SearchHit, WEKNORA_SOURCE_SHA


SPM_SOURCE_SHA = "64e41c0f1a95cb563051680d46f78287e875ede5"


@dataclass(frozen=True, slots=True)
class SPMGateDecision:
    knowledge_base_id: str
    retrieved_count: int
    adapter_active: bool
    evidence_digest: str
    qualification: str = "UNATTESTED_RETRIEVAL_GATE_ONLY"
    spm_source_sha: str = SPM_SOURCE_SHA
    weknora_source_sha: str = WEKNORA_SOURCE_SHA


def gate_from_retrieval(batch: RetrievalBatch, *, expected_knowledge_base_id: str) -> SPMGateDecision:
    """Derive a bounded source-level switch, without admitting external memory.

    A structurally valid ``RetrievalBatch`` can still be forged by a caller;
    the content digest is byte provenance, NOT an authenticated observation.
    """
    if not isinstance(batch, RetrievalBatch):
        raise TypeError("typed WeKnora retrieval batch required")
    if (not isinstance(expected_knowledge_base_id, str)
            or not expected_knowledge_base_id
            or batch.knowledge_base_id != expected_knowledge_base_id):
        raise ValueError("knowledge-base scope mismatch")
    if not isinstance(batch.query, str) or not batch.query.strip():
        raise ValueError("a retrieval query is required")
    if len(batch.hits) > 30:
        raise ValueError("retrieved context budget exceeded")
    seen = set()
    evidence = []
    for hit in batch.hits:
        if (not isinstance(hit, SearchHit)
                or hit.knowledge_base_id != expected_knowledge_base_id
                or not isinstance(hit.chunk_id, str) or not hit.chunk_id
                or not isinstance(hit.knowledge_id, str) or not hit.knowledge_id
                or not isinstance(hit.content, str) or not hit.content):
            raise ValueError("invalid or out-of-scope retrieval hit")
        identity = (hit.knowledge_id, hit.chunk_id)
        if identity in seen:
            raise ValueError("duplicate retrieval chunk identity")
        seen.add(identity)
        evidence.append({
            "knowledge_id": hit.knowledge_id,
            "chunk_id": hit.chunk_id,
            "content_sha256": sha256(hit.content.encode("utf-8")).hexdigest(),
        })
    payload = {
        "knowledge_base_id": expected_knowledge_base_id,
        "query": batch.query,
        "retrieval_hits": evidence,
        "upstream_source_sha": WEKNORA_SOURCE_SHA,
    }
    return SPMGateDecision(
        knowledge_base_id=expected_knowledge_base_id,
        retrieved_count=len(evidence),
        adapter_active=memory_adapter_active(len(evidence)),
        evidence_digest=sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    )


def select_spm_view(runtime, batch: RetrievalBatch, *, expected_knowledge_base_id: str):
    """Revalidate retrieval data at the activation boundary; never train."""
    decision = gate_from_retrieval(batch, expected_knowledge_base_id=expected_knowledge_base_id)
    view = runtime.view_for_retrieval(decision.retrieved_count)
    if view.memory_active is not decision.adapter_active:
        raise RuntimeError("SPM runtime disagrees with retrieval-derived gate")
    return view, decision
