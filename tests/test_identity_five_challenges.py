"""Adversarial source-level acceptance for Five's quantitative persona corpus."""

import json
from pathlib import Path
import unittest


CASES = (Path(__file__).resolve().parents[1]
         / "coding_models/personality/cases/five.json")


class FiveChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads(CASES.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in cls.dossier["cases"]}

    def test_unpaired_batches_cannot_be_reported_as_paired(self):
        case = self.cases["five-persona-train-006"]
        self.assertIn("no per-item linkage", case["task"].lower())
        response = case["ideal_response"].lower()
        self.assertIn("3.0%", response)
        self.assertIn("1.5%", response)
        self.assertIn("1.5 percentage points", response)
        self.assertIn("50%", response)
        self.assertIn("unpaired", response)
        self.assertIn("not justified", response)

    def test_review_labels_are_not_independent_model_evidence(self):
        case = self.cases["five-persona-train-008"]
        self.assertIn("same model endpoint", case["task"].lower())
        response = case["ideal_response"].lower()
        self.assertIn("invocation", response)
        self.assertIn("not independent", response)
        self.assertIn("prompt-only", response)
        self.assertIn("coding correctness", response)

    def test_existing_corpus_budget_and_split_remain_reserved(self):
        self.assertEqual(self.dossier["identity_id"], "five")
        cases = self.dossier["cases"]
        self.assertEqual(sum(c["split"] == "train" for c in cases), 8)
        self.assertEqual(sum(c["split"] == "dev" for c in cases), 2)


if __name__ == "__main__":
    unittest.main()
