-- Rollback-only qualification for future governed Lantern writes.
-- Proves producer-boundary form plus positive/negative admission without durable authority/material effects.

BEGIN;

ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) OWNER TO postgres;
ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) SECURITY DEFINER;
ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) SET search_path TO pg_catalog, bt2, pg_temp;
REVOKE ALL ON FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) TO postgres;

DO $boundary$
DECLARE
  v_secdef boolean;
  v_owner text;
  v_config text[];
  v_public_exec boolean;
  v_postgres_exec boolean;
BEGIN
  SELECT p.prosecdef,p.proowner::regrole::text,p.proconfig,
         has_function_privilege('public','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE'),
         has_function_privilege('postgres','bt2.append_material_v1(uuid,text,text,text,text,text)','EXECUTE')
  INTO v_secdef,v_owner,v_config,v_public_exec,v_postgres_exec
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='bt2' AND p.proname='append_material_v1';

  IF NOT v_secdef OR v_owner<>'postgres' THEN
    RAISE EXCEPTION 'LANTERN_PRODUCER_BOUNDARY_OWNER_OR_SECURITY_DEFINER_MISMATCH';
  END IF;
  IF v_config IS DISTINCT FROM ARRAY['search_path=pg_catalog, bt2, pg_temp']::text[] THEN
    RAISE EXCEPTION USING MESSAGE =
      'LANTERN_PRODUCER_BOUNDARY_SEARCH_PATH_MISMATCH:' || coalesce(array_to_string(v_config,','),'NULL');
  END IF;
  IF v_public_exec OR NOT v_postgres_exec THEN
    RAISE EXCEPTION 'LANTERN_PRODUCER_BOUNDARY_EXECUTE_ACL_MISMATCH';
  END IF;
END
$boundary$;

CREATE TEMP TABLE _ld2_before AS
SELECT
  (SELECT count(*) FROM bt2.material_producer_permits) AS permits,
  (SELECT count(*) FROM bt2.materials) AS materials,
  (SELECT count(*) FROM bt2.material_receipts) AS receipts;

INSERT INTO bt2.material_schema_policy(schema_version,canonicalizer_digest,semantic_projector_digest,semantic_fields)
VALUES('__BT2_LD2_SYNTHETIC_V1__','synthetic-canonicalizer','synthetic-projector',ARRAY['semantic_role','subject_key']::text[]);

INSERT INTO bt2.material_profiles(project_scope,profile_digest,predecessor_digest,policy_digest,accepted)
VALUES('__BT2_LD2_ROLLBACK_TEST__','synthetic-profile',NULL,'synthetic-policy',true);

INSERT INTO bt2.material_producer_permits(
  permit_id,project_scope,producer_principal,schema_version,profile_digest,policy_digest,valid_from,valid_until,invalidated_at
) VALUES(
  '11111111-1111-4111-8111-111111111111'::uuid,
  '__BT2_LD2_ROLLBACK_TEST__','synthetic-producer','__BT2_LD2_SYNTHETIC_V1__',
  'synthetic-profile','synthetic-policy',clock_timestamp()-interval '1 minute',clock_timestamp()+interval '10 minutes',NULL
);

DO $positive$
DECLARE v_receipt uuid;
BEGIN
  v_receipt:=bt2.append_material_v1(
    '22222222-2222-4222-8222-222222222222'::uuid,
    '__BT2_LD2_ROLLBACK_TEST__','synthetic-producer','__BT2_LD2_SYNTHETIC_V1__',
    'synthetic-source-digest',
    '{"semantic_role":"qualification","subject_key":"positive","value":1}'
  );
  IF NOT EXISTS(
    SELECT 1 FROM bt2.material_receipts r
    WHERE r.receipt_id=v_receipt
      AND r.material_id='22222222-2222-4222-8222-222222222222'::uuid
      AND r.permit_id='11111111-1111-4111-8111-111111111111'::uuid
      AND r.producer_principal='synthetic-producer'
  ) THEN
    RAISE EXCEPTION 'LANTERN_POSITIVE_ADMISSION_RECEIPT_MISSING';
  END IF;
