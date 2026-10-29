from __future__ import annotations

import hashlib
import json
import re
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

# V1–V3 identities included every file under tests/, even unrelated BT2 work.
# V4 supersedes that broad binding without changing the historical manifests.
SCOPED_QUALIFICATION_PATTERN = "tests/test_postgres*.py"
SCOPED_QUALIFICATION_FIELD = "qualification_tests_files_sha256"
_GIT_OBJECT_ID = re.compile(r"^[0-9a-f]{40}$")


def manifest_path() -> Path:
    for name in (
        "BUILD_MANIFEST_V4.json",
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


def _git_blob(path: str) -> str:
    cp = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return cp.stdout.strip()


def _qualification_paths_at_head() -> list[str]:
    cp = subprocess.run(
        ["git", "ls-tree", "-r", "-z", "HEAD", "--", "tests"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    paths = []
    for entry in cp.stdout.split("\0"):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        if not (
            path.startswith("tests/")
            and Path(path).name.startswith("test_postgres")
            and path.endswith(".py")
        ):
            continue
        mode, kind, _object_id = metadata.split()
        if mode != "100644" or kind != "blob":
            raise SystemExit(f"V4 qualification test must be a regular Git file: {path}")
        paths.append(path)
    return sorted(paths)


def scoped_qualification_digest(files: dict[str, str]) -> str:
    """SHA-256 of newline-delimited, path-sorted Git blob identities."""
    canonical = "".join(f"{path}:{files[path]}\n" for path in sorted(files))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _verify_scoped_qualification_tests(identity: dict[str, Any]) -> list[str]:
    files = identity.get("qualification_tests_files")
    if not isinstance(files, dict) or not files:
        raise SystemExit("V4 requires a nonempty qualification_tests_files mapping")
    if not all(
        isinstance(path, str)
        and re.fullmatch(r"tests/(?:[^/]+/)*test_postgres[^/]*\.py", path)
        and isinstance(blob, str)
        and _GIT_OBJECT_ID.fullmatch(blob)
        for path, blob in files.items()
    ):
        raise SystemExit("V4 qualification test entries must be exact paths and Git blob IDs")
    expected_paths = sorted(files)
    actual_paths = _qualification_paths_at_head()
    if actual_paths != expected_paths:
        raise SystemExit(
            "V4 qualification test membership mismatch: "
            f"manifest={expected_paths} HEAD={actual_paths}"
        )
    # An untracked matching test must not silently escape package qualification.
    worktree_paths = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "tests").rglob("test_postgres*.py")
    )
    if worktree_paths != actual_paths:
        raise SystemExit(
            "V4 qualification test worktree membership mismatch: "
            f"HEAD={actual_paths} worktree={worktree_paths}"
        )
    _assert_clean_bound_paths(actual_paths)
    for path in actual_paths:
        observed = _git_blob(path)
        if observed != files[path]:
            raise SystemExit(
                f"V4 qualification test blob mismatch for {path}: "
                f"manifest={files[path]} HEAD={observed}"
            )
    computed = scoped_qualification_digest(files)
    if identity.get(SCOPED_QUALIFICATION_FIELD) != computed:
        raise SystemExit(
            "V4 qualification test set digest mismatch: "
            f"manifest={identity.get(SCOPED_QUALIFICATION_FIELD)} actual={computed}"
        )
    return actual_paths


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
    is_v4 = manifest.get("manifest_version") == "BT2_DATABASE_BUILD_MANIFEST_V4"
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
        if key in identity and not (is_v4 and key == "qualification_tests_tree")
    ]
    if is_v4:
        parts.append(f"qualification-tests-scoped:{identity[SCOPED_QUALIFICATION_FIELD]}")
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
    if manifest.get("manifest_version") == "BT2_DATABASE_BUILD_MANIFEST_V4":
        if "qualification_tests_tree" in identity:
            raise SystemExit("V4 must not retain broad qualification_tests_tree binding")
        if "qualification_tests_files" not in identity:
            raise SystemExit("V4 requires scoped qualification test blob bindings")
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

    if manifest.get("manifest_version") == "BT2_DATABASE_BUILD_MANIFEST_V4":
        _verify_scoped_qualification_tests(identity)

    return path, manifest, digest
