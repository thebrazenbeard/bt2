#!/usr/bin/env python3
"""Fail-closed source/package identity verification for BT2 qualification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

COMPONENTS = [
    ("schema_tree", "database/schema", "schema"),
    ("migrations_tree", "database/migrations", "migrations"),
    ("tests_tree", "database/tests", "tests"),
    ("admin_tree", "database/admin", "admin"),
    ("data_tree", "database/data", "data"),
    ("lantern_archive_tree", "archive/supabase-project-lantern/cohosted-historical/2026-09-11", "archive"),
    ("loaders_tree", "database/loaders", "loaders"),
    ("seeds_tree", "database/seeds", "seeds"),
    ("qualification_tools_tree", "tools/qualification", "qualification-tools"),
]


def git(root: Path, *args: str) -> str:
    cp = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if cp.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp.stdout.strip()


def canonical_digest_input(manifest: dict) -> str:
    package = manifest["package_identity"]
    extensions = manifest["target"]["required_extensions"]
    if extensions != ["pgcrypto"]:
        raise SystemExit(f"unexpected required_extensions for V2 package: {extensions}")
    parts = [f"{label}:{package[key]}" for key, _, label in COMPONENTS]
    parts.extend([
        f"postgres-major:{manifest['target']['qualified_major_version']}",
        f"required-extension:{extensions[0]}",
    ])
    return "|".join(parts)


def verify_manifest_source(
    root: Path,
    manifest_path: Path,
    expected_digest: str | None = None,
) -> tuple[dict, str, str, str]:
    if shutil.which("git") is None:
        raise SystemExit("git is required on PATH for source-bound qualification")
    dirty = git(root, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise SystemExit(f"qualification source checkout is not clean:\n{dirty}")

    head = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package = manifest["package_identity"]
    for key, path, _ in COMPONENTS:
        observed = git(root, "rev-parse", f"HEAD:{path}")
        expected = package[key]
        if observed != expected:
            raise SystemExit(
                f"package component tree mismatch for {path}: observed={observed} expected={expected}"
            )

    digest_input = canonical_digest_input(manifest)
    if package.get("digest_input") != digest_input:
        raise SystemExit("manifest digest_input does not match bound component identities")
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    if package.get("package_digest_sha256") != digest:
        raise SystemExit(
            f"manifest package digest mismatch: computed={digest} manifest={package.get('package_digest_sha256')}"
        )
    if expected_digest and digest != expected_digest:
        raise SystemExit(f"package digest mismatch: manifest={digest} expected={expected_digest}")
    if int(manifest["target"]["qualified_major_version"]) != 16:
        raise SystemExit("manifest is not qualified for PostgreSQL 16")
    return manifest, digest, head, tree
