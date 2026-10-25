-- Disposable PostgreSQL 16/17; run AFTER canonical V4 reconstruction and
-- lantern_read_gateway_v1_candidate.sql. All fixture writes roll back.
-- The migration caller must have SET-role membership on the gateway reader.

BEGIN;

DO $baseline$
DECLARE v_snapshot jsonb;
BEGIN
  SELECT lantern_read.current_cut_v1() INTO v_snapshot;
  IF v_snapshot->>'schema' <> 'BT2_LANTERN_READ_GATEWAY_V1'
     OR v_snapshot->>'project_scope' <> 'PROJECT_LANTERN'
     OR (v_snapshot->'cut'->>'material_count')::integer < 1
     OR jsonb_array_length(v_snapshot->'payload') <> (
       v_snapshot->'cut'->>'material_count')::integer THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_BASELINE_FAIL';
  END IF;
END
$baseline$;

-- Deliberately retain old-profile materials, then add a newer accepted profile
-- with one material. A reader that selects solely by scope leaks old members.
INSERT INTO bt2.material_schema_policy(
  schema_version, canonicalizer_digest, semantic_projector_digest, semantic_fields
) VALUES (
  'BT2_LANTERN_GATEWAY_FIXTURE_V1', repeat('9',64), repeat('8',64),
  ARRAY['semantic_role','subject_key']::text[]
);

INSERT INTO bt2.material_profiles(
  project_scope, profile_digest, predecessor_digest, policy_digest, accepted
)
SELECT 'PROJECT_LANTERN', repeat('c',64), c.profile_digest, repeat('d',64), true
  FROM bt2.material_cut_v1('PROJECT_LANTERN') AS c;

INSERT INTO bt2.material_producer_permits(
  permit_id, project_scope, producer_principal, schema_version, profile_digest,
  policy_digest, valid_from, valid_until, invalidated_at
) VALUES (
  '00000000-0000-4000-8000-000000009101'::uuid,
  'PROJECT_LANTERN', 'gateway-ci-fixture', 'BT2_LANTERN_GATEWAY_FIXTURE_V1',
  repeat('c',64), repeat('d',64), clock_timestamp()-interval '1 hour',
  clock_timestamp()+interval '1 hour', NULL
);

WITH p AS (
  SELECT '{"semantic_role":"TEST","subject_key":"GATEWAY_CURRENT_PROFILE"}'::jsonb AS payload
)
INSERT INTO bt2.materials(
  material_id, project_scope, schema_version, semantic_key,
  canonical_digest, source_digest, canonical_payload
)
SELECT
  '00000000-0000-4000-8000-000000009102'::uuid,
  'PROJECT_LANTERN', 'BT2_LANTERN_GATEWAY_FIXTURE_V1',
  encode(public.digest(convert_to(
    jsonb_build_array(payload->'semantic_role', payload->'subject_key')::text,
    'UTF8'), 'sha256'), 'hex'),
  encode(public.digest(convert_to(payload::text, 'UTF8'), 'sha256'), 'hex'),
  repeat('e',64), payload
FROM p;

INSERT INTO bt2.material_receipts(
  receipt_id, material_id, project_scope, producer_principal, permit_id,
  profile_digest, policy_digest, schema_version, semantic_key,
  canonical_digest, source_digest
)
SELECT
  '00000000-0000-4000-8000-000000009103'::uuid,
  m.material_id, m.project_scope, 'gateway-ci-fixture',
  '00000000-0000-4000-8000-000000009101'::uuid,
  repeat('c',64), repeat('d',64), m.schema_version, m.semantic_key,
  m.canonical_digest, m.source_digest
FROM bt2.materials AS m
WHERE m.material_id = '00000000-0000-4000-8000-000000009102'::uuid;

-- A real separate reader is denied bt2 internals and still sees exactly the
-- one current-profile material, with source text enabling independent hashing.
SET LOCAL ROLE bt2_lantern_gateway_reader_v1;

DO $reader$
DECLARE
  v_snapshot jsonb;
  v_material jsonb;
  v_denied boolean := false;
  v_denied_view boolean := false;
