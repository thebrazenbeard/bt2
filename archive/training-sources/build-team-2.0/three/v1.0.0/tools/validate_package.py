#!/usr/bin/env python3
"""Deterministically validate a BT2 role training package.

This verifier checks package structure and manifest/module binding only. It does not
judge trainee answers and it grants no operational authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_relative_path(raw: str) -> bool:
    p = Path(raw)
    return bool(raw) and not p.is_absolute() and ".." not in p.parts


def validate_package(package_dir: Path) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    manifest_path = package_dir / "TRAINING_MANIFEST.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not manifest_path.is_file():
        return {"valid": False, "errors": ["MISSING_TRAINING_MANIFEST"], "warnings": []}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"valid": False, "errors": [f"INVALID_MANIFEST_JSON:{type(exc).__name__}"], "warnings": []}

    for key in ("schema", "package_id", "training_version", "role", "modules", "qualification"):
        if key not in manifest:
            errors.append(f"MISSING_MANIFEST_KEY:{key}")

    role = manifest.get("role", {})
    if role.get("identity") != "Three":
        errors.append("ROLE_IDENTITY_MUST_BE_THREE")

    modules = manifest.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("MODULE_LIST_EMPTY_OR_INVALID")
        modules = []

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    qualification_indexes: list[int] = []

    for idx, module in enumerate(modules, start=1):
        if not isinstance(module, dict):
            errors.append(f"MODULE_NOT_OBJECT:{idx}")
            continue
        if module.get("order") != idx:
            errors.append(f"MODULE_ORDER_MISMATCH:{idx}:{module.get('order')}")
        module_id = module.get("id")
        path_text = module.get("path")
        if not isinstance(module_id, str) or not module_id:
            errors.append(f"MODULE_ID_INVALID:{idx}")
        elif module_id in seen_ids:
            errors.append(f"DUPLICATE_MODULE_ID:{module_id}")
        else:
            seen_ids.add(module_id)

        if not isinstance(path_text, str) or not _safe_relative_path(path_text):
            errors.append(f"MODULE_PATH_INVALID:{idx}")
            continue
        if path_text in seen_paths:
            errors.append(f"DUPLICATE_MODULE_PATH:{path_text}")
        seen_paths.add(path_text)

        module_path = package_dir / path_text
        try:
            resolved = module_path.resolve(strict=True)
        except FileNotFoundError:
            errors.append(f"MODULE_FILE_MISSING:{path_text}")
            continue
        if package_dir not in resolved.parents:
            errors.append(f"MODULE_PATH_ESCAPES_PACKAGE:{path_text}")
        if module_path.is_symlink():
            errors.append(f"MODULE_SYMLINK_FORBIDDEN:{path_text}")
        if not module_path.is_file() or module_path.stat().st_size == 0:
            errors.append(f"MODULE_FILE_EMPTY_OR_NOT_FILE:{path_text}")

        if module.get("qualification_module") is True:
            qualification_indexes.append(idx)

        criteria = module.get("pass_criteria")
        if not isinstance(criteria, list) or not criteria or not all(isinstance(x, str) and x.strip() for x in criteria):
            errors.append(f"PASS_CRITERIA_INVALID:{module_id or idx}")

    if len(qualification_indexes) != 1:
        errors.append(f"QUALIFICATION_MODULE_COUNT:{len(qualification_indexes)}")
    elif qualification_indexes[0] != len(modules):
        errors.append("QUALIFICATION_MODULE_MUST_BE_LAST")

    if not (package_dir / "BOOTSTRAP.md").is_file():
        errors.append("MISSING_BOOTSTRAP")

    non_goals = set(manifest.get("non_goals", []))
    if not any("current assignments" in str(x).lower() for x in non_goals):
        warnings.append("NON_GOALS_DO_NOT_EXPLICITLY_EXCLUDE_CURRENT_ASSIGNMENTS")
    if not any("mutation" in str(x).lower() for x in non_goals):
        warnings.append("NON_GOALS_DO_NOT_EXPLICITLY_EXCLUDE_MUTATION_AUTHORITY")

    return {
        "valid": not errors,
        "package_id": manifest.get("package_id"),
        "training_version": manifest.get("training_version"),
        "manifest_sha256": sha256_file(manifest_path),
        "module_count": len(modules),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    args = parser.parse_args()
    result = validate_package(args.package_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
