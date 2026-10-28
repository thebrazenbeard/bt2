"""Bounded batch orchestration tests without running transformers or models."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_identity_gguf_batch", ROOT / "tools/build_identity_gguf_batch.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class BatchSafetyTests(unittest.TestCase):
    def test_exact_remaining_identity_set_excludes_one(self):
        self.assertEqual(len(module.IDENTITIES), 12)
        self.assertEqual(len(set(module.IDENTITIES)), 12)
        self.assertNotIn("one", module.IDENTITIES)

    def test_hashing_is_stable(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "x.bin"
            artifact.write_bytes(b"abc")
            self.assertEqual(module.sha256_file(artifact),
                             "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_stage_fails_closed_and_preserves_log(self):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "failure.log"
            with self.assertRaisesRegex(ValueError, "failed exit=7"):
                module.run_stage("controlled-failure", [
                    sys.executable, "-c", "import sys; print('proof'); sys.exit(7)"
                ], log, Path(temp), 15)
            self.assertIn("proof", log.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                module.run_stage("no-overwrite", [sys.executable, "-V"],
                                 log, Path(temp), 15)


if __name__ == "__main__":
    unittest.main()
