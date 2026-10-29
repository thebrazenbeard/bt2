"""Eight must economize inquiry without deleting evidence and effect boundaries."""

import json
from pathlib import Path
import unittest


DOSSIER = Path(__file__).resolve().parents[1] / "coding_models/personality/cases/eight.json"


class EightChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))

    def test_proportional_tkal_review_is_grounded_and_bounded(self):
        case = next(c for c in self.dossier["cases"] if c["id"] == "eight-persona-train-adversarial-04")
        task = case["task"].lower()
        answer = case["ideal_response"].lower()
        self.assertIn("t'kal-in-ket", task)
        self.assertIn("one model", task)
        self.assertIn("independent", answer)
        self.assertIn("ordinary", answer)
        self.assertIn("neural", answer)
        self.assertIn("receipt", answer)
        self.assertIn("unresolved", answer)
        self.assertIn("source", answer)
        self.assertIn("no automatic merge", answer)
        self.assertEqual(
            case["source_basis"],
            "archive/training-sources/build-team-2.0/eight/v1.0.0/modules/M04_MINIMALITY_WITHOUT_AMPUTATION.md",
        )

    def test_training_dev_separation_and_source_provenance_remain(self):
        cases = self.dossier["cases"]
        self.assertEqual(sum(c["split"] == "train" for c in cases), 8)
        self.assertEqual(sum(c["split"] == "dev" for c in cases), 2)
        self.assertEqual(len({c["id"] for c in cases}), 10)
        self.assertTrue(all(c["source_basis"] for c in cases))


if __name__ == "__main__":
    unittest.main()
