"""Sequential isolated Labyrinth-scheduled persona LoRA -> Q8_0 GGUF batch.

No shared Ollama writes, no release publication, no activation, no quality claim.
Source and donor checkouts are pinned; each identity has a new directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from build_identity_gguf_batch import (
    exclusive_batch_lock, require_disk_headroom, run_stage, sha256_file,
)
from identity_coding_models import load_models, require
from train_personality_lora import SCHEMA as TRAIN_SCHEMA, CEILING as TRAIN_CEILING, checked_checkout


SCHEMA = "BT2_LABYRINTH_PERSONA_GGUF_BATCH_RECEIPT_V1"
CEILING = "EXPERIMENTAL_PERSONA_WEIGHT_BUILD_AND_SIMPLE_SMOKE_NOT_QUALIFIED"


def inputs(args) -> dict:
    require(1 <= args.threads <= 4 and args.steps in (2, 4, 8) and
            768 <= args.max_length <= 2048, "invalid bounded training parameters")
    require(16 <= args.min_free_gib <= 128, "invalid free-space reserve")
    require(len(args.identities) == len(set(args.identities)) and
            bool(args.identities) and set(args.identities) <= set(load_models()),
            "invalid identity roster")
    source = checked_checkout(Path(args.bt2_dir), args.source_commit,
                              "tools/build_personality_gguf_batch.py")
    labyrinth = checked_checkout(Path(args.labyrinth_dir), args.labyrinth_commit,
                                 "labyrinth/curriculum.py")
    base = Path(args.base_dir).resolve(strict=True)
    files = ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")
    require(all((base / name).is_file() and not (base / name).is_symlink() for name in files),
            "incomplete/nonregular local donor")
    digests = {name: sha256_file(base / name) for name in files}
    require(digests["model.safetensors"] == args.base_sha256,
            "HF donor digest mismatch")
    converter_dir = checked_checkout(Path(args.llama_cpp_dir), args.converter_commit,
                                     "convert_hf_to_gguf.py")
    converter = converter_dir / "convert_hf_to_gguf.py"
    cli = Path(args.llama_cli).resolve(strict=True)
    require(cli.is_file(), "llama-cli executable missing")
    output = Path(args.output_root).resolve(strict=False)
    require(output.parent.is_dir(), "output parent missing")
    for protected in (source, labyrinth, base, converter_dir):
        require(output != protected and protected not in output.parents and
                output not in protected.parents, "output overlaps immutable inputs")
    for identity in args.identities:
        require(not (output / identity).exists(), f"refusing to overwrite {identity}")
    return {"source": source, "labyrinth": labyrinth, "base": base,
            "converter": converter, "cli": cli, "output": output,
            "base_digests": digests, "converter_sha": sha256_file(converter),
            "cli_sha": sha256_file(cli)}


def check_input_digests(ctx: dict) -> None:
    for name, expected in ctx["base_digests"].items():
        require(sha256_file(ctx["base"] / name) == expected,
                f"HF donor input changed: {name}")
    require(sha256_file(ctx["converter"]) == ctx["converter_sha"],
            "converter changed during batch")
    require(sha256_file(ctx["cli"]) == ctx["cli_sha"],
            "llama-cli changed during batch")


def checked_adapter_config(run: Path, training: dict, merge: dict | None = None) -> str:
    """Pin exact PEFT adapter settings across disk, training and merge custody."""
    adapter = run / "adapter"
    require(adapter.is_dir() and not adapter.is_symlink(),
            "missing/nonregular persona adapter directory")
    path = adapter / "adapter_config.json"
    require(path.is_file() and not path.is_symlink(),
            "missing/nonregular persona adapter configuration")
    claimed = training.get("adapter_config_sha256")
    require(isinstance(claimed, str) and re.fullmatch(r"[a-f0-9]{64}", claimed) is not None,
            "missing/invalid training adapter_config_sha256 receipt")
    require(sha256_file(path) == claimed,
            "persona adapter configuration differs from training receipt")
    if merge is not None:
        require(merge.get("adapter_config_sha256") == claimed,
                "missing/mismatched merge adapter_config_sha256 receipt")
    return claimed


def build(identity: str, args, ctx: dict) -> dict:
    require_disk_headroom(ctx["output"], args.min_free_gib, 10)
    check_input_digests(ctx)
    dest = ctx["output"] / identity
    dest.mkdir()  # must be new
    (dest / "gguf").mkdir()
    run, merged = dest / "run", dest / "merged-hf"
    gguf = dest / "gguf" / f"bt2-{identity}-persona-qwen25coder-cpu-lora-q8_0.gguf"
    python = sys.executable
    common = ["--threads", str(args.threads)]
    run_stage(f"persona:{identity}:train", [
        python, str(ctx["source"] / "tools/train_personality_lora.py"), "train",
        "--identity", identity, "--source-commit", args.source_commit,
        "--labyrinth-dir", str(ctx["labyrinth"]),
        "--labyrinth-commit", args.labyrinth_commit,
        "--base-dir", str(ctx["base"]), "--base-sha256", args.base_sha256,
        "--run-dir", str(run), "--arm", "candidate", "--steps", str(args.steps),
        "--max-length", str(args.max_length), "--seed", str(args.seed), *common,
    ], dest / "train.log", ctx["source"], 1800)
    run_stage(f"persona:{identity}:reload", [
        python, str(ctx["source"] / "tools/train_personality_lora.py"),
        "verify-reload", "--run-dir", str(run), *common,
    ], dest / "reload.log", ctx["source"], 360)
    # Require newly produced trainer evidence before an expensive merge/conversion.
    report = json.loads((run / "report.json").read_text(encoding="utf-8"))
    config_sha = checked_adapter_config(run, report)
    require_disk_headroom(ctx["output"], args.min_free_gib, 9)
    run_stage(f"persona:{identity}:merge", [
        python, str(ctx["source"] / "tools/merge_personality_lora_hf.py"),
        "--run-dir", str(run), "--output-dir", str(merged),
        "--labyrinth-dir", str(ctx["labyrinth"]), *common,
    ], dest / "merge.log", ctx["source"], 900)
    merge = json.loads((merged / "BT2_PERSONA_MERGE_RECEIPT.json").read_text(encoding="utf-8"))
    require(checked_adapter_config(run, report, merge) == config_sha,
            "adapter configuration changed during merge")
    require_disk_headroom(ctx["output"], args.min_free_gib, 3)
    run_stage(f"persona:{identity}:convert", [
        python, str(ctx["converter"]), str(merged), "--outfile", str(gguf),
        "--outtype", "q8_0", "--model-name", f"BT2-{identity.title()}-Persona-Experiment",
    ], dest / "convert.log", ctx["source"], 600)
    require(gguf.is_file() and gguf.stat().st_size > 1_000_000_000,
            "GGUF conversion did not produce expected byte scale")
    require_disk_headroom(ctx["output"], args.min_free_gib, 0)
    run_stage(f"persona:{identity}:llama-cli-smoke", [
        str(ctx["cli"]), "-m", str(gguf), "-p",
        "Write a Python function named add that returns a+b. Output code only.",
        "-n", "60", "-c", "1024", "-t", str(args.threads), "-ngl", "0",
        "--temp", "0", "--no-display-prompt", "--single-turn", "--simple-io",
    ], dest / "smoke.log", ctx["source"], 240)
    smoke = (dest / "smoke.log").read_text(encoding="utf-8", errors="replace")
    require("ftype      : Q8_0" in smoke and
            re.search(r"def\s+add\s*\([^)]*\).*?return\s+a\s*\+\s*b", smoke, re.S),
            "llama-cli smoke lacks loaded Q8_0 and simple Python add output")
    require(checked_adapter_config(run, report, merge) == config_sha,
            "adapter configuration changed during conversion/smoke")
    require(report["schema_version"] == TRAIN_SCHEMA and report["claim_ceiling"] == TRAIN_CEILING
            and report["identity_id"] == identity and report["arm"] == "candidate"
            and report["bt2_source_commit"] == args.source_commit
            and report["labyrinth_scheduler_commit"] == args.labyrinth_commit
            and report["base_model_sha256"] == args.base_sha256
            and report["trainable_tensor_sha256_before"] != report["trainable_tensor_sha256_after"]
            and report.get("frozen_parameters_and_buffers_verified_unchanged") is True,
            "persona training evidence mismatch")
    train_sha = sha256_file(run / "report.json")
    require(merge["identity_id"] == identity and merge["base_sha256"] == args.base_sha256
            and merge["adapter_sha256"] == report["adapter_safetensors_sha256"]
            and merge["training_report_sha256"] == train_sha,
            "persona merge source/adapter/report mismatch")
    for name, expected in merge["safetensors"].items():
        require(Path(name).name == name and sha256_file(merged / name) == expected,
                "merged HF shard checksum mismatch")
    check_input_digests(ctx)
    receipt = {
        "schema_version": SCHEMA, "identity_id": identity,
        "claim_ceiling": CEILING, "source_commit": args.source_commit,
        "labyrinth_commit": args.labyrinth_commit,
        "base_sha256": args.base_sha256, "base_file_sha256": ctx["base_digests"],
        "training_report_sha256": train_sha,
        "merged_receipt_sha256": sha256_file(merged / "BT2_PERSONA_MERGE_RECEIPT.json"),
        "adapter_sha256": report["adapter_safetensors_sha256"],
        "adapter_config_sha256": config_sha,
        "frozen_state_verified": True, "steps": args.steps,
        "converter_sha256": ctx["converter_sha"], "llama_cli_sha256": ctx["cli_sha"],
        "gguf_filename": gguf.name, "gguf_bytes": gguf.stat().st_size,
        "gguf_sha256": sha256_file(gguf),
        "smoke_kind": "Q8_0_LOADED_AND_SIMPLE_CODE_ONLY_NOT_PERSONALITY_EVAL",
        "installed": False, "qualified": False, "personality_effect_verified": False,
    }
    hashes = {json.loads(p.read_text(encoding="utf-8"))["gguf_sha256"]
              for p in ctx["output"].glob("*/receipt.json") if p.parent != dest}
    require(receipt["gguf_sha256"] not in hashes, "duplicate persona GGUF digest")
    (dest / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n",
                                        encoding="utf-8")
    print(f"BUILT persona {identity} sha256={receipt['gguf_sha256']}", flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bt2-dir", "source-commit", "labyrinth-dir", "labyrinth-commit",
                 "base-dir", "base-sha256", "llama-cpp-dir", "converter-commit",
                 "llama-cli", "output-root"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--identities", nargs="+", required=True)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--seed", type=int, default=74413)
    parser.add_argument("--min-free-gib", type=int, default=20)
    args = parser.parse_args()
    try:
        ctx = inputs(args)
        ctx["output"].mkdir(exist_ok=True)
        with exclusive_batch_lock(ctx["output"]):
            for identity in args.identities:
                build(identity, args, ctx)
        print(f"COMPLETE experimental persona GGUFs={len(args.identities)}; NOT qualified/installed")
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"persona batch stopped: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
