"""Public DEV personality cases; no holdout or model-effectiveness claims."""

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
USER_SOURCE = "coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md"
HOLDOUT_NAMES = ("merge_ranges", "parse_duration", "stable_toposort", "redact_secrets")


class PublicDevelopmentTraitTests(unittest.TestCase):
    def test_dev_cases_observe_corrected_primary_traits(self):
        for identity, expected in (("four", ("constellation", "mind")),
                                   ("seven", ("resistors", "conservation"))):
            with self.subTest(identity=identity):
                filename = ROOT / "coding_models/personality/cases" / f"{identity}.json"
                cases = json.loads(filename.read_text(encoding="utf-8"))["cases"]
                dev = [case for case in cases if case["split"] == "dev"]
                train = [case for case in cases if case["split"] == "train"]
                self.assertEqual(len(dev), 2)
                self.assertEqual(len(train), 8)
                self.assertEqual([case["level"] for case in dev], ["grounded", "adversarial"])
                self.assertTrue(all(case["source_basis"] == USER_SOURCE for case in dev))
                self.assertTrue(all(term in (dev[i]["task"] + dev[i]["ideal_response"]).casefold()
                                    for i, term in enumerate(expected)))
                self.assertTrue(all("test" in case["ideal_response"].casefold()
                                    or "fixture" in case["ideal_response"].casefold()
                                    for case in dev))
                self.assertTrue(all("def " in case["ideal_response"] for case in dev))
                for case in cases:
                    self.assertFalse(any(name in case["task"] + case["ideal_response"]
                                         for name in HOLDOUT_NAMES), case["id"])

    def test_multiline_public_dev_snippets_are_python(self):
        for identity in ("four", "seven"):
            filename = ROOT / "coding_models/personality/cases" / f"{identity}.json"
            cases = json.loads(filename.read_text(encoding="utf-8"))["cases"]
            for case in (item for item in cases if item["split"] == "dev"):
                snippets = [part for part in case["ideal_response"].split("\n\n")
                            if part.startswith(("def ", "from ", "import "))]
                if snippets:
                    with self.subTest(case=case["id"]):
                        ast.parse("\n\n".join(snippets))


if __name__ == "__main__":
    unittest.main()
