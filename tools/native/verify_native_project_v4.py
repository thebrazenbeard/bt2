#!/usr/bin/env python3
"""Fail-closed static verifier for the BT2 native Project V4 package."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "native/project/PROJECT_FILES_MANIFEST_V4.json"
EXPECTED_POSTURE_SHA256 = "828a3995dd0e49999c7ebc51753cfa17508935b45b99c01c79f456845994826f"

EXPECTED_PAYLOAD_PATHS = {
    "native/project/PROJECT_INSTRUCTIONS_V4.md",
    "native/project/BT2_NATIVE_RUNTIME_V2.md",
    "native/project/BT2_CODING_OPERATIONS_V2.md",
    "native/project/BT2_RECOVERY_AND_STATE_V2.md",
    "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md",
    "docs/runtime/RUNTIME_PROVIDER_DEGRADATION_V1.md",
    "docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md",
    "docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V4.md",
    "docs/runtime/LANTERN_WOWSQL_RUNTIME_CONTRACT_V4.md",
    "docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V4.md",
    "docs/runtime/HYPERCONNECTOME_RUNTIME_MODEL.md",
    "docs/runtime/PLASTICITY_AND_STATE_GOVERNANCE.md",
}

LANTERN_V4_PATHS = {
    "docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md",
    "docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V4.md",
    "docs/runtime/LANTERN_WOWSQL_RUNTIME_CONTRACT_V4.md",
    "docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V4.md",
}


def git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if cp.returncode != 0:
        raise SystemExit(
            f"git {' '.join(args)} failed ({cp.returncode}): {cp.stderr.strip()}"
        )
    return cp.stdout.strip()


def git_text(subject: str, path: str) -> str:
    return git("show", f"{subject}:{path}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    require(
        manifest.get("schema") == "BT2_NATIVE_PROJECT_FILES_MANIFEST_V4",
        "unexpected V4 manifest schema",
    )
    require(
        manifest.get("payload_digest_members")
        == "project_instructions + required_project_files",
        "payload digest membership is not explicit/canonical",
    )
    require(
        manifest.get("general_bt2_availability_dependency") is False,
        "WoWSQL must not be a general BT2 availability dependency",
    )
    require(
        manifest.get("supabase_lantern_fallback") == "FORBIDDEN",
        "Supabase Lantern fallback must remain forbidden",
    )

    source_commit = manifest["payload_source_commit"]
    source_tree = manifest["payload_source_tree"]
    observed_tree = git("rev-parse", f"{source_commit}^{{tree}}")
    require(
        observed_tree == source_tree,
        f"payload source tree mismatch: observed={observed_tree} expected={source_tree}",
    )

    payload = [manifest["project_instructions"], *manifest["required_project_files"]]
    payload_paths = {entry["path"] for entry in payload}
    require(
        payload_paths == EXPECTED_PAYLOAD_PATHS,
        "V4 payload membership differs from the canonical expected set",
    )
    require(len(payload_paths) == len(payload), "duplicate V4 payload paths")
    require(
        LANTERN_V4_PATHS.issubset(payload_paths),
        "complete four-file Lantern V4 package is not payload-bound",
    )

    for entry in payload:
        observed_blob = git("rev-parse", f"{source_commit}:{entry['path']}")
        require(
            observed_blob == entry["git_blob"],
            f"payload blob mismatch for {entry['path']}: "
            f"observed={observed_blob} expected={entry['git_blob']}",
        )

    support_entries = [manifest["source_validation"], manifest["installer"]]
    support_entries.extend(manifest.get("qualification_support", []))
    support_entries.extend(manifest.get("behavior_contract_support", []))
    for entry in support_entries:
        observed_blob = git("rev-parse", f"{source_commit}:{entry['path']}")
        require(
            observed_blob == entry["git_blob"],
            f"support blob mismatch for {entry['path']}: "
            f"observed={observed_blob} expected={entry['git_blob']}",
        )

    digest_input = "".join(
        f"{entry['path']}|{entry['git_blob']}\n"
        for entry in sorted(payload, key=lambda item: item["path"])
    )
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    require(
        digest == manifest["payload_digest"],
        f"payload digest mismatch: computed={digest} manifest={manifest['payload_digest']}",
    )

    instructions = git_text(source_commit, "native/project/PROJECT_INSTRUCTIONS_V4.md")
    installer = git_text(source_commit, "native/project/INSTALL_V4.md")
    spec = git_text(source_commit, "specs/BT2_RUNTIME_PROVIDER_RESILIENCE_V1.yaml")

    instruction_requirements = (
        "# PROJECT LANTERN NATIVE RUNTIME V4",
        "LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md",
        "LANTERN_WOWSQL_READ_QUERIES_V4.md",
        "WoWSQL is not a general availability prerequisite",
        "Never use Supabase or another database as an implicit Lantern/current-runtime fallback.",
        "Mark WoWSQL-dependent facts `UNKNOWN` or `UNAVAILABLE`",
        "This failure does not block unrelated source/review/coordination work.",
        "## Adversarial collaboration posture",
        "Try to kill the literal proposition",
        "Direct commands and factual requests with no embedded proposal do not trigger",
        "Only then infer the underlying objective",
        "`UNKNOWN` is not `SURVIVES`",
        "grants no protected-effect authority",
    )
    for token in instruction_requirements:
        require(token in instructions, f"Project Instructions V4 missing required token: {token}")

    for path in sorted(LANTERN_V4_PATHS):
        require(
            Path(path).name in installer,
            f"installer does not name required Lantern V4 file: {path}",
        )
    require(
        "Lantern V3 remains fail-closed" not in installer,
        "installer contains stale active Lantern V3 wording",
    )
    require(
        "Lantern V4 remains fail-closed with no Supabase fallback." in installer,
        "installer does not state active Lantern V4 fail-closed rule",
    )

    require(
        "BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md" in installer,
        "installer does not name adversarial collaboration Project file",
    )
    require(
        "source/package conformance only" in installer
        and "BEHAVIOR_VERIFIED" in installer,
        "installer collapses source qualification into behavioral installation",
    )

    posture_path = ROOT / "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md"
    posture_digest = hashlib.sha256(posture_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    require(
        posture_digest == EXPECTED_POSTURE_SHA256,
        f"adversarial posture digest mismatch: {posture_digest}",
    )
    adversarial = manifest.get("adversarial_collaboration", {})
    require(
        adversarial.get("source_artifact_sha256") == EXPECTED_POSTURE_SHA256,
        "manifest does not bind exact adversarial posture source digest",
    )
    require(
        adversarial.get("native_project_file")
        == "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md",
        "manifest adversarial native Project file binding is wrong",
    )
    require(
        adversarial.get("effect_authority") == "UNCHANGED",
        "adversarial posture must not grant effect authority",
    )

    spec_requirements = (
        "general_bt2_availability_dependency: false",
        "unavailable_result: UNKNOWN",
        "fallback_forbidden:",
        "- SUPABASE",
        "rule: WOWSQL_OUTAGE_DOES_NOT_BLOCK_SOURCE_WORK",
        "rule: LANTERN_CURRENTNESS_HAS_NO_PROVIDER_FALLBACK",
        "rule: PROVIDER_RECOVERY_REQUIRES_FRESH_READBACK",
    )
    for token in spec_requirements:
        require(token in spec, f"resilience spec missing required token: {token}")

    lantern_package = manifest["lantern_package"]
    require(lantern_package.get("version") == "V4", "active Lantern package is not V4")
    require(
        lantern_package.get("same_subject_required") is True,
        "Lantern V4 same-subject requirement is not enforced",
    )
    require(
        lantern_package.get("source_commit") == source_commit
        and lantern_package.get("source_tree") == source_tree,
        "Lantern package binding diverges from V4 payload source subject",
    )

    print(
        "BT2_NATIVE_PROJECT_V4_STATIC_PASS "
        f"source_commit={source_commit} source_tree={source_tree} "
        f"payload_digest={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
