-- BT2 Lantern read gateway V1: uninstalled forward-only SOURCE CANDIDATE.
-- Apply only to a disposable PostgreSQL 16/17 rebuild AFTER the frozen V4
-- schema/migrations/data. Do not add this to the frozen V4 database manifest.
-- A future V5 release must separately pin/qualify its own migration package.
--
-- Preconditions deliberately outside this file:
--   (1) Operator provisions a NOLOGIN NOINHERIT non-elevated role
--       bt2_lantern_gateway_owner_v1, without membership in other roles.
--   (2) Operator provisions a LOGIN NOINHERIT non-elevated role
--       bt2_lantern_gateway_reader_v1, without other role memberships.
--   (3) Migration caller is canonical V4 owner and has permission to create
--       schema/functions for owner (e.g. role SET membership). This script
--       grants no membership, creates no LOGIN, and switches no role.
--   (4) A separate database/cluster identity and TLS qualification is required.
--
-- No grants to PUBLIC, no dynamic SQL, no write function, no provider cutover.

BEGIN;

DO $preflight$
DECLARE
  v_owner record;
  v_reader record;
  v_migration_actor oid;
BEGIN
  SELECT oid INTO v_migration_actor
    FROM pg_catalog.pg_roles WHERE rolname = CURRENT_USER;
  SELECT oid, rolcanlogin, rolinherit, rolsuper, rolcreatedb, rolcreaterole,
         rolreplication, rolbypassrls
    INTO v_owner
    FROM pg_catalog.pg_roles
   WHERE rolname = 'bt2_lantern_gateway_owner_v1';
  SELECT oid, rolcanlogin, rolinherit, rolsuper, rolcreatedb, rolcreaterole,
         rolreplication, rolbypassrls
    INTO v_reader
    FROM pg_catalog.pg_roles
   WHERE rolname = 'bt2_lantern_gateway_reader_v1';

  IF v_owner.oid IS NULL OR v_owner.rolcanlogin OR v_owner.rolinherit
     OR v_owner.rolsuper OR v_owner.rolcreatedb OR v_owner.rolcreaterole
     OR v_owner.rolreplication OR v_owner.rolbypassrls THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_OWNER_ROLE_NOT_RESTRICTED';
  END IF;
  IF v_reader.oid IS NULL OR NOT v_reader.rolcanlogin OR v_reader.rolinherit
     OR v_reader.rolsuper OR v_reader.rolcreatedb OR v_reader.rolcreaterole
     OR v_reader.rolreplication OR v_reader.rolbypassrls THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_READER_ROLE_NOT_RESTRICTED';
  END IF;
  -- The migration actor alone may SET the NOLOGIN gateway owner to transfer
  -- function ownership. An unrelated member could otherwise SET ROLE to the
  -- definer and read the protected bt2 tables granted to that owner directly.
  -- Reject inherited membership; a CREATEROLE migration actor may already
  -- hold implicit ADMIN on its created roles in managed PostgreSQL 17.
  -- This install-time check cannot substitute for role-grant drift monitoring.
  IF v_migration_actor IS NULL OR NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_auth_members
     WHERE roleid = v_owner.oid AND member = v_migration_actor
       AND set_option AND NOT inherit_option
  ) OR EXISTS (
    SELECT 1 FROM pg_catalog.pg_auth_members
     WHERE member IN (v_owner.oid, v_reader.oid)
  ) OR EXISTS (
    SELECT 1 FROM pg_catalog.pg_auth_members
     WHERE roleid IN (v_owner.oid, v_reader.oid)
       AND (member <> v_migration_actor OR NOT set_option
            OR inherit_option)
  ) THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_ROLE_MEMBERSHIP_NOT_ISOLATED';
  END IF;
END
$preflight$;

CREATE SCHEMA lantern_read;
REVOKE ALL ON SCHEMA lantern_read FROM PUBLIC;

-- These are the *only* internal grants to the restricted NOLOGIN owner.
-- The view retains V4's owner-checked relation semantics; reader has no access.
GRANT USAGE ON SCHEMA bt2 TO bt2_lantern_gateway_owner_v1;
GRANT SELECT ON TABLE bt2.material_profiles, bt2.materials,
  bt2.runtime_visible_materials_v1 TO bt2_lantern_gateway_owner_v1;
