"""Immutable source chunks and reproducible lexical retrieval controls."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re

from .retrieval import Passage, RetrievalBoundaryError


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE))


class LocalCorpus:
    """Offline ingest/restart control, not a learned neural representation."""

    def __init__(self):
        self._documents: dict[tuple[str, str], str] = {}

    def ingest(self, kb: str, document_id: str, content: str) -> str:
        for value in (kb, document_id, content):
            if not isinstance(value, str) or not value.strip():
                raise RetrievalBoundaryError("invalid local document")
        key = (kb, document_id)
        if key in self._documents:
            raise RetrievalBoundaryError("document already exists; no silent overwrite")
        self._documents[key] = content
        return sha256(content.encode("utf-8")).hexdigest()

    def search(self, query: str, kb_ids: tuple[str, ...],
               limit: int = 8) -> tuple[Passage, ...]:
        if not isinstance(query, str) or not query.strip():
            raise RetrievalBoundaryError("invalid query")
        if (not isinstance(kb_ids, tuple) or not kb_ids or
            any(not isinstance(x, str) or not x.strip() for x in kb_ids) or
            len(set(kb_ids)) != len(kb_ids)):
            raise RetrievalBoundaryError("explicit scoped KBs required")
        if type(limit) is not int or not 1 <= limit <= 50:
            raise RetrievalBoundaryError("invalid result limit")
        terms = _tokens(query)
        hits = []
        for (kb, doc), content in self._documents.items():
            if kb not in kb_ids:
                continue
            for index, chunk in enumerate(content.split("\n\n")):
                overlap = len(terms & _tokens(chunk))
                if overlap:
                    hits.append(Passage(kb, doc, f"{doc}:{index}",
                                        chunk, float(overlap)))
        return tuple(sorted(hits, key=lambda hit: (-hit.score, hit.knowledge_base_id,
                                                  hit.knowledge_id, hit.chunk_id))[:limit])

    def _serialized(self) -> dict:
        return {"schema": "BT2_SCOPED_KNOWLEDGE_V1",
                "documents": [{"kb": kb, "id": doc, "content": content,
                               "sha256": sha256(content.encode("utf-8")).hexdigest()}
                              for (kb, doc), content in sorted(self._documents.items())]}

    def save(self, path: Path) -> str:
        """Exclusive, fsynced snapshot; never replace a previous source record."""
        document = self._serialized()
        canonical = json.dumps(document, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
        digest = sha256(canonical).hexdigest()
        snapshot = json.dumps({"payload": document, "payload_sha256": digest},
                              ensure_ascii=False, sort_keys=True).encode("utf-8")
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(os.fspath(path), flags, 0o600)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(snapshot)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            raise
        return digest

    @classmethod
    def load(cls, path: Path) -> "LocalCorpus":
        raw = Path(path).read_bytes()
        if len(raw) > 4_000_000:
            raise RetrievalBoundaryError("snapshot too large")
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise RetrievalBoundaryError("duplicate snapshot key")
                value[key] = item
            return value
        try:
            record = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
            payload = record["payload"]
            canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8")
            if record["payload_sha256"] != sha256(canonical).hexdigest():
                raise RetrievalBoundaryError("snapshot digest mismatch")
            if payload["schema"] != "BT2_SCOPED_KNOWLEDGE_V1":
                raise RetrievalBoundaryError("unknown snapshot schema")
            result = cls()
            for row in payload["documents"]:
                if row["sha256"] != sha256(row["content"].encode("utf-8")).hexdigest():
                    raise RetrievalBoundaryError("document digest mismatch")
                result.ingest(row["kb"], row["id"], row["content"])
            return result
        except RetrievalBoundaryError:
            raise
        except Exception as exc:
            raise RetrievalBoundaryError("malformed snapshot") from exc


def retrieval_control(corpus: LocalCorpus, cases: tuple[tuple[str, str], ...],
                      kb_ids: tuple[str, ...]) -> dict[str, float | int]:
    """Predeclared expected document IDs, no training or per-query adaptation."""
    if not cases:
        raise RetrievalBoundaryError("nonempty evaluation cases required")
    correct = 0
    for query, expected in cases:
        hits = corpus.search(query, kb_ids, 1)
        correct += int(bool(hits) and hits[0].knowledge_id == expected)
    return {"cases": len(cases), "recall_at_1": correct / len(cases),
            "learned_neural_state_measured": False}
