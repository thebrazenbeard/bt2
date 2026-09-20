#!/usr/bin/env python3
"""Run the exact BT2 PostgreSQL 16 canonical blank-rebuild qualification.

Requires:
  - Python 3
  - psql on PATH
  - DATABASE_URL or --database-url pointing at a disposable *empty* PostgreSQL 16 DB

This runner does not append acceptance receipts or mutate any production provider.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True

from source_identity import observe_postgres_container_image, verify_manifest_source

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "database"
FINAL_ORACLE = DB / "tests" / "0011_canonical_state_reconstruction_oracle.sql"
SKIPPED_DATA = DB / "data" / "0005_project_lantern_cohosted_history_receipt_v1.sql"
CANONICAL_DATA_BEFORE_HISTORY = [
    DB / "data" / "0001_verified_training_source_registry_v1.sql",
    DB / "data" / "0002_verified_training_source_registry_receipt_v2.sql",
    DB / "data" / "0003_four_verified_training_source_registration_v1.sql",
    DB / "data" / "0004_verified_training_source_registry_receipt_v3.sql",
]
CANONICAL_DATA_AFTER_HISTORY = [
    DB / "data" / "0006_project_lantern_cohosted_history_receipt_v2.sql",
    DB / "data" / "0007_remaining_numbered_training_source_registration_v1.sql",
    DB / "data" / "0008_verified_training_source_registry_receipt_v4.sql",
]


def run(cmd: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, input=input_text, text=True, check=True)


def psql_args(url: str) -> list[str]:
    return ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", url]


def psql_file(url: str, path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"missing required SQL file: {path.relative_to(ROOT)}")
    run(psql_args(url) + ["-f", str(path)])


def psql_scalar(url: str, sql: str) -> str:
    cp = subprocess.run(
        psql_args(url) + ["-Atqc", sql],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return cp.stdout.strip()


def assert_empty(url: str) -> None:
    relation_count = psql_scalar(
        url,
        "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname IN ('bt2','bt2_legacy') AND c.relkind IN ('r','p','v','m');",
    )
    if relation_count != "0":
        raise SystemExit(f"qualification database is not blank: {relation_count} BT2 relations already exist")


def manifest_path() -> Path:
    v2 = DB / "BUILD_MANIFEST_V2.json"
    return v2 if v2.is_file() else DB / "BUILD_MANIFEST_V1.json"


def check_manifest(expected_digest: str | None) -> tuple[str, str, str]:
    path = manifest_path()
    _, digest, head, tree = verify_manifest_source(ROOT, path, expected_digest)
    print(
        f"QUALIFICATION_MANIFEST={path.relative_to(ROOT)} package_digest={digest} source_commit={head} source_tree={tree}",
        flush=True,
    )
    return digest, head, tree


def command_version(cmd: list[str]) -> str:
    cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    return (cp.stdout or cp.stderr).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    ap.add_argument("--expected-package-digest")
    ap.add_argument("--evidence-out")
    ap.add_argument("--postgres-container-id", default=os.environ.get("POSTGRES_CONTAINER_ID"))
    args = ap.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if shutil.which("psql") is None:
        raise SystemExit("psql is required on PATH")

    package_digest, source_commit, source_tree = check_manifest(args.expected_package_digest)
    image_attestation = observe_postgres_container_image(args.postgres_container_id, args.database_url)

    version_num = psql_scalar(args.database_url, "SHOW server_version_num;")
    server_version = psql_scalar(args.database_url, "SHOW server_version;")
    if not version_num.startswith("16"):
        raise SystemExit(f"PostgreSQL 16 required; observed server_version_num={version_num}")

    assert_empty(args.database_url)
    run(psql_args(args.database_url) + ["-c", "CREATE EXTENSION IF NOT EXISTS pgcrypto;"])

    schema_files = sorted((DB / "schema").glob("*.sql"))
    migration_files = sorted((DB / "migrations").glob("*.sql"))
    for path in schema_files:
        psql_file(args.database_url, path)
    for path in migration_files:
        psql_file(args.database_url, path)

    # Regression suite runs before durable seeds because several smoke tests create
    # intentionally synthetic subjects under rollback. 0011 is the final state oracle.
    regression_tests = [path for path in sorted((DB / "tests").glob("*.sql")) if path != FINAL_ORACLE]
    for path in regression_tests:
        psql_file(args.database_url, path)

    # Canonical durable state. Run seed files twice to prove replay convergence.
    seeds = sorted((DB / "seeds").glob("*.sql"))
    if not seeds:
        raise SystemExit("canonical seed directory is empty")
    for _ in range(2):
        for path in seeds:
            psql_file(args.database_url, path)

    # Explicit frontier sequence. Never glob database/data: 0005 is a retained failed V1 subject.
    for path in CANONICAL_DATA_BEFORE_HISTORY:
        psql_file(args.database_url, path)

    loader = DB / "loaders" / "lantern_cohosted_history_v2.py"
    cp = subprocess.run(
        [sys.executable, str(loader), "--mode", "apply"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    run(psql_args(args.database_url), input_text=cp.stdout)

    if not SKIPPED_DATA.is_file():
        raise SystemExit("expected retained failed Lantern V1 data subject is missing")
    print(f"SKIP historical failed candidate: {SKIPPED_DATA.relative_to(ROOT)}", flush=True)

    for path in CANONICAL_DATA_AFTER_HISTORY:
        psql_file(args.database_url, path)

    psql_file(args.database_url, FINAL_ORACLE)

    executed_order = (
        [str(path.relative_to(ROOT)) for path in schema_files]
        + [str(path.relative_to(ROOT)) for path in migration_files]
        + [str(path.relative_to(ROOT)) for path in regression_tests]
        + [str(path.relative_to(ROOT)) for _ in range(2) for path in seeds]
        + [str(path.relative_to(ROOT)) for path in CANONICAL_DATA_BEFORE_HISTORY]
        + [str(loader.relative_to(ROOT)) + " --mode apply"]
        + ["SKIP " + str(SKIPPED_DATA.relative_to(ROOT))]
        + [str(path.relative_to(ROOT)) for path in CANONICAL_DATA_AFTER_HISTORY]
        + [str(FINAL_ORACLE.relative_to(ROOT))]
    )
    evidence = {
        "source_commit": source_commit,
        "source_tree": source_tree,
        "package_digest_sha256": package_digest,
        "postgres_image_digest": image_attestation["repo_digest"],
        "postgres_image_attestation": image_attestation,
        "postgres_server_version": server_version,
        "postgres_major": 16,
        "git_version": command_version(["git", "--version"]),
        "psql_version": command_version(["psql", "--version"]),
        "python_version": sys.version.split()[0],
        "executed_order": executed_order,
        "blank_rebuild": "PASS",
        "canonical_state_reconstruction": "PASS",
        "topology_sha256": "45d262aae7285a69a66a3d5b35c04537899ba33f5eb7388b9731071e8907c0d8",
        "training_frontier_count": 13,
        "training_frontier_sha256": "8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc",
        "lantern_state_sha256": "29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5",
        "lantern_current_producer_authority": 0,
        "cohosted_history_row_count": 16,
        "cohosted_history_sha256": "6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712",
        "qualification_effect": "NONE",
        "runtime_installation_effect": "NONE",
        "destructive_retirement_effect": "NONE",
    }
    text = json.dumps(evidence, indent=2, sort_keys=True)
    print(text)
    if args.evidence_out:
        Path(args.evidence_out).write_text(text + "\n", encoding="utf-8")

    print(f"BT2_POSTGRES16_CANONICAL_BLANK_REBUILD_PASS package_digest={package_digest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
