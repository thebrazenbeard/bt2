#!/usr/bin/env python3
"""Disposable PostgreSQL 16 regressions for hosted producer-boundary verification."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools" / "qualification" / "verify_wowsql_effective_producer_boundary_v1.sql"
IMAGE = "postgres:16"
CONTAINER = f"bt2-boundary-{uuid.uuid4().hex[:12]}"


def docker(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args], text=True, input=input_text, capture_output=True, check=check
    )


def psql(sql: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return docker(
        "exec", "-i", CONTAINER, "psql", "-U", "postgres",
        "-v", "ON_ERROR_STOP=1", "-q", input_text=sql, check=check,
    )


def reset_fixture() -> None:
    psql(
        "DROP SCHEMA IF EXISTS bt2 CASCADE; "
        "DROP ROLE IF EXISTS bt2_test_child; "
        "DROP ROLE IF EXISTS bt2_test_group; "
        "CREATE SCHEMA bt2; REVOKE ALL ON SCHEMA bt2 FROM PUBLIC;"
    )


def exact_function() -> None:
    psql(
        "CREATE FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) "
        "RETURNS uuid LANGUAGE sql AS 'SELECT $1'; "
        "ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) OWNER TO postgres; "
        "ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) SECURITY DEFINER; "
        "ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) "
        "SET search_path TO pg_catalog, bt2;"
    )


def verify(expect_pass: bool, label: str) -> None:
    result = psql(VERIFIER.read_text(encoding="utf-8"), check=False)
    passed = result.returncode == 0
    if passed != expect_pass:
        raise RuntimeError(
            f"{label}: expected_pass={expect_pass} rc={result.returncode} "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )


def wait_ready() -> None:
    for _ in range(40):
        result = docker("exec", CONTAINER, "pg_isready", "-U", "postgres", check=False)
        if result.returncode == 0:
            return
        time.sleep(0.25)
    raise RuntimeError("PostgreSQL container did not become ready")


def main() -> int:
    if shutil.which("docker") is None:
        raise SystemExit("docker is required")
    docker("run", "-d", "--name", CONTAINER, "-e", "POSTGRES_PASSWORD=bt2test", IMAGE)
    try:
        wait_ready()
        reset_fixture(); exact_function(); verify(True, "safe baseline")

        reset_fixture(); exact_function()
        psql(
            "CREATE ROLE bt2_test_group NOLOGIN; CREATE ROLE bt2_test_child LOGIN NOINHERIT; "
            "GRANT bt2_test_group TO bt2_test_child; "
            "GRANT USAGE ON SCHEMA bt2 TO bt2_test_group;"
        )
        verify(False, "SET ROLE reachability")

        reset_fixture()
        psql(
            "CREATE FUNCTION bt2.append_material_v1(integer,text,text,text,text,text) "
            "RETURNS integer LANGUAGE sql AS 'SELECT $1'; "
            "ALTER FUNCTION bt2.append_material_v1(integer,text,text,text,text,text) OWNER TO postgres; "
            "ALTER FUNCTION bt2.append_material_v1(integer,text,text,text,text,text) SECURITY DEFINER; "
            "ALTER FUNCTION bt2.append_material_v1(integer,text,text,text,text,text) "
            "SET search_path TO pg_catalog, bt2;"
        )
        verify(False, "wrong six-argument signature")

        reset_fixture(); exact_function()
        psql("CREATE ROLE bt2_test_child LOGIN; GRANT CREATE ON SCHEMA bt2 TO bt2_test_child;")
        verify(False, "trusted-schema CREATE")

        print("BT2_WOWSQL_EFFECTIVE_BOUNDARY_REGRESSION_PASS")
        return 0
    finally:
        docker("rm", "-f", CONTAINER, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
