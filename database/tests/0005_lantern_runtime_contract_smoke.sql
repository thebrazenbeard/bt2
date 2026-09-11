-- Project Lantern WoWSQL successor-runtime smoke qualification V1.
-- Read-only. Verifies governed-cut stability, payload cross-binding, payload digest integrity,
-- and fail-closed behavior for an unknown project scope.

DO $test$
DECLARE
  v_b0 record;
  v_b1 record;
  v_cut_count integer;
  v_payload_count bigint;
  v_payload_members jsonb;
  v_mismatch_count integer;
  v_unknown_count integer;
BEGIN
  SELECT count(*) INTO v_cut_count
  FROM bt2.material_cut_v1('PROJECT_LANTERN');
  IF v_cut_count <> 1 THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_CUT_NOT_SINGULAR';
  END IF;

  SELECT * INTO STRICT v_b0
  FROM bt2.material_cut_v1('PROJECT_LANTERN');

  IF v_b0.facade_id <> 'BT2_MATERIAL_CUT_V1' THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_FACADE_ID_MISMATCH';
  END IF;

  SELECT count(*)::bigint,
         coalesce(jsonb_agg(jsonb_build_array(
           material_id::text,
           canonical_digest,
           semantic_key,
           source_digest
         ) ORDER BY material_id),'[]'::jsonb)
  INTO v_payload_count,v_payload_members
  FROM bt2.runtime_visible_materials_v1
  WHERE project_scope='PROJECT_LANTERN';

  IF v_payload_count IS DISTINCT FROM v_b0.material_count THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_PAYLOAD_COUNT_MISMATCH';
  END IF;

  IF v_payload_members IS DISTINCT FROM v_b0.exact_members::jsonb THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_PAYLOAD_MEMBERSHIP_MISMATCH';
  END IF;

  SELECT count(*) INTO v_mismatch_count
  FROM bt2.runtime_visible_materials_v1
  WHERE project_scope='PROJECT_LANTERN'
    AND (
      profile_digest IS DISTINCT FROM v_b0.profile_digest
      OR policy_digest IS DISTINCT FROM v_b0.policy_digest
      OR encode(public.digest(convert_to(canonical_payload::text,'UTF8'),'sha256'),'hex')
         IS DISTINCT FROM canonical_digest
      OR receipt_id IS NULL
      OR created_at IS NULL
    );

  IF v_mismatch_count <> 0 THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_PAYLOAD_CROSS_BINDING_MISMATCH';
  END IF;

  SELECT * INTO STRICT v_b1
  FROM bt2.material_cut_v1('PROJECT_LANTERN');

  IF v_b1.facade_id IS DISTINCT FROM v_b0.facade_id
     OR v_b1.profile_digest IS DISTINCT FROM v_b0.profile_digest
     OR v_b1.predecessor_digest IS DISTINCT FROM v_b0.predecessor_digest
     OR v_b1.policy_digest IS DISTINCT FROM v_b0.policy_digest
     OR v_b1.exact_members::jsonb IS DISTINCT FROM v_b0.exact_members::jsonb
     OR v_b1.material_count IS DISTINCT FROM v_b0.material_count THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_B0_B1_UNSTABLE';
  END IF;

  SELECT count(*) INTO v_unknown_count
  FROM bt2.material_cut_v1('BT2_LANTERN_UNKNOWN_SCOPE_TEST');

  IF v_unknown_count <> 0 THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_UNKNOWN_SCOPE_DID_NOT_FAIL_CLOSED';
  END IF;
END
$test$;
