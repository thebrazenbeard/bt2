-- WoWSQL hosted effective producer-boundary verification V1.
--
-- Blank PostgreSQL reconstruction remains stricter: migration 0018 removes
-- PUBLIC function EXECUTE entirely. Hosted WoWSQL currently blocks REVOKE at
-- its control-plane safety layer, so hosted acceptance verifies effective
-- reachability across directly effective and SET ROLE-accessible role states.

DO $check$
DECLARE
  v_target_count integer;
  v_schema_oid oid;
  v_function_oid oid;
  v_owner text;
  v_secdef boolean;
  v_config text[];
  v_reachable integer;
  v_creators integer;
BEGIN
  SELECT count(*),min(n.oid),min(p.oid)
  INTO v_target_count,v_schema_oid,v_function_oid
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='bt2'
    AND p.proname='append_material_v1'
    AND oidvectortypes(p.proargtypes)='uuid, text, text, text, text, text';

  IF v_target_count<>1 THEN
    RAISE EXCEPTION USING MESSAGE=
      'BT2_WOWSQL_PRODUCER_BOUNDARY_EXACT_SIGNATURE_COUNT:'||v_target_count::text;
  END IF;

  SELECT p.proowner::regrole::text,p.prosecdef,p.proconfig
  INTO v_owner,v_secdef,v_config
  FROM pg_proc p
  WHERE p.oid=v_function_oid;

  IF v_owner IS DISTINCT FROM 'postgres'
     OR NOT v_secdef
     OR v_config IS DISTINCT FROM ARRAY['search_path=pg_catalog, bt2, pg_temp']::text[] THEN
    RAISE EXCEPTION 'BT2_WOWSQL_PRODUCER_BOUNDARY_FORM_MISMATCH';
  END IF;

  WITH RECURSIVE role_paths(login_oid,role_oid,path) AS (
    SELECT r.oid,r.oid,ARRAY[r.oid]::oid[]
    FROM pg_roles r
    WHERE r.rolcanlogin
      AND r.rolname<>'postgres'
    UNION ALL
    SELECT rp.login_oid,m.roleid,rp.path||m.roleid
    FROM role_paths rp
    JOIN pg_auth_members m ON m.member=rp.role_oid
    WHERE m.set_option
      AND NOT m.roleid=ANY(rp.path)
  )
  SELECT count(DISTINCT rp.login_oid)
  INTO v_reachable
  FROM role_paths rp
  WHERE has_schema_privilege(rp.role_oid,v_schema_oid,'USAGE')
    AND has_function_privilege(rp.role_oid,v_function_oid,'EXECUTE');

  IF v_reachable<>0 THEN
    RAISE EXCEPTION USING MESSAGE=
      'BT2_WOWSQL_PRODUCER_BOUNDARY_REACHABLE_NONOWNER_LOGIN:'||v_reachable::text;
  END IF;

  WITH RECURSIVE role_paths(login_oid,role_oid,path) AS (
    SELECT r.oid,r.oid,ARRAY[r.oid]::oid[]
    FROM pg_roles r
    WHERE r.rolcanlogin
      AND r.rolname<>'postgres'
    UNION ALL
    SELECT rp.login_oid,m.roleid,rp.path||m.roleid
    FROM role_paths rp
    JOIN pg_auth_members m ON m.member=rp.role_oid
    WHERE m.set_option
      AND NOT m.roleid=ANY(rp.path)
  )
  SELECT count(DISTINCT rp.login_oid)
  INTO v_creators
  FROM role_paths rp
  WHERE has_schema_privilege(rp.role_oid,v_schema_oid,'CREATE');

  IF v_creators<>0 THEN
    RAISE EXCEPTION USING MESSAGE=
      'BT2_WOWSQL_PRODUCER_BOUNDARY_REACHABLE_SCHEMA_CREATOR:'||v_creators::text;
  END IF;
END
$check$;
