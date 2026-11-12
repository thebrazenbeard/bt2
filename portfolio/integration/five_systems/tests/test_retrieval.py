"""WeKnora scoped contract tests: injected transport, no external calls."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from portfolio.integration.five_systems.local_store import LocalCorpus, retrieval_control
from portfolio.integration.five_systems.retrieval import WeKnoraReadOnly, RetrievalBoundaryError


class WeKnoraTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def send(self, url, data, headers, timeout):
        self.calls.append((url, json.loads(data), headers, timeout))
        return json.dumps({"success": True, "data": [
            {"knowledge_base_id": "kb-a", "knowledge_id": "doc-1",
             "id": "chunk-1", "content": "Pump bearing lubricant spec", "score": 0.81}
        ]}).encode()

    def test_exact_scoped_upstream_contract_and_hash(self):
        adapter = WeKnoraReadOnly("https://kb.example.test", "test-credential", self.send)
        result = adapter.search("pump bearing", ("kb-a",), limit=3)
        self.assertEqual(len(result), 1)
        self.assertEqual(self.calls[0][0], "https://kb.example.test/api/v1/knowledge-search")
        self.assertEqual(self.calls[0][1], {
            "query": "pump bearing", "knowledge_base_ids": ["kb-a"], "match_count": 3})
        self.assertEqual(self.calls[0][2]["X-API-Key"], "test-credential")
        self.assertEqual(len(result[0].content_sha256), 64)

    def test_scope_and_identity_fail_closed(self):
        adapter = WeKnoraReadOnly("http://127.0.0.1:7777", "test", self.send)
        for scope in ((), ("kb-a", "kb-a"), ("",), ["kb-a"]):
            with self.subTest(scope=scope), self.assertRaises(RetrievalBoundaryError):
                adapter.search("pump", scope)
        for origin in ("http://public.example", "file:///x", "https://u:p@x.test",
                       "https://x.test/evil", "https://x.test?x=1",
                       "https:", "https:///missing-host", "https://x.test\n@other.test"):
            with self.subTest(origin=origin), self.assertRaises(RetrievalBoundaryError):
                WeKnoraReadOnly(origin, "test")
        self.assertEqual(self.calls, [])

    def test_out_of_scope_and_ambiguous_results_rejected(self):
        replies = [
            b'{"success":true,"data":[{"knowledge_base_id":"kb-other","knowledge_id":"x","id":"y","content":"bad","score":1}]}',
            b'{"success":true,"data":[{"knowledge_id":"x","id":"y","content":"unknown","score":1}]}',
            b'{"success":true,"success":false,"data":[]}',
            b'{"success":true,"data":[{"knowledge_base_id":"kb-a","knowledge_id":"x","id":"y","content":"bad","score":NaN}]}',
            b'{"success":true,"data":{"results":[]}}',
        ]
        for reply in replies:
            with self.subTest(reply=reply), self.assertRaises(RetrievalBoundaryError):
                WeKnoraReadOnly("https://kb.test", "test", lambda *args: reply).search(
                    "pump", ("kb-a",))


class LocalStoreTests(unittest.TestCase):
    def test_retrieval_baseline_and_state_roundtrip(self):
        corpus = LocalCorpus()
        corpus.ingest("plant", "alpha", "pump bearing lubricant specification")
        corpus.ingest("plant", "beta", "motor winding insulation specification")
        corpus.ingest("other", "secret", "pump bearing confidential operations")
        cases = (("bearing lubricant", "alpha"), ("winding insulation", "beta"))
        metric = retrieval_control(corpus, cases, ("plant",))
        self.assertEqual(metric["recall_at_1"], 1.0)
        self.assertEqual(metric["learned_neural_state_measured"], False)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "saved.json"
            corpus.save(path)
            loaded = LocalCorpus.load(path)
            self.assertEqual(retrieval_control(loaded, cases, ("plant",)), metric)
            with self.assertRaises(FileExistsError):
                corpus.save(path)
            bad = path.read_bytes().replace(b"lubricant", b"alteredxx")
            path.write_bytes(bad)
            with self.assertRaises(RetrievalBoundaryError):
                LocalCorpus.load(path)

    def test_reject_unscoped_or_overwrite(self):
        corpus = LocalCorpus()
        corpus.ingest("plant", "alpha", "bearing grease")
        with self.assertRaises(RetrievalBoundaryError):
            corpus.ingest("plant", "alpha", "revised source")
        with self.assertRaises(RetrievalBoundaryError):
            corpus.search("bearing", ())
        self.assertEqual(corpus.search("bearing", ("other",)), ())


if __name__ == "__main__":
    unittest.main()
