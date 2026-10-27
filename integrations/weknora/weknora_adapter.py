"""Read-only, fail-closed WeKnora hybrid-retrieval boundary.

Bound to Tencent/WeKnora source contract at
26fe2a08e9f63ae34c79584957e4f375408dea4a, not a claim about any
installed WeKnora instance. This module never trains a model or changes weights.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


WEKNORA_SOURCE_SHA = "26fe2a08e9f63ae34c79584957e4f375408dea4a"
_KB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_RESPONSE_MAX_BYTES = 2 * 1024 * 1024


class RetrievalError(Exception):
    """Remote failure or unsafe response, never a partial success."""


class ScopeError(RetrievalError):
    """Requested or returned knowledge base is outside the adapter scope."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


@dataclass(frozen=True)
class SearchHit:
    knowledge_base_id: str
    knowledge_id: str
    chunk_id: str
    content: str
    title: str
    score: float
    match_type: int
    source: str
    channel: str
    filename: str
    start_at: int | None
    end_at: int | None
    metadata: dict[str, Any]

    @property
    def score_semantics(self) -> str:
        # WeKnora SDK documents vector/keyword fusion as raw RRF ~0-.03.
        # Some match types come from other pipeline stages; never infer a
        # calibrated relevance percentage or cosine similarity.
        return "weknora_raw_pipeline_score_not_cosine_or_probability"


@dataclass(frozen=True)
class RetrievalBatch:
    knowledge_base_id: str
    query: str
    retrieved_at_utc: str
    hits: tuple[SearchHit, ...]


@dataclass(frozen=True)
class DocumentIngestionState:
    """Document status independently read back from WeKnora, not an index epoch."""

    knowledge_base_id: str
    knowledge_id: str
    parse_status: str
    enable_status: str
    embedding_model_id: str
    file_hash: str
    checked_at_utc: str

    @property
    def ready(self) -> bool:
        # Upstream finalizing documents are searchable, but enrichment is
        # incomplete. This conservative gate admits completed entries only.
        return self.parse_status == "completed" and self.enable_status == "enabled"


