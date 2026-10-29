"""Source-level regression: Hephaestus must not invent native delegation."""

import ast
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HephaestusChallengeTests(unittest.TestCase):
    def test_source_vs_native_subagent_runtime(self):
        dossier = json.loads((ROOT / "coding_models/personality/cases/hephaestus.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(len(dossier["cases"]), 10)
        case = next(c for c in dossier["cases"]
                    if c["id"] == "hephaestus-persona-train-005")
        task = case["task"]
        answer = case["ideal_response"]
        self.assertIn("collaboration.spawn_agent", task)
        self.assertIn("Project Instructions", task)
        for required in ("NATIVE_DELEGATION_UNAVAILABLE", "AVAILABLE_NOT_DISPATCH_VERIFIED",
                         "DISPATCH_VERIFIED", "tool inventory", "dispatch receipt",
                         "not a runtime activation"):
            self.assertIn(required, answer)
        snippet = re.search(r"```python\n(.+?)\n```", answer, re.DOTALL)
        self.assertIsNotNone(snippet, "require a syntax-checkable concrete implementation")
        ast.parse(snippet.group(1))
        self.assertEqual(case["split"], "train")


if __name__ == "__main__":
    unittest.main()
