from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "database"

TREE_BINDINGS = {
    "schema_tree": "database/schema",
    "migrations_tree": "database/migrations",
    "tests_tree": "database/tests",
    "admin_tree": "database/admin",
    "data_tree": "database/data",
    "lantern_archive_tree": "archive/supabase-project-lantern",
    "loaders_tree": "database/loaders",
    "seeds_tree": "database/seeds",
    "qualification_tools_tree": "tools/qualification",
}


def manifest_path() -> Path:
    for name in (
        "BUILD_MANIFEST_V3.json",
        "BUILD_MANIFEST_V2.json",
        "BUILD_MANIFEST_V1.json",
    ):
        path = DB / name
        if path.is_file():
            return path
    raise SystemExit("no BT2 database build manifest found")


def _git_tree(path: str) -> str:
    cp = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return cp.stdout.strip()


def _assert_clean_bound_paths(paths: list[str]) -> None:
    cp = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no", "--", *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    if cp.stdout.strip():
        raise SystemExit("bound database package paths contain uncommitted changes")


def load_and_verify_manifest(
    *,
    expected_digest: str | None = None,
    postgres_major: int | None = None,
) -> tuple[Path, dict[str, Any], str]:
    path = manifest_path()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    identity = manifest["package_identity"]
    digest = identity["package_digest_sha256"]

    if expected_digest and digest != expected_digest:
        raise SystemExit(
            f"package digest mismatch: manifest={digest} expected={expected_digest}"
        )

    if postgres_major is not None:
        target = manifest["target"]
        supported: set[int] = set()
        if "canonical_qualified_major_version" in target:
            supported.add(int(target["canonical_qualified_major_version"]))
            supported.update(
                int(value)
                for value in target.get("compatibility_qualified_major_versions", [])
            )
        elif "qualified_major_version" in target:
            supported.add(int(target["qualified_major_version"]))
        if postgres_major not in supported:
            raise SystemExit(
                f"manifest does not admit PostgreSQL {postgres_major}: "
                f"supported={sorted(supported)}"
            )

    bound_paths = [
        path_value
        for key, path_value in TREE_BINDINGS.items()
        if key in identity
    ]
    _assert_clean_bound_paths(bound_paths)

    for key, repo_path in TREE_BINDINGS.items():
        expected_tree = identity.get(key)
        if expected_tree is None:
            continue
        actual_tree = _git_tree(repo_path)
        if actual_tree != expected_tree:
            raise SystemExit(
                f"package tree mismatch for {repo_path}: "
                f"manifest={expected_tree} actual={actual_tree}"
            )

    return path, manifest, digest
