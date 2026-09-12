-- WoWSQL hosted effective producer-boundary verification V1.
--
-- Blank PostgreSQL reconstruction remains stricter: migration 0018 removes
-- PUBLIC function EXECUTE entirely. Hosted WoWSQL currently blocks REVOKE at
-- its control-plane safety layer, so hosted acceptance verifies the equivalent
-- security property: no non-owner login role can both resolve the bt2 schema
-- and execute append_material_v1.

DO $check$
DECLARE
  v_owner text;
  v_secdef boolean;
  v_config text[];
  v_reachable integer;
BEGIN
  SELECT p.proowner::regrole::text,p.prosecdef,p.proconfig
  INTO v_owner,v_secdef,v_config
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='bt2'
    AND p.proname='append_material_v1'
    AND p.pronargs=6;

  IF v_owner IS DISTINCT FROM 'postgres'
     OR NOT v_secdef
     OR v_config IS DISTINCT FROM ARRAY['search_path=pg_catalog, bt2']::text[] THEN
    RAISE EXCEPTION 'BT2_WOWSQL_PRODUCER_BOUNDARY_FORM_MISMATCH';
  END IF;

  WITH target AS (
    SELECT n.oid AS schema_oid,p.oid AS function_oid
    FROM pg_namespace n
    JOIN pg_proc p ON p.pronamespace=n.oid
    WHERE n.nspname='bt2'
      AND p.proname='append_material_v1'
      AND p.pronargs=6
  )
  SELECT count(*) INTO v_reachable
  FROM pg_roles r
  CROSS JOIN target t
  WHERE r.rolcanlogin
    AND r.rolname<>'postgres'
    AND has_schema_privilege(r.oid,t.schema_oid,'USAGE')
    AND has_function_privilege(r.oid,t.function_oid,'EXECUTE');

  IF v_reachable<>0 THEN
    RAISE EXCEPTION USING MESSAGE=
      'BT2_WOWSQL_PRODUCER_BOUNDARY_REACHABLE_NONOWNER_LOGIN:'||v_reachable::text;
  END IF;
END
$check$;
