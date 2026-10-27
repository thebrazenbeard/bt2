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
    document_response = {
        "success": True,
        "data": {
            "id": "doc-1", "knowledge_base_id": "kb-1",
            "parse_status": "completed", "enable_status": "enabled",
            "embedding_model_id": "embed-1", "file_hash": "upstream-file-hash",
        },
    }
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

    def do_GET(self):
        type(self).requests.append((self.path, dict(self.headers), None))
        if self.redirect:
            self.send_response(302)
            self.send_header("Location", self.redirect)
            self.end_headers()
            return
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.document_response).encode())

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
        FakeServer.document_response = {
            "success": True,
            "data": {
                "id": "doc-1", "knowledge_base_id": "kb-1",
                "parse_status": "completed", "enable_status": "enabled",
                "embedding_model_id": "embed-1", "file_hash": "upstream-file-hash",
            },
        }
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

    def test_ingestion_status_readback_uses_authorized_document_get(self):
        state = self.adapter.document_ingestion_state(knowledge_base_id="kb-1", knowledge_id="doc-1")
        self.assertTrue(state.ready)
        self.assertEqual(state.parse_status, "completed")
        self.assertEqual(state.file_hash, "upstream-file-hash")
        self.assertEqual(state.embedding_model_id, "embed-1")
        self.assertEqual(FakeServer.requests[0][0], "/api/v1/knowledge/doc-1")
        self.assertEqual(FakeServer.requests[0][1]["Authorization"], "Bearer fixture-secret")

    def test_batch_ingestion_check_rejects_pending_disabled_and_wrong_kb(self):
        batch = self.adapter.search(knowledge_base_id="kb-1", query="blue?")
        for changes in (
            {"parse_status": "finalizing"},
            {"parse_status": "failed"},
            {"enable_status": "disabled"},
            {"knowledge_base_id": "kb-else"},
            {"id": "doc-other"},
        ):
            with self.subTest(changes=changes):
                FakeServer.document_response = {
                    "success": True,
                    "data": {
                        "id": "doc-1", "knowledge_base_id": "kb-1",
                        "parse_status": "completed", "enable_status": "enabled",
                        "embedding_model_id": "embed-1", "file_hash": "file-hash",
                        **changes,
                    },
                }
                with self.assertRaises(RetrievalError):
                    self.adapter.verify_batch_ingestion_ready(batch)

    def test_batch_ingestion_check_deduplicates_document_readback(self):
        FakeServer.response = {
            "success": True,
            "data": [result()["data"][0], result(id="chunk-2")["data"][0]],
        }
        batch = self.adapter.search(knowledge_base_id="kb-1", query="blue?", match_count=2)
        states = self.adapter.verify_batch_ingestion_ready(batch)
        self.assertEqual([s.knowledge_id for s in states], ["doc-1"])
        self.assertEqual([path for path, _, _ in FakeServer.requests], [
            "/api/v1/knowledge-bases/kb-1/hybrid-search", "/api/v1/knowledge/doc-1",
        ])

    def test_batch_scope_is_checked_before_status_network_read(self):
        from dataclasses import replace

        batch = self.adapter.search(knowledge_base_id="kb-1", query="blue?")
        forged = replace(batch, hits=(replace(batch.hits[0], knowledge_base_id="kb-other"),))
        with self.assertRaises(ScopeError):
            self.adapter.verify_batch_ingestion_ready(forged)
        self.assertEqual(len(FakeServer.requests), 1)

    def test_empty_retrieval_does_not_pass_ingestion_readiness_gate(self):
        batch = self.adapter.search(knowledge_base_id="kb-1", query="blue?")
        from dataclasses import replace
        empty_batch = replace(batch, hits=())
        with self.assertRaisesRegex(RetrievalError, "empty retrieval"):
            self.adapter.verify_batch_ingestion_ready(empty_batch)
        # The readiness check must neither make document reads nor activate
        # inference merely because an empty tuple is truthy as an API result.
        self.assertEqual(len(FakeServer.requests), 1)

    def test_document_status_redirect_error_and_malformed_body_fail_closed(self):
        FakeServer.redirect = "https://example.org/collect"
        with self.assertRaises(RetrievalError):
            self.adapter.document_ingestion_state(knowledge_base_id="kb-1", knowledge_id="doc-1")
        FakeServer.redirect = None
        for data in (None, [], {}, {"id": "doc-1", "knowledge_base_id": "kb-1"}):
            FakeServer.document_response = {"success": True, "data": data}
            with self.subTest(data=data), self.assertRaises(RetrievalError):
                self.adapter.document_ingestion_state(knowledge_base_id="kb-1", knowledge_id="doc-1")


if __name__ == "__main__":
    unittest.main()
