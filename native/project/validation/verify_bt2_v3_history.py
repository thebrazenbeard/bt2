"""Check the preserved V3 project-file witness against its immutable Git seed.

This is a source-integrity check, not proof of installation or a live runtime.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = "native/project/PROJECT_FILES_MANIFEST_V3.json"
SEED = "8aa34d42f014e3829f38faa875d7a45e99aa087c"
SEED_TREE = "2b1581eca30aa9de197ee198b771e0cdad00ae7c"
MANIFEST_COMMIT = "f47d458e1517d51fbdf182097be53520ba70128a"
MANIFEST_BLOB = "ae5538e50f545e39ca9c2d4425cf13f87199c2d2"
SCHEMA = "BT2_NATIVE_PROJECT_FILES_MANIFEST_V3"
REQUIRED = frozenset(
    (
        "native/project/PROJECT_INSTRUCTIONS_V3.md",
        "native/project/BT2_NATIVE_RUNTIME_V1.md",
        "native/project/BT2_CODING_OPERATIONS_V1.md",
        "native/project/BT2_RECOVERY_AND_STATE_V1.md",
        "docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V3.md",
        "docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V3.md",
        "docs/runtime/LANTERN_WOWSQL_RUNTIME_CONTRACT_V3.md",
        "docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V3.md",
        "docs/runtime/HYPERCONNECTOME_RUNTIME_MODEL.md",
        "docs/runtime/PLASTICITY_AND_STATE_GOVERNANCE.md",
    )
)


def git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    return git_bytes(root, *args, input_bytes=input_bytes).decode().strip()


def git_bytes(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def verify(root: Path = ROOT, manifest_bytes: bytes | None = None, overrides: dict[str, bytes] | None = None) -> None:
    """Raise ValueError on altered witness or missing/altered seed objects.

    The live V3 acceptance doc was legitimately amended after the seed commit,
    so this intentionally verifies *historical* bytes, not current V3 bytes.
    Optional overrides simulate altered historical bytes for negative controls.
    """
    if git(root, "rev-parse", f"{SEED}^{{tree}}") != SEED_TREE:
        raise ValueError("V3 seed tree mismatch")
    git(root, "merge-base", "--is-ancestor", SEED, "HEAD")
    git(root, "merge-base", "--is-ancestor", MANIFEST_COMMIT, "HEAD")
    raw = manifest_bytes if manifest_bytes is not None else (root / MANIFEST).read_bytes()
    if git(root, "rev-parse", f"{MANIFEST_COMMIT}:{MANIFEST}") != MANIFEST_BLOB:
        raise ValueError("V3 historical manifest object mismatch")
    if git(root, "hash-object", "--stdin", input_bytes=raw) != MANIFEST_BLOB:
        raise ValueError("V3 historical manifest bytes modified")
    manifest = json.loads(raw)
    if manifest.get("schema") != SCHEMA or manifest.get("payload_source_commit") != SEED:
        raise ValueError("V3 schema/seed mismatch")
    if manifest.get("payload_source_tree") != SEED_TREE:
        raise ValueError("V3 claimed tree mismatch")
    if manifest.get("payload_digest_algorithm") != "sha256(sorted(path|git_blob|sha256)+newline)":
        raise ValueError("V3 digest algorithm mismatch")
    entries = [manifest["project_instructions"], *manifest["required_project_files"]]
    paths = [entry["path"] for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != REQUIRED:
        raise ValueError("V3 file list differs from immutable expected set")
    if overrides and not set(overrides).issubset(REQUIRED):
        raise ValueError("unknown payload override")
    lines = []
    for entry in entries:
        path = entry["path"]
        historical_blob = git(root, "rev-parse", f"{SEED}:{path}")
        payload = overrides[path] if overrides and path in overrides else git_bytes(root, "show", f"{SEED}:{path}")
        live_blob = git(root, "hash-object", "--stdin", input_bytes=payload)
        live_sha = hashlib.sha256(payload).hexdigest()
        if entry["git_blob"] != historical_blob or entry["git_blob"] != live_blob or entry["sha256"] != live_sha:
            raise ValueError(f"V3 source witness mismatch: {path}")
        lines.append(f"{path}|{live_blob}|{live_sha}\n")
    aggregate = hashlib.sha256("".join(sorted(lines)).encode()).hexdigest()
    if manifest.get("payload_digest") != aggregate:
        raise ValueError("V3 aggregate manifest digest mismatch")


if __name__ == "__main__":
    verify()
    print("PASS: V3 seed-object history and manifest digest (not live V3 file, installed, or runtime qualification)")
