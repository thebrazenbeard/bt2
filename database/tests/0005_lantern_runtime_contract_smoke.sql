-- Project Lantern WoWSQL successor-runtime clean-room smoke qualification V1.
-- Self-contained and rollback-only: creates a synthetic governed-material universe,
-- verifies stable cut + payload cross-binding + payload digest integrity + fail-closed
-- unknown-scope behavior, then removes every fixture effect with ROLLBACK.

BEGIN;

INSERT INTO bt2.material_schema_policy(
  schema_version,canonicalizer_digest,semantic_projector_digest,semantic_fields
) VALUES (
  'BT2_LANTERN_RUNTIME_SMOKE_V1',
  repeat('c',64),
  repeat('d',64),
  ARRAY['semantic_role','subject_key']::text[]
);

INSERT INTO bt2.material_profiles(
  project_scope,profile_digest,predecessor_digest,policy_digest,accepted
) VALUES (
  'BT2_LANTERN_RUNTIME_SMOKE',repeat('a',64),NULL,repeat('b',64),true
);

INSERT INTO bt2.material_producer_permits(
  permit_id,project_scope,producer_principal,schema_version,
  profile_digest,policy_digest,valid_from,valid_until,invalidated_at
) VALUES (
  '00000000-0000-4000-8000-000000000501'::uuid,
  'BT2_LANTERN_RUNTIME_SMOKE','bt2-test-fixture','BT2_LANTERN_RUNTIME_SMOKE_V1',
  repeat('a',64),repeat('b',64),clock_timestamp()-interval '1 hour',
  clock_timestamp()+interval '1 hour',NULL
);

WITH p AS (
  SELECT '{"semantic_role":"TEST","subject_key":"LANTERN_RUNTIME_SMOKE"}'::jsonb AS payload
)
INSERT INTO bt2.materials(
  material_id,project_scope,schema_version,semantic_key,
  canonical_digest,source_digest,canonical_payload
)
SELECT
  '00000000-0000-4000-8000-000000000502'::uuid,
  'BT2_LANTERN_RUNTIME_SMOKE','BT2_LANTERN_RUNTIME_SMOKE_V1',
  encode(public.digest(convert_to(
    jsonb_build_array(payload->'semantic_role',payload->'subject_key')::text,'UTF8'),'sha256'),'hex'),
  encode(public.digest(convert_to(payload::text,'UTF8'),'sha256'),'hex'),
  repeat('e',64),payload
FROM p;

INSERT INTO bt2.material_receipts(
  receipt_id,material_id,project_scope,producer_principal,permit_id,
  profile_digest,policy_digest,schema_version,semantic_key,
  canonical_digest,source_digest
)
SELECT
  '00000000-0000-4000-8000-000000000503'::uuid,
  m.material_id,m.project_scope,'bt2-test-fixture',
  '00000000-0000-4000-8000-000000000501'::uuid,
  repeat('a',64),repeat('b',64),m.schema_version,m.semantic_key,
  m.canonical_digest,m.source_digest
FROM bt2.materials m
WHERE m.material_id='00000000-0000-4000-8000-000000000502'::uuid;

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
  FROM bt2.material_cut_v1('BT2_LANTERN_RUNTIME_SMOKE');
  IF v_cut_count <> 1 THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_CUT_NOT_SINGULAR';
  END IF;

  SELECT * INTO STRICT v_b0
  FROM bt2.material_cut_v1('BT2_LANTERN_RUNTIME_SMOKE');

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
  WHERE project_scope='BT2_LANTERN_RUNTIME_SMOKE';

  IF v_payload_count IS DISTINCT FROM v_b0.material_count THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_PAYLOAD_COUNT_MISMATCH';
  END IF;

  IF v_payload_members IS DISTINCT FROM v_b0.exact_members::jsonb THEN
    RAISE EXCEPTION 'LANTERN_WOWSQL_PAYLOAD_MEMBERSHIP_MISMATCH';
  END IF;

  SELECT count(*) INTO v_mismatch_count
  FROM bt2.runtime_visible_materials_v1
  WHERE project_scope='BT2_LANTERN_RUNTIME_SMOKE'
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
  FROM bt2.material_cut_v1('BT2_LANTERN_RUNTIME_SMOKE');

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

ROLLBACK;
