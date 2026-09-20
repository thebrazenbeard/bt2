#!/usr/bin/env python3
"""Manifest-V2 driver for true multi-session Lantern qualification.

Reuses the bounded V1 race mechanics, but binds evidence to BUILD_MANIFEST_V2 and
emits the exact top-level fields consumed by bt2.evaluate_bt2_merge_readiness_v1().
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
import run_lantern_multisession_concurrency as races

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "database" / "BUILD_MANIFEST_V2.json"


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
    if not MANIFEST.is_file():
        raise SystemExit("BUILD_MANIFEST_V2.json is required")

    _, package_digest, source_commit, source_tree = verify_manifest_source(
        ROOT, MANIFEST, args.expected_package_digest
    )
    image_attestation = observe_postgres_container_image(args.postgres_container_id, args.database_url)

    version = races.scalar(args.database_url, "SHOW server_version_num;")
    server_version = races.scalar(args.database_url, "SHOW server_version;")
    if not version.startswith("16"):
        raise SystemExit(f"PostgreSQL 16 required; observed {version}")

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
        "source_commit": source_commit,
        "source_tree": source_tree,
        "package_digest_sha256": package_digest,
        "postgres_image_digest": image_attestation["repo_digest"],
        "postgres_image_attestation": image_attestation,
        "postgres_server_version": server_version,
        "postgres_major": 16,
        "git_version": subprocess.run(["git", "--version"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip(),
        "psql_version": subprocess.run(["psql", "--version"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip(),
        "python_version": sys.version.split()[0],
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