GRANT EXECUTE ON FUNCTION bt2.material_cut_v1(text)
  TO bt2_lantern_gateway_owner_v1;

CREATE FUNCTION lantern_read.current_cut_v1()
RETURNS jsonb
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path TO pg_catalog, pg_temp
AS $gateway$
DECLARE
  v_cut record;
  v_count bigint;
  v_members jsonb;
  v_payload jsonb;
  v_bad_digest_count bigint;
  v_estimated_bytes bigint;
  v_profile_count bigint;
BEGIN
  -- V4 material_cut_v1 does its own membership json_agg. Check conservative
  -- input budgets before invoking it; do not modify the frozen V4 function.
  SELECT count(*)::bigint INTO v_profile_count FROM (
    SELECT 1 FROM bt2.material_profiles
     WHERE project_scope = 'PROJECT_LANTERN' AND accepted LIMIT 1025
  ) AS bounded_profiles;
  IF v_profile_count < 1 OR v_profile_count > 1024 THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_PROFILE_COUNT_NOT_ADMITTED';
  END IF;

  -- Count all project material, including older profiles. V4 enforces
  -- material_receipts UNIQUE(material_id), bounding visible membership.
  -- No ORDER BY in this preflight, which could sort unbounded rows.
  -- Byte count is a conservative estimate, not exact output-wire bytes.
  WITH budget_rows AS MATERIALIZED (
    SELECT m.canonical_payload, m.schema_version, m.semantic_key,
           m.canonical_digest, m.source_digest
      FROM bt2.materials AS m
     WHERE m.project_scope = 'PROJECT_LANTERN'
     LIMIT 10001
  )
  SELECT count(*)::bigint,
         coalesce(sum(
           pg_catalog.octet_length(m.canonical_payload::text)::bigint
           + pg_catalog.octet_length(coalesce(m.schema_version,''))
           + pg_catalog.octet_length(coalesce(m.semantic_key,''))
           + pg_catalog.octet_length(coalesce(m.canonical_digest,''))
           + pg_catalog.octet_length(coalesce(m.source_digest,''))
           + 512 -- profile/policy, UUIDs, timestamps and JSON structure
         ), 0)::bigint
    INTO v_count, v_estimated_bytes
    FROM budget_rows AS m;

  IF v_count < 1 OR v_count > 10000 THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_MATERIAL_COUNT_NOT_ADMITTED';
  END IF;
  IF v_estimated_bytes > 8388608 THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_PAYLOAD_BYTE_BUDGET_EXCEEDED';
  END IF;

  SELECT * INTO STRICT v_cut
    FROM bt2.material_cut_v1('PROJECT_LANTERN');
  IF v_cut.facade_id IS DISTINCT FROM 'BT2_MATERIAL_CUT_V1' THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_UNEXPECTED_FACADE';
  END IF;

  -- Filter to the current profile AND policy before building payload. The V4
  -- runtime-visible view alone also contains materials of older profiles.
  WITH current_materials AS MATERIALIZED (
    SELECT m.* FROM bt2.runtime_visible_materials_v1 AS m
     WHERE m.project_scope = 'PROJECT_LANTERN'
       AND m.profile_digest = v_cut.profile_digest
       AND m.policy_digest = v_cut.policy_digest
  )
  SELECT count(*)::bigint,
         coalesce(jsonb_agg(jsonb_build_array(
           m.material_id::text, m.canonical_digest, m.semantic_key,
           m.source_digest) ORDER BY m.material_id), '[]'::jsonb),
         coalesce(jsonb_agg(jsonb_build_object(
           'material_id', m.material_id::text,
           'project_scope', m.project_scope,
           'schema_version', m.schema_version,
           'semantic_key', m.semantic_key,
           'canonical_digest', m.canonical_digest,
           'source_digest', m.source_digest,
           'canonical_payload', m.canonical_payload,
           'canonical_payload_pg_text', m.canonical_payload::text,
           'created_at', m.created_at,
           'receipt_id', m.receipt_id::text,
           'profile_digest', m.profile_digest,
           'policy_digest', m.policy_digest
         ) ORDER BY m.material_id), '[]'::jsonb),
         count(*) FILTER (WHERE m.canonical_digest IS DISTINCT FROM
           pg_catalog.encode(public.digest(
             pg_catalog.convert_to(m.canonical_payload::text, 'UTF8'),
             'sha256'), 'hex'))::bigint
    INTO v_count, v_members, v_payload, v_bad_digest_count
    FROM current_materials AS m;

  IF v_count IS DISTINCT FROM v_cut.material_count
     OR v_members IS DISTINCT FROM v_cut.exact_members::jsonb THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_CURRENT_CUT_MEMBERSHIP_MISMATCH';
  END IF;
  IF v_bad_digest_count <> 0 THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_CANONICAL_DIGEST_MISMATCH';
  END IF;

  RETURN jsonb_build_object(
    'schema', 'BT2_LANTERN_READ_GATEWAY_V1',
    'project_scope', 'PROJECT_LANTERN',
    'cut', row_to_json(v_cut)::jsonb,
    'payload', v_payload
  );
