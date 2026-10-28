#!/usr/bin/env python3
"""Verify V5 *source* package bindings; never claim installation/activation."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "native/project/PROJECT_FILES_MANIFEST_V5.json"
STALE_EFFECTIVE_ENTRYPOINT = re.compile(
    r"(?:PROJECT[_ ]INSTRUCTIONS[_ ]V[1-4]"
    r"|BT2[_ ]COORDINATOR[_ ]RECONSTRUCTION[_ ]V1"
    r"|BT2[_ ]EXODUS[_ ]WORKER[_ ]TOPOLOGY[_ ]V1"
    r"|BT2[_ ]RECOVERY[_ ]AND[_ ]STATE[_ ]V1)",
    flags=re.IGNORECASE,
)
REQUIRED_V5 = {
    "native/project/PROJECT_INSTRUCTIONS_V5.md",
    "native/project/BT2_NATIVE_RUNTIME_V2.md",
    "native/project/BT2_CODING_OPERATIONS_V2.md",
    "native/project/BT2_RECOVERY_AND_STATE_V2.md",
    "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md",
    "native/project/BT2_COORDINATOR_RECONSTRUCTION_V2.md",
    "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json",
    "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json",
    "native/project/INSTALL_V5.md",
    "docs/runtime/LANTERN_POSTGRESQL_OPERATOR_HANDSHAKE_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_READ_QUERIES_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_RUNTIME_CONTRACT_V4.md",
    "docs/runtime/LANTERN_POSTGRESQL_ACCEPTANCE_V4.md",
}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True,
                          check=True).stdout.strip()


def verify_recovery_pointers(instructions: str, reconstruction: str, topology: dict) -> None:
    """Reject misrouted future source packages without erasing historical V1."""
    # Source can mention its historical origins elsewhere, but these effective
    # entrypoints must not advertise a *second*, contradictory recovery route.
    # A positive search for V2 alone would accept an appended V1 instruction.
    for scope, effective_source in (("V5 instructions", instructions),
                                    ("V2 coordinator", reconstruction)):
        stale = STALE_EFFECTIVE_ENTRYPOINT.search(effective_source)
        if stale:
            raise ValueError(f"{scope} has contradictory historical entrypoint: {stale.group()}")
    for marker in (
        "BT2_EXODUS_WORKER_TOPOLOGY_V2.json",
        "BT2_COORDINATOR_RECONSTRUCTION_V2.md",
        "BT2_RECOVERY_AND_STATE_V2.md",
        "provider-neutral PostgreSQL through SQL Connectome",
        "LANTERN_CURRENTNESS = UNKNOWN",
    ):
        if marker not in instructions:
            raise ValueError(f"V5 instructions missing current marker: {marker}")
    if "Use `native/project/BT2_RECOVERY_AND_STATE_V2.md`" not in reconstruction:
        raise ValueError("coordinator reconstruction points to stale recovery state")
    if topology.get("schema_version") != "BT2_EXODUS_WORKER_TOPOLOGY_V2":
        raise ValueError("V5 worker map schema mismatch")
    if topology.get("source_seed_commit") is None or "source_commit" in topology:
        raise ValueError("V2 topology must label historical seed provenance explicitly")
    recovery = topology.get("common_recovery")
    if type(recovery) is not list or len(recovery) < 2:
        raise ValueError("V5 worker recovery is missing")
    if "PROJECT_INSTRUCTIONS_V5" not in recovery[0]:
        raise ValueError("V5 worker recovery points to stale Project Instructions")
    if not any("BT2_RECOVERY_AND_STATE_V2" in step for step in recovery):
        raise ValueError("V5 worker recovery lacks current domain recovery path")
    if any(type(step) is not str or STALE_EFFECTIVE_ENTRYPOINT.search(step)
           for step in recovery):
        raise ValueError("V5 worker recovery retains an active stale pointer")
    if topology.get("chat_dependency") is not False:
        raise ValueError("worker topology cannot require chat continuity")


def verify_retained_historical_payload(ancestor: str) -> None:
    """Prevent source-passing V5 checks after silently rewriting frozen V4 bytes."""
    for path in ("native/project/PROJECT_FILES_MANIFEST_V4.json",
                 "native/project/BT2_COORDINATOR_RECONSTRUCTION_V1.md",
                 "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"):
        if not (ROOT / path).is_file():
            raise ValueError(f"retained V4 source missing: {path}")
        if _git("hash-object", path) != _git("rev-parse", f"{ancestor}:{path}"):
            raise ValueError(f"retained V4 source changed after V5 binding: {path}")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["schema"] != "BT2_NATIVE_PROJECT_FILES_MANIFEST_V5":
        raise SystemExit("wrong V5 manifest schema")
    if manifest["runtime_contract"] != "POSTGRESQL_SQL_CONNECTOME_V4":
        raise SystemExit("V5 source must retain V4 runtime contract")
    if manifest["installation_state"] != "SOURCE_CANDIDATE_NOT_INSTALLED":
        raise SystemExit("V5 source must not self-claim installation")
    if manifest["runtime_state_at_source_binding"] != {
        "bt2_runtime_reconstruction": "NOT_ESTABLISHED",
        "lantern_state_reconstruction": "NOT_ESTABLISHED",
        "v4_runtime_qualification": "NOT_ESTABLISHED",
        "lantern_currentness": "UNKNOWN",
    }:
        raise SystemExit("V5 source must preserve unverified runtime-currentness ceiling")
    protected = manifest["protected_effects"]
    if protected != {
        "merge_deploy_not_granted": True,
        "project_installation_not_granted": True,
        "producer_enablement_not_granted": True,
        "historical_provider_deletion_not_granted": True,
    }:
        raise SystemExit("V5 must preserve protected-effect fences")
    ancestor = manifest["payload_source_commit"]
    if _git("rev-parse", f"{ancestor}^{{tree}}") != manifest["payload_source_tree"]:
        raise SystemExit("V5 ancestor tree mismatch")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
                      cwd=ROOT).returncode != 0:
        raise SystemExit("V5 payload ancestor not present in HEAD")

    entries = {
        manifest["project_instructions"]["path"]: manifest["project_instructions"]["git_blob"],
        manifest["installation_packet"]["path"]: manifest["installation_packet"]["git_blob"],
    }
    for item in manifest["required_project_files"]:
        if item["path"] in entries:
            raise SystemExit("V5 duplicate manifest entry")
        entries[item["path"]] = item["git_blob"]
    if set(entries) != REQUIRED_V5:
        raise SystemExit("V5 manifest member set mismatch")
    for rel, expected in sorted(entries.items()):
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"V5 payload file absent: {rel}")
        # Bind both the immutable candidate *payload commit* and live file bytes.
        if _git("rev-parse", f"{ancestor}:{rel}") != expected:
            raise SystemExit(f"V5 manifest does not match payload ancestry: {rel}")
        if _git("hash-object", rel) != expected:
            raise SystemExit(f"V5 file changed after payload binding: {rel}")

    verify_recovery_pointers(
        (ROOT / "native/project/PROJECT_INSTRUCTIONS_V5.md").read_text(encoding="utf-8"),
        (ROOT / "native/project/BT2_COORDINATOR_RECONSTRUCTION_V2.md").read_text(encoding="utf-8"),
        json.loads((ROOT / "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json").read_text(encoding="utf-8")),
    )
    # Preserve historical V4 bytes, not merely historical path presence.
    verify_retained_historical_payload(ancestor)
    print(f"BT2_NATIVE_V5_SOURCE_PACKAGE_PASS payload_commit={ancestor} "
          "runtime=NOT_ESTABLISHED installation=NOT_INSTALLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
