#!/usr/bin/env python3
"""Training-progress checkpoint helper for BT2 role Three.

The tool records evaluator decisions and checks declarative manifest gates. It does
not judge semantic competence, grant BASE_READY by itself, or grant operational
write authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_STATUSES = {"NOT_STARTED", "PASS", "FAIL", "UNRESOLVED"}
FINAL_RESULTS = {"BASE_READY", "NOT_QUALIFIED", "TRAINING_UNRESOLVED", "TRAINING_SOURCE_CONFLICT"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _inside(child: Path, parent: Path) -> bool:
    child = child.resolve()
    parent = parent.resolve()
    return child == parent or parent in child.parents


def init_checkpoint(package_dir: Path, checkpoint_path: Path) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    checkpoint_path = checkpoint_path.resolve()
    if _inside(checkpoint_path, package_dir):
        raise ValueError("CHECKPOINT_MUST_BE_OUTSIDE_FROZEN_TRAINING_SOURCE")

    manifest_path = package_dir / "TRAINING_MANIFEST.json"
    manifest = load_json(manifest_path)
    modules = manifest["modules"]
    payload = {
        "schema": "BT2_ROLE_TRAINING_CHECKPOINT_V1",
        "package_id": manifest["package_id"],
        "training_version": manifest["training_version"],
        "manifest_sha256": sha256_file(manifest_path),
        "role_identity": manifest["role"]["identity"],
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "modules": [
            {
                "order": m["order"],
                "id": m["id"],
                "status": "NOT_STARTED",
                "attempts": 0,
                "evidence": [],
            }
            for m in modules
        ],
        "critical_disqualifiers_triggered": [],
        "overall_status": "TRAINING_IN_PROGRESS",
        "qualification_receipt": None,
        "limitations": [
            "Checkpoint records training progress only.",
            "It is not operational state and grants no mutation authority.",
            "It is not proof of uninterrupted runtime or subjective continuity."
        ],
    }
    atomic_write_json(checkpoint_path, payload)
    return payload


def verify_binding(package_dir: Path, checkpoint: dict[str, Any]) -> list[str]:
    manifest_path = package_dir.resolve() / "TRAINING_MANIFEST.json"
    manifest = load_json(manifest_path)
    errors: list[str] = []
    if checkpoint.get("package_id") != manifest.get("package_id"):
        errors.append("PACKAGE_ID_MISMATCH")
    if checkpoint.get("training_version") != manifest.get("training_version"):
        errors.append("TRAINING_VERSION_MISMATCH")
    if checkpoint.get("manifest_sha256") != sha256_file(manifest_path):
        errors.append("MANIFEST_SHA256_MISMATCH")
    expected = [(m["order"], m["id"]) for m in manifest["modules"]]
    observed = [(m.get("order"), m.get("id")) for m in checkpoint.get("modules", [])]
    if observed != expected:
        errors.append("MODULE_SEQUENCE_MISMATCH")
    return errors


def record_module(package_dir: Path, checkpoint_path: Path, module_id: str, status: str, evidence: list[str]) -> dict[str, Any]:
    if status not in VALID_STATUSES - {"NOT_STARTED"}:
        raise ValueError("STATUS_MUST_BE_PASS_FAIL_OR_UNRESOLVED")
    checkpoint = load_json(checkpoint_path)
    binding_errors = verify_binding(package_dir, checkpoint)
    if binding_errors:
        raise ValueError("CHECKPOINT_BINDING_INVALID:" + ",".join(binding_errors))

    found = False
    for module in checkpoint["modules"]:
        if module["id"] == module_id:
            found = True
            module["status"] = status
            module["attempts"] = int(module.get("attempts", 0)) + 1
            module["evidence"] = list(evidence)
            module["recorded_at"] = now_utc()
            break
    if not found:
        raise ValueError("UNKNOWN_MODULE_ID")

    checkpoint["updated_at"] = now_utc()
    checkpoint["overall_status"] = "TRAINING_IN_PROGRESS"
    checkpoint["qualification_receipt"] = None
    atomic_write_json(checkpoint_path, checkpoint)
    return checkpoint


def add_disqualifier(package_dir: Path, checkpoint_path: Path, disqualifier: str) -> dict[str, Any]:
    checkpoint = load_json(checkpoint_path)
    binding_errors = verify_binding(package_dir, checkpoint)
    if binding_errors:
        raise ValueError("CHECKPOINT_BINDING_INVALID:" + ",".join(binding_errors))
    values = checkpoint.setdefault("critical_disqualifiers_triggered", [])
    if disqualifier not in values:
        values.append(disqualifier)
    checkpoint["updated_at"] = now_utc()
    checkpoint["overall_status"] = "NOT_QUALIFIED"
    checkpoint["qualification_receipt"] = None
    atomic_write_json(checkpoint_path, checkpoint)
    return checkpoint


def qualify(package_dir: Path, checkpoint_path: Path) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    checkpoint = load_json(checkpoint_path)
    binding_errors = verify_binding(package_dir, checkpoint)
    if binding_errors:
        result = "TRAINING_SOURCE_CONFLICT"
        reasons = binding_errors
    else:
        statuses = [m["status"] for m in checkpoint["modules"]]
        disqualifiers = checkpoint.get("critical_disqualifiers_triggered", [])
        if any(s == "UNRESOLVED" for s in statuses):
            result = "TRAINING_UNRESOLVED"
            reasons = ["ONE_OR_MORE_MODULES_UNRESOLVED"]
        elif any(s != "PASS" for s in statuses):
            result = "NOT_QUALIFIED"
            reasons = ["NOT_ALL_MODULES_PASS"]
        elif disqualifiers:
            result = "NOT_QUALIFIED"
            reasons = ["CRITICAL_DISQUALIFIER_TRIGGERED"]
        else:
            result = "BASE_READY"
            reasons = []

    receipt = {
        "schema": "BT2_ROLE_TRAINING_QUALIFICATION_RECEIPT_V1",
        "result": result,
        "package_id": checkpoint.get("package_id"),
        "training_version": checkpoint.get("training_version"),
        "manifest_sha256": checkpoint.get("manifest_sha256"),
        "qualified_at": now_utc(),
        "reasons": reasons,
        "authority_limit": "Competence status only; grants no operational mutation authority.",
        "continuity_limit": "Does not prove uninterrupted runtime or subjective continuity.",
    }
    checkpoint["overall_status"] = result
    checkpoint["qualification_receipt"] = receipt
    checkpoint["updated_at"] = now_utc()
    atomic_write_json(checkpoint_path, checkpoint)
    return receipt


def verify_checkpoint(package_dir: Path, checkpoint_path: Path) -> dict[str, Any]:
    checkpoint = load_json(checkpoint_path)
    errors = verify_binding(package_dir, checkpoint)
    for module in checkpoint.get("modules", []):
        if module.get("status") not in VALID_STATUSES:
            errors.append(f"INVALID_MODULE_STATUS:{module.get('id')}")
    receipt = checkpoint.get("qualification_receipt")
    if receipt is not None and receipt.get("result") not in FINAL_RESULTS:
        errors.append("INVALID_QUALIFICATION_RESULT")
    return {"valid": not errors, "errors": errors, "overall_status": checkpoint.get("overall_status")}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("package_dir", type=Path)
    p_init.add_argument("checkpoint", type=Path)

    p_record = sub.add_parser("record")
    p_record.add_argument("package_dir", type=Path)
    p_record.add_argument("checkpoint", type=Path)
    p_record.add_argument("module_id")
    p_record.add_argument("status", choices=sorted(VALID_STATUSES - {"NOT_STARTED"}))
    p_record.add_argument("--evidence", action="append", default=[])

    p_disq = sub.add_parser("disqualify")
    p_disq.add_argument("package_dir", type=Path)
    p_disq.add_argument("checkpoint", type=Path)
    p_disq.add_argument("reason")

    p_qual = sub.add_parser("qualify")
    p_qual.add_argument("package_dir", type=Path)
    p_qual.add_argument("checkpoint", type=Path)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("package_dir", type=Path)
    p_verify.add_argument("checkpoint", type=Path)

    args = parser.parse_args()
    if args.cmd == "init":
        result = init_checkpoint(args.package_dir, args.checkpoint)
    elif args.cmd == "record":
        result = record_module(args.package_dir, args.checkpoint, args.module_id, args.status, args.evidence)
    elif args.cmd == "disqualify":
        result = add_disqualifier(args.package_dir, args.checkpoint, args.reason)
    elif args.cmd == "qualify":
        result = qualify(args.package_dir, args.checkpoint)
    else:
        result = verify_checkpoint(args.package_dir, args.checkpoint)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
