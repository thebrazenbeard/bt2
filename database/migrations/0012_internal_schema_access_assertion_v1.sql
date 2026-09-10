-- BT2 internal service-boundary assertion V1.
-- Executable through the supported WoWSQL SQL route; makes exposure drift fail closed.
-- Explicit ACL tightening remains in database/admin/BT2_INTERNAL_SCHEMA_ACCESS_BOUNDARY_V1.sql.

CREATE OR REPLACE FUNCTION bt2.assert_internal_access_boundary_v1()
RETURNS void LANGUAGE plpgsql STABLE AS $function$
DECLARE v_role text;
BEGIN
  FOREACH v_role IN ARRAY ARRAY['anon','authenticated','service_role']::text[] LOOP
    IF has_schema_privilege(v_role,'bt2','USAGE')
       OR has_schema_privilege(v_role,'bt2_legacy','USAGE')
       OR has_schema_privilege(v_role,'bt2','CREATE')
       OR has_schema_privilege(v_role,'bt2_legacy','CREATE') THEN
      RAISE EXCEPTION USING MESSAGE='BT2_INTERNAL_SCHEMA_EXPOSED_TO_ROLE:'||v_role;
    END IF;

    IF EXISTS(
      SELECT 1
      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname IN ('bt2','bt2_legacy') AND c.relkind IN ('r','v','m','S')
        AND (
          has_table_privilege(v_role,c.oid,'SELECT')
          OR has_table_privilege(v_role,c.oid,'INSERT')
          OR has_table_privilege(v_role,c.oid,'UPDATE')
          OR has_table_privilege(v_role,c.oid,'DELETE')
        )
    ) THEN
      RAISE EXCEPTION USING MESSAGE='BT2_INTERNAL_RELATION_EXPOSED_TO_ROLE:'||v_role;
    END IF;
  END LOOP;

  IF EXISTS(
    SELECT 1 FROM pg_views
    WHERE schemaname='public' AND definition ILIKE '%bt2.%'
  ) THEN
    RAISE EXCEPTION 'PUBLIC_VIEW_BRIDGES_BT2';
  END IF;

  IF EXISTS(
    SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='public' AND p.prokind IN ('f','p')
      AND pg_get_functiondef(p.oid) ILIKE '%bt2.%'
  ) THEN
    RAISE EXCEPTION 'PUBLIC_FUNCTION_BRIDGES_BT2';
  END IF;
END
$function$;

SELECT bt2.assert_internal_access_boundary_v1();
