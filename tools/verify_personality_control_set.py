"""Check matched BT2 personality control *receipts*, not model effectiveness.

This is a static integrity gate. It neither loads a model nor infers behavioral
improvement. An independently held holdout and real inference remain necessary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from identity_coding_models import require
from train_identity_lora_pilot import sha256_file
from train_personality_lora import SCHEMA, CEILING


SHA256 = re.compile(r"[a-f0-9]{64}\Z")
ARMS = ("candidate", "sham", "corrupt")
MATCHED_FIELDS = (
    "identity_id", "device", "cpu_dtype", "gradient_checkpointing_enabled", "bt2_source_commit",
    "labyrinth_scheduler_commit", "instruction_mode", "personality_dataset_sha256",
    "persona_instruction_sha256", "base_model_sha256", "base_metadata_sha256",
    "base_model_bytes", "schedule", "seed", "steps", "max_length", "threads",
    "versions", "trainable_tensor_sha256_before",
    "frozen_parameter_sha256_unchanged", "persistent_buffer_sha256_unchanged",
)


def _digest(value: object, description: str) -> None:
    require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
            f"invalid {description} SHA-256")


def load_receipt(path: Path, arm: str) -> dict:
    """Verify physical adapter receipts and basic per-arm training invariants."""
    require(path.is_dir() and not path.is_symlink(), "unsafe or absent control run")
    report_file = path / "report.json"
    require(report_file.is_file() and not report_file.is_symlink(),
            "missing or unsafe control report")
    report = json.loads(report_file.read_text(encoding="utf-8"))
    require(isinstance(report, dict) and report.get("schema_version") == SCHEMA,
            "unsupported control receipt schema")
    require(report.get("claim_ceiling") == CEILING and
            report.get("arm") == arm and report.get("device") == "cpu",
            "incorrect claim ceiling, arm or device")
    require(report.get("qualified") is False and report.get("installed") is False and
            report.get("behavioral_improvement_verified") is False,
            "control receipt overclaims qualification")
    require(report.get("frozen_parameters_and_buffers_verified_unchanged") is True,
            "missing frozen-state verification")
    # Receipts produced before opt-in checkpointing existed represent its default.
    report.setdefault("gradient_checkpointing_enabled", False)
    require(type(report["gradient_checkpointing_enabled"]) is bool,
            "invalid checkpointing receipt")
    for field in ("trainable_tensor_sha256_before", "trainable_tensor_sha256_after",
                  "frozen_parameter_sha256_unchanged", "persistent_buffer_sha256_unchanged",
                  "adapter_safetensors_sha256", "adapter_config_sha256",
                  "persona_instruction_sha256", "base_model_sha256", "personality_dataset_sha256"):
        _digest(report.get(field), field)
    for filename, field in (("adapter_model.safetensors", "adapter_safetensors_sha256"),
                            ("adapter_config.json", "adapter_config_sha256")):
        file = path / "adapter" / filename
        require(file.is_file() and not file.is_symlink(), f"missing or unsafe {filename}")
        require(sha256_file(file) == report[field], f"{filename} differs from receipt")
    before, after = (report[key] for key in ("trainable_tensor_sha256_before",
                                              "trainable_tensor_sha256_after"))
    require((after != before) == (arm != "sham"),
            f"{arm} LoRA update inconsistent with control arm")
    require(report.get("learning_rate") == (0.0 if arm == "sham" else 0.0002),
            f"{arm} learning rate inconsistent with control arm")
    require(report.get("corruption_control") ==
            ("WEAK_ROTATED_WITHIN_ROLE_TARGET" if arm == "corrupt" else "NONE"),
            "wrong control-label strategy")
    require(report.get("crossrole_source_receipts") == [],
            "cross-role sources invalid for candidate/sham/rotated corruption")
    schedule = report.get("schedule")
    losses = report.get("losses")
    steps = report.get("steps")
    require(type(steps) is int and steps >= 2 and steps % 2 == 0 and
            isinstance(schedule, list) and isinstance(losses, list) and
            len(schedule) == len(losses) == steps,
            "control steps, schedule, and losses disagree")
    for number, (case, loss) in enumerate(zip(schedule, losses), 1):
        require(isinstance(case, dict) and isinstance(loss, dict) and
                loss.get("step") == number and loss.get("case_id") == case.get("case_id") and
                type(loss.get("loss")) in (float, int) and math.isfinite(loss["loss"]),
                "missing or malformed scheduled loss")
    return report


def verify_control_set(paths: dict[str, Path]) -> dict:
    require(set(paths) == set(ARMS), "exact candidate, sham, and corrupt runs required")
    require(len({path.resolve(strict=True) for path in paths.values()}) == len(ARMS),
            "control arms must use separate run directories")
    reports = {arm: load_receipt(paths[arm], arm) for arm in ARMS}
    candidate = reports["candidate"]
    require(candidate["instruction_mode"] == "neutral",
            "matched-control verdict requires neutral (unprompted) instruction")
    for arm in ARMS[1:]:
        for field in MATCHED_FIELDS:
            require(reports[arm].get(field) == candidate.get(field),
                    f"{arm} unmatched on {field}")
    return {
        "status": "MATCHED_STATIC_RECEIPTS_ONLY",
        "identity_id": candidate["identity_id"],
        "arms": list(ARMS),
        "steps_per_arm": candidate["steps"],
        "corrupt_label_strength": "WEAK_ROTATED_WITHIN_ROLE_TARGET",
        "training_receipt_consistency": True,
        "model_inference_executed": False,
        "behavioral_improvement_verified": False,
        "coding_retention_verified": False,
        "report_sha256": {arm: hashlib.sha256(
            (paths[arm] / "report.json").read_bytes()).hexdigest() for arm in ARMS},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arm in ARMS:
        parser.add_argument(f"--{arm}", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_control_set({arm: getattr(args, arm) for arm in ARMS}),
                         indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"personality controls not matched: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