END
$positive$;

DO $no_permit$
BEGIN
  BEGIN
    PERFORM bt2.append_material_v1(
      '33333333-3333-4333-8333-333333333333'::uuid,
      '__BT2_LD2_ROLLBACK_TEST__','unpermitted-producer','__BT2_LD2_SYNTHETIC_V1__',
      'synthetic-source-digest-2',
      '{"semantic_role":"qualification","subject_key":"no-permit"}'
    );
    RAISE EXCEPTION 'LANTERN_NO_PERMIT_UNEXPECTEDLY_SUCCEEDED';
  EXCEPTION WHEN no_data_found THEN
    NULL;
  END;
END
$no_permit$;

UPDATE bt2.material_producer_permits
SET invalidated_at=clock_timestamp()
WHERE permit_id='11111111-1111-4111-8111-111111111111'::uuid;

DO $invalidated$
BEGIN
  BEGIN
    PERFORM bt2.append_material_v1(
      '44444444-4444-4444-8444-444444444444'::uuid,
      '__BT2_LD2_ROLLBACK_TEST__','synthetic-producer','__BT2_LD2_SYNTHETIC_V1__',
      'synthetic-source-digest-3',
      '{"semantic_role":"qualification","subject_key":"invalidated"}'
    );
    RAISE EXCEPTION 'LANTERN_INVALIDATED_PERMIT_UNEXPECTEDLY_SUCCEEDED';
  EXCEPTION WHEN no_data_found THEN
    NULL;
  END;
END
$invalidated$;

UPDATE bt2.material_producer_permits
SET invalidated_at=NULL
WHERE permit_id='11111111-1111-4111-8111-111111111111'::uuid;

DO $incomplete$
BEGIN
  BEGIN
    PERFORM bt2.append_material_v1(
      '55555555-5555-4555-8555-555555555555'::uuid,
      '__BT2_LD2_ROLLBACK_TEST__','synthetic-producer','__BT2_LD2_SYNTHETIC_V1__',
      'synthetic-source-digest-4',
      '{"semantic_role":"qualification"}'
    );
    RAISE EXCEPTION 'LANTERN_INCOMPLETE_SEMANTIC_PAYLOAD_UNEXPECTEDLY_SUCCEEDED';
  EXCEPTION WHEN raise_exception THEN
    IF position('unknown or incomplete semantic projector' IN SQLERRM)=0 THEN RAISE; END IF;
  END;
END
$incomplete$;

DO $duplicate_semantic$
BEGIN
  BEGIN
    PERFORM bt2.append_material_v1(
      '66666666-6666-4666-8666-666666666666'::uuid,
      '__BT2_LD2_ROLLBACK_TEST__','synthetic-producer','__BT2_LD2_SYNTHETIC_V1__',
      'synthetic-source-digest-5',
      '{"semantic_role":"qualification","subject_key":"positive","value":2}'
    );
    RAISE EXCEPTION 'LANTERN_DUPLICATE_SEMANTIC_SUBJECT_UNEXPECTEDLY_SUCCEEDED';
  EXCEPTION WHEN unique_violation THEN
    NULL;
  END;
END
$duplicate_semantic$;

DO $oracle$
DECLARE v_before record;
BEGIN
  SELECT * INTO v_before FROM _ld2_before;
  IF (SELECT count(*) FROM bt2.material_producer_permits) <> v_before.permits+1
     OR (SELECT count(*) FROM bt2.materials) <> v_before.materials+1
     OR (SELECT count(*) FROM bt2.material_receipts) <> v_before.receipts+1 THEN
    RAISE EXCEPTION 'LANTERN_ROLLBACK_QUALIFIER_UNEXPECTED_INTERMEDIATE_COUNTS';
  END IF;
END
$oracle$;

ROLLBACK;
