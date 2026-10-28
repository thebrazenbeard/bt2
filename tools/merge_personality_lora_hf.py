"""Merge a pinned, experimental BT2 personality LoRA into a NEW HF directory.

Only candidate adapters are eligible. This step does not quantize, install,
publish, activate, independently evaluate, or qualify a personality model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import time

from identity_coding_models import ROOT, require
from train_identity_lora_pilot import sha256_file
from train_personality_lora import (SCHEMA, CEILING, checked_checkout,
                                    require_isolated_output, verify_donor_metadata)


MERGE_SCHEMA = "BT2_LABYRINTH_PERSONALITY_MERGED_HF_V1"
MERGE_CEILING = "EXPERIMENTAL_MERGED_PERSONALITY_NOT_GGUF_NOT_QUALIFIED"


def _sha(value: object, label: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None,
            f"{label} must be a lowercase sha256 digest")
    return value


def _commit(value: object, label: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{40}", value) is not None,
            f"{label} must be an exact lowercase Git commit")
    return value


def validate_merge_inputs(run_dir: Path, output_dir: Path, labyrinth_dir: Path,
                          *, bt2_dir: Path = ROOT) -> dict:
    """Check source, donor, adapter and output custody before importing torch."""
    require(not run_dir.is_symlink(), "run directory must not be a symlink")
    run = run_dir.resolve(strict=True)
    require(run.is_dir(), "run path must be an existing directory")
    report_file = run / "report.json"
    require(report_file.is_file() and not report_file.is_symlink(), "missing/nonregular run report")
    report = json.loads(report_file.read_text(encoding="utf-8"))
    require(isinstance(report, dict) and report.get("schema_version") == SCHEMA,
            "unexpected personality training report schema")
    require(report.get("claim_ceiling") == CEILING, "unexpected personality evidence ceiling")
    require(report.get("arm") == "candidate", "only a trained candidate adapter may be merged")
    require(report.get("frozen_parameters_and_buffers_verified_unchanged") is True,
            "frozen parameters and buffers lack verified unchanged state")
    require(report.get("qualified") is False and report.get("installed") is False and
            report.get("behavioral_improvement_verified") is False,
            "personality report must preserve unqualified, non-installed scope")
    identity = report.get("identity_id")
    require(isinstance(identity, str) and re.fullmatch(r"[a-z]+", identity) is not None,
            "invalid personality identity")
    bt2_commit = _commit(report.get("bt2_source_commit"), "BT2 source")
    labyrinth_commit = _commit(report.get("labyrinth_scheduler_commit"), "Labyrinth source")
    donor_sha = _sha(report.get("base_model_sha256"), "HF donor")
    adapter_sha = _sha(report.get("adapter_safetensors_sha256"), "persona adapter")
    dataset_sha = _sha(report.get("personality_dataset_sha256"), "persona dataset")
    _sha(report.get("persona_instruction_sha256"), "persona instruction")
    train_before = _sha(report.get("trainable_tensor_sha256_before"), "initial LoRA state")
    train_after = _sha(report.get("trainable_tensor_sha256_after"), "trained LoRA state")
    require(train_before != train_after, "candidate LoRA state did not change during training")
    _sha(report.get("frozen_parameter_sha256_unchanged"), "frozen parameter state")
    _sha(report.get("persistent_buffer_sha256_unchanged"), "frozen buffer state")
    require(report.get("steps") in (2, 4) and isinstance(report.get("schedule"), list) and
            len(report["schedule"]) == report["steps"], "invalid persona schedule receipt")

    bt2 = checked_checkout(bt2_dir, bt2_commit, "tools/train_personality_lora.py")
    labyrinth = checked_checkout(labyrinth_dir, labyrinth_commit, "labyrinth/curriculum.py")
    dataset = bt2 / "coding_models/personality/cases" / f"{identity}.json"
    require(dataset.is_file() and not dataset.is_symlink(), "missing pinned persona dataset")
    require(sha256_file(dataset) == dataset_sha, "persona source dataset differs from receipt")

    donor = Path(report.get("base_model_dir", "")).resolve(strict=True)
    require(donor.is_dir(), "base donor must be an existing directory")
    donor_file = donor / "model.safetensors"
    require(donor_file.is_file() and not donor_file.is_symlink(), "missing/nonregular donor weights")
    require(sha256_file(donor_file) == donor_sha, "HF donor changed since persona training")
    donor_meta = verify_donor_metadata(donor, report.get("base_metadata_sha256"))
    adapter = run / "adapter"
    require(adapter.is_dir() and not adapter.is_symlink(), "missing/nonregular adapter directory")
    adapter_file = adapter / "adapter_model.safetensors"
    require(adapter_file.is_file() and not adapter_file.is_symlink(), "missing/nonregular adapter weights")
    require(sha256_file(adapter_file) == adapter_sha, "persona adapter bytes differ from receipt")

    require(not output_dir.exists() and not output_dir.is_symlink(),
            "merge destination must be an entirely new directory")
    require(output_dir.parent.is_dir(), "merge destination parent does not exist")
    output = output_dir.resolve(strict=False)
    require_isolated_output(output, run, donor, bt2, labyrinth)
    return {
        "report": report, "report_file": report_file, "run": run,
        "base_dir": donor, "adapter_dir": adapter, "output_dir": output,
        "bt2_dir": bt2, "labyrinth_dir": labyrinth,
        "dataset_file": dataset, "report_sha256": sha256_file(report_file),
        "donor_meta_sha256": donor_meta,
    }


def merge(args) -> dict:
    require(1 <= args.threads <= 4, "CPU threads must be in 1..4")
    context = validate_merge_inputs(
        Path(args.run_dir), Path(args.output_dir), Path(args.labyrinth_dir),
    )
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(args.threads)
    begun = time.monotonic()
    base = AutoModelForCausalLM.from_pretrained(
        str(context["base_dir"]), local_files_only=True,
        dtype=torch.float32, low_cpu_mem_usage=True,
    )
    adapted = PeftModel.from_pretrained(
        base, str(context["adapter_dir"]), is_trainable=False,
    )
    merged = adapted.merge_and_unload(safe_merge=True)
    tokenizer = AutoTokenizer.from_pretrained(
        str(context["base_dir"]), local_files_only=True,
    )
    # A fresh exclusive directory is acquired only after the expensive merge.
    output = context["output_dir"]
    output.mkdir()
    merged.save_pretrained(str(output), safe_serialization=True, max_shard_size="3GB")
    tokenizer.save_pretrained(str(output))
    weights = sorted(output.glob("*.safetensors"))
    require(bool(weights), "merged personality checkpoint has no safetensors")
    metadata = [name for name in ("config.json", "tokenizer.json", "tokenizer_config.json")
                if (output / name).is_file()]
    require(set(metadata) == {"config.json", "tokenizer.json", "tokenizer_config.json"},
            "merged checkpoint is missing required tokenizer/config files")
    require(sha256_file(context["base_dir"] / "model.safetensors") ==
            context["report"]["base_model_sha256"],
            "HF donor changed during personality merge")
    require(sha256_file(context["adapter_dir"] / "adapter_model.safetensors") ==
            context["report"]["adapter_safetensors_sha256"],
            "persona adapter changed during merge")
    require(sha256_file(context["report_file"]) == context["report_sha256"],
            "personality training report changed during merge")
    require(sha256_file(context["dataset_file"]) ==
            context["report"]["personality_dataset_sha256"],
            "persona dataset changed during merge")
    for name, digest in context["donor_meta_sha256"].items():
        require(sha256_file(context["base_dir"] / name) == digest,
                f"donor {name} changed during merge")
    checked_checkout(context["bt2_dir"], context["report"]["bt2_source_commit"],
                     "tools/train_personality_lora.py")
    checked_checkout(context["labyrinth_dir"],
                     context["report"]["labyrinth_scheduler_commit"],
                     "labyrinth/curriculum.py")
    receipt = {
        "schema_version": MERGE_SCHEMA,
        "claim_ceiling": MERGE_CEILING,
        "identity_id": context["report"]["identity_id"],
        "bt2_source_commit": context["report"]["bt2_source_commit"],
        "labyrinth_scheduler_commit": context["report"]["labyrinth_scheduler_commit"],
        "personality_dataset_sha256": context["report"]["personality_dataset_sha256"],
        "persona_instruction_sha256": context["report"]["persona_instruction_sha256"],
        "training_report_sha256": context["report_sha256"],
        "base_sha256": context["report"]["base_model_sha256"],
        "base_metadata_sha256": context["donor_meta_sha256"],
        "adapter_sha256": context["report"]["adapter_safetensors_sha256"],
        "safetensors": {file.name: sha256_file(file) for file in weights},
        "metadata_sha256": {name: sha256_file(output / name) for name in metadata},
        "merge_method": "PEFT merge_and_unload(safe_merge=True)",
        "elapsed_seconds": round(time.monotonic() - begun, 3),
        "quality_qualified": False,
        "installed": False,
        "gguf_converted": False,
    }
    (output / "BT2_PERSONA_MERGE_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--labyrinth-dir", required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    try:
        print(json.dumps(merge(args), indent=2), flush=True)
        return 0
    except (OSError, ValueError, RuntimeError, ImportError, KeyError,
            subprocess.CalledProcessError, json.JSONDecodeError) as error:
        parser.exit(1, f"personality HF merge failed: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
