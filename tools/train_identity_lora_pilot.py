"""Bounded CPU PEFT LoRA mechanism pilot for BT2 coding identities.

This is NOT a qualified trainer or proof of skill improvement. It uses the
existing unqualified train split, saves a separate adapter, and has an
independent fresh-process reload command. Large model files stay outside Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import time

from identity_coding_models import ROOT, load_models, require
from identity_sft_candidates import validate_cases


REPORT_VERSION = "BT2_IDENTITY_LORA_CPU_PILOT_V1"
TRAINING_CEILING = "MECHANISM_ONLY_UNQUALIFIED"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def preflight(identity: str, base_dir: Path, base_sha256: str, run_dir: Path) -> dict:
    models = load_models()
    require(identity in models, f"unknown BT2 identity {identity}")
    candidates = validate_cases()[identity]["cases"]
    require(len([c for c in candidates if c["split"] == "train"]) == 4,
            "unexpected training split")
    base_dir = base_dir.resolve(strict=True)
    require(base_dir.is_dir(), "HF base must be a local directory")
    required = ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")
    for filename in required:
        path = base_dir / filename
        require(path.is_file() and not path.is_symlink(), f"missing/nonregular HF file: {filename}")
    require(len(base_sha256) == 64 and all(c in "0123456789abcdef" for c in base_sha256.lower()),
            "expected model.safetensors SHA-256 required")
    digest = sha256_file(base_dir / "model.safetensors")
    require(digest == base_sha256.lower(), "HF base safetensors digest mismatch")
    require(not run_dir.exists() and not run_dir.is_symlink(), "run directory already exists")
    require(run_dir.parent.is_dir(), "run parent directory missing")
    dataset_path = ROOT / "coding_models/training/cases" / f"{identity}.json"
    return {
        "identity_id": identity,
        "role": models[identity]["role"],
        "profile": models[identity],
        "cases": candidates,
        "source_entrypoint": models[identity]["source_entrypoint"],
        "base_dir": base_dir,
        "base_sha256": digest,
        "candidate_dataset_sha256": sha256_file(dataset_path),
        "model_bytes": (base_dir / "model.safetensors").stat().st_size,
    }


def system_instruction(model: dict) -> str:
    return (
        f"Act as an ephemeral BT2 coding specialist configured for {model['display_name']}. "
        f"Role: {model['role']}. Objective: {model['objective']} "
        "Provide concrete, source-bound coding and review actions. Distinguish "
        "observation from inference; never invent tests, authority, runtime "
        "currentness, installation or protected effects."
    )


def make_training_example(tokenizer, model: dict, case: dict, response: str, max_length: int):
    prompt = tokenizer.apply_chat_template(
        [{"role": "system", "content": system_instruction(model)},
         {"role": "user", "content": case["task"]}],
        tokenize=False, add_generation_prompt=True,
    )
    prefix = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    target = tokenizer(response + tokenizer.eos_token, add_special_tokens=False)["input_ids"]
    require(bool(target), f"empty target for {case['id']}")
    require(len(prefix) + len(target) <= max_length,
            f"{case['id']}: {len(prefix) + len(target)} tokens exceeds max_length={max_length}; "
            "do not silently truncate supervised tokens")
    ids = prefix + target
    labels = [-100] * len(prefix) + target
    return ids, labels


def trainable_digest(model, torch) -> str:
    digest = hashlib.sha256()
    count = 0
    for name, parameter in sorted(model.named_parameters()):
        if not parameter.requires_grad:
            continue
        count += 1
        meta = json.dumps([name, list(parameter.shape), str(parameter.dtype)], separators=(",", ":"))
        data = parameter.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
        digest.update(meta.encode() + b"\0" + data)
    require(count > 0, "no trainable LoRA tensors")
    return digest.hexdigest()


def training_run(args) -> dict:
    require(args.device == "cpu", "V1 pilot is CPU-only; no unqualified CUDA fallback")
    require(1 <= args.steps <= 4, "steps must be within 1..4")
    require(256 <= args.max_length <= 1024, "max_length must be within 256..1024")
    require(1 <= args.threads <= 4, "CPU threads must be within 1..4")
    require(args.arm in ("candidate", "sham", "corrupt"), "invalid arm")
    run_dir = Path(args.run_dir).resolve(strict=False)
    evidence = preflight(args.identity, Path(args.base_dir), args.base_sha256, run_dir)

    import torch
    import transformers
    import peft
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, TaskType, get_peft_model

    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    started = time.monotonic()

    tokenizer = AutoTokenizer.from_pretrained(str(evidence["base_dir"]), local_files_only=True)
    base = AutoModelForCausalLM.from_pretrained(
        str(evidence["base_dir"]), local_files_only=True, dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    base.config.use_cache = False
    model = get_peft_model(base, LoraConfig(
        r=4, lora_alpha=8, lora_dropout=0.0, bias="none",
        task_type=TaskType.CAUSAL_LM, target_modules=["q_proj", "v_proj"],
    ))
    model.train()
    before = trainable_digest(model, torch)
    train = [case for case in evidence["cases"] if case["split"] == "train"]
    responses = [case["ideal_response"] for case in train]
    if args.arm == "corrupt":
        responses = responses[1:] + responses[:1]
    lr = 0.0 if args.arm == "sham" else 0.0002
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    losses = []
    for step in range(args.steps):
        case = train[step]
        ids, labels = make_training_example(
            tokenizer, evidence["profile"], case, responses[step], args.max_length,
        )
        input_tensor = torch.tensor([ids], dtype=torch.long)
        label_tensor = torch.tensor([labels], dtype=torch.long)
        result = model(input_ids=input_tensor, labels=label_tensor)
        loss = result.loss
        require(bool(torch.isfinite(loss).item()), "nonfinite training loss")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            [p for p in model.parameters() if p.requires_grad], 1.0,
            error_if_nonfinite=True,
        )
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        losses.append({"case_id": case["id"], "loss": float(loss.detach().cpu())})
        print(f"step {step+1}/{args.steps} case={case['id']} loss={losses[-1]['loss']:.6f}", flush=True)
    after = trainable_digest(model, torch)
    require((after != before) == (args.arm != "sham"),
            "unexpected trained/sham adapter tensor-change state")

    # The output directory is acquired only after all training checks pass.
    run_dir.mkdir()
    adapter_dir = run_dir / "adapter"
    model.save_pretrained(str(adapter_dir), safe_serialization=True)
    saved = adapter_dir / "adapter_model.safetensors"
    require(saved.is_file(), "PEFT adapter save did not produce safetensors")
    report = {
        "schema_version": REPORT_VERSION,
        "claim_ceiling": TRAINING_CEILING,
        "identity_id": args.identity,
        "arm": args.arm,
        "source_entrypoint": evidence["source_entrypoint"],
        "base_model_dir": str(evidence["base_dir"]),
        "base_model_sha256": evidence["base_sha256"],
        "base_model_bytes": evidence["model_bytes"],
        "candidate_dataset_sha256": evidence["candidate_dataset_sha256"],
        "source_commit": args.source_commit,
        "seed": args.seed,
        "steps": args.steps,
        "max_length": args.max_length,
        "device": "cpu",
        "threads": args.threads,
        "learning_rate": lr,
        "trainable_tensor_sha256_before": before,
        "trainable_tensor_sha256_after": after,
        "adapter_safetensors_sha256": sha256_file(saved),
        "losses": losses,
        "duration_seconds": round(time.monotonic() - started, 3),
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__,
                     "peft": peft.__version__},
        "limitations": [
            "Unqualified synthetic examples, no independent code-competence evaluation",
            "No matched completed controls unless separate sham and corrupted arms are run",
            "No GGUF conversion, installation, production activation, or skill-improvement claim",
        ],
    }
    (run_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def verify_reload(args) -> dict:
    import torch
    from transformers import AutoModelForCausalLM
    from peft import PeftModel

    run = Path(args.run_dir).resolve(strict=True)
    report = json.loads((run / "report.json").read_text(encoding="utf-8"))
    require(report.get("schema_version") == REPORT_VERSION, "wrong report schema")
    base = Path(report["base_model_dir"])
    require(sha256_file(base / "model.safetensors") == report["base_model_sha256"],
            "base model changed since training")
    adapter_file = run / "adapter/adapter_model.safetensors"
    require(sha256_file(adapter_file) == report["adapter_safetensors_sha256"],
            "adapter bytes changed since training")
    torch.set_num_threads(min(4, max(1, args.threads)))
    model = AutoModelForCausalLM.from_pretrained(
        str(base), local_files_only=True, dtype=torch.float32, low_cpu_mem_usage=True,
    )
    peft_model = PeftModel.from_pretrained(model, str(run / "adapter"), is_trainable=True)
    reloaded = trainable_digest(peft_model, torch)
    require(reloaded == report["trainable_tensor_sha256_after"],
            "fresh-process numeric LoRA tensor digest mismatch")
    return {"identity_id": report["identity_id"], "arm": report["arm"],
            "reloaded_tensor_digest": reloaded, "status": "ADAPTER_TENSORS_RELOADED_EXACTLY",
            "competence_qualified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train", help="bounded CPU LoRA training arm")
    train.add_argument("--identity", required=True)
    train.add_argument("--base-dir", required=True)
    train.add_argument("--base-sha256", required=True)
    train.add_argument("--run-dir", required=True)
    train.add_argument("--source-commit", required=True)
    train.add_argument("--arm", choices=("candidate", "sham", "corrupt"), default="candidate")
    train.add_argument("--device", choices=("cpu",), default="cpu")
    train.add_argument("--steps", type=int, default=2)
    train.add_argument("--max-length", type=int, default=768)
    train.add_argument("--threads", type=int, default=2)
    train.add_argument("--seed", type=int, default=74413)
    reload_parser = sub.add_parser("verify-reload")
    reload_parser.add_argument("--run-dir", required=True)
    reload_parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    try:
        report = training_run(args) if args.command == "train" else verify_reload(args)
        print(json.dumps(report, indent=2), flush=True)
    except (OSError, ValueError, RuntimeError, ImportError, json.JSONDecodeError) as error:
        parser.exit(1, f"BT2 identity LoRA pilot failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
