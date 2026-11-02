"""Standard-library checks of the synthetic historical source contract."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "historical_adjudication_v1.schema.json"
SAMPLE_PATH = ROOT / "examples" / "historical_adjudication.synthetic.json"


class HistoricalAdjudicationContractTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))

    def test_sample_uses_only_known_required_fields(self):
        required = set(self.schema["required"])
        self.assertEqual(set(self.sample), required)
        self.assertEqual(set(self.schema["properties"]), required)
        self.assertIs(self.schema["additionalProperties"], False)

    def test_permissions_and_currentness_remain_hard_hold(self):
        constraints = self.schema["properties"]
        for field, expected in (
            ("source_state", "HISTORICAL_NOT_INSTALLED"),
            ("private_locator", "REDACTED"),
            ("rights", "UNVERIFIED"),
            ("public_admission", "HOLD"),
        ):
            self.assertEqual(constraints[field]["const"], expected)
            self.assertEqual(self.sample[field], expected)
        self.assertEqual(self.sample["source_test"], "NOT_RUN")
        self.assertEqual(self.sample["independent_review"], "NOT_PERFORMED")

    def test_sample_contains_only_synthetic_opaque_identifiers(self):
        self.assertTrue(self.sample["artifact_id"].startswith("SYNTHETIC_"))
        self.assertIsNone(self.sample["duplicate_group"])
        self.assertFalse(any("path" in key or "hash" in key for key in self.sample))
        serialized = json.dumps(self.sample)
        self.assertNotIn("C:\\\\", serialized)
        self.assertNotIn("Users", serialized)
        self.assertNotIn("OneDrive", serialized)

    def test_schema_has_no_positive_admission_or_data_rights_values(self):
        constraints = self.schema["properties"]
        self.assertNotIn("GRANTED", json.dumps(constraints))
        self.assertNotIn("APPROVED", json.dumps(constraints))
        self.assertEqual(self.sample["current_git_comparison"], "NOT_PERFORMED")


if __name__ == "__main__":
    unittest.main()
