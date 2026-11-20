"""Hostile synthetic coverage for live Semantic Atlas catalog surfaces."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from provider_access import evaluate_access
from test_access_surface import snapshot

class SemanticCaptureCoverage(unittest.TestCase):
    def sample(self, name, role=None):
        value = copy.deepcopy(snapshot())
        obj = copy.deepcopy(value["tables"][0])
        obj.update(schema="semantic_atlas", name=name, rls_enabled=True, force_rls=False)
        for r in ("anon", "authenticated"):
            obj[r] = {p: False for p in ("select", "insert", "update", "delete")}
        if role:
            obj[role]["select"] = True
            value["schema_rights"][1][role + "_usage"] = True
        value["tables"].append(obj)
        return value

    def test_semantic_capture_direct_grant_holds(self):
        result = evaluate_access(self.sample("semantic_capture_events", "anon"))
        self.assertEqual(result["verdict"], "HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("UNLISTED_MEMORY_TABLE_GRANT", result["reason_codes"])

    def test_semantic_capture_restricted_still_reviewed(self):
        result = evaluate_access(self.sample("semantic_capture_outcomes"))
        self.assertEqual(result["verdict"], "REVIEW_UNLISTED_SURFACES")

    def test_pending_semantic_view_grant_holds(self):
        result = evaluate_access(self.sample("pending_semantic_captures", "authenticated"))
        self.assertEqual(result["verdict"], "HOLD_PRIVILEGE_EXPOSURE")

    def test_live_probe_includes_semantic_capture_surfaces(self):
        sql = (Path(__file__).resolve().parents[1] / "provider_access_probe.sql").read_text()
        self.assertIn("OR n.nspname='semantic_atlas'", sql)
        self.assertIn("p.proname LIKE 'capture_semantic_%'", sql)
        self.assertIn("p.proname LIKE 'record_semantic_capture_%'", sql)

    def test_semantic_capture_function_execute_holds(self):
        value = snapshot()
        fn = copy.deepcopy(value["functions"][1])
        fn.update(name="capture_semantic_event_v1", anon_execute=True)
        value["schema_rights"][1]["anon_usage"] = True
        value["functions"].append(fn)
        result = evaluate_access(value)
        self.assertEqual(result["verdict"], "HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("UNLISTED_MEMORY_FUNCTION_EXECUTE", result["reason_codes"])
