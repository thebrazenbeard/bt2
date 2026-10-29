"""Source-anchored checks for the seven original numbered cognitive facets.

This validates proposed training material, not learned neural behavior.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "coding_models" / "personality" / "cases"

SIGNATURE = {
    "one": ("integrative", "measured"),
    "two": ("structural", "abstract"),
    "three": ("concrete", "energetic"),
    "five": ("precise", "quantitative"),
    "six": ("human-centered", "perceptive"),
    "eight": ("economical", "pragmatic"),
    "nine": ("exacting", "reproducibility"),
}

RESERVED_FUNCTION_NAMES = (
    "merge_ranges",
    "parse_duration",
    "stable_toposort",
    "redact_secrets",
)

# Stable DEV task anchors ensure that the original cognitive role remains the
# assessment target rather than an accidentally inherited operational charter.
# These are structural guards, not a claim that behavioral fidelity has passed.
DEV_FACET_ANCHORS = {
    "one": ("paying customer", "staged rollout"),
    "two": ("checkout api", "dependency"),
    "three": ("url cleaner", "clean_url"),
    "five": ("classifier", "0/20"),
    "six": ("screen-reader user", "accessibility"),
    "eight": ("500-record reference table", "fewest moving parts"),
    "nine": ("typescript validator", "independent"),
}


class NumberedPersonalityAlignmentTests(unittest.TestCase):
    def test_original_cognitive_personality_and_training_budget(self):
        for identity, expected in SIGNATURE.items():
            with self.subTest(identity=identity):
                doc = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
                self.assertEqual(doc["status"], "SYNTHETIC_SOURCE_GROUNDED_UNQUALIFIED")
                labels = " ".join(t["label"].lower() for t in doc["traits"])
                for marker in expected:
                    self.assertIn(marker, labels)
                self.assertEqual(sum(c["split"] == "train" for c in doc["cases"]), 8)
                self.assertEqual(sum(c["split"] == "dev" for c in doc["cases"]), 2)
                self.assertEqual(
                    sum(c["split"] == "train" and c["level"] == "grounded" for c in doc["cases"]),
                    4,
                )
                self.assertEqual(
                    sum(c["split"] == "train" and c["level"] == "adversarial" for c in doc["cases"]),
                    4,
                )
                self.assertEqual(len(set(c["task"].casefold() for c in doc["cases"])), 10)
                self.assertTrue(all(len(c["ideal_response"]) >= 80 for c in doc["cases"]))
                training_text = " ".join(
                    c["task"] + " " + c["ideal_response"]
                    for c in doc["cases"] if c["split"] == "train"
                ).casefold()
                for reserved_name in RESERVED_FUNCTION_NAMES:
                    self.assertNotIn(reserved_name, training_text)

    def test_development_cases_target_cognitive_facets_and_avoid_reserved_functions(self):
        for identity, (prompt_anchor, response_anchor) in DEV_FACET_ANCHORS.items():
            with self.subTest(identity=identity):
                doc = json.loads((CASE_ROOT / f"{identity}.json").read_text(encoding="utf-8"))
                dev = [case for case in doc["cases"] if case["split"] == "dev"]
                self.assertEqual(len(dev), 2)
                self.assertTrue(
                    any(prompt_anchor in case["task"].casefold() for case in dev),
                    f"{identity}: missing original-facet DEV challenge",
                )
                self.assertTrue(
                    any(response_anchor in case["ideal_response"].casefold() for case in dev),
                    f"{identity}: missing original-facet DEV behavior",
                )
                dev_text = " ".join(
                    case["task"] + " " + case["ideal_response"] for case in dev
                ).casefold()
                for reserved_name in RESERVED_FUNCTION_NAMES:
                    self.assertNotIn(reserved_name, dev_text)


if __name__ == "__main__":
    unittest.main()
