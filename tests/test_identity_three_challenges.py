"""Public source-quality checks for Three's implementation-first examples.

These checks inspect authored training material; they do not grade any model.
"""

import ast
import json
from pathlib import Path
import re
import unittest


DOSSIER = Path(__file__).resolve().parents[1] / "coding_models/personality/cases/three.json"


class ThreeAdversarialSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in json.loads(
            DOSSIER.read_text(encoding="utf-8"))["cases"]}

    def test_duplicate_save_example_closes_same_tick_reentry(self):
        example = self.cases["three-persona-train-006"]
        answer = example["ideal_response"]
        self.assertEqual(example["split"], "train")
        self.assertIn("useRef", answer)
        self.assertIn("inFlight.current", answer)
        self.assertIn("finally", answer)
        self.assertIn("same-tick", answer)
        self.assertIn("idempotency", answer)

    def test_malformed_parser_example_has_parseable_fix_and_negative_witness(self):
        example = self.cases["three-persona-train-008"]
        answer = example["ideal_response"]
        self.assertEqual(example["split"], "train")
        code = re.search(r"```python\n(.*?)\n```", answer, re.DOTALL)
        self.assertIsNotNone(code, "Three's repair should show actual Python")
        syntax = ast.parse(code.group(1))
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and
                            node.name == "parse_ints" for node in syntax.body))
        self.assertIn("ValueError", answer)
        self.assertIn("parse_ints('')", answer)
        self.assertIn("parse_ints('1,nope,3')", answer)


if __name__ == "__main__":
    unittest.main()
