#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "native/project/PROJECT_FILES_MANIFEST_V4.json"

REQUIRED_V4 = {
    "native/project/PROJECT_INSTRUCTIONS_V4.md",
    "native/project/BT2_NATIVE_RUNTIME_V2.md",
    "native/project/INSTALL_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_OPERATOR_HANDSHAKE_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_READ_QUERIES_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_RUNTIME_CONTRACT_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_ACCEPTANCE_V4.md",
}

HISTORICAL_V3 = {
    "docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V3.md",
    "docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V3.md",
    "docs/runtime/LANTERN_WOWSQL_RUNTIME_CONTRACT_V3.md",
    "docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V3.md",
}


def git_blob(path: Path) -> str:
    cp = subprocess.run(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return cp.stdout.strip()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if manifest["schema"] != "BT2_NATIVE_PROJECT_FILES_MANIFEST_V4":
        raise SystemExit("unexpected V4 manifest schema")
    if manifest["runtime_contract"] != "POSTGRESQL_SQL_CONNECTOME_V4":
        raise SystemExit("V4 manifest is not provider-neutral PostgreSQL/SQL Connectome")

    state = manifest["runtime_state_at_source_binding"]
    if state["lantern_currentness"] != "UNKNOWN":
        raise SystemExit("source candidate must not claim Lantern currentness")
    if state["bt2_runtime_reconstruction"] != "NOT_ESTABLISHED":
        raise SystemExit("source candidate must not claim BT2 runtime reconstruction")
    if state["v4_runtime_qualification"] != "NOT_ESTABLISHED":
        raise SystemExit("source candidate must not claim V4 runtime qualification")

    protected = manifest["protected_effects"]
    if not all(protected.values()):
        raise SystemExit("V4 manifest must keep all protected-effect fences engaged")

    manifest_entries = {
        manifest["project_instructions"]["path"]: manifest["project_instructions"]["git_blob"],
        manifest["installation_packet"]["path"]: manifest["installation_packet"]["git_blob"],
    }
    manifest_entries.update(
        {entry["path"]: entry["git_blob"] for entry in manifest["required_project_files"]}
    )

    if set(manifest_entries) != REQUIRED_V4:
        missing = sorted(REQUIRED_V4 - set(manifest_entries))
        extra = sorted(set(manifest_entries) - REQUIRED_V4)
        raise SystemExit(f"V4 manifest membership mismatch missing={missing} extra={extra}")

    for rel, expected_blob in sorted(manifest_entries.items()):
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"missing V4 file: {rel}")
        actual_blob = git_blob(path)
        if actual_blob != expected_blob:
            raise SystemExit(
                f"V4 blob mismatch for {rel}: expected={expected_blob} actual={actual_blob}"
            )

    for rel in sorted(HISTORICAL_V3):
        if not (ROOT / rel).is_file():
            raise SystemExit(f"historical V3 evidence was removed: {rel}")

    instructions = (ROOT / "native/project/PROJECT_INSTRUCTIONS_V4.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "provider-neutral PostgreSQL through SQL Connectome",
        "retired from the currentness role",
        "LANTERN_CURRENTNESS = UNKNOWN",
        "Do not fall back to WoWSQL, Supabase",
    ]
    for phrase in required_phrases:
        if phrase not in instructions:
            raise SystemExit(f"V4 instructions missing required boundary: {phrase}")

    read_contract = (
        ROOT / "docs/runtime/LANTERN_POSTGRESQL_READ_QUERIES_V4.md"
    ).read_text(encoding="utf-8")
    for phrase in [
        "REPEATABLE READ READ ONLY",
        "bt2.material_cut_v1",
        "bt2.runtime_visible_materials_v1",
    ]:
        if phrase not in read_contract:
            raise SystemExit(f"V4 read contract missing: {phrase}")

    print(
        "BT2_LANTERN_POSTGRESQL_V4_SOURCE_PACKAGE_PASS "
        f"payload_source_commit={manifest['payload_source_commit']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
