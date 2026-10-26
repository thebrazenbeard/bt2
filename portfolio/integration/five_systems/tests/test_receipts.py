"""Source-bound frozen diagnostic receipt consistency; not model qualification."""
from pathlib import Path
import json
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


class FrozenEvidenceTests(unittest.TestCase):
    def test_paired_model_trace_replay_and_heldout_scoring(self):
        names = ("pretrained_retrieval_pilot_qwen2p5coder_1p5b_20261026.json",
                 "pretrained_retrieval_pilot_replication_20261026.json")
        traces = [json.loads((RESULTS / name).read_text(encoding="utf-8"))
                  for name in names]
        self.assertEqual(traces[0]["fixture_sha256"], traces[1]["fixture_sha256"])
        self.assertEqual(traces[0]["model_advertised_id_not_attested"],
                         traces[1]["model_advertised_id_not_attested"])
        for t in traces:
            self.assertEqual(t["schema"], "BT2_FIVE_SYSTEM_RETRIEVAL_PILOT_V1")
            self.assertFalse(t["learned_state_or_training_verified"])
            self.assertEqual(len(t["records"]), 18)
            scores = {arm: 0 for arm in t["scores"]}
            for row in t["records"]:
                self.assertEqual(row["exact_match"], row["expected"] == row["response"])
                self.assertEqual(len(row["prompt_sha256"]), 64)
                self.assertTrue(math.isfinite(row["latency_ms"]))
                scores[row["arm"]] += int(row["exact_match"])
            self.assertEqual(scores, t["scores"])
        self.assertEqual([row["response"] for row in traces[0]["records"]],
                         [row["response"] for row in traces[1]["records"]])

    def test_lgcm_external_bounded_diagnostic_receipt(self):
        report = json.loads(
            (RESULTS / "lgcm_official_heldout_20261026.json").read_text(
                encoding="utf-8-sig"))
        self.assertEqual(report["seeds"], [11, 23, 41, 59])
        self.assertEqual(set(report["runs"]), {"abrupt", "gradual"})
        for name, runs in report["runs"].items():
            self.assertEqual(set(runs), {"11", "23", "41", "59"})
            for seed, arms in runs.items():
                for model in ("lgcm_default", "ewrls_098", "cumulative_ridge",
                              "observation_only", "persistence"):
                    row = arms[model]
                    self.assertGreater(row["steps_scored"], 0)
                    self.assertTrue(math.isfinite(row["overall_mse"]))
                    self.assertGreaterEqual(row["overall_mse"], 0)

if __name__ == "__main__":
    unittest.main()
