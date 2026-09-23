#!/usr/bin/env python3
"""Fail-closed source/package identity verification for BT2 qualification."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

POSTGRES_REPODIGEST_RE = re.compile(r"^postgres@sha256:[0-9a-f]{64}$")


def observe_postgres_container_image(container_id: str | None, database_url: str) -> dict[str, object]:
    if not container_id or not container_id.strip():
        raise SystemExit("POSTGRES_CONTAINER_ID or --postgres-container-id is required")
    if shutil.which("docker") is None:
        raise SystemExit("docker is required on PATH to verify PostgreSQL image identity")

    def docker(*args: str) -> str:
        cp = subprocess.run(
            ["docker", *args],
            text=True,
            capture_output=True,
            check=True,
        )
        return cp.stdout.strip()

    container_id = container_id.strip()
    running = docker("inspect", container_id, "--format", "{{.State.Running}}")
    if running != "true":
        raise SystemExit(f"PostgreSQL container is not running: {container_id}")

    image_id = docker("inspect", container_id, "--format", "{{.Image}}")
    if not image_id:
        raise SystemExit(f"PostgreSQL container image id unavailable: {container_id}")

    configured_image = docker("inspect", container_id, "--format", "{{.Config.Image}}")

    parsed = urlsplit(database_url)
    if parsed.scheme not in {"postgresql", "postgres"} or not parsed.hostname:
        raise SystemExit("DATABASE_URL must be an explicit postgres/postgresql URL")
    database_host = parsed.hostname
    try:
        database_port = parsed.port or 5432
    except ValueError as exc:
        raise SystemExit(f"invalid DATABASE_URL port: {exc}") from exc

    raw_port_bindings = docker(
        "inspect",
        container_id,
        "--format",
        '{{json (index .NetworkSettings.Ports "5432/tcp")}}',
    )
    try:
        port_bindings = json.loads(raw_port_bindings)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"invalid Docker PostgreSQL port binding JSON for {container_id}: {exc}"
        ) from exc
    if not isinstance(port_bindings, list) or not port_bindings:
        raise SystemExit(
            f"PostgreSQL container has no published 5432/tcp binding: {container_id}"
        )

    loopback_hosts = {"localhost", "127.0.0.1", "::1"}
    matching_bindings: list[dict[str, str]] = []
    for binding in port_bindings:
        if not isinstance(binding, dict):
            continue
        host_ip = binding.get("HostIp")
        host_port = binding.get("HostPort")
        if not isinstance(host_ip, str) or not isinstance(host_port, str):
            continue
        try:
            observed_port = int(host_port)
        except ValueError:
            continue
        if observed_port != database_port:
            continue
        if host_ip in {"", "0.0.0.0", "::"}:
            if database_host in loopback_hosts:
                matching_bindings.append({"HostIp": host_ip, "HostPort": host_port})
        elif database_host == host_ip:
            matching_bindings.append({"HostIp": host_ip, "HostPort": host_port})

    if not matching_bindings:
        raise SystemExit(
            "DATABASE_URL does not target the inspected PostgreSQL container's "
            f"published 5432/tcp endpoint: url_host={database_host!r} "
            f"url_port={database_port} bindings={port_bindings!r}"
        )

    raw_repo_digests = docker("image", "inspect", image_id, "--format", "{{json .RepoDigests}}")
    try:
        repo_digests = json.loads(raw_repo_digests)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid Docker RepoDigests JSON for {image_id}: {exc}") from exc
    if not isinstance(repo_digests, list):
        raise SystemExit(f"Docker RepoDigests must be a list for {image_id}")

    matching = sorted({
        value for value in repo_digests
        if isinstance(value, str) and POSTGRES_REPODIGEST_RE.fullmatch(value)
    })
    if len(matching) != 1:
        raise SystemExit(
            "expected exactly one verified postgres@sha256:<64 lowercase hex> RepoDigest; "
            f"observed={repo_digests!r}"
        )

    return {
        "verification_method": "DOCKER_CONTAINER_IMAGE_INSPECT",
        "container_id": container_id,
        "container_image_id": image_id,
        "configured_image": configured_image,
        "repo_digest": matching[0],
        "database_target_binding": {
            "database_host": database_host,
            "database_port": database_port,
            "container_port": 5432,
            "matching_published_bindings": matching_bindings,
        },
    }


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