BEGIN
  IF current_user <> 'bt2_lantern_gateway_reader_v1'
     OR pg_catalog.has_schema_privilege(current_user, 'bt2', 'USAGE')
     OR pg_catalog.has_schema_privilege(current_user, 'bt2', 'CREATE')
     OR pg_catalog.has_schema_privilege(current_user, 'bt2_legacy', 'USAGE') THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_READER_INTERNAL_PRIVILEGE';
  END IF;

  SELECT lantern_read.current_cut_v1() INTO v_snapshot;
  IF v_snapshot->'cut'->>'profile_digest' <> repeat('c',64)
     OR v_snapshot->'cut'->>'policy_digest' <> repeat('d',64)
     OR (v_snapshot->'cut'->>'material_count')::integer <> 1
     OR jsonb_array_length(v_snapshot->'payload') <> 1 THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_PRIOR_PROFILE_OVERREAD';
  END IF;
  v_material := v_snapshot->'payload'->0;
  IF v_material->>'material_id' <> '00000000-0000-4000-8000-000000009102'
     OR v_material->>'profile_digest' <> repeat('c',64)
     OR v_material->>'policy_digest' <> repeat('d',64)
     OR v_material->>'canonical_payload_pg_text' IS NULL
     OR v_material->>'canonical_digest' <> pg_catalog.encode(public.digest(
       pg_catalog.convert_to(v_material->>'canonical_payload_pg_text','UTF8'),
       'sha256'), 'hex') THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_READER_PAYLOAD_CROSS_BINDING';
  END IF;

  BEGIN
    PERFORM * FROM bt2.material_cut_v1('PROJECT_LANTERN');
  EXCEPTION WHEN insufficient_privilege THEN
    v_denied := true;
  END;
  BEGIN
    PERFORM * FROM bt2.runtime_visible_materials_v1;
  EXCEPTION WHEN insufficient_privilege THEN
    v_denied_view := true;
  END;
  IF NOT v_denied OR NOT v_denied_view THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_DIRECT_BT2_READER_ACCESS';
  END IF;
END
$reader$;

RESET ROLE;

-- An oversized but count-valid canonical payload must be rejected before the
-- server builds the JSONB aggregate. This large fixture is rollback-only.
WITH p AS (
  SELECT pg_catalog.jsonb_build_object(
    'semantic_role', 'TEST', 'subject_key', 'GATEWAY_LARGE',
    'padding', repeat('x', 8388609)) AS payload
)
INSERT INTO bt2.materials(
  material_id, project_scope, schema_version, semantic_key,
  canonical_digest, source_digest, canonical_payload
)
SELECT
  '00000000-0000-4000-8000-000000009104'::uuid,
  'PROJECT_LANTERN', 'BT2_LANTERN_GATEWAY_FIXTURE_V1',
  encode(public.digest(convert_to(
    jsonb_build_array(payload->'semantic_role', payload->'subject_key')::text,
    'UTF8'), 'sha256'), 'hex'),
  encode(public.digest(convert_to(payload::text, 'UTF8'), 'sha256'), 'hex'),
  repeat('f',64), payload
FROM p;

INSERT INTO bt2.material_receipts(
  receipt_id, material_id, project_scope, producer_principal, permit_id,
  profile_digest, policy_digest, schema_version, semantic_key,
  canonical_digest, source_digest
)
SELECT
  '00000000-0000-4000-8000-000000009105'::uuid,
  m.material_id, m.project_scope, 'gateway-ci-fixture',
  '00000000-0000-4000-8000-000000009101'::uuid,
  repeat('c',64), repeat('d',64), m.schema_version, m.semantic_key,
  m.canonical_digest, m.source_digest
FROM bt2.materials AS m
WHERE m.material_id = '00000000-0000-4000-8000-000000009104'::uuid;

DO $oversize$
DECLARE v_observed text;
BEGIN
  BEGIN
    PERFORM lantern_read.current_cut_v1();
  EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS v_observed = MESSAGE_TEXT;
  END;
  IF v_observed IS DISTINCT FROM 'LANTERN_GATEWAY_PAYLOAD_BYTE_BUDGET_EXCEEDED' THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_OVERSIZE_NOT_REJECTED:got=%',
      coalesce(v_observed, 'NONE');
  END IF;
END
$oversize$;

SELECT bt2.assert_internal_access_boundary_v1();
ROLLBACK;
