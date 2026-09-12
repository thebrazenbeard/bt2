-- Canonical Project Lantern governed-state seed V1.
-- Reconstructs the exact accepted policy/profile/historical permits/materials/receipts.
-- Historical permits are evidence only; the resulting current producer authority must be zero.

BEGIN;
SET LOCAL TIME ZONE 'UTC';

INSERT INTO bt2.material_schema_policy(
  schema_version,canonicalizer_digest,semantic_projector_digest,semantic_fields
) VALUES (
  'LANTERN_MATERIAL_V1',
  'gitblob:875d5cd01a0fb4236847522451062e4eed59ec21',
  'semantic_fields_exact_v1@profileblob:1bd7e0e2bbaf08967ae16bc61f5ed02e95208d90',
  ARRAY['semantic_role','subject_key']::text[]
) ON CONFLICT (schema_version) DO NOTHING;

INSERT INTO bt2.material_profiles(
  project_scope,profile_digest,predecessor_digest,policy_digest,accepted_at,accepted
) VALUES (
  'PROJECT_LANTERN','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1',NULL,
  'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445',
  '2026-08-29T15:17:38.935082+00:00',true
) ON CONFLICT (project_scope,profile_digest) DO NOTHING;

INSERT INTO bt2.material_producer_permits(
  permit_id,project_scope,producer_principal,schema_version,profile_digest,policy_digest,
  valid_from,valid_until,invalidated_at
) VALUES
('7896e7a5-d199-5d70-ae3a-521b65a8c529','PROJECT_LANTERN','BT2_LANTERN_BOOTSTRAP_V1','LANTERN_MATERIAL_V1','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1','ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445','2026-08-29T15:17:38.936639+00:00','2026-08-30T15:17:38.936639+00:00',NULL),
('d47c6a72-c623-402f-81e2-aa98231fc6cd','PROJECT_LANTERN','BT2_LANTERN_PROVIDER_QUAL_V1','LANTERN_MATERIAL_V1','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1','ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445','2026-09-01T18:08:01.238212+00:00','2026-09-01T18:29:01.238828+00:00',NULL),
('4a75891b-104b-45b1-9425-bec3dc230c44','PROJECT_LANTERN','BT2_LANTERN_PROVIDER_QUAL_ALT_RETRY','LANTERN_MATERIAL_V1','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1','ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445','2026-09-01T18:39:43.617688+00:00','2026-09-01T18:55:43.617694+00:00','2026-09-01T18:42:08.269266+00:00')
ON CONFLICT (permit_id) DO NOTHING;

INSERT INTO bt2.materials(
  material_id,project_scope,schema_version,semantic_key,canonical_digest,source_digest,canonical_payload,created_at
) VALUES
('575acfa9-1274-5bbd-9a82-7e672af12e5d','PROJECT_LANTERN','LANTERN_MATERIAL_V1','a9d93e13e508d9f7822dd836aadeb497fe00b8a952c81f37ae46a8701d7f449a','3f0fa23013e3541032e66d3ad0e08ac1dd4e9f3e0b40399efb2511ab88895a18','b292790de0d8dafe37e2c9adf7948aa9d46200f3e02f328b4b511f2be017bf26','{"schema_blob":"8ce8608fc1b89e9dde5d58eace152ea9dc19d0f7","subject_key":"PROJECT_LANTERN","profile_blob":"1bd7e0e2bbaf08967ae16bc61f5ed02e95208d90","semantic_role":"PROJECT_GENESIS","source_commit":"b557b4c98dd4a32d603114e22ffa3b8319daf8de"}'::jsonb,'2026-08-29T15:17:38.94052+00:00'),
('e71548f3-3f09-49fd-9ed6-5d0179fd608c','PROJECT_LANTERN','LANTERN_MATERIAL_V1','103c9b6587abc54cd73d7f4ef79c70011c92a3cd17c04ee193edc777b0385020','50076d0f429e229a8c20bd966566920c1954eb87f82cd941b9e841077f5a2a68','2a1a0f0e6c80ab787d39629660a14f98b14c669873269c21bc0f251a64b4ed3b','{"subject_key":"I-03-2026-09-01","semantic_role":"LANTERN_PROVIDER_QUALIFICATION"}'::jsonb,'2026-09-01T18:09:11.317148+00:00')
ON CONFLICT (material_id) DO NOTHING;

