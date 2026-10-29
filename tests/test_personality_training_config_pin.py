"""Fail-closed custody checks for the PEFT config that controls merged weights."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "train_personality_lora", ROOT / "tools/train_personality_lora.py"
)
trainer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trainer)


class AdapterConfigReceiptTests(unittest.TestCase):
    def test_rejects_undocumented_config_and_same_weight_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            adapter = run / "adapter"
            adapter.mkdir()
            file = adapter / "adapter_config.json"
            file.write_text('{"r": 4, "lora_alpha": 8}', encoding="utf-8")
            original = trainer.sha256_file(file)
            with self.assertRaisesRegex(ValueError, "configuration receipt"):
                trainer.verify_adapter_config(run, {})
            self.assertEqual(trainer.verify_adapter_config(
                run, {"adapter_config_sha256": original}), original)
            # Adapter tensor bytes have not changed; the merge scaling has.
            file.write_text('{"r": 4, "lora_alpha": 16}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "configuration changed"):
                trainer.verify_adapter_config(run, {"adapter_config_sha256": original})

    def test_rejects_symlink_or_missing_config(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            adapter = run / "adapter"
            adapter.mkdir()
            outside = run / "outside.json"
            outside.write_text('{}', encoding="utf-8")
            config = adapter / "adapter_config.json"
            with self.assertRaisesRegex(ValueError, "unsafe"):
                trainer.verify_adapter_config(
                    run, {"adapter_config_sha256": trainer.sha256_file(outside)})
            try:
                config.symlink_to(outside)
            except (NotImplementedError, OSError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaisesRegex(ValueError, "unsafe"):
                trainer.verify_adapter_config(
                    run, {"adapter_config_sha256": trainer.sha256_file(outside)})


if __name__ == "__main__":
    unittest.main()
