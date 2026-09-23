-- BT2 merge-readiness evaluator V1.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
--
-- This function is an evidence aggregator only. `ready=true` means the exact package
-- digest has the required technical/One/Two acceptance evidence. It does NOT merge,
-- cut over, delete Supabase, retire any source/provider, grant producer authority,
-- install training, or authorize any destructive effect.

CREATE OR REPLACE FUNCTION bt2.evaluate_bt2_merge_readiness_v1(
  p_package_digest_sha256 text
) RETURNS TABLE(
  ready boolean,
  blockers text[],
  evidence jsonb
)
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
  v_blockers text[] := ARRAY[]::text[];
  v_secdef boolean;
  v_owner text;
  v_config text[];
  v_public_exec boolean;
  v_postgres_exec boolean;
  v_append_only_trigger boolean := false;
  v_training_frontier boolean := false;
  v_lantern_history boolean := false;
  v_blank_rebuild boolean := false;
  v_concurrency boolean := false;
  v_runtime boolean := false;
  v_producer_boundary boolean := false;
  v_one_acceptance boolean := false;
  v_two_acceptance boolean := false;
BEGIN
  IF p_package_digest_sha256 IS NULL
     OR p_package_digest_sha256 !~ '^[0-9a-f]{64}$' THEN
    v_blockers := array_append(v_blockers,'INVALID_PACKAGE_DIGEST');
  END IF;

  SELECT EXISTS(
    SELECT 1
    FROM pg_trigger tg
    JOIN pg_class c ON c.oid=tg.tgrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='bt2'
      AND c.relname='migration_receipts'
      AND tg.tgname='migration_receipts_no_update_delete_v1'
      AND NOT tg.tgisinternal
  ) INTO v_append_only_trigger;

  IF NOT v_append_only_trigger THEN
    v_blockers := array_append(v_blockers,'MIGRATION_RECEIPT_LEDGER_NOT_APPEND_ONLY');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V4'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'registered_package_count'='13'
      AND r.evidence->>'frontier_digest_sha256'='8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc'
  ) INTO v_training_frontier;

  IF NOT v_training_frontier THEN
    v_blockers := array_append(v_blockers,'TRAINING_13_PACKAGE_FRONTIER_MISSING_OR_MISMATCH');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2'
      AND r.result_state='VERIFIED'
  ) INTO v_lantern_history;

  IF NOT v_lantern_history THEN
    v_blockers := array_append(v_blockers,'LANTERN_COHOSTED_HISTORY_RECEIPT_MISSING');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-BLANK-REBUILD-V1'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'package_digest_sha256'=p_package_digest_sha256
      AND r.evidence->>'postgres_major'='16'
      AND r.evidence->>'blank_rebuild'='PASS'
  ) INTO v_blank_rebuild;

  IF NOT v_blank_rebuild THEN
    v_blockers := array_append(v_blockers,'BLANK_REBUILD_RECEIPT_MISSING_OR_MISMATCH');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-LANTERN-LD2-CONCURRENCY-V1'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'package_digest_sha256'=p_package_digest_sha256
      AND r.evidence->>'true_multisession'='true'
      AND r.evidence->>'same_subject_race'='PASS'
      AND r.evidence->>'different_subject_race'='PASS'
      AND r.evidence->>'profile_lineage_race'='PASS'
      AND r.evidence->>'permit_invalidation_race'='PASS'
  ) INTO v_concurrency;

  IF NOT v_concurrency THEN
    v_blockers := array_append(v_blockers,'MULTISESSION_CONCURRENCY_RECEIPT_MISSING_OR_MISMATCH');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-LANTERN-WOWSQL-PROJECT-RUNTIME-V1'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'package_digest_sha256'=p_package_digest_sha256
      AND r.evidence->>'runtime_commit'='94ad89d05ab1557813ed09d2b6fe65907a4194c5'
      AND r.evidence->>'runtime_tree'='fa23273a9bd06f96a2057ddc649dc09d1b882a55'
      AND r.evidence->>'p1'='PASS'
      AND r.evidence->>'p2'='PASS'
      AND r.evidence->>'p3'='PASS'
      AND r.evidence->>'p4'='PASS'
      AND r.evidence->>'p5'='PASS'
      AND r.evidence->>'p6'='PASS'
  ) INTO v_runtime;

  IF NOT v_runtime THEN
    v_blockers := array_append(v_blockers,'LANTERN_PROJECT_RUNTIME_RECEIPT_MISSING_OR_MISMATCH');
  END IF;

  SELECT p.prosecdef,p.proowner::regrole::text,p.proconfig,
         has_function_privilege('public','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE'),
         has_function_privilege('postgres','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE')
  INTO v_secdef,v_owner,v_config,v_public_exec,v_postgres_exec
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='bt2'
    AND p.proname='append_material_v1'
    AND oidvectortypes(p.proargtypes)='uuid, text, text, text, text, text';

  v_producer_boundary := coalesce(v_secdef,false)
    AND v_owner='postgres'
    AND v_config IS NOT DISTINCT FROM ARRAY['search_path=pg_catalog, bt2, pg_temp']::text[]
    AND NOT coalesce(v_public_exec,true)
    AND coalesce(v_postgres_exec,false);

  IF NOT v_producer_boundary THEN
    v_blockers := array_append(v_blockers,'LANTERN_PRODUCER_BOUNDARY_NOT_ESTABLISHED');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-ONE-ACCEPTANCE-V1'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'package_digest_sha256'=p_package_digest_sha256
      AND r.evidence->>'acceptance'='PASS'
  ) INTO v_one_acceptance;

  IF NOT v_one_acceptance THEN
    v_blockers := array_append(v_blockers,'ONE_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bt2.migration_receipts r
    WHERE r.migration_key='BT2-TWO-ACCEPTANCE-V1'
      AND r.result_state='VERIFIED'
      AND r.evidence->>'package_digest_sha256'=p_package_digest_sha256
      AND r.evidence->>'acceptance'='PASS'
  ) INTO v_two_acceptance;

  IF NOT v_two_acceptance THEN
    v_blockers := array_append(v_blockers,'TWO_ACCEPTANCE_RECEIPT_MISSING_OR_MISMATCH');
  END IF;

  RETURN QUERY
  SELECT
    coalesce(cardinality(v_blockers),0)=0,
    v_blockers,
    jsonb_build_object(
      'package_digest_sha256',p_package_digest_sha256,
      'migration_receipt_ledger_append_only',v_append_only_trigger,
      'training_13_package_frontier',v_training_frontier,
      'lantern_cohosted_history_v2',v_lantern_history,
      'blank_rebuild_postgresql_16',v_blank_rebuild,
      'lantern_true_multisession_concurrency',v_concurrency,
      'lantern_wowsql_project_runtime',v_runtime,
      'lantern_producer_boundary_live',v_producer_boundary,
      'one_acceptance',v_one_acceptance,
      'two_acceptance',v_two_acceptance,
      'destructive_source_retirement_authority',false,
      'destructive_provider_retirement_authority',false,
      'supabase_project_lantern_delete_authority',false
    );
END
$function$;

COMMENT ON FUNCTION bt2.evaluate_bt2_merge_readiness_v1(text) IS
  'Fail-closed evidence aggregator for exact BT2 migration merge subject. No merge/cutover/retirement/provider-delete effect.';
