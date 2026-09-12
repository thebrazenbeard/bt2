-- Project Lantern WoWSQL authorized admission qualification V1.
-- One-statement atomic, synthetic-scope only, deliberate rollback sentinel.
-- No real PROJECT_LANTERN permit/profile/material/receipt is created or changed.

DO $qualification$
DECLARE
  v_scope constant text := 'BT2_LANTERN_ADMISSION_SMOKE';
  v_schema constant text := 'BT2_LANTERN_ADMISSION_SMOKE_V1';
  v_profile constant text := repeat('a',64);
  v_policy constant text := repeat('b',64);
  v_permit constant uuid := '00000000-0000-4000-8000-000000000601'::uuid;
  v_material constant uuid := '00000000-0000-4000-8000-000000000602'::uuid;
  v_duplicate_material constant uuid := '00000000-0000-4000-8000-000000000603'::uuid;
  v_unauth_material constant uuid := '00000000-0000-4000-8000-000000000604'::uuid;
  v_receipt uuid;
  v_real_profiles_before bigint;
  v_real_permits_before bigint;
  v_real_materials_before bigint;
  v_real_receipts_before bigint;
  v_duplicate_rejected boolean := false;
  v_unauthorized_rejected boolean := false;
BEGIN
  IF EXISTS (SELECT 1 FROM bt2.material_profiles WHERE project_scope=v_scope)
     OR EXISTS (SELECT 1 FROM bt2.material_producer_permits WHERE project_scope=v_scope)
     OR EXISTS (SELECT 1 FROM bt2.materials WHERE project_scope=v_scope)
     OR EXISTS (SELECT 1 FROM bt2.material_receipts WHERE project_scope=v_scope)
     OR EXISTS (SELECT 1 FROM bt2.material_schema_policy WHERE schema_version=v_schema) THEN
    RAISE EXCEPTION 'LANTERN_ADMISSION_SMOKE_PREEXISTING_FIXTURE';
  END IF;

  SELECT count(*) INTO v_real_profiles_before FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN';
  SELECT count(*) INTO v_real_permits_before FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN';
  SELECT count(*) INTO v_real_materials_before FROM bt2.materials WHERE project_scope='PROJECT_LANTERN';
  SELECT count(*) INTO v_real_receipts_before FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN';

  INSERT INTO bt2.material_schema_policy(
    schema_version,canonicalizer_digest,semantic_projector_digest,semantic_fields
  ) VALUES (
    v_schema,repeat('c',64),repeat('d',64),ARRAY['semantic_role','subject_key']::text[]
  );

  INSERT INTO bt2.material_profiles(
    project_scope,profile_digest,predecessor_digest,policy_digest,accepted
  ) VALUES (v_scope,v_profile,NULL,v_policy,true);

  INSERT INTO bt2.material_producer_permits(
    permit_id,project_scope,producer_principal,schema_version,
    profile_digest,policy_digest,valid_from,valid_until,invalidated_at
  ) VALUES (
    v_permit,v_scope,'bt2-admission-smoke',v_schema,
    v_profile,v_policy,clock_timestamp()-interval '1 minute',
    clock_timestamp()+interval '10 minutes',NULL
  );

  SELECT bt2.append_material_v1(
    v_material,v_scope,'bt2-admission-smoke',v_schema,repeat('e',64),
    '{"semantic_role":"TEST","subject_key":"AUTHORIZED_ADMISSION"}'
  ) INTO v_receipt;

  IF NOT EXISTS (
    SELECT 1
    FROM bt2.materials m
    JOIN bt2.material_receipts r ON r.material_id=m.material_id
    WHERE m.material_id=v_material
      AND m.project_scope=v_scope
      AND m.schema_version=v_schema
      AND r.receipt_id=v_receipt
      AND r.project_scope=v_scope
      AND r.producer_principal='bt2-admission-smoke'
      AND r.permit_id=v_permit
      AND r.profile_digest=v_profile
      AND r.policy_digest=v_policy
      AND r.schema_version=v_schema
      AND r.semantic_key=m.semantic_key
      AND r.canonical_digest=m.canonical_digest
      AND r.source_digest=m.source_digest
  ) THEN
    RAISE EXCEPTION 'LANTERN_AUTHORIZED_ADMISSION_RECEIPT_BINDING_FAILED';
  END IF;

  BEGIN
    PERFORM bt2.append_material_v1(
      v_duplicate_material,v_scope,'bt2-admission-smoke',v_schema,repeat('f',64),
      '{"semantic_role":"TEST","subject_key":"AUTHORIZED_ADMISSION"}'
    );
  EXCEPTION WHEN unique_violation THEN
    v_duplicate_rejected := true;
  END;
  IF NOT v_duplicate_rejected THEN
    RAISE EXCEPTION 'LANTERN_DUPLICATE_SEMANTIC_ADMISSION_ACCEPTED';
  END IF;

  BEGIN
    PERFORM bt2.append_material_v1(
      v_unauth_material,v_scope,'bt2-unauthorized-smoke',v_schema,repeat('1',64),
      '{"semantic_role":"TEST","subject_key":"UNAUTHORIZED_ADMISSION"}'
    );
  EXCEPTION WHEN no_data_found THEN
    v_unauthorized_rejected := true;
  END;
  IF NOT v_unauthorized_rejected THEN
    RAISE EXCEPTION 'LANTERN_UNAUTHORIZED_PRODUCER_ACCEPTED';
  END IF;

  IF (SELECT count(*) FROM bt2.materials WHERE project_scope=v_scope) <> 1
     OR (SELECT count(*) FROM bt2.material_receipts WHERE project_scope=v_scope) <> 1
     OR (SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope=v_scope) <> 1
     OR (SELECT count(*) FROM bt2.material_profiles WHERE project_scope=v_scope) <> 1 THEN
    RAISE EXCEPTION 'LANTERN_ADMISSION_SMOKE_FIXTURE_CARDINALITY_INVALID';
  END IF;

  IF (SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN') IS DISTINCT FROM v_real_profiles_before
     OR (SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN') IS DISTINCT FROM v_real_permits_before
     OR (SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN') IS DISTINCT FROM v_real_materials_before
     OR (SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN') IS DISTINCT FROM v_real_receipts_before THEN
    RAISE EXCEPTION 'REAL_PROJECT_LANTERN_STATE_CHANGED_DURING_ADMISSION_SMOKE';
  END IF;

  RAISE EXCEPTION 'LANTERN_AUTHORIZED_ADMISSION_ROLLBACK_PASS';
END
$qualification$;
