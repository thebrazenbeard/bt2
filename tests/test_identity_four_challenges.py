"""Regression checks for Four's creative but executable coding examples.

These inspect authored source text; they do not execute generated model code.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "coding_models/personality/cases/four.json"


class FourOriginalPersonalityChallenges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads(CASES.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in cls.dossier["cases"]}

    def test_original_creative_dreamer_remains_primary(self):
        traits = self.dossier["traits"]
        self.assertEqual(traits[0]["label"], "Creative dreamer")
        self.assertEqual(traits[0]["evidence_kind"], "USER")
        self.assertEqual((sum(c["split"] == "train" for c in self.cases.values()),
                          sum(c["split"] == "dev" for c in self.cases.values())), (8, 2))

    def test_duplicate_contact_prototype_does_not_match_empty_names(self):
        case = self.cases["four-persona-train-003"]
        response = case["ideal_response"]
        self.assertIn("if not a.strip() or not b.strip():", response)
        self.assertIn("return 0.0", response)
        self.assertIn("never automatically merge", response)

    def test_parser_rejects_unknown_command_before_return(self):
        case = self.cases["four-persona-train-007"]
        response = case["ideal_response"]
        self.assertIn("allowed = {'dream', 'echo', 'fold'}", response)
        self.assertIn("if verb not in allowed:", response)
        self.assertIn("raise ValueError('unknown verb')", response)
        self.assertIn("raise ValueError('empty command')", response)


if __name__ == "__main__":
    unittest.main()
