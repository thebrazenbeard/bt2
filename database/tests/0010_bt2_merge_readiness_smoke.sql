-- BT2 merge-readiness smoke V1.
-- This test proves that technical readiness is bound to one exact package digest and
-- immutable evidence. It does NOT authorize merge, cutover, provider deletion, or source retirement.

BEGIN;

DO $baseline$
DECLARE
  v_ready boolean;
  v_blockers text[];
BEGIN
  SELECT ready,blockers INTO v_ready,v_blockers
  FROM bt2.evaluate_bt2_merge_readiness_v1(
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  );

  IF v_ready THEN
    RAISE EXCEPTION 'BT2_MERGE_READINESS_UNEXPECTED_BASELINE_PASS';
  END IF;

  IF NOT ('BLANK_REBUILD_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('MULTISESSION_CONCURRENCY_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('LANTERN_PROJECT_RUNTIME_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('ONE_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('TWO_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers)) THEN
    RAISE EXCEPTION 'BT2_MERGE_READINESS_BASELINE_BLOCKERS_INCOMPLETE:%',v_blockers;
  END IF;
END
$baseline$;

INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,
  result_state,evidence,applied_at,verified_at
)
VALUES
(
  'BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4',
  'TEST','bt2.training_packages',repeat('1',64),'VERIFIED',
  jsonb_build_object(
    'registered_package_count',13,
    'frontier_digest_sha256','8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2',
  'TEST','bt2_legacy.source_rows',repeat('2',64),'VERIFIED',
  jsonb_build_object(
    'row_count',16,
    'combined_rows_sha256','6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-BLANK-REBUILD-V1',
  'TEST','BT2_DATABASE_PACKAGE',repeat('3',64),'VERIFIED',
  jsonb_build_object(
    'package_digest_sha256','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'postgres_major',16,
    'blank_rebuild','PASS'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-LANTERN-LD2-CONCURRENCY-V1',
  'TEST','bt2.append_material_v1',repeat('4',64),'VERIFIED',
  jsonb_build_object(
    'package_digest_sha256','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'true_multisession',true,
    'same_subject_race','PASS',
    'different_subject_race','PASS',
    'profile_lineage_race','PASS',
    'permit_invalidation_race','PASS'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-LANTERN-WOWSQL-PROJECT-RUNTIME-V1',
  'TEST','CHATGPT_PROJECT_RUNTIME',repeat('5',64),'VERIFIED',
  jsonb_build_object(
    'package_digest_sha256','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'runtime_commit','94ad89d05ab1557813ed09d2b6fe65907a4194c5',
    'runtime_tree','fa23273a9bd06f96a2057ddc649dc09d1b882a55',
    'p1','PASS','p2','PASS','p3','PASS','p4','PASS','p5','PASS','p6','PASS'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-ONE-ACCEPTANCE-V1',
  'TEST','BT2_MIGRATION',repeat('6',64),'VERIFIED',
  jsonb_build_object(
    'package_digest_sha256','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'acceptance','PASS'
  ),clock_timestamp(),clock_timestamp()
),
(
  'BT2-TWO-ACCEPTANCE-V1',
  'TEST','BT2_MIGRATION',repeat('7',64),'VERIFIED',
  jsonb_build_object(
    'package_digest_sha256','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'acceptance','PASS'
  ),clock_timestamp(),clock_timestamp()
);

DO $positive$
DECLARE
  v_ready boolean;
  v_blockers text[];
BEGIN
  SELECT ready,blockers INTO v_ready,v_blockers
  FROM bt2.evaluate_bt2_merge_readiness_v1(
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  );

  IF NOT v_ready OR coalesce(cardinality(v_blockers),0)<>0 THEN
    RAISE EXCEPTION 'BT2_MERGE_READINESS_EXPECTED_PASS_FAILED:%',v_blockers;
  END IF;
END
$positive$;

DO $digest_binding$
DECLARE
  v_ready boolean;
  v_blockers text[];
BEGIN
  SELECT ready,blockers INTO v_ready,v_blockers
  FROM bt2.evaluate_bt2_merge_readiness_v1(
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
  );

  IF v_ready THEN
    RAISE EXCEPTION 'BT2_MERGE_READINESS_WRONG_DIGEST_UNEXPECTEDLY_PASSED';
  END IF;
  IF NOT ('BLANK_REBUILD_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('MULTISESSION_CONCURRENCY_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('LANTERN_PROJECT_RUNTIME_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('ONE_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers))
     OR NOT ('TWO_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH' = ANY(v_blockers)) THEN
    RAISE EXCEPTION 'BT2_MERGE_READINESS_DIGEST_BINDING_NOT_ENFORCED:%',v_blockers;
  END IF;
END
$digest_binding$;

ROLLBACK;
