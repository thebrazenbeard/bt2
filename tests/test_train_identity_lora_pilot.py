"""Dependency-free unit tests for the CPU-only model pilot's source boundaries."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "train_identity_lora_pilot", ROOT / "tools/train_identity_lora_pilot.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TrainingSourceContractTest(unittest.TestCase):
    def test_system_instruction_does_not_claim_active_identity(self):
        model = module.load_models()["one"]
        system = module.system_instruction(model)
        self.assertIn("ephemeral BT2 coding specialist", system)
        self.assertIn("never invent tests", system)

    def test_preflight_fails_on_nonexistent_base(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                module.preflight("one", Path(temp) / "absent",
                                 "0" * 64, Path(temp) / "pilot")

    def test_preflight_fails_on_unknown_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unknown BT2 identity"):
                module.preflight("ten", Path(temp), "0" * 64, Path(temp) / "pilot")

    def test_preflight_rejects_wrong_hf_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("model.safetensors", "config.json", "tokenizer.json",
                         "tokenizer_config.json"):
                (root / name).write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                module.preflight("one", root, "0" * 64, root / "new-run")


if __name__ == "__main__":
    unittest.main()
