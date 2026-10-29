"""Lightweight source-only guards for isolated persona HF merge preflight."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "merge_personality_lora_hf", ROOT / "tools/merge_personality_lora_hf.py",
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
import personality_donor_provenance as provenance  # noqa: E402


class MergePersonaPreflightTests(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, "_weight_patcher"):
            self._weight_patcher.stop()

    def test_missing_run_fails_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(FileNotFoundError):
                module.validate_merge_inputs(root / "missing", root / "out", root / "lab")
            self.assertFalse((root / "out").exists())

    def _fixture(self, temp):
        root = Path(temp)
        source = root / "bt2"
        source.mkdir()
        dataset = source / "coding_models/personality/cases/one.json"
        dataset.parent.mkdir(parents=True)
        dataset.write_text('{"case":"source-bound"}', encoding="utf-8")
        notice = source / provenance.NOTICE_SOURCE
        notice.parent.mkdir(parents=True, exist_ok=True)
        notice.write_text(
            f"Modified from {provenance.DONOR_REPO} at {provenance.DONOR_REVISION}.\n",
            encoding="utf-8")
        license_source = source / provenance.UPSTREAM_LICENSE_SOURCE
        license_source.parent.mkdir(parents=True, exist_ok=True)
        upstream_license = ROOT / provenance.UPSTREAM_LICENSE_SOURCE
        license_source.write_bytes(upstream_license.read_bytes())
        labyrinth = root / "labyrinth"
        labyrinth.mkdir()
        donor = root / "donor"
        donor.mkdir()
        (donor / "model.safetensors").write_bytes(b"pinned HF donor bytes")
        weight_sha = module.sha256_file(donor / "model.safetensors")
        self._weight_patcher = mock.patch.object(provenance, "DONOR_WEIGHTS_SHA256", weight_sha)
        self._weight_patcher.start()
        for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
            (donor / name).write_text("{}", encoding="utf-8")
        run = root / "run"
        (run / "adapter").mkdir(parents=True)
        (run / "adapter/adapter_model.safetensors").write_bytes(b"candidate LoRA values")
        (run / "adapter/adapter_config.json").write_text(
            '{"r": 4, "lora_alpha": 8}', encoding="utf-8"
        )
        report = {
            "schema_version": module.SCHEMA,
            "claim_ceiling": module.CEILING,
            "arm": "candidate",
            "identity_id": "one",
            "bt2_source_commit": "a" * 40,
            "labyrinth_scheduler_commit": "b" * 40,
            "base_model_dir": str(donor),
            "base_model_sha256": module.sha256_file(donor / "model.safetensors"),
            "donor_provenance": provenance.verify_donor_identity(donor, weight_sha,
                                                                   bt2=source),
            "base_metadata_sha256": {
                name: module.sha256_file(donor / name)
                for name in ("config.json", "tokenizer.json", "tokenizer_config.json")
            },
            "adapter_safetensors_sha256": module.sha256_file(run / "adapter/adapter_model.safetensors"),
            "adapter_config_sha256": module.sha256_file(run / "adapter/adapter_config.json"),
            "personality_dataset_sha256": module.sha256_file(dataset),
            "persona_instruction_sha256": "c" * 64,
            "frozen_parameters_and_buffers_verified_unchanged": True,
            "trainable_tensor_sha256_before": "d" * 64,
            "trainable_tensor_sha256_after": "e" * 64,
            "frozen_parameter_sha256_unchanged": "f" * 64,
            "persistent_buffer_sha256_unchanged": "1" * 64,
            "qualified": False,
            "installed": False,
            "behavioral_improvement_verified": False,
            "steps": 2,
            "schedule": [{"case_id": "a", "level": "grounded"},
                         {"case_id": "b", "level": "adversarial"}],
        }
        (run / "report.json").write_text(json.dumps(report), encoding="utf-8")
        return root, source, labyrinth, donor, run, report

    def _check(self, run, out, labyrinth, source):
        with mock.patch.object(module, "checked_checkout",
                               side_effect=lambda path, _sha, _file: Path(path).resolve(strict=True)):
            return module.validate_merge_inputs(run, out, labyrinth, bt2_dir=source)

    def test_accepts_exact_candidate_without_mutating_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, report = self._fixture(temp)
            output = root / "separate-merged"
            result = self._check(run, output, labyrinth, source)
            self.assertEqual(result["report"], report)
            self.assertEqual(result["base_dir"], donor)
            self.assertFalse(output.exists())

    def test_rejects_report_schema_control_arms_and_missing_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, report = self._fixture(temp)
            for field, bad in (("schema_version", "wrong"),
                               ("claim_ceiling", "PRODUCTION"),
                               ("arm", "sham"),
                               ("arm", "corrupt"),
                               ("frozen_parameters_and_buffers_verified_unchanged", False),
                               ("qualified", True),
                               ("installed", True),
                               ("behavioral_improvement_verified", True),
                               ("bt2_source_commit", "not-a-hash"),
                               ("persona_instruction_sha256", "bad"),
                               ("adapter_config_sha256", "bad"),
                               ("donor_provenance", {}),
                               ("trainable_tensor_sha256_before", "bad"),
                               ("frozen_parameter_sha256_unchanged", "bad")):
                with self.subTest(field=field, bad=bad):
                    broken = dict(report, **{field: bad})
                    (run / "report.json").write_text(json.dumps(broken), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        self._check(run, root / "output", labyrinth, source)
                    self.assertFalse((root / "output").exists())

    def test_rejects_donor_adapter_dataset_drift_and_unsafe_destinations(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, report = self._fixture(temp)
            for path in (donor / "model.safetensors",
                         source / provenance.UPSTREAM_LICENSE_SOURCE,
                         run / "adapter/adapter_model.safetensors",
                         run / "adapter/adapter_config.json",
                         source / "coding_models/personality/cases/one.json"):
                with self.subTest(path=path):
                    before = path.read_bytes()
                    path.write_bytes(before + b"!changed!")
                    with self.assertRaises(ValueError):
                        self._check(run, root / "output", labyrinth, source)
                    path.write_bytes(before)
            for destination in (donor / "inside", run / "inside", source / "inside",
                                labyrinth / "inside", root / "already-there"):
                with self.subTest(destination=destination):
                    if destination.name == "already-there":
                        destination.mkdir()
                    with self.assertRaises(ValueError):
                        self._check(run, destination, labyrinth, source)

    def test_rejects_donor_metadata_changed_since_training(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, report = self._fixture(temp)
            for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
                with self.subTest(name=name):
                    file = donor / name
                    original = file.read_bytes()
                    file.write_bytes(original + b"changed-after-training")
                    with self.assertRaisesRegex(ValueError, "donor metadata"):
                        self._check(run, root / "output", labyrinth, source)
                    file.write_bytes(original)
            extra = donor / "special_tokens_map.json"
            extra.write_text('{"eos_token": "<eos>"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                self._check(run, root / "output", labyrinth, source)
            self.assertFalse((root / "output").exists())

    def test_rejects_missing_or_untrusted_training_metadata_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, report = self._fixture(temp)
            for bad in (None, {}, {"config.json": "0" * 64},
                        dict(report["base_metadata_sha256"], **{"unexpected.json": "0" * 64})):
                with self.subTest(metadata=bad):
                    broken = dict(report)
                    if bad is None:
                        broken.pop("base_metadata_sha256")
                    else:
                        broken["base_metadata_sha256"] = bad
                    (run / "report.json").write_text(json.dumps(broken), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        self._check(run, root / "output", labyrinth, source)

    def test_merge_writes_source_bound_receipt_in_new_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source, labyrinth, donor, run, _report = self._fixture(temp)
            output = root / "merged-hf"
            context = self._check(run, output, labyrinth, source)

            class FakeMerged:
                def save_pretrained(self, path, *, safe_serialization, max_shard_size):
                    self_assert = (safe_serialization, max_shard_size)
                    assert self_assert == (True, "3GB")
                    (Path(path) / "model-00001-of-00001.safetensors").write_bytes(b"merged weights")
                    (Path(path) / "config.json").write_text("{}", encoding="utf-8")

            class FakeAdapted:
                def merge_and_unload(self, *, safe_merge):
                    assert safe_merge is True
                    return FakeMerged()

            class FakePeftModel:
                @staticmethod
                def from_pretrained(_base, _path, *, is_trainable):
                    assert is_trainable is False
                    return FakeAdapted()

            class FakeAutoModel:
                @staticmethod
                def from_pretrained(_path, **kwargs):
                    assert kwargs["local_files_only"] is True
                    return object()

            class FakeTokenizer:
                def save_pretrained(self, path):
                    for name in ("tokenizer.json", "tokenizer_config.json"):
                        (Path(path) / name).write_text("{}", encoding="utf-8")

            fake = {
                "torch": types.SimpleNamespace(set_num_threads=lambda _n: None, float32="float32"),
                "peft": types.SimpleNamespace(PeftModel=FakePeftModel),
                "transformers": types.SimpleNamespace(
                    AutoModelForCausalLM=FakeAutoModel,
                    AutoTokenizer=types.SimpleNamespace(
                        from_pretrained=lambda _path, **_kwargs: FakeTokenizer()),
                ),
            }
            args = types.SimpleNamespace(run_dir=str(run), output_dir=str(output),
                                         labyrinth_dir=str(labyrinth), threads=2)
            with mock.patch.object(module, "validate_merge_inputs", return_value=context), \
                 mock.patch.object(module, "checked_checkout", return_value=root), \
                 mock.patch.dict(sys.modules, fake):
                receipt = module.merge(args)
            file = output / "BT2_PERSONA_MERGE_RECEIPT.json"
            self.assertTrue(file.is_file())
            self.assertEqual(json.loads(file.read_text(encoding="utf-8")), receipt)
            self.assertEqual(receipt["identity_id"], "one")
            self.assertEqual(receipt["base_sha256"], module.sha256_file(donor / "model.safetensors"))
            self.assertEqual(receipt["adapter_sha256"],
                             module.sha256_file(run / "adapter/adapter_model.safetensors"))
            self.assertEqual(receipt["adapter_config_sha256"],
                             module.sha256_file(run / "adapter/adapter_config.json"))
            self.assertEqual(receipt["training_report_sha256"],
                             module.sha256_file(run / "report.json"))
            self.assertEqual(receipt["safetensors"], {
                "model-00001-of-00001.safetensors":
                    module.sha256_file(output / "model-00001-of-00001.safetensors"),
            })
            self.assertFalse(receipt["gguf_converted"])
            self.assertFalse(receipt["installed"])
            self.assertEqual(receipt["donor_provenance"], report_from :=
                             json.loads((run / "report.json").read_text(encoding="utf-8"))["donor_provenance"])
            self.assertEqual(receipt["attribution_companions_sha256"][provenance.LICENSE_COMPANION],
                             report_from["license_sha256"])
            self.assertTrue((output / provenance.LICENSE_COMPANION).is_file())
            self.assertTrue((output / provenance.NOTICE_COMPANION).is_file())


if __name__ == "__main__":
    unittest.main()
