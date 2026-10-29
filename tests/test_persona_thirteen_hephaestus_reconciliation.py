"""User-archetype reconciliation checks; source/data only, not model qualification."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "coding_models" / "personality" / "cases"


def dossier(identity: str) -> dict:
    return json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))


class PersonalitySourceReconciliationTests(unittest.TestCase):
    def test_thirteen_skepticism_is_broader_than_authority_review(self):
        doc = dossier("thirteen")
        self.assertEqual(doc["status"], "SYNTHETIC_SOURCE_GROUNDED_UNQUALIFIED")
        explicit = [trait for trait in doc["traits"] if trait["evidence_kind"] == "USER"]
        self.assertEqual(len(explicit), 1)
        self.assertEqual(explicit[0]["label"], "Skeptical reviewer")
        self.assertEqual(
            explicit[0]["source_basis"],
            "coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md",
        )
        train = [case for case in doc["cases"] if case["split"] == "train"]
        dev = [case for case in doc["cases"] if case["split"] == "dev"]
        self.assertEqual((len(train), len(dev)), (8, 2))
        # This is a content-coverage gate, not an empirical personality score.
        prompts = " ".join(case["task"].casefold() for case in train)
        for topic in ("cache", "scores[-2:]", "coverage", "policy", "json decoder"):
            self.assertIn(topic, prompts)
        self.assertTrue(any("bounded pass" in case["ideal_response"].casefold()
                            for case in doc["cases"]))

    def test_hephaestus_matches_native_project_engineering_source(self):
        doc = dossier("hephaestus")
        train = [case for case in doc["cases"] if case["split"] == "train"]
        dev = [case for case in doc["cases"] if case["split"] == "dev"]
        self.assertEqual((len(train), len(dev)), (8, 2))
        self.assertEqual(len({c["skill_domain"] for c in train}), 8)
        self.assertGreaterEqual(sum("project" in c["task"].casefold() for c in train), 7)
        self.assertTrue(any("python" in c["task"].casefold() for c in train))
        self.assertTrue(any("not a stable" in c["ideal_response"].casefold()
                            for c in train))
        sources = [t.get("upstream_source", "") for t in doc["traits"]]
        self.assertTrue(all(s.startswith("thebrazenbeard/hephaestus@357803035")
                            for s in sources))
        self.assertTrue(all(t["evidence_kind"] == "INFERENCE"
                            for t in doc["traits"]))

    def test_no_case_overlap_or_shadow_holdout(self):
        cases = dossier("thirteen")["cases"] + dossier("hephaestus")["cases"]
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        self.assertEqual(len({" ".join(c["task"].split()).casefold() for c in cases}), len(cases))
        for case in cases:
            self.assertNotIn("reserved_cases.jsonl", case["task"])
            self.assertGreater(len(case["ideal_response"]), 80)


if __name__ == "__main__":
    unittest.main()
