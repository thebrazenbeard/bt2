"""Source-only checks for honest BT2 coding-evaluation candidate packaging."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "validate_identity_coding_evals", ROOT / "tools/validate_identity_coding_evals.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class EvaluationDraftValidationTests(unittest.TestCase):
    def test_exact_identity_coverage_and_case_count(self):
        drafts = module.validate_all()
        self.assertEqual(len(drafts), 13)
        self.assertEqual(sum(len(item["cases"]) for item in drafts.values()), 39)
        self.assertTrue(all(item["status"] == module.STATUS for item in drafts.values()))

    def test_refuses_promotion_to_qualified(self):
        draft = module.validate_all()["one"]
        draft["status"] = "MODEL_QUALIFIED"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "one.json"
            path.write_text(json.dumps(draft), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "author draft"):
                module.validate_evaluation_file(path, "one")

    def test_refuses_unsafe_source_paths(self):
        draft = module.validate_all()["one"]
        draft["source_refs"] = ["../../outside.md"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "one.json"
            path.write_text(json.dumps(draft), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe source path"):
                module.validate_evaluation_file(path, "one")

    def test_duplicate_case_id_rejected(self):
        draft = module.validate_all()["one"]
        draft["cases"][1]["case_id"] = draft["cases"][0]["case_id"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "one.json"
            path.write_text(json.dumps(draft), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate/invalid"):
                module.validate_evaluation_file(path, "one")


if __name__ == "__main__":
    unittest.main()
