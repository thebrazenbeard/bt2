"""Merge a verified experimental BT2 PEFT LoRA into a new local HF checkpoint.

No GGUF, Ollama installation, qualification, or automatic publication occurs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from train_identity_lora_pilot import REPORT_VERSION, sha256_file, require


def validate_merge_inputs(run_dir: Path, output_dir: Path) -> dict:
    run_dir = run_dir.resolve(strict=True)
    report_path = run_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema_version") == REPORT_VERSION, "unexpected training report schema")
    require(report.get("arm") == "candidate", "only a genuine candidate adapter may be merged")
    require(report.get("claim_ceiling") == "MECHANISM_ONLY_UNQUALIFIED",
            "unexpected claim ceiling")
    base_dir = Path(report["base_model_dir"]).resolve(strict=True)
    adapter_dir = (run_dir / "adapter").resolve(strict=True)
    require(base_dir.is_dir() and adapter_dir.is_dir(), "base or adapter missing")
    require(sha256_file(base_dir / "model.safetensors") == report["base_model_sha256"],
            "base model hash drift")
    require(sha256_file(adapter_dir / "adapter_model.safetensors") ==
            report["adapter_safetensors_sha256"], "adapter hash drift")
    require(not output_dir.exists() and not output_dir.is_symlink(),
            "output directory must be new")
    require(output_dir.parent.is_dir(), "output parent must exist")
    require(output_dir.resolve(strict=False) != base_dir and
            base_dir not in output_dir.resolve(strict=False).parents,
            "cannot merge into base checkpoint")
    return {"report": report, "base_dir": base_dir, "adapter_dir": adapter_dir}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    try:
        require(1 <= args.threads <= 4, "CPU threads must be 1..4")
        output = Path(args.output_dir).resolve(strict=False)
        inputs = validate_merge_inputs(Path(args.run_dir), output)
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.set_num_threads(args.threads)
        started = time.monotonic()
        base = AutoModelForCausalLM.from_pretrained(
            str(inputs["base_dir"]), local_files_only=True,
            dtype=torch.float32, low_cpu_mem_usage=True,
        )
        model = PeftModel.from_pretrained(base, str(inputs["adapter_dir"]),
                                           is_trainable=False)
        merged = model.merge_and_unload(safe_merge=True)
        tokenizer = AutoTokenizer.from_pretrained(
            str(inputs["base_dir"]), local_files_only=True,
        )
        output.mkdir()
        merged.save_pretrained(str(output), safe_serialization=True,
                               max_shard_size="3GB")
        tokenizer.save_pretrained(str(output))
        weight_files = sorted(output.glob("*.safetensors"))
        require(bool(weight_files), "merged HF model saved no safetensors")
        receipt = {
            "schema_version": "BT2_ONE_MERGED_HF_EXPERIMENT_V1",
            "identity_id": inputs["report"]["identity_id"],
            "claim_ceiling": "UNQUALIFIED_MERGED_EXPERIMENT_NOT_GGUF",
            "base_sha256": inputs["report"]["base_model_sha256"],
            "adapter_sha256": inputs["report"]["adapter_safetensors_sha256"],
            "training_report_sha256": sha256_file(Path(args.run_dir) / "report.json"),
            "safetensors": {p.name: sha256_file(p) for p in weight_files},
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "model_quality_qualified": False,
            "installed": False,
        }
        (output / "BT2_MERGE_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8",
        )
        print(json.dumps(receipt, indent=2), flush=True)
    except (OSError, ValueError, RuntimeError, ImportError, json.JSONDecodeError) as error:
        parser.exit(1, f"BT2 HF adapter merge failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
