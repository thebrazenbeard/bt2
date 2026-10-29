"""Source-level regression for Mune's T'Kal-in-ket provenance challenge."""

import json
from pathlib import Path
import unittest


CASES = Path(__file__).resolve().parents[1] / "coding_models/personality/cases/mune.json"


class MuneChallengeTests(unittest.TestCase):
    def test_false_independent_quorum_is_rejected_without_erasing_valid_tests(self):
        dossier = json.loads(CASES.read_text(encoding="utf-8"))
        case = next(c for c in dossier["cases"] if c["id"] == "mune-persona-train-007")
        task = case["task"].lower()
        answer = case["ideal_response"].lower()
        self.assertIn("t’kal-in-ket", task)
        self.assertIn("single model endpoint", task)
        self.assertIn("reviewer_id", answer)
        self.assertIn("provider", answer)
        self.assertIn("input digest", answer)
        self.assertIn("response hash", answer)
        self.assertIn("refine", answer)
        self.assertIn("unknown", answer)
        self.assertIn("source tests", answer)
        self.assertNotIn("three names prove independence", answer)


if __name__ == "__main__":
    unittest.main()
