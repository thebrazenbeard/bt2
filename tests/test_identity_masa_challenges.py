"""Masa's causal-debugging challenges, distinct from model qualification."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "coding_models/personality/cases/masa.json"


class MasaCausalChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads(CASES.read_text(encoding="utf-8"))
        cls.case = next(item for item in cls.dossier["cases"]
                        if item["id"] == "masa-persona-train-002")

    def test_frozen_source_and_split(self):
        self.assertEqual(self.dossier["identity_id"], "masa")
        self.assertEqual(sum(item["split"] == "train" for item in self.dossier["cases"]), 8)
        self.assertEqual(sum(item["split"] == "dev" for item in self.dossier["cases"]), 2)
        self.assertIn("08_incident_and_checkpoint_state.md", self.case["source_basis"])

    def test_marker_restoration_is_not_causal_proof(self):
        text = self.case["ideal_response"].lower()
        self.assertIn("could mask", text)
        self.assertIn("negative control", text)
        self.assertIn("necessity", text)
        self.assertIn("independent downstream", text)

    def test_challenge_requires_discriminating_experiment(self):
        task = self.case["task"].lower()
        self.assertIn("proof", task)
        self.assertIn("peer", task)
        response = self.case["ideal_response"].lower()
        self.assertIn("falsif", response)
        self.assertIn("mune", response)


if __name__ == "__main__":
    unittest.main()
