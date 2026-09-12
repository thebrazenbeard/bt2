#!/usr/bin/env python3
"""Qualify Lantern admission with genuine independent PostgreSQL sessions.

Runs only against a disposable PostgreSQL 16 database. Uses a synthetic project scope,
commits the minimum fixtures needed for real races, and removes every synthetic row.
No PROJECT_LANTERN row or authority is modified.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
SCOPE = "BT2_LD2_CONCURRENCY_V2"
SCHEMA = "BT2_LD2_CONCURRENCY_SCHEMA_V2"
PRODUCER = "bt2-ld2-concurrency-v2"
PROFILE_A = "bt2-ld2-profile-a"
PROFILE_B = "bt2-ld2-profile-b"
POLICY = "bt2-ld2-policy"
PERMIT = "77777777-7777-4777-8777-777777777778"


def base(url: str) -> list[str]:
    return ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-qAt", "-d", url]


def sql(url: str, statement: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(base(url) + ["-c", statement], cwd=ROOT, text=True, capture_output=True, check=check)


def scalar(url: str, statement: str) -> str:
    return sql(url, statement).stdout.strip()


def cleanup(url: str) -> None:
    # FK-safe cleanup, bounded strictly to the synthetic scope/schema.
    for statement in [
        f"DELETE FROM bt2.material_receipts WHERE project_scope='{SCOPE}';",
        f"DELETE FROM bt2.materials WHERE project_scope='{SCOPE}';",
        f"DELETE FROM bt2.material_producer_permits WHERE project_scope='{SCOPE}';",
        f"DELETE FROM bt2.material_profiles WHERE project_scope='{SCOPE}';",
        f"DELETE FROM bt2.material_schema_policy WHERE schema_version='{SCHEMA}';",
    ]:
        sql(url, statement)


def assert_zero(url: str) -> None:
    counts = scalar(
        url,
        "SELECT concat_ws(',',"
        f"(SELECT count(*) FROM bt2.material_schema_policy WHERE schema_version='{SCHEMA}'),"
        f"(SELECT count(*) FROM bt2.material_profiles WHERE project_scope='{SCOPE}'),"
        f"(SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='{SCOPE}'),"
        f"(SELECT count(*) FROM bt2.materials WHERE project_scope='{SCOPE}'),"
        f"(SELECT count(*) FROM bt2.material_receipts WHERE project_scope='{SCOPE}'));",
    )
    if counts != "0,0,0,0,0":
        raise RuntimeError(f"synthetic residue present: {counts}")


def setup(url: str) -> None:
    assert_zero(url)
    sql(url, f"INSERT INTO bt2.material_schema_policy(schema_version,canonicalizer_digest,semantic_projector_digest,semantic_fields) VALUES('{SCHEMA}','synthetic-canonicalizer','synthetic-projector',ARRAY['semantic_role','subject_key']::text[]);")
    sql(url, f"INSERT INTO bt2.material_profiles(project_scope,profile_digest,predecessor_digest,policy_digest,accepted) VALUES('{SCOPE}','{PROFILE_A}',NULL,'{POLICY}',true);")
    sql(url, f"INSERT INTO bt2.material_producer_permits(permit_id,project_scope,producer_principal,schema_version,profile_digest,policy_digest,valid_from,valid_until,invalidated_at) VALUES('{PERMIT}'::uuid,'{SCOPE}','{PRODUCER}','{SCHEMA}','{PROFILE_A}','{POLICY}',clock_timestamp()-interval '1 minute',clock_timestamp()+interval '30 minutes',NULL);")


def append_sql(material_id: str, subject_key: str, source_digest: str) -> str:
    payload = json.dumps({"semantic_role": "qualification", "subject_key": subject_key}, separators=(",", ":"))
    payload_sql = payload.replace("'", "''")
    return (
        "SELECT bt2.append_material_v1("
        f"'{material_id}'::uuid,'{SCOPE}','{PRODUCER}','{SCHEMA}','{source_digest}','{payload_sql}');"
    )


def spawn_named(url: str, command: str, prefix: str) -> tuple[subprocess.Popen[str], str]:
    app_name = f"{prefix}-{uuid.uuid4().hex[:12]}"
    env = os.environ.copy()
    env["PGAPPNAME"] = app_name
    proc = subprocess.Popen(
        base(url) + ["-c", command],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return proc, app_name


def wait_for_pg_sleep(url: str, proc: subprocess.Popen[str], app_name: str, timeout: float = 8.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = scalar(
            url,
            "SELECT concat_ws('|',pid,coalesce(wait_event,'')) FROM pg_stat_activity "
            f"WHERE application_name='{app_name}';",
        )
        if row:
            pid_text, _, wait_event = row.partition('|')
            if wait_event == "PgSleep":
                return int(pid_text)
        if proc.poll() is not None:
            out, err = proc.communicate()
            raise RuntimeError(f"session exited before server-observed gate: app={app_name} rc={proc.returncode} stdout={out!r} stderr={err!r}")
        time.sleep(0.05)
    proc.kill()
    out, err = proc.communicate()
    raise RuntimeError(f"server-observed gate timeout: app={app_name} stdout={out!r} stderr={err!r}")


def wait_for_session(url: str, proc: subprocess.Popen[str], app_name: str, timeout: float = 4.0) -> tuple[int, str]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = scalar(
            url,
            "SELECT concat_ws('|',pid,coalesce(wait_event_type,''),coalesce(wait_event,'')) "
            "FROM pg_stat_activity "
            f"WHERE application_name='{app_name}';",
        )
        if row:
            pid_text, wait_type, wait_event = (row.split('|', 2) + ['', ''])[:3]
            return int(pid_text), f"{wait_type}:{wait_event}".strip(':')
        if proc.poll() is not None:
            out, err = proc.communicate()
            raise RuntimeError(f"session exited before overlap observation: app={app_name} rc={proc.returncode} stdout={out!r} stderr={err!r}")
        time.sleep(0.05)
    proc.kill()
    out, err = proc.communicate()
    raise RuntimeError(f"session overlap observation timeout: app={app_name} stdout={out!r} stderr={err!r}")


def spawn_gated(url: str, statement: str, gate_epoch: str) -> tuple[subprocess.Popen[str], int]:
    command = (
        "SELECT pg_sleep(GREATEST(0, "
        f"{gate_epoch}::double precision - EXTRACT(EPOCH FROM clock_timestamp()))); "
        f"{statement}"
    )
    proc, app_name = spawn_named(url, command, "bt2-ld2-race")
    return proc, wait_for_pg_sleep(url, proc, app_name)


def finish(proc: subprocess.Popen[str]) -> tuple[int, str, str]:
    out, err = proc.communicate()
    return proc.returncode, out, err


def assert_two_sessions(url: str, pids: list[int]) -> None:
    pid_list = ",".join(str(p) for p in pids)
    observed = scalar(url, f"SELECT count(*) FROM pg_stat_activity WHERE pid IN ({pid_list});")
    if observed != "2" or len(set(pids)) != 2:
        raise RuntimeError(f"true two-session overlap not established: pids={pids} active={observed}")


def same_subject_race(url: str) -> dict:
    gate_epoch = scalar(url, "SELECT EXTRACT(EPOCH FROM clock_timestamp()+interval '5 seconds')::text;")
    a, pid_a = spawn_gated(url, append_sql("10000000-0000-4000-8000-000000000001", "same-subject", "same-a"), gate_epoch)
    b, pid_b = spawn_gated(url, append_sql("10000000-0000-4000-8000-000000000002", "same-subject", "same-b"), gate_epoch)
    assert_two_sessions(url, [pid_a, pid_b])
    ra = finish(a); rb = finish(b)
    successes = sum(1 for r in (ra, rb) if r[0] == 0)
    count = scalar(url, f"SELECT count(*) FROM bt2.materials WHERE project_scope='{SCOPE}' AND canonical_payload->>'subject_key'='same-subject';")
    if successes != 1 or count != "1":
        raise RuntimeError(f"same-subject race failed: rc={[ra[0],rb[0]]} count={count} stderr={[ra[2],rb[2]]}")
    sql(url, f"DELETE FROM bt2.material_receipts WHERE project_scope='{SCOPE}'; DELETE FROM bt2.materials WHERE project_scope='{SCOPE}';")
    return {"status": "PASS", "backend_pids": [pid_a, pid_b], "successes": successes}


def different_subject_race(url: str) -> dict:
    gate_epoch = scalar(url, "SELECT EXTRACT(EPOCH FROM clock_timestamp()+interval '5 seconds')::text;")
    a, pid_a = spawn_gated(url, append_sql("20000000-0000-4000-8000-000000000001", "different-a", "diff-a"), gate_epoch)
    b, pid_b = spawn_gated(url, append_sql("20000000-0000-4000-8000-000000000002", "different-b", "diff-b"), gate_epoch)
    assert_two_sessions(url, [pid_a, pid_b])
    ra = finish(a); rb = finish(b)
    count = scalar(url, f"SELECT count(*) FROM bt2.materials WHERE project_scope='{SCOPE}' AND canonical_payload->>'subject_key' IN ('different-a','different-b');")
    if ra[0] != 0 or rb[0] != 0 or count != "2":
        raise RuntimeError(f"different-subject race failed: rc={[ra[0],rb[0]]} count={count} stderr={[ra[2],rb[2]]}")
    sql(url, f"DELETE FROM bt2.material_receipts WHERE project_scope='{SCOPE}'; DELETE FROM bt2.materials WHERE project_scope='{SCOPE}';")
    return {"status": "PASS", "backend_pids": [pid_a, pid_b], "successes": 2}


def mutation_holder(url: str, mutation: str, sleep_seconds: int = 6) -> tuple[subprocess.Popen[str], int]:
    # The server-side sleep begins only after the mutation has executed in the open transaction.
    command = f"BEGIN; {mutation} SELECT pg_sleep({sleep_seconds}); COMMIT;"
    proc, app_name = spawn_named(url, command, "bt2-ld2-mutation")
    return proc, wait_for_pg_sleep(url, proc, app_name)


def profile_lineage_race(url: str) -> dict:
    mutation = f"INSERT INTO bt2.material_profiles(project_scope,profile_digest,predecessor_digest,policy_digest,accepted) VALUES('{SCOPE}','{PROFILE_B}','{PROFILE_A}','{POLICY}',true);"
    holder, holder_pid = mutation_holder(url, mutation)
    admission, admission_app = spawn_named(
        url,
        append_sql("30000000-0000-4000-8000-000000000001", "profile-race", "profile-race"),
        "bt2-ld2-admission",
    )
    admission_pid, admission_wait = wait_for_session(url, admission, admission_app)
    assert_two_sessions(url, [holder_pid, admission_pid])
    # Holder has already mutated; admission is now independently observed while the holder remains open.
    holder_result = finish(holder)
    admission_result = finish(admission)
    count = scalar(url, f"SELECT count(*) FROM bt2.materials WHERE project_scope='{SCOPE}' AND canonical_payload->>'subject_key'='profile-race';")
    if holder_result[0] != 0 or admission_result[0] == 0 or count != "0":
        raise RuntimeError(f"profile-lineage race failed: holder_rc={holder_result[0]} admission_rc={admission_result[0]} count={count} admission_stderr={admission_result[2]}")
    if "accepted profile lineage changed during admission" not in admission_result[2]:
        raise RuntimeError(f"profile-lineage admission failed for unexpected reason: {admission_result[2]}")
    sql(url, f"DELETE FROM bt2.material_profiles WHERE project_scope='{SCOPE}' AND profile_digest='{PROFILE_B}';")
    return {
        "status": "PASS",
        "mutation_backend_pid": holder_pid,
        "admission_backend_pid": admission_pid,
        "admission_wait_event": admission_wait,
        "overlap_verified": True,
        "admission_rejected": True,
    }


def permit_invalidation_race(url: str) -> dict:
    mutation = f"UPDATE bt2.material_producer_permits SET invalidated_at=clock_timestamp() WHERE permit_id='{PERMIT}'::uuid;"
    holder, holder_pid = mutation_holder(url, mutation)
    admission, admission_app = spawn_named(
        url,
        append_sql("40000000-0000-4000-8000-000000000001", "permit-race", "permit-race"),
        "bt2-ld2-admission",
    )
    admission_pid, admission_wait = wait_for_session(url, admission, admission_app)
    assert_two_sessions(url, [holder_pid, admission_pid])
    holder_result = finish(holder)
    admission_result = finish(admission)
    count = scalar(url, f"SELECT count(*) FROM bt2.materials WHERE project_scope='{SCOPE}' AND canonical_payload->>'subject_key'='permit-race';")
    if holder_result[0] != 0 or admission_result[0] == 0 or count != "0":
        raise RuntimeError(f"permit-invalidation race failed: holder_rc={holder_result[0]} admission_rc={admission_result[0]} count={count} admission_stderr={admission_result[2]}")
    return {
        "status": "PASS",
        "mutation_backend_pid": holder_pid,
        "admission_backend_pid": admission_pid,
        "admission_wait_event": admission_wait,
        "overlap_verified": True,
        "admission_rejected": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    ap.add_argument("--evidence-out")
    args = ap.parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if shutil.which("psql") is None:
        raise SystemExit("psql is required on PATH")
    version = scalar(args.database_url, "SHOW server_version_num;")
    if not version.startswith("16"):
        raise SystemExit(f"PostgreSQL 16 required; observed {version}")

    manifest = json.loads((ROOT / "database" / "BUILD_MANIFEST_V1.json").read_text(encoding="utf-8"))
    package_digest = manifest["package_identity"]["package_digest_sha256"]

    real_before = scalar(args.database_url, "SELECT concat_ws(',',(SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN'),(SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN' AND invalidated_at IS NULL AND valid_from<=clock_timestamp() AND valid_until>clock_timestamp()),(SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN'),(SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN'));")

    evidence: dict[str, object] = {
        "package_digest_sha256": package_digest,
        "postgres_major": 16,
        "true_multisession": True,
        "real_project_lantern_before": real_before,
    }
    try:
        setup(args.database_url)
        evidence["same_subject_race"] = same_subject_race(args.database_url)
        evidence["different_subject_race"] = different_subject_race(args.database_url)
        evidence["profile_lineage_race"] = profile_lineage_race(args.database_url)
        # Restore base lineage after the profile race before the permit race.
        evidence["permit_invalidation_race"] = permit_invalidation_race(args.database_url)
    finally:
        cleanup(args.database_url)

    assert_zero(args.database_url)
    real_after = scalar(args.database_url, "SELECT concat_ws(',',(SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN'),(SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN' AND invalidated_at IS NULL AND valid_from<=clock_timestamp() AND valid_until>clock_timestamp()),(SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN'),(SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN'));")
    evidence["real_project_lantern_after"] = real_after
    evidence["zero_synthetic_residue"] = True
    if real_after != real_before:
        raise RuntimeError(f"real PROJECT_LANTERN state changed: before={real_before} after={real_after}")

    text = json.dumps(evidence, indent=2, sort_keys=True)
    print(text)
    if args.evidence_out:
        Path(args.evidence_out).write_text(text + "\n", encoding="utf-8")
    print(f"BT2_LANTERN_TRUE_MULTISESSION_CONCURRENCY_PASS package_digest={package_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
