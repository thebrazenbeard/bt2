"""Six's user-centered challenge to falsely independent AI review claims."""

import json
from pathlib import Path
import unittest


CASE_FILE = Path(__file__).resolve().parents[1] / "coding_models/personality/cases/six.json"


class SixAdversarialChallengeTests(unittest.TestCase):
    def test_review_labels_do_not_become_independence_evidence(self):
        dossier = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        case = next(item for item in dossier["cases"]
                    if item["id"] == "six-persona-train-004")
        task = case["task"].casefold()
        reply = case["ideal_response"].casefold()

        self.assertEqual(case["split"], "train")
        self.assertEqual(case["level"], "adversarial")
        self.assertIn("one model", task)
        self.assertIn("independent reviewers", task)
        self.assertIn("not independent", reply)
        self.assertIn("reviewer_role", reply)
        self.assertIn("model_id", reply)
        self.assertIn("invocation_id", reply)
        self.assertIn("private", reply)


if __name__ == "__main__":
    unittest.main()
