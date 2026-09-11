#!/usr/bin/env python3
"""Emit deterministic SQL for corrected Project Lantern cohosted historical evidence V2.

V2 supersedes the failed V1 evidence subject after live source comparison proved the
V1 governance relation checksum expectation was wrong. Archived row bytes are unchanged.
This loader preserves source rows only in bt2_legacy.source_rows and never promotes
historical governance/coordination/workforce state into active BT2 tables.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_DIR = ROOT / "archive" / "supabase-project-lantern" / "cohosted-historical" / "2026-09-11"
PROJECT_REF = "agvhmutlrolbaijzlbqk"
SOURCE_SYSTEM = f"SUPABASE:{PROJECT_REF}:COHOSTED_HISTORY_V2"
ARCHIVE_SHA256 = "6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712"
SNAPSHOT_REF = "cohosted-historical-20260911-v2"
FILES = [
    ("bug_ops.role_registry.json", "bug_ops", "role_registry", 4, "f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055"),
    ("bug_ops.system_config.json", "bug_ops", "system_config", 1, "3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203"),
    ("governance.project_notices.json", "governance", "project_notices", 7, "09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78"),
    ("r9a0_coordination.events.json", "r9a0_coordination", "events", 3, "5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4"),
    ("r9a0_governance.migration_applications.json", "r9a0_governance", "migration_applications", 1, "b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a"),
]
ACTIVE_TABLES = [
    ("governance_notices", "bt2.governance_notices"),
    ("coordination_events", "bt2.coordination_events"),
    ("agents", "bt2.agents"),
    ("training_packages", "bt2.training_packages"),
    ("training_qualifications", "bt2.training_qualifications"),
    ("training_installation_events", "bt2.training_installation_events"),
    ("bugs", "bt2.bugs"),
    ("bug_events", "bt2.bug_events"),
]


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def archive_payload(path: Path, expected_schema: str, expected_relation: str, expected_count: int) -> bytes:
    raw = path.read_bytes()
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise SystemExit(f"archive count mismatch: {path}")
    seen = set()
    for row in rows:
        if set(row) != {"source_schema", "source_relation", "source_primary_key", "row_data"}:
            raise SystemExit(f"archive envelope mismatch: {path}")
        if row["source_schema"] != expected_schema or row["source_relation"] != expected_relation:
            raise SystemExit(f"archive source identity mismatch: {path}")
        if not isinstance(row["source_primary_key"], str) or not row["source_primary_key"]:
            raise SystemExit(f"archive primary key mismatch: {path}")
        if row["source_primary_key"] in seen:
            raise SystemExit(f"duplicate archive primary key: {path}")
        seen.add(row["source_primary_key"])
        if not isinstance(row["row_data"], dict):
            raise SystemExit(f"archive row_data mismatch: {path}")
    return raw


def snapshot_metadata() -> str:
    metadata = {
        "classification": "HISTORICAL_PROVENANCE_ONLY",
        "authority_effect": "NONE",
        "currentness_effect": "NONE",
        "archive_sha256": ARCHIVE_SHA256,
        "row_count": 16,
        "relation_counts": {f"{s}.{r}": c for _, s, r, c, _ in FILES},
        "relation_rowset_sha256": {f"{s}.{r}": d for _, s, r, _, d in FILES},
        "supersedes_snapshot_ref": "cohosted-historical-20260911-v1",
        "correction_reason": "V1 governance relation digest expectation was disproved by live Supabase and target row-for-row equality",
    }
    return json.dumps(metadata, sort_keys=True, separators=(",", ":"))


def register_snapshot_expr() -> str:
    return (
        "bt2.register_legacy_source_snapshot_v1("
        "'SUPABASE','Project Lantern','agvhmutlrolbaijzlbqk',"
        f"'{SNAPSHOT_REF}','{ARCHIVE_SHA256}','private','OBSERVED',"
        f"{sql_literal(snapshot_metadata())}::jsonb)"
    )


def import_statement(raw: bytes) -> str:
    encoded = base64.b64encode(raw).decode("ascii")
    return (
        "SELECT bt2.import_legacy_source_rows_v1("
        f"{register_snapshot_expr()},{sql_literal(SOURCE_SYSTEM)},"
        f"convert_from(decode('{encoded}','base64'),'UTF8')::jsonb);"
    )


def active_baseline_sql() -> str:
    values = ",\n    ".join(f"('{name}',(SELECT count(*) FROM {table}))" for name, table in ACTIVE_TABLES)
    return f"""CREATE TEMP TABLE _lantern_archive_active_before(
  subject text PRIMARY KEY,
  row_count bigint NOT NULL
) ON COMMIT DROP;
INSERT INTO _lantern_archive_active_before(subject,row_count)
VALUES
    {values};"""


def active_non_effect_sql() -> str:
    unions = "\n      UNION ALL\n      ".join(
        f"SELECT '{name}'::text AS subject,count(*)::bigint AS row_count FROM {table}"
        for name, table in ACTIVE_TABLES
    )
    return f"""IF EXISTS (
    SELECT 1
    FROM _lantern_archive_active_before b
    JOIN (
      {unions}
    ) a USING(subject)
    WHERE a.row_count IS DISTINCT FROM b.row_count
  ) THEN
    RAISE EXCEPTION 'LANTERN_ARCHIVE_ACTIVE_STATE_CHANGED';
  END IF;"""


def verification_sql() -> str:
    relation_checks = []
    for _, schema, relation, count, digest in FILES:
        relation_checks.append(
            f"IF (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system={sql_literal(SOURCE_SYSTEM)} "
            f"AND source_schema='{schema}' AND source_relation='{relation}') <> {count} THEN "
            f"RAISE EXCEPTION 'LANTERN_ARCHIVE_COUNT_MISMATCH:{schema}.{relation}'; END IF;"
        )
        relation_checks.append(
            "IF (SELECT encode(public.digest(convert_to(coalesce(jsonb_agg(row_data ORDER BY source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex') "
            f"FROM bt2_legacy.source_rows WHERE source_system={sql_literal(SOURCE_SYSTEM)} "
            f"AND source_schema='{schema}' AND source_relation='{relation}') <> '{digest}' THEN "
            f"RAISE EXCEPTION 'LANTERN_ARCHIVE_DIGEST_MISMATCH:{schema}.{relation}'; END IF;"
        )
    relation_body = "\n  ".join(relation_checks)
    non_effect = active_non_effect_sql()
    return f"""
