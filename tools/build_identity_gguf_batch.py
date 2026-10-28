"""Serial, isolated, unqualified BT2 CPU LoRA -> merged HF -> Q8_0 GGUF batch.

This orchestration intentionally does not install models, call Ollama, publish
artifacts, or assert quality/identity qualification. Each identity acquires a
fresh dedicated directory; pre-existing output directories are never replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


IDENTITIES = (
    "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "thirteen", "masa", "mune", "hephaestus",
)
CLAIM_CEILING = "EXPERIMENTAL_BUILD_AND_SMOKE_NOT_QUALIFIED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_inputs(args: argparse.Namespace) -> dict:
    workspace = Path(args.work_root).resolve(strict=True)
    source = workspace / "bt2"
    python = workspace / "venv/Scripts/python.exe"
    base = workspace / "hf_base"
    converter = workspace / "llama.cpp/convert_hf_to_gguf.py"
    llama_cli = Path(args.llama_cli).resolve(strict=True)
    for needed in (source / "tools/train_identity_lora_pilot.py",
                   source / "tools/merge_identity_lora_hf.py", python,
                   base / "model.safetensors", converter, llama_cli):
        require(needed.is_file(), f"missing required local file: {needed}")
    require(sha256_file(base / "model.safetensors") == args.base_sha256,
            "pinned HF base digest mismatch")
    require(len(args.source_commit) == 40 and
            all(ch in "0123456789abcdef" for ch in args.source_commit),
            "exact lowercase 40-character source Git commit required")
    git_head = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    require(git_head == args.source_commit, "checked-out BT2 source commit mismatch")
    git_dirty = subprocess.run(["git", "-C", str(source), "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout.strip()
    require(not git_dirty, "BT2 source checkout is not clean")
    require(1 <= args.steps <= 4 and 1 <= args.threads <= 4,
            "bounded steps and CPU threads required")
    require(256 <= args.max_length <= 1024, "invalid token length bound")
    require(len(set(args.identities)) == len(args.identities), "duplicate identities")
    require(bool(args.identities) and all(i in IDENTITIES for i in args.identities),
            "batch accepts only the twelve not-yet-built identities")
    output = Path(args.output_root).resolve(strict=False)
    require(output != workspace and output not in workspace.parents and
            workspace not in output.parents and output != base and
            base not in output.parents, "output overlaps immutable source workspace")
    require(output.parent.is_dir(), "output-root parent directory must exist")
    for identity in args.identities:
        require(not (output / identity).exists(),
                f"identity output already exists; never overwrite: {identity}")
    return {"workspace": workspace, "source": source, "python": python,
            "base": base, "converter": converter, "llama_cli": llama_cli,
            "output": output}


def run_stage(stage: str, command: list[str], log: Path, cwd: Path, timeout: int) -> None:
    started = time.monotonic()
    print(f"BEGIN {stage} log={log}", flush=True)
    with log.open("x", encoding="utf-8") as stream:
        try:
            result = subprocess.run(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                    stdout=stream, stderr=subprocess.STDOUT,
                                    check=False, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"{stage} exceeded {timeout}s; review {log}") from exc
    require(result.returncode == 0,
            f"{stage} failed exit={result.returncode}; review {log}")
    print(f"PASS {stage} seconds={time.monotonic()-started:.1f}", flush=True)


def build_one(identity: str, args: argparse.Namespace, ctx: dict) -> dict:
    free = shutil.disk_usage(ctx["output"].parent).free
    require(free >= args.min_free_gib * (1024 ** 3),
            f"free disk below {args.min_free_gib} GiB safety threshold")
    dest = ctx["output"] / identity
    dest.mkdir()  # no exist_ok: never overwrite partial experiments
    run = dest / "run"
    merged = dest / "merged-hf"
    gguf_dir = dest / "gguf"
    gguf_dir.mkdir()
    gguf = gguf_dir / f"bt2-{identity}-qwen25coder-cpu-lora-q8_0.gguf"
    py = str(ctx["python"])
    common = ["--threads", str(args.threads)]
    run_stage(f"{identity}:train", [
        py, str(ctx["source"] / "tools/train_identity_lora_pilot.py"), "train",
        "--identity", identity, "--base-dir", str(ctx["base"]),
        "--base-sha256", args.base_sha256, "--run-dir", str(run),
        "--source-commit", args.source_commit, "--arm", "candidate",
        "--steps", str(args.steps), "--max-length", str(args.max_length),
        "--seed", str(args.seed), *common,
    ], dest / "train.log", ctx["source"], 900)
    run_stage(f"{identity}:verify-reload", [
        py, str(ctx["source"] / "tools/train_identity_lora_pilot.py"),
        "verify-reload", "--run-dir", str(run), *common,
    ], dest / "reload.log", ctx["source"], 360)
    run_stage(f"{identity}:merge-hf", [
        py, str(ctx["source"] / "tools/merge_identity_lora_hf.py"),
        "--run-dir", str(run), "--output-dir", str(merged), *common,
    ], dest / "merge.log", ctx["source"], 600)
    run_stage(f"{identity}:convert-gguf", [
        py, str(ctx["converter"]), str(merged),
        "--outfile", str(gguf), "--outtype", "q8_0",
        "--model-name", f"BT2-{identity.title()}-Coder-Experiment",
    ], dest / "convert.log", ctx["source"], 420)
    require(gguf.stat().st_size > 1_000_000_000,
            "unexpectedly small Q8_0 GGUF; conversion not verified")
    # An actual separate-process loader and generation probe, not a role exam.
    run_stage(f"{identity}:llama-cli-smoke", [
        str(ctx["llama_cli"]), "-m", str(gguf), "-p",
        "Write a Python function named add that returns a+b. Output code only.",
        "-n", "60", "-c", "1024", "-t", str(args.threads), "-ngl", "0",
        "--temp", "0", "--no-display-prompt", "--single-turn", "--simple-io",
    ], dest / "smoke.log", ctx["source"], 240)
    report = json.loads((run / "report.json").read_text(encoding="utf-8"))
    merge = json.loads((merged / "BT2_MERGE_RECEIPT.json").read_text(encoding="utf-8"))
    require(report["identity_id"] == identity and report["arm"] == "candidate" and
            report["claim_ceiling"] == "MECHANISM_ONLY_UNQUALIFIED",
            "training report identity/evidence mismatch")
    require(merge["identity_id"] == identity and
            merge["adapter_sha256"] == report["adapter_safetensors_sha256"],
            "HF merge identity/adapter mismatch")
    receipt = {
        "schema_version": "BT2_IDENTITY_GGUF_BATCH_RECEIPT_V1",
        "identity_id": identity,
        "claim_ceiling": CLAIM_CEILING,
        "training_report_sha256": sha256_file(run / "report.json"),
        "merged_hf_receipt_sha256": sha256_file(merged / "BT2_MERGE_RECEIPT.json"),
        "adapter_sha256": report["adapter_safetensors_sha256"],
        "tensor_sha256_before": report["trainable_tensor_sha256_before"],
        "tensor_sha256_after": report["trainable_tensor_sha256_after"],
        "training_steps": args.steps,
        "base_sha256": args.base_sha256,
        "source_commit": args.source_commit,
        "gguf_name": gguf.name,
        "gguf_bytes": gguf.stat().st_size,
        "gguf_sha256": sha256_file(gguf),
        "smoke_exit_code": 0,
        "smoke_kind": "GENERATION_PROCESS_EXIT_ONLY_NOT_CORRECTNESS",
        "installed": False,
        "qualified": False,
    }
    (dest / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n",
                                        encoding="utf-8")
    print(f"BUILT {identity} gguf_sha256={receipt['gguf_sha256']}", flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--identities", nargs="+", required=True)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--seed", type=int, default=74413)
    parser.add_argument("--min-free-gib", type=int, default=20)
    args = parser.parse_args()
    try:
        require(16 <= args.min_free_gib <= 128, "invalid disk-space guard")
        ctx = inspect_inputs(args)
        ctx["output"].mkdir(exist_ok=True)
        for identity in args.identities:
            build_one(identity, args, ctx)
        print(f"COMPLETE built={len(args.identities)}; models remain unqualified/uninstalled",
              flush=True)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"BT2 identity GGUF batch stopped: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
