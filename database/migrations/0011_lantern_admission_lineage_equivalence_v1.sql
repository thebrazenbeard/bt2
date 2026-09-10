-- Canonical governed-material admission equivalence with source Lantern.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.
-- This migration changes no producer authorization and creates no material rows.

CREATE OR REPLACE FUNCTION bt2.material_profile_lineage_v1(p_project_scope text)
RETURNS TABLE(profile_digest text,predecessor_digest text,policy_digest text,lineage jsonb)
LANGUAGE sql STABLE AS $function$
WITH RECURSIVE scoped AS MATERIALIZED (
  SELECT p.project_scope,p.profile_digest,p.predecessor_digest,p.policy_digest
  FROM bt2.material_profiles p
  WHERE p.project_scope=$1 AND p.accepted
), stats AS (
  SELECT count(*)::int AS total,
    count(*) FILTER (WHERE predecessor_digest IS NULL)::int AS genesis_count,
    count(*) FILTER (WHERE predecessor_digest IS NOT NULL AND predecessor_digest=profile_digest)::int AS self_count,
    count(*) FILTER (WHERE predecessor_digest IS NOT NULL AND NOT EXISTS(
      SELECT 1 FROM scoped parent WHERE parent.profile_digest=scoped.predecessor_digest))::int AS orphan_count
  FROM scoped
), forks AS (
  SELECT predecessor_digest FROM scoped WHERE predecessor_digest IS NOT NULL
  GROUP BY predecessor_digest HAVING count(*)>1
), genesis AS (
  SELECT * FROM scoped WHERE predecessor_digest IS NULL
), walk AS (
  SELECT g.project_scope,g.profile_digest,g.predecessor_digest,g.policy_digest,
         ARRAY[g.profile_digest]::text[] AS path
  FROM genesis g
  UNION ALL
  SELECT c.project_scope,c.profile_digest,c.predecessor_digest,c.policy_digest,w.path||c.profile_digest
  FROM walk w JOIN scoped c ON c.predecessor_digest=w.profile_digest
  WHERE NOT c.profile_digest=ANY(w.path)
), leaves AS (
  SELECT s.* FROM scoped s
  WHERE NOT EXISTS(SELECT 1 FROM scoped c WHERE c.predecessor_digest=s.profile_digest)
), valid AS (
  SELECT l.*,
    (SELECT jsonb_agg(jsonb_build_array(s.profile_digest,s.predecessor_digest,s.policy_digest)
                      ORDER BY s.profile_digest) FROM scoped s) AS lineage
  FROM leaves l CROSS JOIN stats st
  WHERE st.total>0 AND st.genesis_count=1 AND st.self_count=0 AND st.orphan_count=0
    AND NOT EXISTS(SELECT 1 FROM forks)
    AND (SELECT count(*) FROM walk)=st.total
    AND (SELECT count(*) FROM leaves)=1
)
SELECT v.profile_digest,v.predecessor_digest,v.policy_digest,v.lineage FROM valid v
$function$;

CREATE OR REPLACE FUNCTION bt2.append_material_v1(
  p_material_id uuid,p_project_scope text,p_producer_principal text,
  p_schema_version text,p_source_digest text,p_payload_text text
) RETURNS uuid
LANGUAGE plpgsql AS $function$
DECLARE
  v_permit record;
  v_policy record;
  v_payload_json json; v_payload jsonb; v_receipt uuid:=gen_random_uuid();
  v_semantic_key text; v_canonical_digest text;
  v_pre record; v_locked record;
BEGIN
  IF lower(current_setting('transaction_isolation'))<>'read committed' THEN
    RAISE EXCEPTION 'append_material_v1 requires READ COMMITTED transaction isolation';
  END IF;
  v_payload_json:=p_payload_text::json;
  PERFORM bt2.assert_no_duplicate_json_keys_v1(v_payload_json);
  v_payload:=v_payload_json::jsonb;
  SELECT * INTO STRICT v_policy FROM bt2.material_schema_policy
  WHERE schema_version=p_schema_version;

  SELECT * INTO v_pre FROM bt2.material_profile_lineage_v1(p_project_scope);
  IF NOT FOUND THEN RAISE EXCEPTION 'accepted profile lineage is invalid'; END IF;

  LOCK TABLE bt2.material_profiles IN SHARE MODE;

  SELECT * INTO v_locked FROM bt2.material_profile_lineage_v1(p_project_scope);
  IF NOT FOUND THEN RAISE EXCEPTION 'accepted profile lineage is invalid after serialization'; END IF;
  IF v_locked.profile_digest IS DISTINCT FROM v_pre.profile_digest
     OR v_locked.predecessor_digest IS DISTINCT FROM v_pre.predecessor_digest
     OR v_locked.policy_digest IS DISTINCT FROM v_pre.policy_digest
     OR v_locked.lineage IS DISTINCT FROM v_pre.lineage THEN
    RAISE EXCEPTION 'accepted profile lineage changed during admission';
  END IF;

  SELECT * INTO STRICT v_permit FROM bt2.material_producer_permits
  WHERE project_scope=p_project_scope
    AND producer_principal=p_producer_principal
    AND schema_version=p_schema_version
    AND profile_digest=v_locked.profile_digest
    AND policy_digest=v_locked.policy_digest
    AND invalidated_at IS NULL
    AND valid_from<=clock_timestamp()
    AND valid_until>clock_timestamp()
  FOR SHARE;

  IF v_policy.semantic_fields<>ARRAY['semantic_role','subject_key']::text[]
     OR NOT(v_payload?'semantic_role' AND v_payload?'subject_key') THEN
    RAISE EXCEPTION 'unknown or incomplete semantic projector';
  END IF;

  v_semantic_key:=encode(public.digest(convert_to(
    jsonb_build_array(v_payload->'semantic_role',v_payload->'subject_key')::text,'UTF8'),'sha256'),'hex');
  v_canonical_digest:=encode(public.digest(convert_to(v_payload::text,'UTF8'),'sha256'),'hex');

  INSERT INTO bt2.materials(
    material_id,project_scope,schema_version,semantic_key,canonical_digest,source_digest,canonical_payload
  ) VALUES(
    p_material_id,p_project_scope,p_schema_version,v_semantic_key,v_canonical_digest,p_source_digest,v_payload
  );
  INSERT INTO bt2.material_receipts(
    receipt_id,material_id,project_scope,producer_principal,permit_id,profile_digest,policy_digest,
    schema_version,semantic_key,canonical_digest,source_digest
  ) VALUES(
    v_receipt,p_material_id,p_project_scope,p_producer_principal,v_permit.permit_id,
    v_locked.profile_digest,v_locked.policy_digest,p_schema_version,v_semantic_key,
    v_canonical_digest,p_source_digest
  );
  RETURN v_receipt;
END
$function$;
