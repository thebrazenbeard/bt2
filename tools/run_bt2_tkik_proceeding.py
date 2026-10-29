"""Run a source-pinned T'Kal-in-ket REFINE case with attributed BT2 reviews.

This executes the external protocol from its own checkout; it does not vendor
the unlicensed source, authenticate reviewers, or execute a neural model.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from identity_coding_models import require
from train_personality_lora import checked_checkout


TKIK_COMMIT = "b0af150c2405b519fd921bac33e5f9f1f35f92d7"
TKIK_CORE_BLOB = "69e85a62672e1dfffacec08fde98e9df26716300"
LENSES = ("purist_logic", "pragmatism", "bridge")


def _nonempty(value: object, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"missing {field}")
    return value


def validate_packet(packet: object) -> dict:
    require(isinstance(packet, dict) and set(packet) == {
        "case_id", "hypothesis", "falsifier", "proposer", "definitions",
        "evidence", "reviews", "challenges", "rationale", "refined_claim",
        "review_custody_limitations"}, "invalid inquiry packet fields")
    for key in ("case_id", "hypothesis", "falsifier", "proposer", "rationale",
                "refined_claim", "review_custody_limitations"):
        _nonempty(packet[key], key)
    require(isinstance(packet["definitions"], dict) and
            all(isinstance(k, str) and isinstance(v, str) and k and v
                for k, v in packet["definitions"].items()), "invalid definitions")
    evidence = packet["evidence"]
    require(isinstance(evidence, list) and 1 <= len(evidence) <= 32,
            "bounded evidence required")
    for item in evidence:
        require(isinstance(item, dict) and set(item) == {
            "identifier", "claim", "source", "method", "reliability", "uncertainty"},
            "invalid evidence fields")
        for key, value in item.items():
            _nonempty(value, f"evidence.{key}")
    reviews = packet["reviews"]
    require(isinstance(reviews, list) and len(reviews) == 3,
            "exactly three T'Kal review lenses required")
    require({r.get("lens") for r in reviews if isinstance(r, dict)} == set(LENSES),
            "missing or duplicate review lens")
    reviewer_ids = []
    for item in reviews:
        require(isinstance(item, dict) and set(item) == {
            "lens", "reviewer_id", "finding", "objection", "execution_ref"},
            "invalid review fields")
        for key in ("reviewer_id", "finding", "objection"):
            _nonempty(item[key], f"review.{key}")
        require(item["execution_ref"] is None,
                "native review cannot masquerade as authenticated model invocation")
        reviewer_ids.append(item["reviewer_id"])
    require(len(set(reviewer_ids)) == 3, "distinct native reviewer IDs required")
    challenges = packet["challenges"]
    require(isinstance(challenges, list) and 1 <= len(challenges) <= 16,
            "bounded cross-examination required")
    for item in challenges:
        require(isinstance(item, dict) and set(item) == {
            "identifier", "lens", "target", "question", "status", "defense"},
            "invalid challenge fields")
        for key in ("identifier", "target", "question", "defense"):
            _nonempty(item[key], f"challenge.{key}")
        require(item["lens"] in LENSES and item["status"] == "CONCEDED",
                "this bounded protocol accepts only expressly conceded REFINE attacks")
    return packet


def _load_core(repo: Path):
    repo = checked_checkout(repo, TKIK_COMMIT, "tkik/core.py")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD:tkik/core.py"],
                         capture_output=True, text=True, check=True).stdout.strip()
    require(sha == TKIK_CORE_BLOB, "T'Kal core source pin differs")
    file = repo / "tkik/core.py"
    module_name = "_bt2_tkik_core_" + hashlib.sha256(str(file).encode()).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(module_name, file)
    require(spec is not None and spec.loader is not None, "cannot load pinned T'Kal core")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run(packet: object, tkik_repo: Path) -> dict:
    packet = validate_packet(packet)
    core = _load_core(tkik_repo)
    case = core.Case(packet["case_id"], packet["hypothesis"], packet["falsifier"],
                     packet["proposer"], definitions=dict(packet["definitions"]))
    for item in packet["evidence"]:
        case.add_evidence(core.Evidence(**item))
    for item in packet["reviews"]:
        case.add_review(core.Review(**item))
    for item in packet["challenges"]:
        case.ask(core.Challenge(item["identifier"], item["lens"], item["target"],
                                item["question"]))
        case.resolve(item["identifier"], item["status"], item["defense"])
    case.determine("REFINE", packet["rationale"])
    payload = json.dumps(packet, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return {
        "schema": "BT2_TKIK_NATIVE_REVIEW_V1",
        "case_id": case.case_id, "state": case.state, "verdict": case.verdict,
        "frozen_claim_sha256": case._frozen_claim_digest,
        "packet_sha256": hashlib.sha256(payload).hexdigest(),
        "tkik_repo": "thebrazenbeard/t-kal-in-ket", "tkik_commit": TKIK_COMMIT,
        "tkik_core_blob": TKIK_CORE_BLOB,
        "native_reviewer_ids": [case.reviews[lens].reviewer_id for lens in LENSES],
        "challenge_statuses": {c.identifier: c.status for c in case.challenges},
        "refined_claim": packet["refined_claim"],
        "review_custody_limitations": packet["review_custody_limitations"],
        "neural_inference_executed": False,
        "independent_model_or_host_attestation": False,
        "behavioral_personality_qualified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tkik-repo", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        require(args.packet.is_file() and not args.packet.is_symlink(), "unsafe packet")
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
        result = run(packet, args.tkik_repo)
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            print(encoded, end="")
        else:
            require(args.output.parent.is_dir(), "output parent missing")
            with args.output.open("x", encoding="utf-8") as dest:
                dest.write(encoded)
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"BT2 T'Kal proceeding rejected: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