INSERT INTO bt2.material_receipts(
  receipt_id,material_id,project_scope,producer_principal,permit_id,profile_digest,policy_digest,
  schema_version,semantic_key,canonical_digest,source_digest,admitted_at
) VALUES
('1970d9cd-9a15-457b-9a49-00b1a45fad88','575acfa9-1274-5bbd-9a82-7e672af12e5d','PROJECT_LANTERN','BT2_LANTERN_BOOTSTRAP_V1','7896e7a5-d199-5d70-ae3a-521b65a8c529','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1','ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445','LANTERN_MATERIAL_V1','a9d93e13e508d9f7822dd836aadeb497fe00b8a952c81f37ae46a8701d7f449a','3f0fa23013e3541032e66d3ad0e08ac1dd4e9f3e0b40399efb2511ab88895a18','b292790de0d8dafe37e2c9adf7948aa9d46200f3e02f328b4b511f2be017bf26','2026-08-29T15:17:38.94108+00:00'),
('f7ff38f6-6f67-411d-9c37-ea7377fdbcec','e71548f3-3f09-49fd-9ed6-5d0179fd608c','PROJECT_LANTERN','BT2_LANTERN_PROVIDER_QUAL_V1','d47c6a72-c623-402f-81e2-aa98231fc6cd','99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1','ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445','LANTERN_MATERIAL_V1','103c9b6587abc54cd73d7f4ef79c70011c92a3cd17c04ee193edc777b0385020','50076d0f429e229a8c20bd966566920c1954eb87f82cd941b9e841077f5a2a68','2a1a0f0e6c80ab787d39629660a14f98b14c669873269c21bc0f251a64b4ed3b','2026-09-01T18:09:11.3177+00:00')
ON CONFLICT (receipt_id) DO NOTHING;

DO $verify$
DECLARE
  v_digest text;
BEGIN
  IF (SELECT count(*) FROM bt2.material_schema_policy WHERE schema_version='LANTERN_MATERIAL_V1') <> 1
     OR (SELECT count(*) FROM bt2.material_profiles WHERE project_scope='PROJECT_LANTERN') <> 1
     OR (SELECT count(*) FROM bt2.material_producer_permits WHERE project_scope='PROJECT_LANTERN') <> 3
     OR (SELECT count(*) FROM bt2.materials WHERE project_scope='PROJECT_LANTERN') <> 2
     OR (SELECT count(*) FROM bt2.material_receipts WHERE project_scope='PROJECT_LANTERN') <> 2 THEN
    RAISE EXCEPTION 'PROJECT_LANTERN_CANONICAL_STATE_CARDINALITY_MISMATCH';
  END IF;

  WITH state AS (
    SELECT jsonb_build_object(
      'policy',(SELECT jsonb_agg(to_jsonb(p) ORDER BY schema_version) FROM bt2.material_schema_policy p WHERE schema_version='LANTERN_MATERIAL_V1'),
      'profile',(SELECT jsonb_agg(to_jsonb(p) ORDER BY project_scope,profile_digest) FROM bt2.material_profiles p WHERE project_scope='PROJECT_LANTERN'),
      'permits',(SELECT jsonb_agg(to_jsonb(p) ORDER BY permit_id) FROM bt2.material_producer_permits p WHERE project_scope='PROJECT_LANTERN'),
      'materials',(SELECT jsonb_agg(to_jsonb(m) ORDER BY material_id) FROM bt2.materials m WHERE project_scope='PROJECT_LANTERN'),
      'receipts',(SELECT jsonb_agg(to_jsonb(r) ORDER BY receipt_id) FROM bt2.material_receipts r WHERE project_scope='PROJECT_LANTERN')
    ) AS doc
  )
  SELECT encode(public.digest(convert_to(doc::text,'UTF8'),'sha256'),'hex') INTO v_digest FROM state;

  IF v_digest <> '29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5' THEN
    RAISE EXCEPTION 'PROJECT_LANTERN_CANONICAL_STATE_DIGEST_MISMATCH:%',v_digest;
  END IF;

  IF EXISTS (
    SELECT 1 FROM bt2.material_producer_permits
    WHERE project_scope='PROJECT_LANTERN'
      AND invalidated_at IS NULL
      AND valid_from <= clock_timestamp()
      AND valid_until > clock_timestamp()
  ) THEN
    RAISE EXCEPTION 'PROJECT_LANTERN_REBUILD_CREATED_CURRENT_PRODUCER_AUTHORITY';
  END IF;
END
$verify$;

COMMIT;
