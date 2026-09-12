#!/usr/bin/env python3
"""Deterministically verify one Hephaestus training package directory.

This helper verifies bytes and simple manifest consistency. It does not execute training,
assess competence, or grant authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CHECKSUM_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")
MODULE_RE = re.compile(r"(?ms)^\s{4}path: (modules/[^\n]+)\n\s{4}sha256: ([0-9a-f]{64})$")
VERSION_RE = re.compile(r"(?m)^package_version: ([^\s]+)$")
PATH_RE = re.compile(r"(?m)^package_path: (.+)$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str) -> None:
    print(json.dumps({"status": "FAIL", "reason": msg}, sort_keys=True))
    raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("package_dir", type=Path)
    args = ap.parse_args()
    root = args.package_dir.resolve()
    checksums = root / "CHECKSUMS.sha256"
    manifest = root / "TRAINING_MANIFEST.yaml"
    if not checksums.is_file() or not manifest.is_file():
        fail("missing TRAINING_MANIFEST.yaml or CHECKSUMS.sha256")

    expected: dict[str, str] = {}
    for raw in checksums.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        m = CHECKSUM_RE.match(raw)
        if not m:
            fail(f"malformed checksum line: {raw!r}")
        digest, rel = m.groups()
        if rel in expected:
            fail(f"duplicate checksum path: {rel}")
        expected[rel] = digest

    def is_runtime_cache(p: Path) -> bool:
        rel = p.relative_to(root)
        return "__pycache__" in rel.parts or p.suffix in {".pyc", ".pyo"}

    actual = {
        str(p.relative_to(root)).replace("\\", "/")
        for p in root.rglob("*")
        if p.is_file() and p.name != "CHECKSUMS.sha256" and not is_runtime_cache(p)
    }
    if actual != set(expected):
        fail(f"file-set mismatch missing={sorted(set(expected)-actual)} extra={sorted(actual-set(expected))}")

    mismatches = []
    for rel, digest in sorted(expected.items()):
        got = sha256(root / rel)
        if got != digest:
            mismatches.append({"path": rel, "expected": digest, "actual": got})
    if mismatches:
        fail(f"checksum mismatches: {mismatches}")

    text = manifest.read_text(encoding="utf-8")
    vm = VERSION_RE.search(text)
    pm = PATH_RE.search(text)
    if not vm or not pm:
        fail("manifest missing package_version or package_path")
    version = vm.group(1)
    if root.name.startswith("v") and root.name != f"v{version}":
        fail(f"directory/version mismatch dir={root.name} manifest={version}")

    module_pairs = MODULE_RE.findall(text)
    if len(module_pairs) != 10:
        fail(f"expected 10 manifest module hash bindings, found {len(module_pairs)}")
    module_mismatches = []
    for rel, digest in module_pairs:
        p = root / rel
        got = sha256(p)
        if got != digest:
            module_mismatches.append({"path": rel, "expected": digest, "actual": got})
    if module_mismatches:
        fail(f"manifest module hash mismatches: {module_mismatches}")

    result = {
        "status": "PASS",
        "package_version": version,
        "package_path": pm.group(1),
        "verified_files_excluding_checksum_file": len(expected),
        "manifest_sha256": sha256(manifest),
        "checksums_sha256": sha256(checksums),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
