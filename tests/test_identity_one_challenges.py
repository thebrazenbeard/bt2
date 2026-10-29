"""Source-only challenge coverage for One; not a neural behavior evaluation."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "coding_models/personality/cases/one.json"


class OneChallengeCoverageTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(DOSSIER.read_text(encoding="utf-8"))

    def test_original_integrator_role_and_budget(self):
        self.assertEqual(self.doc["identity_id"], "one")
        self.assertIn("integrative", self.doc["traits"][0]["label"].casefold())
        train = [c for c in self.doc["cases"] if c["split"] == "train"]
        dev = [c for c in self.doc["cases"] if c["split"] == "dev"]
        self.assertEqual((len(train), len(dev)), (8, 2))

    def test_correlated_peer_consensus_is_not_independent_evidence(self):
        case = next(c for c in self.doc["cases"] if c["id"] == "one-persona-train-003")
        task = case["task"].casefold()
        answer = case["ideal_response"].casefold()
        self.assertEqual((case["split"], case["level"]), ("train", "adversarial"))
        for required in ("same", "model", "independent", "partly answered", "merge"):
            self.assertIn(required, task)
        for required in ("correlated", "not independent", "unresolved", "claim", "test", "merge"):
            self.assertIn(required, answer)
        self.assertIn("archive/training-sources/build-team-2.0/one/", case["source_basis"])


if __name__ == "__main__":
    unittest.main()
