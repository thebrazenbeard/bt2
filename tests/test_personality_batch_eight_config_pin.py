"""Eight-step bounds and fail-closed adapter configuration custody, CPU-only."""

from pathlib import Path
import hashlib
import sys
import tempfile
from types import SimpleNamespace
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_personality_gguf_batch import checked_adapter_config, inputs  # noqa: E402


class BatchEightAndAdapterConfigTests(unittest.TestCase):
    def test_eight_steps_passes_bounded_parameter_guard(self):
        # A valid eight-step job gets as far as checkout verification; it should
        # not fail the bounded parameter guard as three or nine steps must.
        base = dict(threads=2, steps=8, max_length=2048, min_free_gib=20,
                    identities=["four"], bt2_dir="/nonexistent-personality-source",
                    source_commit="a" * 40)
        with self.assertRaises(Exception) as observed:
            inputs(SimpleNamespace(**base))
        self.assertNotIn("invalid bounded training parameters", str(observed.exception))
        for bad in (-1, 0, 3, 5, 7, 9, 100):
            with self.subTest(steps=bad):
                with self.assertRaisesRegex(ValueError, "invalid bounded training parameters"):
                    inputs(SimpleNamespace(**(base | {"steps": bad})))

    def test_adapter_config_requires_matching_training_merge_and_file_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            adapter = run / "adapter"
            adapter.mkdir()
            config = adapter / "adapter_config.json"
            config.write_text('{"r": 8, "lora_alpha": 16}', encoding="utf-8")
            digest = hashlib.sha256(config.read_bytes()).hexdigest()
            training = {"adapter_config_sha256": digest}
            merge = {"adapter_config_sha256": digest}
            self.assertEqual(checked_adapter_config(run, training), digest)
            self.assertEqual(checked_adapter_config(run, training, merge), digest)

            with self.assertRaisesRegex(ValueError, "training adapter_config_sha256"):
                checked_adapter_config(run, {})
            with self.assertRaisesRegex(ValueError, "training adapter_config_sha256"):
                checked_adapter_config(run, {"adapter_config_sha256": "A" * 64})
            with self.assertRaisesRegex(ValueError, "merge adapter_config_sha256"):
                checked_adapter_config(run, training, {})
            with self.assertRaisesRegex(ValueError, "merge adapter_config_sha256"):
                checked_adapter_config(run, training, {"adapter_config_sha256": "0" * 64})
            config.write_text('{"r": 1, "lora_alpha": 16}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from training receipt"):
                checked_adapter_config(run, training, merge)
            config.unlink()
            with self.assertRaisesRegex(ValueError, "missing/nonregular"):
                checked_adapter_config(run, training, merge)


if __name__ == "__main__":
    unittest.main()
