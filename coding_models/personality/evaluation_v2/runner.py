"""Unqualified, blind, paired GGUF inference evaluation for BT2 personalities.

Opaque cases are supplied by an independent evaluator at run time. This tool
never executes model-generated code and never assigns correctness from syntax.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import time


ROSTER = frozenset(("one", "two", "three", "four", "five", "six", "seven",
                    "eight", "nine", "thirteen", "masa", "mune", "hephaestus"))
VARIANTS = frozenset(("donor", "coding", "persona_previous", "candidate",
                      "sham", "corrupt"))
EXPERIMENTAL_ARMS = frozenset(("candidate", "sham", "corrupt"))
PROMPT_MODES = ("neutral", "traits")
NEUTRAL_INSTRUCTION = (
    "You are a coding assistant. Solve the task accurately. Report uncertainty "
    "and never invent tests, tool execution, or observations."
)
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
CLAIM_CEILING = "UNQUALIFIED_BLIND_INFERENCE_EVIDENCE_REQUIRES_INDEPENDENT_REVIEW"
MAX_GENERATIONS_PER_RUN = 128


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    require(path.is_file() and not path.is_symlink(), f"missing/unsafe input {path}")
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            item = json.loads(line)
            require(isinstance(item, dict), f"row {line_no} must be an object")
            rows.append(item)
    return rows


def write_jsonl_new(path: Path, rows: list[dict]) -> None:
    require(path.parent.is_dir() and not path.is_symlink(), "output parent missing/unsafe")
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def write_json_new(path: Path, data: dict) -> None:
    require(path.parent.is_dir() and not path.is_symlink(), "output parent missing/unsafe")
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def validated_cases(rows: list[dict]) -> list[dict]:
    require(bool(rows), "no evaluation cases")
    seen = set()
    for row in rows:
        key = row.get("case_id")
        require(isinstance(key, str) and 1 <= len(key) <= 120 and key not in seen,
                "missing/duplicate case identifier")
        seen.add(key)
        require(row.get("domain") in ("code", "behavior"), "invalid case domain")
        require(isinstance(row.get("prompt"), str) and len(row["prompt"].strip()) >= 10,
                "empty/short case prompt")
        require(isinstance(row.get("rubric_id"), str) and row["rubric_id"].strip(),
                "independent rubric identifier required")
        if row["domain"] == "code":
            require(isinstance(row.get("function"), str) and
                    re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", row["function"]),
                    "code case requires a Python function identifier")
    return rows


def validated_models(rows: list[dict]) -> list[dict]:
    require(bool(rows), "no model manifest")
    seen, instructions = set(), {}
    for row in rows:
        identity, variant = row.get("identity"), row.get("variant")
        require(identity in ROSTER and variant in VARIANTS,
                "invalid identity or model variant")
        pair = (identity, variant)
        require(pair not in seen, f"duplicate model variant {pair}")
        seen.add(pair)
        require(isinstance(row.get("model_path"), str) and row["model_path"].strip(),
                "model path required")
        require(Path(row["model_path"]).is_absolute(),
                "model path must be absolute for reproducible CLI invocation")
        require(isinstance(row.get("model_sha256"), str) and
                SHA_RE.fullmatch(row["model_sha256"]), "pinned model SHA-256 required")
        require(isinstance(row.get("trait_instruction"), str) and
                len(row["trait_instruction"].strip()) >= 10,
                "source-grounded trait instruction required")
        # Every arm must receive the *same* trait prompt for an identity.
        old = instructions.setdefault(identity, row["trait_instruction"])
        require(old == row["trait_instruction"],
                f"trait-prompt control not matched for {identity}")
        if variant in EXPERIMENTAL_ARMS:
            require(isinstance(row.get("training_report_path"), str) and
                    Path(row["training_report_path"]).is_absolute() and
                    isinstance(row.get("training_report_sha256"), str) and
                    SHA_RE.fullmatch(row["training_report_sha256"]),
                    f"training receipt required for experimental arm {pair}")
    return rows


def chat_prompt(instruction: str, task: str) -> str:
    return ("<|im_start|>system\n" + instruction + "<|im_end|>\n"
            "<|im_start|>user\n" + task + "<|im_end|>\n"
            "<|im_start|>assistant\n")


def plan(models: list[dict], cases: list[dict], seed: int) -> list[dict]:
    require(type(seed) is int and 0 <= seed < 2**31, "invalid seed")
    planned = []
    for model in validated_models(models):
        for case in validated_cases(cases):
            for mode in PROMPT_MODES:
                instruction = (NEUTRAL_INSTRUCTION if mode == "neutral"
                               else model["trait_instruction"])
                full = chat_prompt(instruction, case["prompt"])
                planned.append({
                    "identity": model["identity"], "variant": model["variant"],
                    "model_path": model["model_path"],
                    "model_sha256": model["model_sha256"],
                    "training_report_path": model.get("training_report_path"),
                    "training_report_sha256": model.get("training_report_sha256"),
                    "case_id": case["case_id"], "domain": case["domain"],
                    "function": case.get("function"), "rubric_id": case["rubric_id"],
                    "prompt_mode": mode, "prompt": full,
                    "prompt_sha256": digest(full),
                    "case_prompt_sha256": digest(case["prompt"]),
                })
    random.Random(seed).shuffle(planned)
    for index, row in enumerate(planned, 1):
        row["run_id"] = f"run-{index:06d}"
    return planned


def validate_plan(rows: list[dict]) -> None:
    require(bool(rows), "empty inference plan")
    run_ids = set()
    prompt_by_task_mode = {}
    arm_coverage = {}
    for row in rows:
        key = row.get("run_id")
        require(isinstance(key, str) and key not in run_ids, "duplicate run ID")
        run_ids.add(key)
        require(row.get("identity") in ROSTER and row.get("variant") in VARIANTS,
                "invalid planned identity/variant")
        require(row.get("prompt_mode") in PROMPT_MODES, "invalid prompt mode")
        require(isinstance(row.get("prompt"), str) and
                digest(row["prompt"]) == row.get("prompt_sha256"),
                "planned prompt digest mismatch")
        require(isinstance(row.get("model_sha256"), str) and
                SHA_RE.fullmatch(row["model_sha256"]), "missing model digest")
        comparison = (row["identity"], row["case_id"], row["prompt_mode"])
        arm = (row["identity"], row["variant"])
        coverage = arm_coverage.setdefault(arm, set())
        require((row["case_id"], row["prompt_mode"]) not in coverage,
                "duplicate task/mode in the same evaluation arm")
        coverage.add((row["case_id"], row["prompt_mode"]))
        fingerprint = (row["prompt_sha256"], row.get("rubric_id"),
                       row.get("case_prompt_sha256"), row.get("domain"))
        prior = prompt_by_task_mode.setdefault(comparison, fingerprint)
        require(prior == fingerprint,
                f"unmatched paired prompt for {comparison}")
    for identity in {arm[0] for arm in arm_coverage}:
        sets = [coverage for (name, variant), coverage in arm_coverage.items()
                if name == identity]
        require(all(coverage == sets[0] for coverage in sets),
                f"incomplete paired case coverage for {identity}")


def verify_inputs(plan_rows: list[dict], cli: Path, expected_cli_sha256: str) -> None:
    require(cli.is_file() and not cli.is_symlink(), "missing/unsafe llama-cli executable")
    require(SHA_RE.fullmatch(expected_cli_sha256) is not None and
            file_digest(cli) == expected_cli_sha256, "llama-cli changed")
    checked = set()
    checked_receipts = {}
    for row in plan_rows:
        name, expected = row["model_path"], row["model_sha256"]
        if (name, expected) in checked:
            continue
        path = Path(name)
        require(path.is_file() and not path.is_symlink(), f"missing/unsafe model {name}")
        require(file_digest(path) == expected, f"model digest mismatch: {name}")
        checked.add((name, expected))
    for row in plan_rows:
        if row["variant"] not in EXPERIMENTAL_ARMS:
            continue
        report_path = row.get("training_report_path")
        report_sha = row.get("training_report_sha256")
        require(isinstance(report_path, str) and Path(report_path).is_absolute() and
                isinstance(report_sha, str) and SHA_RE.fullmatch(report_sha),
                "missing experimental training receipt")
        if (report_path, report_sha) not in checked_receipts:
            path = Path(report_path)
            require(path.is_file() and not path.is_symlink(), "missing/unsafe training receipt")
            require(file_digest(path) == report_sha, "training report checksum mismatch")
            checked_receipts[(report_path, report_sha)] = json.loads(
                path.read_text(encoding="utf-8"))
        report = checked_receipts[(report_path, report_sha)]
        require(report.get("identity_id") == row["identity"] and
                report.get("arm") == row["variant"] and
                report.get("frozen_parameters_and_buffers_verified_unchanged") is True and
                report.get("installed") is False and report.get("qualified") is False,
                "training receipt does not establish declared experimental control")


def generate(plan_rows: list[dict], *, cli: Path, expected_cli_sha256: str,
             max_tokens: int, threads: int, timeout: int, seed: int) -> list[dict]:
    require(1 <= max_tokens <= 1024 and 1 <= threads <= 4 and
            1 <= timeout <= 900 and 0 <= seed < 2**31,
            "unbounded inference settings")
    require(1 <= len(plan_rows) <= MAX_GENERATIONS_PER_RUN,
            "oversized inference plan: shard by identity into bounded jobs")
    validate_plan(plan_rows)
    verify_inputs(plan_rows, cli, expected_cli_sha256)
    results = []
    for row in plan_rows:
        argv = [str(cli), "-m", row["model_path"], "-p", row["prompt"],
                "-n", str(max_tokens), "-t", str(threads), "-ngl", "0",
                "--temp", "0", "--seed", str(seed), "--no-display-prompt",
                "--single-turn", "--simple-io"]
        begun = time.monotonic()
        try:
            done = subprocess.run(argv, capture_output=True, text=True,
                                  timeout=timeout, check=False)
            response, error, code = done.stdout, done.stderr, done.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            response, error, code = "", str(exc), -1
        require(len(response) <= 100_000, "oversized inference output; refuse silent truncation")
        results.append({
            "run_id": row["run_id"], "identity": row["identity"],
            "variant": row["variant"], "case_id": row["case_id"],
            "domain": row["domain"], "function": row.get("function"),
            "rubric_id": row["rubric_id"], "prompt_mode": row["prompt_mode"],
            "model_sha256": row["model_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "exit_code": code, "response": response,
            "response_sha256": digest(response),
            "error_tail": error[-2000:],
            "elapsed_seconds": round(time.monotonic() - begun, 3),
            "generator": {"llama_cli_sha256": expected_cli_sha256,
                          "max_tokens": max_tokens, "threads": threads,
                          "temperature": 0, "seed": seed, "n_gpu_layers": 0},
        })
    # Refuse a receipt if a model, control report, or CLI changed mid-evaluation.
    verify_inputs(plan_rows, cli, expected_cli_sha256)
    return results


def syntax_diagnostic(response: str, function: str | None) -> dict:
    """Static observation only, deliberately NOT code correctness."""
    if not function:
        return {"python_parse": None, "declares_interface": None}
    match = re.search(r"```(?:python)?\s*\n(.*?)```", response, re.I | re.S)
    source = match.group(1) if match else response
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"python_parse": False, "declares_interface": False}
    return {"python_parse": True, "declares_interface": any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and
        node.name == function for node in tree.body)}


def blind_packet(responses: list[dict], plan_rows: list[dict],
                 seed: int) -> tuple[list[dict], list[dict]]:
    require(type(seed) is int and 0 <= seed < 2**31, "invalid blind seed")
    reviewed, custody = [], []
    require(bool(responses), "no generated responses")
    validate_plan(plan_rows)
    planned = {item["run_id"]: item for item in plan_rows}
    require(len(responses) == len(planned), "inference coverage differs from registered plan")
    run_ids = set()
    for item in responses:
        require(item.get("run_id") not in run_ids, "duplicate inference run ID")
        run_ids.add(item["run_id"])
        expected = planned.get(item["run_id"])
        require(expected is not None, "unknown inference run ID")
        for field in ("identity", "variant", "case_id", "domain", "function",
                      "rubric_id", "prompt_mode", "model_sha256", "prompt_sha256"):
            require(item.get(field) == expected.get(field),
                    f"inference identity/prompt custody mismatch: {field}")
        require(item.get("exit_code") == 0, "inference failure blocks blind scoring")
        require(digest(item.get("response", "")) == item.get("response_sha256"),
                "response tampered before blind review")
        reviewed.append({
            "case_id": item["case_id"], "domain": item["domain"],
            "rubric_id": item["rubric_id"], "function": item.get("function"),
            "response": item["response"],
            "response_sha256": item["response_sha256"],
            "syntax_diagnostic_not_correctness": syntax_diagnostic(
                item["response"], item.get("function") if item["domain"] == "code" else None),
        })
        custody.append({
            "run_id": item["run_id"], "identity": item["identity"],
            "variant": item["variant"], "case_id": item["case_id"],
            "domain": item["domain"], "prompt_mode": item["prompt_mode"],
            "model_sha256": item["model_sha256"],
            "response_sha256": item["response_sha256"],
        })
    permutation = list(range(len(reviewed)))
    random.Random(seed).shuffle(permutation)
    blinded, key = [], []
    for index, position in enumerate(permutation, 1):
        review_id = f"blind-{index:06d}"
        blinded.append({"review_id": review_id, **reviewed[position]})
        key.append({"review_id": review_id, **custody[position]})
    return blinded, key


def summarize(key: list[dict], reviews: list[dict]) -> dict:
    """Only human-scored observations enter paired deltas; missing is not zero."""
    require(bool(key), "empty blind key")
    by_id = {}
    for review in reviews:
        review_id = review.get("review_id")
        require(isinstance(review_id, str) and review_id not in by_id,
                "duplicate/invalid review ID")
        for metric in ("correctness", "role_fidelity"):
            value = review.get(metric)
            require(value is None or (type(value) is int and 0 <= value <= 4),
                    f"independent 0..4 human score or null required: {metric}")
        require(any(review.get(metric) is not None
                    for metric in ("correctness", "role_fidelity")),
                "review must contain at least one independently assessed metric")
        by_id[review_id] = review
    key_ids = {item["review_id"] for item in key}
    require(len(key_ids) == len(key) and set(by_id) <= key_ids,
            "review IDs cannot be matched to custody key")
    keyed = {item["review_id"]: item for item in key}
    for review_id, review in by_id.items():
        require(review.get("response_sha256") == keyed[review_id].get("response_sha256"),
                "review response digest does not match blinded evidence")
    cells = {}
    for item in key:
        review = by_id.get(item["review_id"])
        if review is None:
            continue
        cell = (item["identity"], item["case_id"], item["domain"], item["prompt_mode"])
        variants = cells.setdefault(cell, {})
        require(item["variant"] not in variants, "duplicate comparison arm")
        variants[item["variant"]] = review
    comparisons = []
    for identity in sorted({cell[0] for cell in cells}):
        for comparison in ("donor", "coding", "persona_previous", "sham", "corrupt"):
            for domain in ("behavior", "code"):
                for mode in PROMPT_MODES:
                    matched = [
                        (arms["candidate"], arms[comparison])
                        for (cell_identity, case_id, cell_domain, cell_mode), arms in cells.items()
                        if cell_identity == identity and cell_domain == domain and
                        cell_mode == mode and "candidate" in arms and comparison in arms
                    ]
                    if not matched:
                        continue
                    correctness = [(a["correctness"], b["correctness"]) for a, b in matched
                                   if a["correctness"] is not None and b["correctness"] is not None]
                    fidelity = [(a["role_fidelity"], b["role_fidelity"]) for a, b in matched
                                if a["role_fidelity"] is not None and b["role_fidelity"] is not None]
                    comparisons.append({
                        "identity": identity, "candidate_vs": comparison,
                        "domain": domain, "prompt_mode": mode,
                        "paired_reviewed_cases": len(matched),
                        "paired_correctness_scores": len(correctness),
                        "paired_role_fidelity_scores": len(fidelity),
                        "mean_correctness_delta": (round(sum(a-b for a, b in correctness) /
                                                          len(correctness), 4) if correctness else None),
                        "mean_role_fidelity_delta": (round(sum(a-b for a, b in fidelity) /
                                                            len(fidelity), 4) if fidelity else None),
                    })
    return {
        "claim_ceiling": CLAIM_CEILING, "qualified": False,
        "total_expected_reviews": len(key), "human_scored_reviews": len(by_id),
        "missing_human_reviews": len(key) - len(by_id),
        "comparisons": comparisons,
        "caveat": "Human judgments are not oracle tests or automatically significant; "
                  "absence of a paired arm is not a zero score. Syntax is not correctness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    make_plan = commands.add_parser("plan")
    make_plan.add_argument("--models", type=Path, required=True)
    make_plan.add_argument("--cases", type=Path, required=True)
    make_plan.add_argument("--out", type=Path, required=True)
    make_plan.add_argument("--seed", type=int, default=20261029)
    run = commands.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--llama-cli", type=Path, required=True)
    run.add_argument("--llama-cli-sha256", required=True)
    run.add_argument("--tokens", type=int, default=384)
    run.add_argument("--threads", type=int, default=2)
    run.add_argument("--timeout", type=int, default=180)
    run.add_argument("--seed", type=int, default=42)
    blind = commands.add_parser("blind")
    blind.add_argument("--plan", type=Path, required=True)
    blind.add_argument("--responses", type=Path, required=True)
    blind.add_argument("--packet", type=Path, required=True)
    blind.add_argument("--key", type=Path, required=True)
    blind.add_argument("--seed", type=int, default=81119)
    score = commands.add_parser("score")
    score.add_argument("--key", type=Path, required=True)
    score.add_argument("--reviews", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "plan":
        rows = plan(read_jsonl(args.models), read_jsonl(args.cases), args.seed)
        write_jsonl_new(args.out, rows)
        print(f"planned {len(rows)} independent paired inferences")
    elif args.action == "run":
        rows = generate(read_jsonl(args.plan), cli=args.llama_cli,
                        expected_cli_sha256=args.llama_cli_sha256,
                        max_tokens=args.tokens, threads=args.threads,
                        timeout=args.timeout, seed=args.seed)
        write_jsonl_new(args.out, rows)
        print(f"recorded {len(rows)} unqualified inference results")
    elif args.action == "blind":
        packet, key = blind_packet(read_jsonl(args.responses),
                                   read_jsonl(args.plan), args.seed)
        require(args.packet != args.key and not args.packet.exists() and
                not args.key.exists(), "blind packet and key need distinct unused paths")
        write_jsonl_new(args.packet, packet)
        write_jsonl_new(args.key, key)
        print(f"created {len(packet)} blind items and a separate custody key")
    else:
        report = summarize(read_jsonl(args.key), read_jsonl(args.reviews))
        write_json_new(args.out, report)
        print(f"human reviews={report['human_scored_reviews']}, "
              f"matched contrasts={len(report['comparisons'])}; NOT qualified")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"blind persona evaluator failed: {exc}") from exc
