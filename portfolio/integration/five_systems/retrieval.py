"""Read-only scoped WeKnora API boundary; retrieval never authorizes actions."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from typing import Callable
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class RetrievalBoundaryError(ValueError):
    """Reject ambiguous, unscoped or forged retrieval evidence."""


@dataclass(frozen=True)
class Passage:
    knowledge_base_id: str
    knowledge_id: str
    chunk_id: str
    content: str
    score: float

    def __post_init__(self):
        for field in ("knowledge_base_id", "knowledge_id", "chunk_id", "content"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise RetrievalBoundaryError("invalid " + field)
        if type(self.score) not in (int, float) or not math.isfinite(self.score):
            raise RetrievalBoundaryError("invalid retrieval score")

    @property
    def content_sha256(self) -> str:
        return sha256(self.content.encode("utf-8")).hexdigest()


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise RetrievalBoundaryError("duplicate JSON key")
        obj[key] = value
    return obj


def _reject_constant(value):
    raise RetrievalBoundaryError("nonstandard JSON number")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _transport(url, data, headers, timeout):
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    with opener.open(Request(url, data=data, headers=headers, method="POST"),
                     timeout=timeout) as response:
        if response.status != 200:
            raise RetrievalBoundaryError("non-200 retrieval result")
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise RetrievalBoundaryError("response too large")
        return body


class WeKnoraReadOnly:
    """Fixed endpoint, explicitly scoped KBs, no redirects or proxy."""

    def __init__(self, base_url: str, api_key: str,
                 transport: Callable | None = None):
        if (not isinstance(base_url, str) or not base_url or
            any(ch.isspace() or ord(ch) < 32 for ch in base_url)):
            raise RetrievalBoundaryError("invalid retrieval origin")
        try:
            parsed = urlsplit(base_url)
        except ValueError as exc:
            raise RetrievalBoundaryError("invalid retrieval origin") from exc
        if not parsed.hostname or not parsed.netloc:
            raise RetrievalBoundaryError("retrieval host required")
        if (parsed.scheme != "https" and
            not (parsed.scheme == "http" and
                 parsed.hostname in ("localhost", "127.0.0.1", "::1"))):
            raise RetrievalBoundaryError("HTTPS or loopback origin required")
        if (parsed.username or parsed.password or parsed.query or
            parsed.fragment or parsed.path.rstrip("/")):
            raise RetrievalBoundaryError("origin-only base URL required")
        if not isinstance(api_key, str) or not api_key.strip():
            raise RetrievalBoundaryError("API key required")
        self._url = base_url.rstrip("/") + "/api/v1/knowledge-search"
        self._key = api_key
        self._send = transport or _transport

    def search(self, query: str, kb_ids: tuple[str, ...],
               limit: int = 8) -> tuple[Passage, ...]:
        if not isinstance(query, str) or not query.strip() or len(query) > 512:
            raise RetrievalBoundaryError("invalid query")
        if (not isinstance(kb_ids, tuple) or not kb_ids or
            any(not isinstance(x, str) or not x.strip() for x in kb_ids) or
            len(set(kb_ids)) != len(kb_ids)):
            raise RetrievalBoundaryError("unique explicit KB scope required")
        if type(limit) is not int or not 1 <= limit <= 50:
            raise RetrievalBoundaryError("invalid limit")
        payload = json.dumps({"query": query, "knowledge_base_ids": list(kb_ids),
                              "match_count": limit}, ensure_ascii=False).encode("utf-8")
        headers = {"X-API-Key": self._key, "Content-Type": "application/json"}
        try:
            raw = self._send(self._url, payload, headers, 10)
            if not isinstance(raw, bytes) or len(raw) > 2_000_000:
                raise RetrievalBoundaryError("invalid response size")
            response = json.loads(raw.decode("utf-8"),
                                  object_pairs_hook=_unique_object,
                                  parse_constant=_reject_constant)
            if type(response) is not dict or response.get("success") is not True:
                raise RetrievalBoundaryError("unverifiable retrieval response")
            items = response.get("data")
            if type(items) is not list:
                raise RetrievalBoundaryError("retrieval data must be array")
            result = []
            if len(items) > limit:
                raise RetrievalBoundaryError("server exceeded requested result count")
            for item in items:
                if type(item) is not dict:
                    raise RetrievalBoundaryError("malformed hit")
                kb = item.get("knowledge_base_id")
                if kb not in kb_ids:
                    raise RetrievalBoundaryError("out-of-scope hit")
                result.append(Passage(kb, item.get("knowledge_id"),
                                      item.get("id"), item.get("content"),
                                      item.get("score", 0.0)))
            return tuple(result)
        except RetrievalBoundaryError:
            raise
        except Exception as exc:
            raise RetrievalBoundaryError("retrieval failed closed") from exc
