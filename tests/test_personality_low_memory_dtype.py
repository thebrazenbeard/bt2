"""CPU dtype option is explicit, bounded and pinned in reload receipts."""

import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from train_personality_lora import (  # noqa: E402
    SCHEMA, preflight, resolve_cpu_dtype, verify_reload,
)


class LowMemoryDtypeTests(unittest.TestCase):
    def test_dtype_resolver_is_bounded_without_torch_import(self):
        fake_torch = SimpleNamespace(float32=object(), bfloat16=object())
        self.assertIs(resolve_cpu_dtype(fake_torch, "float32"), fake_torch.float32)
        self.assertIs(resolve_cpu_dtype(fake_torch, "bfloat16"), fake_torch.bfloat16)
        for invalid in ("float16", "float64", "auto", "", None):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                ValueError, "unsupported CPU model dtype"
            ):
                resolve_cpu_dtype(fake_torch, invalid)

    def test_preflight_rejects_unbounded_dtype_before_touching_sources(self):
        args = SimpleNamespace(device="cpu", cpu_dtype="float16")
        with self.assertRaisesRegex(ValueError, "unsupported CPU model dtype"):
            preflight(args)

    def test_reload_rejects_tampered_dtype_receipt_before_importing_weights(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / "report.json").write_text(json.dumps({
                "schema_version": SCHEMA,
                "cpu_dtype": "float16",
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported CPU model dtype receipt"):
                verify_reload(SimpleNamespace(run_dir=str(run), threads=2))


if __name__ == "__main__":
    unittest.main()