class WeKnoraRetrievalAdapter:
    """Single-KB hybrid search via WeKnora's scoped REST endpoint.

    `allowed_knowledge_base_ids` is an independently configured allowlist,
    not a discovery result from a potentially compromised remote service.
    Prefer a read-only, KB-scoped WeKnora API key. Never pass this key to logs.
    """

    def __init__(self, *, base_url: str, api_key: str,
                 allowed_knowledge_base_ids: tuple[str, ...],
                 timeout_seconds: float = 10.0):
        parsed = urlsplit(base_url)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname
                or parsed.username or parsed.password or parsed.query
                or parsed.fragment or parsed.path not in ("", "/")):
            raise ValueError("base_url must be an HTTP(S) origin without credentials or path")
        if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("unencrypted HTTP is allowed only for loopback WeKnora")
        if not api_key or not isinstance(api_key, str):
            raise ValueError("a nonempty API key is required")
        if not allowed_knowledge_base_ids or any(
            not isinstance(k, str) or not _KB_ID.fullmatch(k) or k in (".", "..")
            for k in allowed_knowledge_base_ids
        ):
            raise ValueError("explicit nonempty, valid KB ID allowlist required")
        if not (0 < timeout_seconds <= 120) or not math.isfinite(timeout_seconds):
            raise ValueError("timeout must be finite, positive, and at most 120s")
        self._origin = base_url.rstrip("/")
        self._api_key = api_key
        self._allow = frozenset(allowed_knowledge_base_ids)
        self._timeout = timeout_seconds
        self._opener = build_opener(_NoRedirect())

    def search(self, *, knowledge_base_id: str, query: str,
               match_count: int = 10) -> RetrievalBatch:
        if knowledge_base_id not in self._allow:
            raise ScopeError("knowledge base is not in the configured allowlist")
        if not isinstance(query, str) or not query.strip() or len(query.encode("utf-8")) > 8192:
            raise ValueError("query must contain 1..8192 UTF-8 bytes")
        if type(match_count) is not int or not 1 <= match_count <= 30:
            raise ValueError("match_count must be an integer between 1 and 30")

        payload = json.dumps({
            "query_text": query.strip(),
            "vector_threshold": 0.0,
            "keyword_threshold": 0.0,
            "match_count": match_count,
            "disable_keywords_match": False,
            "disable_vector_match": False,
            "knowledge_base_ids": [knowledge_base_id],
            # No rerank: preserve the raw WeKnora RRF/fusion score.
        }).encode("utf-8")
        url = (self._origin + "/api/v1/knowledge-bases/"
               + quote(knowledge_base_id, safe="") + "/hybrid-search")
        request = Request(url, data=payload, method="POST", headers={
            "Authorization": "Bearer " + self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        obj = self._request_json(request)
        if not isinstance(obj, dict) or obj.get("success") is not True or not isinstance(obj.get("data"), list):
            raise RetrievalError("WeKnora returned an unsuccessful or malformed result")
        if len(obj["data"]) > match_count:
            raise RetrievalError("WeKnora returned more hits than the requested context budget")
        hits = tuple(self._parse_hit(item, knowledge_base_id) for item in obj["data"])
        return RetrievalBatch(
            knowledge_base_id=knowledge_base_id,
            query=query.strip(),
            retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
            hits=hits,
        )

    def _request_json(self, request: Request) -> Any:
        """Shared bounded transport with no redirect of the bearer token."""
        try:
            with self._opener.open(request, timeout=self._timeout) as response:
                raw = response.read(_RESPONSE_MAX_BYTES + 1)
        except HTTPError as exc:
            status = exc.code
            exc.close()
            raise RetrievalError(f"WeKnora returned HTTP {status}") from None
        except (URLError, OSError) as exc:
            raise RetrievalError("WeKnora request failed") from exc
        if len(raw) > _RESPONSE_MAX_BYTES:
            raise RetrievalError("WeKnora response exceeds safety size limit")
        try:
            return json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise RetrievalError("WeKnora returned invalid JSON") from None

    def document_ingestion_state(self, *, knowledge_base_id: str,
                                 knowledge_id: str) -> DocumentIngestionState:
        """Read GET /knowledge/:id after ingestion; never trigger ingestion.

        Upstream enforces document-parent KB read access. The returned KB ID is
        also checked locally against the explicitly configured KB allowlist.
        A successful status read does not prove that the search index and the
        document row belong to one atomic snapshot.
        """
        if knowledge_base_id not in self._allow:
            raise ScopeError("knowledge base is not in the configured allowlist")
        if (not isinstance(knowledge_id, str) or not _KB_ID.fullmatch(knowledge_id)
                or knowledge_id in (".", "..")):
            raise ValueError("knowledge_id must be a valid single path segment")
        request = Request(
            self._origin + "/api/v1/knowledge/" + quote(knowledge_id, safe=""),
            method="GET",
            headers={"Authorization": "Bearer " + self._api_key, "Accept": "application/json"},
        )
        obj = self._request_json(request)
        if not isinstance(obj, dict) or obj.get("success") is not True:
            raise RetrievalError("WeKnora returned unsuccessful document readback")
        data = obj.get("data")
        if not isinstance(data, dict):
            raise RetrievalError("WeKnora returned malformed document readback")
        if data.get("knowledge_base_id") != knowledge_base_id:
            raise ScopeError("document readback is outside the requested knowledge base")
        if data.get("id") != knowledge_id:
            raise RetrievalError("document readback identity mismatch")
        if (data.get("parse_status") not in (
                "pending", "processing", "finalizing", "completed", "failed", "deleting", "cancelled")
                or data.get("enable_status") not in ("enabled", "disabled")
                or not isinstance(data.get("embedding_model_id"), str)
                or not isinstance(data.get("file_hash"), str)):
            raise RetrievalError("document readback has malformed ingestion fields")
        return DocumentIngestionState(
            knowledge_base_id=knowledge_base_id,
            knowledge_id=knowledge_id,
            parse_status=data["parse_status"],
            enable_status=data["enable_status"],
            embedding_model_id=data["embedding_model_id"],
            file_hash=data["file_hash"],
            checked_at_utc=datetime.now(timezone.utc).isoformat(),
        )

    def verify_batch_ingestion_ready(self, batch: RetrievalBatch) -> tuple[DocumentIngestionState, ...]:
        """Read back each distinct hit's ingest status before experimental use.

        This checks server-reported terminal state, *not* content/hash custody,
        caller authenticity of a constructed batch, ACL revision or index epoch.
        Call immediately after ``search`` and do not use as memory admission.
        """
        if not isinstance(batch, RetrievalBatch) or batch.knowledge_base_id not in self._allow:
            raise ScopeError("retrieval batch is outside the configured knowledge-base scope")
        if type(batch.hits) is not tuple or len(batch.hits) > 30:
            raise RetrievalError("invalid retrieval batch context budget")
        if not batch.hits:
            raise RetrievalError("empty retrieval batch has no ingestion evidence")
        knowledge_ids = []
        seen = set()
        for hit in batch.hits:
            if not isinstance(hit, SearchHit) or hit.knowledge_base_id != batch.knowledge_base_id:
                raise ScopeError("retrieval hit is outside the requested knowledge base")
            if not isinstance(hit.knowledge_id, str) or not _KB_ID.fullmatch(hit.knowledge_id):
                raise RetrievalError("retrieval hit has invalid document identity")
            if hit.knowledge_id not in seen:
                seen.add(hit.knowledge_id)
                knowledge_ids.append(hit.knowledge_id)
        states = tuple(self.document_ingestion_state(
            knowledge_base_id=batch.knowledge_base_id, knowledge_id=knowledge_id,
        ) for knowledge_id in knowledge_ids)
        if any(not state.ready for state in states):
            raise RetrievalError("retrieval batch references incomplete or disabled ingestion")
        return states

    @staticmethod
    def _parse_hit(item: Any, expected_kb: str) -> SearchHit:
        if not isinstance(item, dict):
            raise RetrievalError("WeKnora returned an invalid retrieval hit")
        kb = item.get("knowledge_base_id")
        if kb != expected_kb:
            raise ScopeError("retrieval hit lacks correct knowledge base provenance")
        for field in ("id", "knowledge_id", "content"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise RetrievalError(f"retrieval hit lacks {field} provenance/content")
        score = item.get("score")
        try:
            valid_score = (type(score) in (float, int) and math.isfinite(float(score)))
        except (OverflowError, ValueError):
            valid_score = False
        if not valid_score:
            raise RetrievalError("retrieval hit has invalid score")
        match_type = item.get("match_type")
        if type(match_type) is not int or not 0 <= match_type <= 9:
            raise RetrievalError("retrieval hit has invalid or unsupported match type")
        metadata = item.get("metadata")
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise RetrievalError("retrieval hit metadata is not an object")
        for f in ("knowledge_title", "knowledge_source", "knowledge_channel", "knowledge_filename"):
            if item.get(f, "") is not None and not isinstance(item.get(f, ""), str):
                raise RetrievalError(f"retrieval hit {f} is malformed")
        for f in ("start_at", "end_at"):
            if item.get(f) is not None and type(item[f]) is not int:
                raise RetrievalError(f"retrieval hit {f} is malformed")
        return SearchHit(
            knowledge_base_id=kb, knowledge_id=item["knowledge_id"],
            chunk_id=item["id"], content=item["content"],
            title=item.get("knowledge_title") or "", score=float(score),
            match_type=match_type, source=item.get("knowledge_source") or "",
            channel=item.get("knowledge_channel") or "",
            filename=item.get("knowledge_filename") or "",
            start_at=item.get("start_at"), end_at=item.get("end_at"),
            metadata=metadata,
        )
