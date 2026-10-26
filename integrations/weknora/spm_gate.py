"""Source-only WeKnora-to-SPM activation decision; NOT memory admission.

WeKnora provides untrusted search evidence; SPM's memory specialist activates
only in the presence of retrieval. This boundary passes a *count*, never
untrusted document instructions, and cannot attest the retrieval index epoch.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import inspect
import json
import math
from pathlib import Path

from spm_bench.memory_specialist import memory_adapter_active
from weknora_adapter import RetrievalBatch, SearchHit, WEKNORA_SOURCE_SHA


SPM_SOURCE_SHA = "64e41c0f1a95cb563051680d46f78287e875ede5"
SPM_GATE_MODULE_SHA256 = "601b465b7ee881fd38acbd45c8f9d7897f556e404eac66615e918ce47f14cf4a"


def _finite_score(value: object) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _verify_spm_gate_source() -> None:
    """Bind the imported SPM activation implementation to reviewed bytes."""
    path = Path(inspect.getfile(memory_adapter_active))
    if sha256(path.read_bytes()).hexdigest() != SPM_GATE_MODULE_SHA256:
        raise RuntimeError("imported SPM activation source differs from pinned contract")


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
    _verify_spm_gate_source()
    if (not isinstance(expected_knowledge_base_id, str)
            or not expected_knowledge_base_id
            or batch.knowledge_base_id != expected_knowledge_base_id):
        raise ValueError("knowledge-base scope mismatch")
    if not isinstance(batch.query, str) or not batch.query.strip():
        raise ValueError("a retrieval query is required")
    if type(batch.hits) is not tuple or len(batch.hits) > 30:
        raise ValueError("retrieved context budget exceeded")
    seen = set()
    evidence = []
    total_bytes = 0
    for hit in batch.hits:
        if (not isinstance(hit, SearchHit)
                or hit.knowledge_base_id != expected_knowledge_base_id
                or not isinstance(hit.chunk_id, str) or not hit.chunk_id
                or not isinstance(hit.knowledge_id, str) or not hit.knowledge_id
                or not isinstance(hit.content, str) or not hit.content):
            raise ValueError("invalid or out-of-scope retrieval hit")
        if (not _finite_score(hit.score)
                or type(hit.match_type) is not int or not 0 <= hit.match_type <= 9
                or not isinstance(hit.metadata, dict)
                or any(type(offset) is not int or offset < 0
                       for offset in (hit.start_at, hit.end_at) if offset is not None)
                or (hit.start_at is not None and hit.end_at is not None
                    and hit.end_at < hit.start_at)
                or any(not isinstance(s, str) for s in
                       (hit.title, hit.source, hit.channel, hit.filename))):
            raise ValueError("malformed retrieval evidence metadata")
        total_bytes += len(hit.content.encode("utf-8"))
        if total_bytes > 2 * 1024 * 1024:
            raise ValueError("retrieved content exceeds declared byte ceiling")
        identity = (hit.knowledge_id, hit.chunk_id)
        if identity in seen:
            raise ValueError("duplicate retrieval chunk identity")
        seen.add(identity)
        evidence.append({
            "knowledge_id": hit.knowledge_id,
            "chunk_id": hit.chunk_id,
            "content_sha256": sha256(hit.content.encode("utf-8")).hexdigest(),
            "score": float(hit.score),
            "match_type": hit.match_type,
            "source": hit.source,
            "channel": hit.channel,
            "filename": hit.filename,
            "metadata": hit.metadata,
        })
    payload = {
        "knowledge_base_id": expected_knowledge_base_id,
        "query": batch.query,
        "retrieval_hits": evidence,
        "upstream_source_sha": WEKNORA_SOURCE_SHA,
    }
    try:
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    except (TypeError, ValueError) as exc:
        raise ValueError("retrieval metadata is not canonical JSON") from exc
    return SPMGateDecision(
        knowledge_base_id=expected_knowledge_base_id,
        retrieved_count=len(evidence),
        adapter_active=memory_adapter_active(len(evidence)),
        evidence_digest=digest,
    )


def select_spm_view(runtime, batch: RetrievalBatch, *, expected_knowledge_base_id: str):
    """Revalidate retrieval data at the activation boundary; never train."""
    decision = gate_from_retrieval(batch, expected_knowledge_base_id=expected_knowledge_base_id)
    view = runtime.view_for_retrieval(decision.retrieved_count)
    if view.memory_active is not decision.adapter_active:
        raise RuntimeError("SPM runtime disagrees with retrieval-derived gate")
    return view, decision
