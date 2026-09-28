from __future__ import annotations

import hashlib
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
    "qualification_tests_tree": "tests",
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


def canonical_digest_input(manifest: dict[str, Any]) -> str:
    identity = manifest["package_identity"]
    labels = {
        "schema_tree": "schema",
        "migrations_tree": "migrations",
        "tests_tree": "tests",
        "admin_tree": "admin",
        "data_tree": "data",
        "lantern_archive_tree": "archive",
        "loaders_tree": "loaders",
        "seeds_tree": "seeds",
        "qualification_tools_tree": "qualification-tools",
        "qualification_tests_tree": "qualification-tests",
    }
    parts = [
        f"{labels[key]}:{identity[key]}"
        for key in TREE_BINDINGS
        if key in identity
    ]
    target = manifest["target"]
    if "canonical_qualified_major_version" in target:
        parts.append(
            f"canonical-postgres-major:{int(target['canonical_qualified_major_version'])}"
        )
        for value in target.get("compatibility_qualified_major_versions", []):
            parts.append(f"compat-postgres-major:{int(value)}")
    else:
        parts.append(f"postgres-major:{int(target['qualified_major_version'])}")
    for extension in target.get("required_extensions", []):
        parts.append(f"required-extension:{extension}")
    return "|".join(parts)


def load_and_verify_manifest(
    *,
    expected_digest: str | None = None,
    postgres_major: int | None = None,
) -> tuple[Path, dict[str, Any], str]:
    path = manifest_path()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    identity = manifest["package_identity"]
    digest_input = canonical_digest_input(manifest)
    if identity.get("digest_input") != digest_input:
        raise SystemExit("manifest digest_input does not match bound component identities")
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    if identity.get("package_digest_sha256") != digest:
        raise SystemExit(
            f"manifest package digest mismatch: computed={digest} "
            f"manifest={identity.get('package_digest_sha256')}"
        )

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
