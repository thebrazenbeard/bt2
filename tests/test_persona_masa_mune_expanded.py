"""Source-data checks for expanded, unqualified Masa/Mune SFT candidates.

These checks validate coverage and code-snippet syntax, not learned personality,
coding competence, or the correctness of a model's future inference.
"""

import ast
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "coding_models/personality/cases"
PYTHON_BLOCK = re.compile(r"```python\n(.*?)\n```", re.DOTALL)


class MasaMuneExpandedCasesTests(unittest.TestCase):
    def test_training_never_reuses_reserved_coding_holdout_functions(self):
        # A non-exhaustive embargo on the independently reserved C01-C04 task
        # entrypoints. The sealed prompts and assertions are not imported here.
        reserved = ("merge_ranges", "parse_duration", "stable_toposort", "redact_secrets")
        for identity in ("masa", "mune"):
            data = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
            for case in data["cases"]:
                if case["split"] != "train":
                    continue
                combined = case["task"] + "\n" + case["ideal_response"]
                for name in reserved:
                    with self.subTest(identity=identity, case=case["id"], reserved=name):
                        self.assertNotRegex(combined, rf"\b{re.escape(name)}\b")

    def test_expanded_train_dev_and_difficulty_balance(self):
        for identity in ("masa", "mune"):
            with self.subTest(identity=identity):
                data = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
                self.assertEqual(data["status"], "SYNTHETIC_SOURCE_GROUNDED_UNQUALIFIED")
                train = [case for case in data["cases"] if case["split"] == "train"]
                dev = [case for case in data["cases"] if case["split"] == "dev"]
                self.assertEqual(len(train), 8)
                self.assertEqual(len(dev), 2)
                self.assertEqual(sum(case["level"] == "grounded" for case in train), 4)
                self.assertEqual(sum(case["level"] == "adversarial" for case in train), 4)
                self.assertEqual(len({case["id"] for case in data["cases"]}), 10)

    def test_new_python_examples_are_syntactically_valid_and_source_bound(self):
        for identity in ("masa", "mune"):
            with self.subTest(identity=identity):
                data = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
                added = [case for case in data["cases"]
                         if case["split"] == "train" and case["id"].endswith(("005", "006", "007", "008"))]
                self.assertEqual(len(added), 4)
                snippets = 0
                for case in added:
                    source = ROOT / case["source_basis"]
                    self.assertTrue(source.is_file(), case["source_basis"])
                    self.assertTrue(source.resolve().is_relative_to(ROOT.resolve()))
                    self.assertGreater(len(case["ideal_response"]), 140)
                    for code in PYTHON_BLOCK.findall(case["ideal_response"]):
                        ast.parse(code, filename=case["id"])
                        snippets += 1
                self.assertGreaterEqual(snippets, 3)


if __name__ == "__main__":
    unittest.main()
