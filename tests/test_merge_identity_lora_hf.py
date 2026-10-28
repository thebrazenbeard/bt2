"""Fail-closed source tests for experimental LoRA merge preflight."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("merge_identity_lora_hf",
                                           ROOT / "tools/merge_identity_lora_hf.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class MergePreflightTest(unittest.TestCase):
    def test_missing_run_is_not_treated_as_mergeable(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                module.validate_merge_inputs(Path(temp) / "missing", Path(temp) / "output")

    def test_corrupt_or_empty_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "run"
            run.mkdir()
            (run / "report.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected training report schema"):
                module.validate_merge_inputs(run, Path(temp) / "output")


if __name__ == "__main__":
    unittest.main()
