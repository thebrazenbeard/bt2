#!/usr/bin/env python3
"""Manifest-bound driver for true multi-session Lantern qualification.

Reuses the bounded V1 race mechanics and binds evidence to the exact admitted
PostgreSQL package/major before emitting the readiness evidence fields.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil

import run_lantern_multisession_concurrency as races
from bt2_build_manifest import load_and_verify_manifest

ROOT = Path(__file__).resolve().parents[2]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    ap.add_argument("--expected-package-digest")
    ap.add_argument("--evidence-out")
    args = ap.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if shutil.which("psql") is None:
        raise SystemExit("psql is required on PATH")
    version = races.scalar(args.database_url, "SHOW server_version_num;")
    try:
        postgres_major = int(version) // 10000
    except ValueError as exc:
        raise SystemExit(f"unparseable server_version_num: {version}") from exc

    manifest_path, _manifest, package_digest = load_and_verify_manifest(
        expected_digest=args.expected_package_digest,
        postgres_major=postgres_major,
    )
    print(
        f"QUALIFICATION_MANIFEST={manifest_path.relative_to(ROOT)} "
        f"package_digest={package_digest} postgres_major={postgres_major}",
        flush=True,
    )

    real_before = races.scalar(
        args.database_url,
        "SELECT concat_ws(',',"
        "(SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN'),"
        "(SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN' "
        " AND invalidated_at IS NULL AND valid_from<=clock_timestamp() AND valid_until>clock_timestamp()),"
        "(SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN'),"
        "(SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN'));",
    )

    details: dict[str, object] = {}
    try:
        races.setup(args.database_url)
        details["same_subject"] = races.same_subject_race(args.database_url)
        details["different_subject"] = races.different_subject_race(args.database_url)
        details["profile_lineage"] = races.profile_lineage_race(args.database_url)
        details["permit_invalidation"] = races.permit_invalidation_race(args.database_url)
    finally:
        races.cleanup(args.database_url)

    races.assert_zero(args.database_url)
    real_after = races.scalar(
        args.database_url,
        "SELECT concat_ws(',',"
        "(SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN'),"
        "(SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN' "
        " AND invalidated_at IS NULL AND valid_from<=clock_timestamp() AND valid_until>clock_timestamp()),"
        "(SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN'),"
        "(SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN'));",
    )
    if real_after != real_before:
        raise RuntimeError(f"real PROJECT_LANTERN state changed: before={real_before} after={real_after}")

    evidence = {
        "package_digest_sha256": package_digest,
        "postgres_major": postgres_major,
        "true_multisession": True,
        "same_subject_race": "PASS",
        "different_subject_race": "PASS",
        "profile_lineage_race": "PASS",
        "permit_invalidation_race": "PASS",
        "zero_synthetic_residue": True,
        "real_project_lantern_before": real_before,
        "real_project_lantern_after": real_after,
        "race_details": details,
        "qualification_effect": "NONE",
        "producer_authority_effect": "NONE",
        "destructive_retirement_effect": "NONE",
    }
    text = json.dumps(evidence, indent=2, sort_keys=True)
    print(text)
    if args.evidence_out:
        Path(args.evidence_out).write_text(text + "\n", encoding="utf-8")
    print(f"BT2_LANTERN_TRUE_MULTISESSION_CONCURRENCY_PASS package_digest={package_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
