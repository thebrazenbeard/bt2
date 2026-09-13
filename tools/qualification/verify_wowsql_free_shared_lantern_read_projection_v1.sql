-- Verify the WoWSQL free-shared Lantern read projection V1.
-- Must be executable by the restricted project role without bt2 schema USAGE.

DO $check$
DECLARE
  v_count bigint;
  v_cut jsonb;
  v_expected jsonb := '[
    ["575acfa9-1274-5bbd-9a82-7e672af12e5d","3f0fa23013e3541032e66d3ad0e08ac1dd4e9f3e0b40399efb2511ab88895a18","a9d93e13e508d9f7822dd836aadeb497fe00b8a952c81f37ae46a8701d7f449a","b292790de0d8dafe37e2c9adf7948aa9d46200f3e02f328b4b511f2be017bf26"],
    ["e71548f3-3f09-49fd-9ed6-5d0179fd608c","50076d0f429e229a8c20bd966566920c1954eb87f82cd941b9e841077f5a2a68","103c9b6587abc54cd73d7f4ef79c70011c92a3cd17c04ee193edc777b0385020","2a1a0f0e6c80ab787d39629660a14f98b14c669873269c21bc0f251a64b4ed3b"]
  ]'::jsonb;
  v_actual jsonb;
BEGIN
  IF current_database() <> 'db_bt2_479e4ad9' THEN
    RAISE EXCEPTION 'WRONG_BT2_DATABASE:%',current_database();
  END IF;
  IF has_schema_privilege(current_user,'bt2','USAGE') THEN
    RAISE EXCEPTION 'PROJECT_ROLE_UNEXPECTEDLY_HAS_BT2_SCHEMA_USAGE';
  END IF;
  IF NOT has_schema_privilege(current_user,'bt2_project_read','USAGE') THEN
    RAISE EXCEPTION 'PROJECT_ROLE_CANNOT_USE_READ_PROJECTION';
  END IF;

  SELECT material_count INTO v_count
  FROM bt2_project_read.lantern_projection_meta_v1
  WHERE projection_id='BT2_LANTERN_FREE_SHARED_READ_V1'
    AND project_scope='PROJECT_LANTERN'
    AND target_project='bt2-479e4ad9'
    AND source_state_digest='29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5'
    AND source_seed_git_blob='afe33f1eae5322b18264efa9ed3502f9fe37c10d'
    AND producer_mode='FROZEN_ZERO_PRODUCER'
    AND profile_digest='99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1'
    AND policy_digest='ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445';
  IF v_count IS DISTINCT FROM 2 THEN RAISE EXCEPTION 'PROJECTION_META_MISMATCH'; END IF;

  SELECT to_jsonb(c) - 'project_scope' INTO v_cut
  FROM bt2_project_read.lantern_cut_v1 c
  WHERE project_scope='PROJECT_LANTERN';
  IF v_cut IS NULL
     OR v_cut->>'facade_id' <> 'BT2_MATERIAL_CUT_V1'
     OR v_cut->>'profile_digest' <> '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1'
     OR v_cut->>'policy_digest' <> 'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445'
     OR (v_cut->>'material_count')::bigint <> 2
     OR v_cut->'exact_members' IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'PROJECTION_CUT_MISMATCH';
  END IF;

  SELECT jsonb_agg(jsonb_build_array(material_id::text,canonical_digest,semantic_key,source_digest)
                   ORDER BY material_id)
  INTO v_actual
  FROM bt2_project_read.lantern_materials_v1
  WHERE project_scope='PROJECT_LANTERN';
  IF v_actual IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'PROJECTION_MATERIAL_MEMBERSHIP_MISMATCH';
  END IF;
  IF EXISTS (
    SELECT 1 FROM bt2_project_read.lantern_materials_v1
    WHERE profile_digest <> '99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1'
       OR policy_digest <> 'ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445'
  ) THEN
    RAISE EXCEPTION 'PROJECTION_BINDING_MISMATCH';
  END IF;
END
$check$;