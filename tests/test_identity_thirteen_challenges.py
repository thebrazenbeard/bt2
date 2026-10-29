"""Regression for Thirteen's trained skepticism about neural evidence."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "coding_models/personality/cases/thirteen.json"


class ThirteenChallengeTests(unittest.TestCase):
    def test_neural_personality_claim_requires_real_controls_and_retention(self):
        dossier = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        self.assertEqual(dossier["identity_id"], "thirteen")
        self.assertEqual(dossier["traits"][0]["label"], "Skeptical reviewer")
        train = [c for c in dossier["cases"] if c["split"] == "train"]
        dev = [c for c in dossier["cases"] if c["split"] == "dev"]
        self.assertEqual((len(train), len(dev)), (8, 2))
        case = next(c for c in train if c["id"] == "thirteen-persona-train-006")

        task = case["task"].lower()
        answer = case["ideal_response"].lower()
        for required in ("lora", "personality", "coding competence"):
            with self.subTest(task_term=required):
                self.assertIn(required, task)
        for required in ("weight", "prompt-only", "sham", "corrupt",
                         "sealed", "retention", "unknown"):
            with self.subTest(answer_term=required):
                self.assertIn(required, answer)
        self.assertIn("different evidence", answer)
        self.assertNotIn("sustain the claim", answer)


if __name__ == "__main__":
    unittest.main()
