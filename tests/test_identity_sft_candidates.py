"""Source-only candidate-data tests; no training or model invocation."""

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "identity_sft_candidates", ROOT / "tools/identity_sft_candidates.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class IdentitySftCandidatesTest(unittest.TestCase):
    def test_exact_coverage_and_counts(self):
        cases = module.validate_cases()
        self.assertEqual(len(cases), 13)
        self.assertTrue(all(len(group["cases"]) == 6 for group in cases.values()))

    def test_export_preserves_split_and_source_labels(self):
        train = module.export_conversations("one", "train")
        dev = module.export_conversations("one", "dev")
        self.assertEqual((len(train), len(dev)), (4, 2))
        self.assertEqual({c["metadata"]["case_id"] for c in train}
                         & {c["metadata"]["case_id"] for c in dev}, set())
        self.assertTrue(all(c["metadata"]["label_status"] == module.STATUS for c in train))
        self.assertTrue(all([m["role"] for m in c["messages"]] ==
                            ["system", "user", "assistant"] for c in dev))

    def test_export_rejects_unknown_identity_and_split(self):
        with self.assertRaisesRegex(ValueError, "unknown identity"):
            module.export_conversations("ten", "train")
        with self.assertRaisesRegex(ValueError, "split must be"):
            module.export_conversations("one", "heldout")


if __name__ == "__main__":
    unittest.main()