DO $verify$
DECLARE
  v_combined_digest text;
  v_snapshot_count integer;
BEGIN
  IF (SELECT count(*) FROM bt2_legacy.source_rows WHERE source_system={sql_literal(SOURCE_SYSTEM)}) <> 16 THEN
    RAISE EXCEPTION 'LANTERN_ARCHIVE_EXPECTED_16_ROWS';
  END IF;
  {relation_body}

  SELECT encode(public.digest(convert_to(
    coalesce(jsonb_agg(jsonb_build_object(
      'source_schema',source_schema,
      'source_relation',source_relation,
      'source_primary_key',source_primary_key,
      'row_data',row_data
    ) ORDER BY source_schema,source_relation,source_primary_key)::text,'[]'),'UTF8'),'sha256'),'hex')
  INTO v_combined_digest
  FROM bt2_legacy.source_rows
  WHERE source_system={sql_literal(SOURCE_SYSTEM)};

  IF v_combined_digest <> '{ARCHIVE_SHA256}' THEN
    RAISE EXCEPTION 'LANTERN_ARCHIVE_COMBINED_DIGEST_MISMATCH';
  END IF;

  SELECT count(*) INTO v_snapshot_count
  FROM bt2.source_snapshots
  WHERE source_kind='SUPABASE'
    AND source_name='Project Lantern'
    AND canonical_locator='{PROJECT_REF}'
    AND source_ref='{SNAPSHOT_REF}'
    AND source_commit='{ARCHIVE_SHA256}'
    AND visibility='private'
    AND evidence_class='OBSERVED'
    AND metadata->>'classification'='HISTORICAL_PROVENANCE_ONLY'
    AND metadata->>'archive_sha256'='{ARCHIVE_SHA256}'
    AND metadata->>'row_count'='16';

  IF v_snapshot_count <> 1 THEN
    RAISE EXCEPTION 'LANTERN_ARCHIVE_EXACT_SNAPSHOT_MISSING_OR_DUPLICATED';
  END IF;

  {non_effect}
END
$verify$;
""".strip()


def emit(mode: str) -> str:
    payloads = [archive_payload(ARCHIVE_DIR / name, schema, relation, count) for name, schema, relation, count, _ in FILES]
    statements = ["BEGIN;", active_baseline_sql()]
    statements.extend(import_statement(raw) for raw in payloads)
    statements.extend(import_statement(raw) for raw in payloads)
    statements.append(verification_sql())
    statements.append("COMMIT;" if mode == "apply" else "ROLLBACK;")
    return "\n\n".join(statements) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["apply", "verify-rollback"], default="verify-rollback")
    args = parser.parse_args()
    print(emit(args.mode), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
