"""Identity Nine's reproducibility challenge to false T'Kal independence."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestIdentityNineChallenges(unittest.TestCase):
    def test_tkal_quorum_requires_actual_independence_and_answered_attacks(self):
        dossier = json.loads((ROOT / "coding_models/personality/cases/nine.json").read_text())
        case = next(c for c in dossier["cases"]
                    if c["id"] == "nine-persona-train-adversarial-04")
        task = case["task"].lower()
        response = case["ideal_response"].lower()
        for required in ("t'kal", "three reviewer", "partly_answered", "sustain"):
            with self.subTest(task_term=required):
                self.assertIn(required, task)
        for required in ("model endpoint", "reviewer id", "provider", "host", "input digest",
                         "directed", "partly_answered", "refine", "merge authority"):
            with self.subTest(response_term=required):
                self.assertIn(required, response)
        self.assertNotIn("three independent model runs proved", response)
        self.assertEqual(case["split"], "train")
        self.assertEqual(case["level"], "adversarial")


if __name__ == "__main__":
    unittest.main()
