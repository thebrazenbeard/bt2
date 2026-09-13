-- BT2 WoWSQL free-shared Lantern read projection V1.
-- Provider compatibility surface for the restricted project role.
-- This projection grants no producer authority and intentionally freezes writes.

CREATE SCHEMA IF NOT EXISTS bt2_project_read;

CREATE TABLE IF NOT EXISTS bt2_project_read.lantern_projection_meta_v1 (
  projection_id text PRIMARY KEY,
  project_scope text NOT NULL UNIQUE,
  target_project text NOT NULL,
  source_state_digest text NOT NULL,
  source_seed_git_blob text NOT NULL,
  producer_mode text NOT NULL,
  material_count integer NOT NULL CHECK (material_count >= 0),
  profile_digest text NOT NULL,
  policy_digest text NOT NULL,
  installed_by text NOT NULL,
  installed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  CHECK (projection_id = 'BT2_LANTERN_FREE_SHARED_READ_V1'),
  CHECK (project_scope = 'PROJECT_LANTERN'),
  CHECK (target_project = 'bt2-479e4ad9'),
  CHECK (producer_mode = 'FROZEN_ZERO_PRODUCER')
);

CREATE TABLE IF NOT EXISTS bt2_project_read.lantern_cut_v1 (
  project_scope text PRIMARY KEY,
  facade_id text NOT NULL,
  profile_digest text NOT NULL,
  predecessor_digest text,
  policy_digest text NOT NULL,
  exact_members jsonb NOT NULL,
  material_count bigint NOT NULL CHECK (material_count >= 0),
  CHECK (project_scope = 'PROJECT_LANTERN'),
  CHECK (facade_id = 'BT2_MATERIAL_CUT_V1')
);

CREATE TABLE IF NOT EXISTS bt2_project_read.lantern_materials_v1 (
  material_id uuid PRIMARY KEY,
  project_scope text NOT NULL,
  schema_version text NOT NULL,
  semantic_key text NOT NULL,
  canonical_digest text NOT NULL,
  source_digest text NOT NULL,
  canonical_payload jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  receipt_id uuid NOT NULL UNIQUE,
  profile_digest text NOT NULL,
  policy_digest text NOT NULL,
  CHECK (project_scope = 'PROJECT_LANTERN')
);

INSERT INTO bt2_project_read.lantern_projection_meta_v1(
  projection_id,project_scope,target_project,source_state_digest,source_seed_git_blob,
  producer_mode,material_count,profile_digest,policy_digest,installed_by
) VALUES (
  'BT2_LANTERN_FREE_SHARED_READ_V1','PROJECT_LANTERN','bt2-479e4ad9',
  '29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5',
  'afe33f1eae5322b18264efa9ed3502f9fe37c10d','FROZEN_ZERO_PRODUCER',2,
  '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1',
  'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445',
  session_user
) ON CONFLICT (projection_id) DO NOTHING;

INSERT INTO bt2_project_read.lantern_cut_v1(
  project_scope,facade_id,profile_digest,predecessor_digest,policy_digest,
  exact_members,material_count
) VALUES (
  'PROJECT_LANTERN','BT2_MATERIAL_CUT_V1',
  '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1',NULL,
  'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445',
  '[
    ["575acfa9-1274-5bbd-9a82-7e672af12e5d","3f0fa23013e3541032e66d3ad0e08ac1dd4e9f3e0b40399efb2511ab88895a18","a9d93e13e508d9f7822dd836aadeb497fe00b8a952c81f37ae46a8701d7f449a","b292790de0d8dafe37e2c9adf7948aa9d46200f3e02f328b4b511f2be017bf26"],
    ["e71548f3-3f09-49fd-9ed6-5d0179fd608c","50076d0f429e229a8c20bd966566920c1954eb87f82cd941b9e841077f5a2a68","103c9b6587abc54cd73d7f4ef79c70011c92a3cd17c04ee193edc777b0385020","2a1a0f0e6c80ab787d39629660a14f98b14c669873269c21bc0f251a64b4ed3b"]
  ]'::jsonb,2
) ON CONFLICT (project_scope) DO NOTHING;

INSERT INTO bt2_project_read.lantern_materials_v1(
  material_id,project_scope,schema_version,semantic_key,canonical_digest,
  source_digest,canonical_payload,created_at,receipt_id,profile_digest,policy_digest
) VALUES
(
  '575acfa9-1274-5bbd-9a82-7e672af12e5d','PROJECT_LANTERN','LANTERN_MATERIAL_V1',
  'a9d93e13e508d9f7822dd836aadeb497fe00b8a952c81f37ae46a8701d7f449a',
  '3f0fa23013e3541032e66d3ad0e08ac1dd4e9f3e0b40399efb2511ab88895a18',
  'b292790de0d8dafe37e2c9adf7948aa9d46200f3e02f328b4b511f2be017bf26',
  '{"schema_blob":"8ce8608fc1b89e9dde5d58eace152ea9dc19d0f7","subject_key":"PROJECT_LANTERN","profile_blob":"1bd7e0e2bbaf08967ae16bc61f5ed02e95208d90","semantic_role":"PROJECT_GENESIS","source_commit":"b557b4c98dd4a32d603114e22ffa3b8319daf8de"}'::jsonb,
  '2026-08-29T15:17:38.94052+00:00','1970d9cd-9a15-457b-9a49-00b1a45fad88',
  '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1',
  'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445'
),
(
  'e71548f3-3f09-49fd-9ed6-5d0179fd608c','PROJECT_LANTERN','LANTERN_MATERIAL_V1',
  '103c9b6587abc54cd73d7f4ef79c70011c92a3cd17c04ee193edc777b0385020',
  '50076d0f429e229a8c20bd966566920c1954eb87f82cd941b9e841077f5a2a68',
  '2a1a0f0e6c80ab787d39629660a14f98b14c669873269c21bc0f251a64b4ed3b',
  '{"subject_key":"I-03-2026-09-01","semantic_role":"LANTERN_PROVIDER_QUALIFICATION"}'::jsonb,
  '2026-09-01T18:09:11.317148+00:00','f7ff38f6-6f67-411d-9c37-ea7377fdbcec',
  '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1',
  'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445'
)
ON CONFLICT (material_id) DO NOTHING;
