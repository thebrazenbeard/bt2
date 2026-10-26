import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from weknora_adapter import RetrievalError, ScopeError, WeKnoraRetrievalAdapter


def result(**overrides):
    hit = {
        "id": "chunk-1", "knowledge_id": "doc-1", "knowledge_base_id": "kb-1",
        "content": "The test document says blue.", "knowledge_title": "Test doc",
        "knowledge_source": "file", "knowledge_channel": "api", "knowledge_filename": "a.md",
        "score": 0.0273, "match_type": 0, "start_at": 0, "end_at": 32,
        "metadata": {"sha256": "fixture-hash"},
    }
    hit.update(overrides)
    return {"success": True, "data": [hit]}


class FakeServer(BaseHTTPRequestHandler):
    requests = []
    response = result()
    status = 200
    redirect = None

    def do_POST(self):
        payload = self.rfile.read(int(self.headers["Content-Length"]))
        type(self).requests.append((self.path, dict(self.headers), json.loads(payload)))
        if self.redirect:
            self.send_response(302)
            self.send_header("Location", self.redirect)
            self.end_headers()
            return
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.response).encode())

    def log_message(self, *_):
        pass


class AdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        FakeServer.requests = []
        FakeServer.response = result()
        FakeServer.status = 200
        FakeServer.redirect = None
        self.adapter = WeKnoraRetrievalAdapter(
            base_url=f"http://127.0.0.1:{self.server.server_port}", api_key="fixture-secret",
            allowed_knowledge_base_ids=("kb-1",),
        )

    def test_hybrid_request_is_scoped_with_full_provenance_and_raw_rrf(self):
        batch = self.adapter.search(knowledge_base_id="kb-1", query="  blue?  ", match_count=3)
        self.assertEqual(batch.knowledge_base_id, "kb-1")
        self.assertEqual(batch.query, "blue?")
        self.assertEqual(len(batch.hits), 1)
        h = batch.hits[0]
        self.assertEqual((h.knowledge_id, h.chunk_id, h.source), ("doc-1", "chunk-1", "file"))
        self.assertEqual(h.score, 0.0273)
        self.assertIn("not_cosine", h.score_semantics)
        self.assertEqual(h.metadata["sha256"], "fixture-hash")
        path, headers, body = FakeServer.requests[0]
        self.assertEqual(path, "/api/v1/knowledge-bases/kb-1/hybrid-search")
        self.assertEqual(headers["Authorization"], "Bearer fixture-secret")
        self.assertEqual(body["knowledge_base_ids"], ["kb-1"])
        self.assertNotIn("rerank", body)
        self.assertEqual(body["match_count"], 3)

    def test_unauthorized_kb_never_reaches_transport(self):
        with self.assertRaises(ScopeError):
            self.adapter.search(knowledge_base_id="kb-other", query="blue?")
        self.assertEqual(FakeServer.requests, [])

    def test_cross_kb_or_missing_kb_provenance_fails_closed(self):
        for kb in ("kb-other", None):
            FakeServer.response = result(knowledge_base_id=kb)
            with self.assertRaises(ScopeError):
                self.adapter.search(knowledge_base_id="kb-1", query="blue?")

    def test_corrupt_hits_do_not_return_partial_success(self):
        for bad_field in ("score", "id", "knowledge_id", "match_type"):
            FakeServer.response = result(**{bad_field: None})
            with self.assertRaises(RetrievalError):
                self.adapter.search(knowledge_base_id="kb-1", query="blue?")

    def test_malformed_even_falsey_metadata_rejected(self):
        for metadata in ([], "", 0, False):
            with self.subTest(metadata=metadata):
                FakeServer.response = result(metadata=metadata)
                with self.assertRaises(RetrievalError):
                    self.adapter.search(knowledge_base_id="kb-1", query="blue?")

    def test_server_must_obey_requested_context_budget(self):
        FakeServer.response = {
            "success": True,
            "data": [result()["data"][0], result(id="chunk-2")["data"][0]],
        }
        with self.assertRaises(RetrievalError):
            self.adapter.search(knowledge_base_id="kb-1", query="blue?", match_count=1)

    def test_server_errors_do_not_leak_token(self):
        FakeServer.status = 503
        with self.assertRaises(RetrievalError) as caught:
            self.adapter.search(knowledge_base_id="kb-1", query="blue?")
        self.assertNotIn("fixture-secret", str(caught.exception))

    def test_unsuccessful_response_is_rejected(self):
        FakeServer.response = {"success": False, "data": [result()["data"][0]]}
        with self.assertRaises(RetrievalError):
            self.adapter.search(knowledge_base_id="kb-1", query="blue?")

    def test_unbounded_numeric_scores_are_rejected(self):
        for score in (float("nan"), float("inf"), 10 ** 400):
            FakeServer.response = result(score=score)
            with self.assertRaises(RetrievalError):
                self.adapter.search(knowledge_base_id="kb-1", query="blue?")

    def test_redirect_refused_instead_of_forwarding_bearer_token(self):
        FakeServer.redirect = "https://example.org/collect"
        with self.assertRaises(RetrievalError):
            self.adapter.search(knowledge_base_id="kb-1", query="blue?")
        self.assertEqual(len(FakeServer.requests), 1)

    def test_invalid_query_count_and_origin(self):
        for value in ("", "   ", "x" * 8193):
            with self.assertRaises(ValueError):
                self.adapter.search(knowledge_base_id="kb-1", query=value)
        with self.assertRaises(ValueError):
            self.adapter.search(knowledge_base_id="kb-1", query="ok", match_count=31)
        with self.assertRaises(ValueError):
            WeKnoraRetrievalAdapter(base_url="http://user:secret@localhost:8080", api_key="x",
                                     allowed_knowledge_base_ids=("kb-1",))
        with self.assertRaises(ValueError):
            WeKnoraRetrievalAdapter(base_url="http://192.0.2.55:8080", api_key="x",
                                     allowed_knowledge_base_ids=("kb-1",))


if __name__ == "__main__":
    unittest.main()
