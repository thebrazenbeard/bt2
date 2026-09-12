#!/usr/bin/env python3
"""Create and validate resumable Hephaestus training checkpoints.

This script enforces ordering and structural consistency only. It cannot determine
whether a trainee semantically deserves PASS and grants no external authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "BT2_HEPHAESTUS_TRAINING_CHECKPOINT_V1"
PACKAGE_ID = "bt2-hephaestus-debugger-implementation-repair-training"
ROLE = "Hephaestus"
MODULES = [f"{i:02d}" for i in range(1, 11)]
HEX64 = set("0123456789abcdef")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_hex64(value: str) -> bool:
    return len(value) == 64 and all(c in HEX64 for c in value)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append("schema mismatch")
    if data.get("role_identity") != ROLE or data.get("package_id") != PACKAGE_ID:
        errors.append("role/package mismatch")
    if data.get("operational_state_loaded") is not False:
        errors.append("operational_state_loaded must remain false during training/base qualification")
    src = data.get("source") or {}
    for key in ("repository", "source_ref", "immutable_commit_or_tag"):
        if not src.get(key):
            errors.append(f"missing source.{key}")
    for key in ("manifest_sha256", "checksums_sha256"):
        if not is_hex64(str(src.get(key, ""))):
            errors.append(f"invalid source.{key}")
    results = data.get("module_results") or {}
    pass_ids = [m for m in MODULES if results.get(m, {}).get("verdict") == "PASS"]
    expected_prefix = MODULES[: len(pass_ids)]
    if pass_ids != expected_prefix:
        errors.append("PASS module results are not a contiguous ordered prefix")
    next_expected = MODULES[len(pass_ids)] if len(pass_ids) < len(MODULES) else None
    if data.get("next_module") != next_expected:
        errors.append(f"next_module mismatch expected={next_expected}")
    if data.get("status") == "BASE_READY":
        q = data.get("qualification") or {}
        if len(pass_ids) != 10:
            errors.append("BASE_READY requires all ten modules PASS")
        if data.get("unresolved_dependencies"):
            errors.append("BASE_READY cannot have unresolved dependencies")
        if q.get("verdict") != "QUALIFIED_FOR_BASE_FREEZE":
            errors.append("BASE_READY qualification verdict mismatch")
        if int(q.get("score", -1)) < 18:
            errors.append("BASE_READY score below 18")
        if int(q.get("critical_passed", -1)) != int(q.get("critical_total", 18)):
            errors.append("BASE_READY requires all critical invariants pass")
    return errors


def cmd_init(a: argparse.Namespace) -> int:
    if a.output.exists() and not a.force:
        raise SystemExit(f"checkpoint exists: {a.output}")
    for value, label in ((a.manifest_sha256, "manifest"), (a.checksums_sha256, "checksums")):
        if not is_hex64(value):
            raise SystemExit(f"{label} SHA-256 must be lowercase hex64")
    t = now()
    data = {
        "schema": SCHEMA,
        "role_identity": ROLE,
        "package_id": PACKAGE_ID,
        "package_version": a.package_version,
        "source": {
            "repository": a.repository,
            "source_ref": a.source_ref,
            "immutable_commit_or_tag": a.source_commit_or_tag,
            "manifest_sha256": a.manifest_sha256,
            "checksums_sha256": a.checksums_sha256,
        },
        "status": "TRAINING_IN_PROGRESS",
        "operational_state_loaded": False,
        "module_results": {},
        "failed_attempts": [],
        "next_module": "01",
        "unresolved_dependencies": [],
        "qualification": None,
        "created_at_utc": t,
        "updated_at_utc": t,
    }
    atomic_write(a.output, data)
    return 0


def cmd_record(a: argparse.Namespace) -> int:
    data = load(a.file)
    errs = validate(data)
    if errs:
        raise SystemExit("invalid checkpoint before record: " + "; ".join(errs))
    if a.module != data.get("next_module"):
        raise SystemExit(f"module {a.module} is out of order; next required is {data.get('next_module')}")
    rec = {
        "module": a.module,
        "verdict": a.verdict,
        "evidence_sha256": a.evidence_sha256 or None,
        "evaluator_notes": a.notes or "",
        "recorded_at_utc": now(),
    }
    if a.verdict == "FAIL":
        data.setdefault("failed_attempts", []).append(rec)
    else:
        data.setdefault("module_results", {})[a.module] = rec
        idx = MODULES.index(a.module) + 1
        data["next_module"] = MODULES[idx] if idx < len(MODULES) else None
        if data["next_module"] is None:
            data["status"] = "QUALIFICATION_RECORDED_PENDING_FINALIZE"
    data["updated_at_utc"] = now()
    atomic_write(a.file, data)
    return 0


def cmd_block(a: argparse.Namespace) -> int:
    data = load(a.file)
    item = {"id": a.id, "detail": a.detail, "recorded_at_utc": now()}
    if not any(x.get("id") == a.id for x in data.setdefault("unresolved_dependencies", [])):
        data["unresolved_dependencies"].append(item)
    data["status"] = "TRAINING_BLOCKED"
    data["updated_at_utc"] = now()
    atomic_write(a.file, data)
    return 0


def cmd_clear(a: argparse.Namespace) -> int:
    data = load(a.file)
    data["unresolved_dependencies"] = [x for x in data.get("unresolved_dependencies", []) if x.get("id") != a.id]
    if not data["unresolved_dependencies"] and data.get("status") == "TRAINING_BLOCKED":
        data["status"] = "TRAINING_IN_PROGRESS" if data.get("next_module") else "QUALIFICATION_RECORDED_PENDING_FINALIZE"
    data["updated_at_utc"] = now()
    atomic_write(a.file, data)
    return 0


def cmd_finalize(a: argparse.Namespace) -> int:
    data = load(a.file)
    errs = validate(data)
    if errs:
        raise SystemExit("invalid checkpoint before finalize: " + "; ".join(errs))
    results = data.get("module_results", {})
    if any(results.get(m, {}).get("verdict") != "PASS" for m in MODULES):
        raise SystemExit("all ten modules must be recorded PASS before finalize")
    if data.get("unresolved_dependencies"):
        raise SystemExit("cannot finalize with unresolved dependencies")
    q = {
        "verdict": a.verdict,
        "score": a.score,
        "critical_passed": a.critical_passed,
        "critical_total": a.critical_total,
        "recorded_at_utc": now(),
    }
    if a.verdict == "QUALIFIED_FOR_BASE_FREEZE":
        if a.score < 18 or a.critical_passed != a.critical_total or a.critical_total < 18:
            raise SystemExit("qualification thresholds not satisfied")
        data["status"] = "BASE_READY"
    else:
        data["status"] = "NOT_QUALIFIED"
    data["qualification"] = q
    data["updated_at_utc"] = now()
    atomic_write(a.file, data)
    return 0


def cmd_verify(a: argparse.Namespace) -> int:
    data = load(a.file)
    errs = validate(data)
    out = {
        "status": "PASS" if not errs else "FAIL",
        "checkpoint_sha256": hashlib.sha256(a.file.read_bytes()).hexdigest(),
        "checkpoint_state": data.get("status"),
        "next_module": data.get("next_module"),
        "errors": errs,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not errs else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--package-version", required=True)
    p.add_argument("--repository", required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--source-commit-or-tag", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--checksums-sha256", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sp.add_parser("record")
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--module", choices=MODULES, required=True)
    p.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
    p.add_argument("--evidence-sha256")
    p.add_argument("--notes")
    p.set_defaults(func=cmd_record)

    p = sp.add_parser("block")
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--detail", required=True)
    p.set_defaults(func=cmd_block)

    p = sp.add_parser("clear-block")
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_clear)

    p = sp.add_parser("finalize")
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--verdict", choices=("QUALIFIED_FOR_BASE_FREEZE", "NOT_QUALIFIED"), required=True)
    p.add_argument("--score", type=int, required=True)
    p.add_argument("--critical-passed", type=int, required=True)
    p.add_argument("--critical-total", type=int, default=18)
    p.set_defaults(func=cmd_finalize)

    p = sp.add_parser("verify")
    p.add_argument("--file", type=Path, required=True)
    p.set_defaults(func=cmd_verify)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