END
$gateway$;

-- Function owner transfer requires schema CREATE for the *new* owner and
-- schema ownership/CREATE for the migration caller. Keep the caller as schema
-- owner, grant the restricted target role CREATE only inside this transaction,
-- transfer the function, revoke the temporary grant, then transfer the schema.
-- Moving ALTER SCHEMA first fails for managed nonsuperuser callers (PG17).
-- Apply ACLs while the migration caller still owns function and schema;
-- after ownership transfer it cannot grant/revoke them as a managed role.
REVOKE ALL ON FUNCTION lantern_read.current_cut_v1() FROM PUBLIC;
GRANT USAGE ON SCHEMA lantern_read TO bt2_lantern_gateway_reader_v1;
GRANT EXECUTE ON FUNCTION lantern_read.current_cut_v1()
  TO bt2_lantern_gateway_reader_v1;
GRANT CREATE ON SCHEMA lantern_read TO bt2_lantern_gateway_owner_v1;
ALTER FUNCTION lantern_read.current_cut_v1()
  OWNER TO bt2_lantern_gateway_owner_v1;
REVOKE CREATE ON SCHEMA lantern_read FROM bt2_lantern_gateway_owner_v1;
ALTER SCHEMA lantern_read OWNER TO bt2_lantern_gateway_owner_v1;

SELECT bt2.assert_internal_access_boundary_v1();

DO $postflight$
BEGIN
  IF pg_catalog.has_schema_privilege(
    'bt2_lantern_gateway_reader_v1', 'bt2', 'USAGE')
     OR pg_catalog.has_schema_privilege(
       'bt2_lantern_gateway_reader_v1', 'bt2_legacy', 'USAGE')
     OR NOT pg_catalog.has_schema_privilege(
       'bt2_lantern_gateway_reader_v1', 'lantern_read', 'USAGE')
     -- Resolve by catalog OID: the managed migration caller intentionally
     -- loses lantern_read USAGE after ownership handoff, so text-to-
     -- regprocedure resolution here would fail before checking the reader.
     OR NOT EXISTS (
       SELECT 1 FROM pg_catalog.pg_proc AS p
       JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
       WHERE n.nspname = 'lantern_read'
         AND p.proname = 'current_cut_v1'
         AND p.pronargs = 0
         AND p.prokind = 'f'
         AND pg_catalog.has_function_privilege(
           'bt2_lantern_gateway_reader_v1', p.oid, 'EXECUTE')
     )
     OR EXISTS (
       SELECT 1 FROM pg_catalog.pg_proc AS p
       JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
       CROSS JOIN LATERAL pg_catalog.aclexplode(
         coalesce(p.proacl, pg_catalog.acldefault('f', p.proowner))) AS acl
       WHERE n.nspname = 'lantern_read'
         AND p.proname = 'current_cut_v1'
         AND p.pronargs = 0
         AND p.prokind = 'f'
         AND acl.grantee = 0 AND acl.privilege_type = 'EXECUTE'
     ) THEN
    RAISE EXCEPTION 'LANTERN_GATEWAY_ACL_POSTFLIGHT_FAILED';
  END IF;
END
$postflight$;

COMMIT;
