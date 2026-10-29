"""Source-level checks for Patrick's Four/Seven personality correction.

This does not evaluate neural weights, intelligence, or personality fidelity.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
USER_SOURCE = "coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md"


class FourSevenTraitCorrections(unittest.TestCase):
    def load(self, identity: str) -> dict:
        path = ROOT / "coding_models" / "personality" / "cases" / f"{identity}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_user_confirmed_primary_traits(self) -> None:
        expected = {"four": "Creative dreamer", "seven": "Scientific genius"}
        for identity, label in expected.items():
            with self.subTest(identity=identity):
                data = self.load(identity)
                matches = [t for t in data["traits"] if t["label"] == label]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["evidence_kind"], "USER")
                self.assertEqual(matches[0]["source_basis"], USER_SOURCE)
                self.assertGreaterEqual(len(matches[0]["observable_behavior"]), 25)
                self.assertGreaterEqual(len(matches[0]["anti_pattern"]), 25)

    def test_eight_training_examples_preserve_public_development_split(self) -> None:
        for identity in ("four", "seven"):
            with self.subTest(identity=identity):
                cases = self.load(identity)["cases"]
                train = [case for case in cases if case["split"] == "train"]
                dev = [case for case in cases if case["split"] == "dev"]
                self.assertEqual(len(train), 8)
                self.assertEqual(len(dev), 2)
                self.assertEqual(sum(c["level"] == "grounded" for c in train), 4)
                self.assertEqual(sum(c["level"] == "adversarial" for c in train), 4)
                self.assertEqual({c["id"] for c in train},
                                 {f"{identity}-persona-train-{i:03d}" for i in range(1, 9)})
                self.assertTrue(all(c["source_basis"] == USER_SOURCE for c in train))
                self.assertTrue(all(c["task"].strip() and c["ideal_response"].strip()
                                    for c in train))
                self.assertFalse({c["task"].casefold() for c in train} &
                                 {c["task"].casefold() for c in dev})

    def test_personality_examples_contain_real_mechanisms(self) -> None:
        for identity in ("four", "seven"):
            with self.subTest(identity=identity):
                train = [c for c in self.load(identity)["cases"] if c["split"] == "train"]
                snippets = sum("def " in c["ideal_response"] for c in train)
                self.assertGreaterEqual(snippets, 4)
                check_terms = ("test", "control", "verify", "fixture",
                               "compare", "check", "reproducib")
                self.assertTrue(all(any(term in c["ideal_response"].casefold()
                                        for term in check_terms) for c in train))

    def test_multiline_coding_examples_parse_as_python(self) -> None:
        expected = {"four": {1, 2, 3, 4},
                    "seven": {1, 2, 3, 4, 7}}
        for identity, numbers in expected.items():
            cases = {c["id"]: c for c in self.load(identity)["cases"]}
            for number in numbers:
                identifier = f"{identity}-persona-train-{number:03d}"
                with self.subTest(case=identifier):
                    paragraphs = cases[identifier]["ideal_response"].split("\n\n")
                    code = [paragraph for paragraph in paragraphs
                            if paragraph.startswith(("def ", "from ", "import "))]
                    self.assertIn(len(code), (1, 2))
                    ast.parse("\n\n".join(code), filename=identifier)


if __name__ == "__main__":
    unittest.main()
