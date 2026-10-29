"""Keep Patrick's explicit personality corrections ahead of later job titles."""

import json
from pathlib import Path
import unittest


CASE_ROOT = Path(__file__).resolve().parents[1] / "coding_models/personality/cases"
SOURCE_BRIDGE = "coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md"


class OriginalDesignationsTests(unittest.TestCase):
    def test_explicit_user_personalities_remain_first_class(self):
        # A newer implementation/reviewer assignment must not rename these
        # original personality targets in future training revisions.
        for identity, title in (
            ("four", "Creative dreamer"),
            ("seven", "Scientific genius"),
            ("thirteen", "Skeptical reviewer"),
        ):
            with self.subTest(identity=identity):
                dossier = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
                explicit = [trait for trait in dossier["traits"] if trait["evidence_kind"] == "USER"]
                self.assertEqual(len(explicit), 1)
                self.assertEqual(explicit[0]["label"], title)
                self.assertEqual(explicit[0]["source_basis"], SOURCE_BRIDGE)
                self.assertTrue(explicit[0]["observable_behavior"])
                self.assertTrue(explicit[0]["anti_pattern"])


if __name__ == "__main__":
    unittest.main()
