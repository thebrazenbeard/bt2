"""Labyrinth-scheduled, BT2/PEFT-trained role-disposition LoRA experiment.

This is an opt-in *separate* training path, not Labyrinth's numerical train-hf.
No model download, installed-runtime mutation, auto-merge, or qualification.
All roles start from the same verified HF donor; output directories are new.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

from identity_coding_models import ROOT, load_models, require
from train_identity_lora_pilot import sha256_file, trainable_digest
from validate_personality_sft import CASE_ROOT, validate_persona_cases


SCHEMA = "BT2_LABYRINTH_SCHEDULED_PERSONALITY_LORA_V2"
CEILING = "SYNTHETIC_ROLE_DISPOSITION_WEIGHT_UPDATE_NOT_BEHAVIOR_QUALIFIED"
LEVELS = ("grounded", "adversarial")
REQUIRED_BASE = ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")
REQUIRED_METADATA = REQUIRED_BASE[1:]
OPTIONAL_METADATA = ("generation_config.json", "special_tokens_map.json",
                     "added_tokens.json", "vocab.json", "merges.txt",
                     "tokenizer.model")
KNOWN_METADATA = REQUIRED_METADATA + OPTIONAL_METADATA


def donor_metadata_digests(base: Path) -> dict[str, str]:
    """Pin required and optional HF model/tokenizer inputs, including absence."""
    digests = {}
    for name in KNOWN_METADATA:
        file = base / name
        if name in OPTIONAL_METADATA and not file.exists() and not file.is_symlink():
            continue
        require(file.is_file() and not file.is_symlink(),
                f"missing or unsafe HF donor metadata: {name}")
        digests[name] = sha256_file(file)
    return digests


def verify_donor_metadata(base: Path, expected: object) -> dict[str, str]:
    require(isinstance(expected, dict) and
            set(REQUIRED_METADATA) <= set(expected) <= set(KNOWN_METADATA),
            "missing or invalid training-time donor metadata receipt")
    require(all(isinstance(value, str) and len(value) == 64 and
                all(ch in "0123456789abcdef" for ch in value)
                for value in expected.values()),
            "invalid training-time donor metadata SHA-256")
    actual = donor_metadata_digests(base)
    require(actual == expected, "donor metadata changed since personality training")
    return actual


def checked_checkout(path: Path, expected: str, package_file: str) -> Path:
    require(len(expected) == 40 and all(ch in "0123456789abcdef" for ch in expected),
            "exact lowercase source commit required")
    repo = path.resolve(strict=True)
    require((repo / package_file).is_file() and not (repo / package_file).is_symlink(),
            "missing or unsafe pinned source file")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    require(head == expected, f"source checkout not at expected commit: {repo}")
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True, check=True).stdout.strip()
    require(not dirty, f"source checkout must be clean: {repo}")
    return repo


def build_schedule(cases: list[dict], *, labyrinth_dir: Path, seed: int, steps: int) -> list[dict]:
    """Use Labyrinth's ungraded scheduler; never fabricate scores or promotion."""
    require(steps in (2, 4), "pilot requires 2 or 4 optimizer steps")
    # This checkout was verified against its exact Git commit by preflight.
    sys.path.insert(0, str(labyrinth_dir))
    curriculum = importlib.import_module("labyrinth.curriculum")
    require(Path(curriculum.__file__).resolve() == (labyrinth_dir / "labyrinth/curriculum.py").resolve(),
            "imported Labyrinth does not match pinned source")
    result: dict[str, tuple] = {}
    for index, level in enumerate(LEVELS):
        ids = tuple(c["id"] for c in cases if c["split"] == "train" and c["level"] == level)
        require(len(ids) == 2, f"expected two training cases in {level}")
        spec = curriculum.CurriculumSpec(levels=(level,), window_size=2,
                                        distinct_challenges_required=2)
        result[level] = curriculum.schedule_training_cases(
            spec, {level: ids}, run_seed=seed + index * 1009, steps=steps // 2,
        )
    ordered = []
    for visit in range(steps // 2):
        for level in LEVELS:
            item = result[level][visit]
            ordered.append({"case_id": item.challenge_id, "level": item.level,
                            "labyrinth_case_seed": item.seed})
    require(len({x["case_id"] for x in ordered}) == steps,
            "experimental pilot must visit distinct training examples")
    return ordered


def persona_instruction(profile: dict, traits: list[dict]) -> str:
    behaviors = "; ".join(t["observable_behavior"] for t in traits)
    counterexamples = "; ".join(t["anti_pattern"] for t in traits)
    return (
        f"Act as an ephemeral BT2 coding specialist configured for {profile['display_name']}. "
        f"Role: {profile['role']}. Objective: {profile['objective']}. "
        f"Use these source-grounded *operational response tendencies*, not claims of "
        f"subjective emotion or identity continuity: {behaviors}. "
        f"Avoid the paired counterexamples: {counterexamples}. "
        "Respond concretely and in natural first-person working language. "
        "Distinguish facts, uncertainty, code source, authority and runtime effect; "
        "never fabricate test results, permission, personal experience or acceptance."
    )


def encode_case(tokenizer, instruction: str, case: dict, answer: str, max_length: int):
    prompt = tokenizer.apply_chat_template(
        [{"role": "system", "content": instruction},
         {"role": "user", "content": case["task"]}],
        tokenize=False, add_generation_prompt=True,
    )
    prefix = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    target = tokenizer(answer + tokenizer.eos_token, add_special_tokens=False)["input_ids"]
    require(bool(target) and len(prefix) + len(target) <= max_length,
            f"persona example {case['id']} exceeds {max_length} tokens or lacks target")
    return prefix + target, [-100] * len(prefix) + target


def require_isolated_output(output: Path, *protected: Path) -> None:
    for root in protected:
        require(output != root and root not in output.parents and output not in root.parents,
                "run path overlaps immutable donor or pinned source checkout")


def preflight(args) -> dict:
    require(args.device == "cpu", "this Qwen persona pilot only supports CPU")
    require(args.arm in ("candidate", "sham", "corrupt"), "unknown arm")
    require(args.steps in (2, 4) and 768 <= args.max_length <= 2048 and 1 <= args.threads <= 4,
            "unbounded persona training parameters")
    require(type(args.seed) is int and 0 <= args.seed <= 2**31 - 3000,
            "invalid deterministic seed")
    bt2 = checked_checkout(ROOT, args.source_commit, "tools/train_personality_lora.py")
    labyrinth = checked_checkout(Path(args.labyrinth_dir), args.labyrinth_commit,
                                 "labyrinth/curriculum.py")
    dossiers = validate_persona_cases()
    require(args.identity in dossiers, "unknown BT2 personality identity")
    dossier = dossiers[args.identity]
    base = Path(args.base_dir).resolve(strict=True)
    require(base.is_dir(), "HF donor must be a local directory")
    for name in REQUIRED_BASE:
        file = base / name
        require(file.is_file() and not file.is_symlink(), f"missing or unsafe HF donor file: {name}")
    require(sha256_file(base / "model.safetensors") == args.base_sha256,
            "pinned HF donor digest mismatch")
    base_metadata_sha256 = donor_metadata_digests(base)
    output = Path(args.run_dir).resolve(strict=False)
    require(not output.exists() and not output.is_symlink() and output.parent.is_dir(),
            "run directory must be new under existing parent")
    require_isolated_output(output, base, bt2, labyrinth)
    cases = dossier["cases"]
    schedule = build_schedule(cases, labyrinth_dir=labyrinth, seed=args.seed, steps=args.steps)
    return {"bt2": bt2, "labyrinth": labyrinth, "base": base, "dossier": dossier,
            "profile": load_models()[args.identity], "schedule": schedule,
            "cases_by_id": {c["id"]: c for c in cases}, "output": output,
            "dataset_sha256": sha256_file(CASE_ROOT / f"{args.identity}.json"),
            "base_metadata_sha256": base_metadata_sha256}


def run_training(args) -> dict:
    info = preflight(args)
    import torch
    import transformers
    import peft
    from labyrinth.hf_pilot import (
        _frozen_parameter_digest, _buffer_digest, _assert_frozen_state,
    )
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, TaskType, get_peft_model

    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    begun = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(str(info["base"]), local_files_only=True)
    instruction = persona_instruction(info["profile"], info["dossier"]["traits"])
    chosen = [info["cases_by_id"][item["case_id"]] for item in info["schedule"]]
    targets = [case["ideal_response"] for case in chosen]
    if args.arm == "corrupt":
        targets = targets[1:] + targets[:1]
    # Check the *entire* selected supervision budget before loading 3 GB weights.
    encoded = [encode_case(tokenizer, instruction, case, target, args.max_length)
               for case, target in zip(chosen, targets)]
    base_model = AutoModelForCausalLM.from_pretrained(
        str(info["base"]), local_files_only=True, dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    base_model.config.use_cache = False
    model = get_peft_model(base_model, LoraConfig(
        r=4, lora_alpha=8, lora_dropout=0.0, bias="none",
        task_type=TaskType.CAUSAL_LM, target_modules=["q_proj", "v_proj"],
    ))
    model.train()
    before = trainable_digest(model, torch)
    frozen_before = _frozen_parameter_digest(model, torch)
    buffers_before = _buffer_digest(model, torch)
    learning_rate = 0.0 if args.arm == "sham" else 0.0002
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),
                                  lr=learning_rate)
    losses = []
    for step, (case, pair) in enumerate(zip(chosen, encoded)):
        ids, labels = pair
        output = model(input_ids=torch.tensor([ids], dtype=torch.long),
                       labels=torch.tensor([labels], dtype=torch.long))
        loss = output.loss
        require(bool(torch.isfinite(loss).item()), "nonfinite persona training loss")
        loss.backward()
        torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad),
                                       1.0, error_if_nonfinite=True)
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        losses.append({"step": step + 1, "case_id": case["id"],
                       "loss": float(loss.detach().cpu())})
        print(f"persona step {step+1}/{args.steps} case={case['id']} loss={losses[-1]['loss']:.6f}", flush=True)
    after = trainable_digest(model, torch)
    _assert_frozen_state(model, torch, frozen_before, buffers_before, "persona training")
    require(sha256_file(info["base"] / "model.safetensors") == args.base_sha256,
            "HF donor changed during persona run")
    verify_donor_metadata(info["base"], info["base_metadata_sha256"])
    checked_checkout(info["bt2"], args.source_commit, "tools/train_personality_lora.py")
    checked_checkout(info["labyrinth"], args.labyrinth_commit, "labyrinth/curriculum.py")
    require((after != before) == (args.arm != "sham"),
            "trainable LoRA tensor update contradicts control arm")

    run = info["output"]
    run.mkdir()
    model.save_pretrained(str(run / "adapter"), safe_serialization=True)
    adapter = run / "adapter/adapter_model.safetensors"
    require(adapter.is_file(), "no saved LoRA safetensors")
    report = {
        "schema_version": SCHEMA,
        "claim_ceiling": CEILING,
        "identity_id": args.identity, "arm": args.arm, "device": "cpu",
        "bt2_source_commit": args.source_commit,
        "labyrinth_scheduler_commit": args.labyrinth_commit,
        "labyrinth_role": "ungraded deterministic training-case schedule",
        "labyrinth_case_seeds": "recorded for schedule provenance; not PyTorch RNG reseeds",
        "gradient_engine": "BT2/PyTorch/PEFT LoRA, not Labyrinth numeric train-hf",
        "personality_dataset_sha256": info["dataset_sha256"],
        "persona_instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "base_model_dir": str(info["base"]),
        "base_model_sha256": args.base_sha256,
        "base_metadata_sha256": info["base_metadata_sha256"],
        "base_model_bytes": (info["base"] / "model.safetensors").stat().st_size,
        "schedule": info["schedule"], "seed": args.seed, "steps": args.steps,
        "max_length": args.max_length, "threads": args.threads,
        "learning_rate": learning_rate, "losses": losses,
        "trainable_tensor_sha256_before": before,
        "trainable_tensor_sha256_after": after,
        "frozen_parameter_sha256_unchanged": frozen_before,
        "persistent_buffer_sha256_unchanged": buffers_before,
        "frozen_parameters_and_buffers_verified_unchanged": True,
        "adapter_safetensors_sha256": sha256_file(adapter),
        "duration_seconds": round(time.monotonic() - begun, 3),
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__,
                     "peft": peft.__version__},
        "qualified": False, "installed": False, "behavioral_improvement_verified": False,
    }
    (run / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def verify_reload(args) -> dict:
    import torch
    from transformers import AutoModelForCausalLM
    from peft import PeftModel

    run = Path(args.run_dir).resolve(strict=True)
    report = json.loads((run / "report.json").read_text(encoding="utf-8"))
    require(report["schema_version"] == SCHEMA, "wrong persona receipt schema")
    donor = Path(report["base_model_dir"])
    require(sha256_file(donor / "model.safetensors") == report["base_model_sha256"],
            "donor changed after persona training")
    verify_donor_metadata(donor, report.get("base_metadata_sha256"))
    file = run / "adapter/adapter_model.safetensors"
    require(sha256_file(file) == report["adapter_safetensors_sha256"],
            "persona adapter changed after training")
    torch.set_num_threads(args.threads)
    base = AutoModelForCausalLM.from_pretrained(
        str(donor), local_files_only=True, dtype=torch.float32, low_cpu_mem_usage=True,
    )
    adapter = PeftModel.from_pretrained(base, str(run / "adapter"), is_trainable=True)
    digest = trainable_digest(adapter, torch)
    require(digest == report["trainable_tensor_sha256_after"],
            "fresh-process persona adapter LoRA values do not match")
    return {"status": "EXACT_ADAPTER_TENSORS_RELOADED", "identity_id": report["identity_id"],
            "tensor_sha256": digest, "behavioral_improvement_verified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train")
    train.add_argument("--identity", required=True)
    train.add_argument("--source-commit", required=True)
    train.add_argument("--labyrinth-dir", required=True)
    train.add_argument("--labyrinth-commit", required=True)
    train.add_argument("--base-dir", required=True)
    train.add_argument("--base-sha256", required=True)
    train.add_argument("--run-dir", required=True)
    train.add_argument("--device", default="cpu")
    train.add_argument("--arm", choices=("candidate", "sham", "corrupt"), default="candidate")
    train.add_argument("--steps", type=int, default=4)
    train.add_argument("--max-length", type=int, default=1536)
    train.add_argument("--threads", type=int, default=2)
    train.add_argument("--seed", type=int, default=74413)
    reload_cmd = sub.add_parser("verify-reload")
    reload_cmd.add_argument("--run-dir", required=True)
    reload_cmd.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    try:
        result = run_training(args) if args.command == "train" else verify_reload(args)
        print(json.dumps(result, indent=2), flush=True)
        return 0
    except (ValueError, OSError, RuntimeError, ImportError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"personality LoRA pilot failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
