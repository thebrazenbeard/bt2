"""Dependency-free falsification tests for matched personality control receipts."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from train_personality_lora import (  # noqa: E402
    SCHEMA, CEILING, configure_gradient_checkpointing,
)
from verify_personality_control_set import ARMS, verify_control_set  # noqa: E402


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class MatchedControlsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = {arm: self.root / arm for arm in ARMS}
        for arm in ARMS:
            self.paths[arm].joinpath("adapter").mkdir(parents=True)
            adapter = self.paths[arm] / "adapter"
            (adapter / "adapter_model.safetensors").write_bytes(arm.encode())
            (adapter / "adapter_config.json").write_text('{"r":4}', encoding="utf-8")
            before = digest("shared initial adapters")
            report = {
                "schema_version": SCHEMA, "claim_ceiling": CEILING, "arm": arm,
                "identity_id": "seven", "device": "cpu", "cpu_dtype": "float32",
                "gradient_checkpointing_enabled": False,
                "bt2_source_commit": "a" * 40, "labyrinth_scheduler_commit": "b" * 40,
                "instruction_mode": "neutral", "personality_dataset_sha256": digest("corpus"),
                "persona_instruction_sha256": digest("neutral"),
                "base_model_sha256": digest("donor"),
                "base_metadata_sha256": {"config.json": digest("config")},
                "base_model_bytes": 1000,
                "schedule": [{"case_id": "seven-a", "level": "grounded", "labyrinth_case_seed": 1},
                             {"case_id": "seven-b", "level": "adversarial", "labyrinth_case_seed": 2}],
                "losses": [{"step": 1, "case_id": "seven-a", "loss": 2.5},
                           {"step": 2, "case_id": "seven-b", "loss": 2.3}],
                "seed": 74413, "steps": 2, "max_length": 1536, "threads": 2,
                "versions": {"torch": "x", "peft": "y", "transformers": "z"},
                "trainable_tensor_sha256_before": before,
                "trainable_tensor_sha256_after": (before if arm == "sham" else digest(arm)),
                "frozen_parameter_sha256_unchanged": digest("frozen base"),
                "persistent_buffer_sha256_unchanged": digest("frozen buffers"),
                "frozen_parameters_and_buffers_verified_unchanged": True,
                "adapter_safetensors_sha256": hashlib.sha256(arm.encode()).hexdigest(),
                "adapter_config_sha256": digest('{"r":4}'),
                "learning_rate": 0.0 if arm == "sham" else 0.0002,
                "corruption_control": "WEAK_ROTATED_WITHIN_ROLE_TARGET" if arm == "corrupt" else "NONE",
                "crossrole_source_receipts": [], "qualified": False, "installed": False,
                "behavioral_improvement_verified": False,
            }
            self.write_report(arm, report)

    def write_report(self, arm, report):
        (self.paths[arm] / "report.json").write_text(json.dumps(report), encoding="utf-8")

    def mutate(self, arm, field, value):
        file = self.paths[arm] / "report.json"
        report = json.loads(file.read_text(encoding="utf-8"))
        report[field] = value
        self.write_report(arm, report)

    def test_exact_static_matching_never_claims_behavioral_qualification(self):
        result = verify_control_set(self.paths)
        self.assertEqual(result["status"], "MATCHED_STATIC_RECEIPTS_ONLY")
        self.assertFalse(result["model_inference_executed"])
        self.assertFalse(result["coding_retention_verified"])
        self.assertEqual(len(result["report_sha256"]), 3)

    def test_mismatched_schedule_seed_donor_prompt_frozen_and_init_fail_closed(self):
        fields = {
            "schedule": [{"case_id": "seven-different"}],
            "seed": 4, "base_model_sha256": digest("other donor"),
            "persona_instruction_sha256": digest("trait prompting"),
            "frozen_parameter_sha256_unchanged": digest("different frozen"),
            "trainable_tensor_sha256_before": digest("different initialization"),
            "cpu_dtype": "bfloat16", "steps": 4,
            "gradient_checkpointing_enabled": True,
        }
        original = json.loads((self.paths["corrupt"] / "report.json").read_text())
        for field, value in fields.items():
            with self.subTest(field=field):
                self.mutate("corrupt", field, value)
                with self.assertRaises(ValueError):
                    verify_control_set(self.paths)
                self.write_report("corrupt", copy.deepcopy(original))

    def test_tamper_and_fabricated_qualification_fail_closed(self):
        self.mutate("candidate", "qualified", True)
        with self.assertRaisesRegex(ValueError, "overclaims qualification"):
            verify_control_set(self.paths)
        self.mutate("candidate", "qualified", False)
        adapter = self.paths["candidate"] / "adapter" / "adapter_config.json"
        adapter.write_text('{"r":8}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from receipt"):
            verify_control_set(self.paths)

    def test_sham_must_stay_unchanged_and_corrupt_must_use_negative_labels(self):
        self.mutate("sham", "trainable_tensor_sha256_after", digest("updated sham"))
        with self.assertRaisesRegex(ValueError, "sham LoRA update"):
            verify_control_set(self.paths)
        self.mutate("sham", "trainable_tensor_sha256_after", digest("shared initial adapters"))
        self.mutate("corrupt", "corruption_control", "NONE")
        with self.assertRaisesRegex(ValueError, "wrong control-label strategy"):
            verify_control_set(self.paths)

    def test_unprompted_requirement_and_run_uniqueness(self):
        self.mutate("candidate", "instruction_mode", "traits")
        with self.assertRaisesRegex(ValueError, "neutral"):
            verify_control_set(self.paths)
        self.mutate("candidate", "instruction_mode", "neutral")
        aliased = dict(self.paths, sham=self.paths["candidate"])
        with self.assertRaisesRegex(ValueError, "separate run"):
            verify_control_set(aliased)

    def test_checkpointing_switch_only_changes_opt_in_runtime_configuration(self):
        class FakeModel:
            def __init__(self):
                self.calls = []

            def gradient_checkpointing_enable(self, **kwargs):
                self.calls.append(kwargs)

        model = FakeModel()
        configure_gradient_checkpointing(model, False)
        self.assertEqual(model.calls, [])
        configure_gradient_checkpointing(model, True)
        self.assertEqual(model.calls, [{"gradient_checkpointing_kwargs":
                                        {"use_reentrant": False}}])
        with self.assertRaisesRegex(ValueError, "invalid gradient checkpointing flag"):
            configure_gradient_checkpointing(model, 1)


if __name__ == "__main__":
    unittest.main()
