"""Direct integration tests: run with pinned LGCM source on PYTHONPATH."""

import json
from pathlib import Path
import unittest

from lgcm_prequential import regime_fixture, run_probe


class LGCMPrequentialTests(unittest.TestCase):
    def test_prequential_restart_matches_uninterrupted_model(self):
        report = run_probe()
        self.assertEqual(report["count"], 60)
        self.assertEqual(report["generation"], 60)
        self.assertTrue(report["restart_equivalent"])
        self.assertEqual(report["snapshot"]["generation"], 30)
        self.assertEqual(len(report["snapshot"]["manifest_sha256"]), 64)
        self.assertEqual([step["sequence"] for step in report["steps"]], list(range(60)))
        self.assertEqual(report["steps"][0]["squared_error"], 0.36)
        self.assertEqual(len(regime_fixture()), 60)
        self.assertEqual(len(report["final_manifest_sha256"]), 64)
        self.assertEqual(len(report["model_config_sha256"]), 64)
        self.assertNotEqual(report["lgcm_source_commit"], "UNKNOWN")
        self.assertGreater(report["persistence_baseline_mse"], 0)

    def test_committed_per_event_receipts_reproduce_under_pinned_source(self):
        reference = json.loads((Path(__file__).parent / "results" /
            "LGCM_PREQUENTIAL_REGRESSION_20261026.json").read_text(encoding="utf-8"))
        current = run_probe()
        self.assertEqual(current["lgcm_source_commit"], reference["lgcm_source_commit"])
        self.assertEqual(current["data_sha256"], reference["data_sha256"])
        self.assertEqual(current["model_config_sha256"], reference["model_config_sha256"])
        self.assertEqual(current["final_manifest_sha256"], reference["final_manifest_sha256"])
        for now, recorded in zip(current["steps"], reference["steps"], strict=True):
            self.assertEqual(now["sequence"], recorded["sequence"])
            self.assertEqual(now["active_expert"], recorded["active_expert"])
            self.assertAlmostEqual(now["prediction"], recorded["prediction"], places=10)

    def test_invalid_numeric_stream_rejected_before_learning(self):
        for values in ((0.2,), (float("nan"), 0.4), (True, 0.2), (1.1, -0.3)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                run_probe(values, restart_at=1)
        for bad_restart in (0, 60, -1, True):
            with self.subTest(restart=bad_restart), self.assertRaises(ValueError):
                run_probe(restart_at=bad_restart)


if __name__ == "__main__":
    unittest.main()
