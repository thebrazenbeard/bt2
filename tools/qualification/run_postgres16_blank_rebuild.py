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
    # Refuse to treat an already-built database as a blank-rebuild subject.
    relation_count = psql_scalar(
        url,
        "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname IN ('bt2','bt2_legacy') AND c.relkind IN ('r','p','v','m');",
    )
    if relation_count != "0":
        raise SystemExit(f"qualification database is not blank: {relation_count} BT2 relations already exist")


def check_manifest(expected_digest: str | None) -> str:
    manifest_path = DB / "BUILD_MANIFEST_V1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = manifest["package_identity"]["package_digest_sha256"]
    if expected_digest and digest != expected_digest:
        raise SystemExit(f"package digest mismatch: manifest={digest} expected={expected_digest}")
    if int(manifest["target"]["qualified_major_version"]) != 16:
        raise SystemExit("manifest is not qualified for PostgreSQL 16")
    return digest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    ap.add_argument("--expected-package-digest")
    args = ap.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if shutil.which("psql") is None:
        raise SystemExit("psql is required on PATH")

    package_digest = check_manifest(args.expected_package_digest)

    version_num = psql_scalar(args.database_url, "SHOW server_version_num;")
    if not version_num.startswith("16"):
        raise SystemExit(f"PostgreSQL 16 required; observed server_version_num={version_num}")

    assert_empty(args.database_url)

    run(psql_args(args.database_url) + ["-c", "CREATE EXTENSION IF NOT EXISTS pgcrypto;"])

    # Structural substrate.
    for path in sorted((DB / "schema").glob("*.sql")):
        psql_file(args.database_url, path)
    for path in sorted((DB / "migrations").glob("*.sql")):
        psql_file(args.database_url, path)

    # Run the regression suite against the structurally blank database first.
    # 0011 is the persistent-state oracle and is intentionally deferred until after reconstruction.
    for path in sorted((DB / "tests").glob("*.sql")):
        if path == FINAL_ORACLE:
            continue
        psql_file(args.database_url, path)

    # Canonical durable state. Replay seeds once to prove idempotent convergence.
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

    # Final semantic acceptance oracle over the persistently reconstructed state.
    psql_file(args.database_url, FINAL_ORACLE)

    print(f"BT2_POSTGRES16_CANONICAL_BLANK_REBUILD_PASS package_digest={package_digest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
