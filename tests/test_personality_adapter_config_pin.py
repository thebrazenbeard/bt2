"""Independent tamper guards for trained persona adapter configuration."""

import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

import test_merge_personality_lora_hf as prior

module = prior.module


class AdapterConfigPinTests(unittest.TestCase):
    def _fixture(self, temp):
        root, source, labyrinth, donor, run, report = (
            prior.MergePersonaPreflightTests("test_missing_run_fails_without_output")._fixture(temp)
        )
        config_file = run / "adapter/adapter_config.json"
        config_file.write_text(json.dumps({"r": 8, "lora_alpha": 16}), encoding="utf-8")
        report["adapter_config_sha256"] = module.sha256_file(config_file)
        (run / "report.json").write_text(json.dumps(report), encoding="utf-8")
        return root, source, labyrinth, donor, run, report

    def _preflight(self, run, output, labyrinth, source):
        with mock.patch.object(module, "checked_checkout",
                               side_effect=lambda path, _sha, _file: Path(path).resolve(strict=True)):
            return module.validate_merge_inputs(run, output, labyrinth, bt2_dir=source)

    def test_valid_pin_and_eight_step_schedule(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, report = self._fixture(temp)
            report["steps"] = 8
            report["schedule"] = [dict(case_id=str(i), level="grounded") for i in range(8)]
            (run / "report.json").write_text(json.dumps(report), encoding="utf-8")
            context = self._preflight(run, root / "merged", labyrinth, source)
            self.assertEqual(context["adapter_config_sha256"], report["adapter_config_sha256"])
            self.assertFalse((root / "merged").exists())

    def test_rejects_unbounded_schedule_and_legacy_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, report = self._fixture(temp)
            for steps in (0, 1, 3, 5, 9, 100):
                with self.subTest(steps=steps):
                    bad = dict(report, steps=steps,
                               schedule=[dict(case_id=str(i), level="grounded")
                                         for i in range(steps)])
                    (run / "report.json").write_text(json.dumps(bad), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "schedule receipt"):
                        self._preflight(run, root / "merged", labyrinth, source)
            legacy = dict(report, schema_version="BT2_LABYRINTH_SCHEDULED_PERSONALITY_LORA_V1")
            (run / "report.json").write_text(json.dumps(legacy), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                self._preflight(run, root / "merged", labyrinth, source)

    def test_rejects_unpinned_or_modified_lora_alpha_without_weight_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, report = self._fixture(temp)
            config_file = run / "adapter/adapter_config.json"
            adapter_file = run / "adapter/adapter_model.safetensors"
            original_weights_digest = module.sha256_file(adapter_file)
            self._preflight(run, root / "merged", labyrinth, source)
            config_file.write_text(json.dumps({"r": 8, "lora_alpha": 128}), encoding="utf-8")
            self.assertEqual(module.sha256_file(adapter_file), original_weights_digest)
            with self.assertRaisesRegex(ValueError, "adapter config"):
                self._preflight(run, root / "merged", labyrinth, source)
            config_file.write_text(json.dumps({"r": 8, "lora_alpha": 16}), encoding="utf-8")
            for invalid in (None, "0" * 64, "NOT-A-SHA"):
                with self.subTest(receipt=invalid):
                    altered = dict(report)
                    if invalid is None:
                        altered.pop("adapter_config_sha256")
                    else:
                        altered["adapter_config_sha256"] = invalid
                    (run / "report.json").write_text(json.dumps(altered), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        self._preflight(run, root / "merged", labyrinth, source)
            self.assertFalse((root / "merged").exists())

    def test_detects_adapter_config_mutated_by_merge_before_output_is_created(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, _report = self._fixture(temp)
            output = root / "merged"
            context = self._preflight(run, output, labyrinth, source)

            class FakeAdapted:
                def merge_and_unload(self, *, safe_merge):
                    assert safe_merge
                    (run / "adapter/adapter_config.json").write_text(
                        json.dumps({"r": 8, "lora_alpha": 10000}), encoding="utf-8")
                    return object()

            class FakePeft:
                @staticmethod
                def from_pretrained(_base, _path, *, is_trainable):
                    assert is_trainable is False
                    return FakeAdapted()

            fake = {
                "torch": types.SimpleNamespace(set_num_threads=lambda _n: None, float32="float32"),
                "peft": types.SimpleNamespace(PeftModel=FakePeft),
                "transformers": types.SimpleNamespace(
                    AutoModelForCausalLM=types.SimpleNamespace(
                        from_pretrained=lambda *a, **k: object()),
                    AutoTokenizer=types.SimpleNamespace(
                        from_pretrained=lambda *a, **k: object()),
                ),
            }
            args = types.SimpleNamespace(run_dir=str(run), output_dir=str(output),
                                         labyrinth_dir=str(labyrinth), threads=2)
            with mock.patch.object(module, "validate_merge_inputs", return_value=context), \
                 mock.patch.dict(sys.modules, fake):
                with self.assertRaisesRegex(ValueError, "adapter config"):
                    module.merge(args)
            self.assertFalse(output.exists())

    def test_merge_receipt_includes_pinned_adapter_config_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, report = self._fixture(temp)
            output = root / "merged"
            context = self._preflight(run, output, labyrinth, source)

            class FakeMerged:
                def save_pretrained(self, path, **_kwargs):
                    (Path(path) / "model.safetensors").write_bytes(b"merged")
                    (Path(path) / "config.json").write_text("{}", encoding="utf-8")

            class FakeAdapted:
                def merge_and_unload(self, *, safe_merge):
                    assert safe_merge
                    return FakeMerged()

            class FakeTokenizer:
                def save_pretrained(self, path):
                    for name in ("tokenizer.json", "tokenizer_config.json"):
                        (Path(path) / name).write_text("{}", encoding="utf-8")

            fake = {
                "torch": types.SimpleNamespace(set_num_threads=lambda _n: None, float32="float32"),
                "peft": types.SimpleNamespace(PeftModel=types.SimpleNamespace(
                    from_pretrained=lambda *a, **k: FakeAdapted())),
                "transformers": types.SimpleNamespace(
                    AutoModelForCausalLM=types.SimpleNamespace(
                        from_pretrained=lambda *a, **k: object()),
                    AutoTokenizer=types.SimpleNamespace(
                        from_pretrained=lambda *a, **k: FakeTokenizer()),
                ),
            }
            args = types.SimpleNamespace(run_dir=str(run), output_dir=str(output),
                                         labyrinth_dir=str(labyrinth), threads=2)
            with mock.patch.object(module, "validate_merge_inputs", return_value=context), \
                 mock.patch.object(module, "checked_checkout", return_value=root), \
                 mock.patch.dict(sys.modules, fake):
                receipt = module.merge(args)
            self.assertEqual(receipt["adapter_config_sha256"], report["adapter_config_sha256"])
            recorded = json.loads((output / "BT2_PERSONA_MERGE_RECEIPT.json").read_text())
            self.assertEqual(recorded["adapter_config_sha256"], report["adapter_config_sha256"])

    def test_rejects_missing_or_symlinked_adapter_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, _donor, run, _report = self._fixture(temp)
            config = run / "adapter/adapter_config.json"
            content = config.read_bytes()
            config.unlink()
            with self.assertRaisesRegex(ValueError, "adapter config"):
                self._preflight(run, root / "merged", labyrinth, source)
            external_config = root / "external_config.json"
            external_config.write_bytes(content)
            config.symlink_to(external_config)
            with self.assertRaisesRegex(ValueError, "adapter config"):
                self._preflight(run, root / "merged", labyrinth, source)
            self.assertFalse((root / "merged").exists())


if __name__ == "__main__":
    unittest.main()
