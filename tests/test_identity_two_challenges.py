"""Regression for Two's structural reasoning across changed effect boundaries.

Static curriculum quality checks; not a neural or independent-peer evaluation.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "coding_models/personality/cases/two.json"


class TwoConditionalInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))

    def test_duplicate_work_case_changes_with_external_effects(self):
        case = next(c for c in self.dossier["cases"]
                    if c["id"] == "two-persona-train-008")
        self.assertEqual((case["split"], case["level"]), ("train", "adversarial"))
        task = case["task"].lower()
        answer = case["ideal_response"].lower()
        # Prevent the easy anti-cluster reflex: the same architecture must be
        # judged under both harmless duplicate computation and future effects.
        for concept in ("duplicate", "future", "billing", "notification"):
            self.assertIn(concept, task)
        for concept in ("idempotency", "effect boundary", "current", "future", "retry"):
            self.assertIn(concept, answer)
        self.assertIn("test", answer)
        self.assertNotIn("always avoid distributed", answer)


if __name__ == "__main__":
    unittest.main()
