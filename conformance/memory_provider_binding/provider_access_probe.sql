-- READ-ONLY BT2 V1 provider privilege metadata. No private row contents.
-- Supabase connector may be used to execute this SELECT on the explicitly
-- chosen provider project; resulting snapshot is UNTRUSTED JSON evidence.
-- A metadata grant is not authorization to read or write memory rows.
WITH tab AS (
 SELECT n.nspname AS schema,c.relname AS name,
        c.relrowsecurity AS rls_enabled,c.relforcerowsecurity AS force_rls,
        jsonb_build_object('select',has_table_privilege('anon',c.oid,'SELECT'),
          'insert',has_table_privilege('anon',c.oid,'INSERT'),
          'update',has_table_privilege('anon',c.oid,'UPDATE'),
          'delete',has_table_privilege('anon',c.oid,'DELETE')) AS anon,
        jsonb_build_object('select',has_table_privilege('authenticated',c.oid,'SELECT'),
          'insert',has_table_privilege('authenticated',c.oid,'INSERT'),
          'update',has_table_privilege('authenticated',c.oid,'UPDATE'),
          'delete',has_table_privilege('authenticated',c.oid,'DELETE')) AS authenticated
 FROM pg_catalog.pg_class c
 JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
 WHERE c.relkind IN ('r','p','v','m') AND (
   (n.nspname='public' AND c.relname LIKE 'vera_memory_%')
   OR n.nspname='semantic_atlas' -- cover all Atlas tables/views, not only historic prefixes
 )
 ORDER BY n.nspname,c.relname LIMIT 33
),
fn AS (
 SELECT n.nspname AS schema,p.proname AS name,p.prosecdef AS security_definer,
        has_function_privilege('anon',p.oid,'EXECUTE') AS anon_execute,
        has_function_privilege('authenticated',p.oid,'EXECUTE') AS authenticated_execute,
        (coalesce(array_to_string(p.proconfig,','),'') LIKE 'search_path=pg_catalog%') AS search_path_limited
 FROM pg_catalog.pg_proc p
 JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
 WHERE (n.nspname='public' AND p.proname LIKE 'vera_memory_%')
    OR (n.nspname='semantic_atlas' AND (
      p.proname LIKE 'search_current_%' OR p.proname LIKE 'runtime_%' OR p.proname LIKE 'memory_%'
      OR p.proname LIKE 'capture_semantic_%' OR p.proname LIKE 'record_semantic_capture_%'))
 ORDER BY n.nspname,p.proname LIMIT 33
),
sch AS (
 SELECT n.nspname AS schema,
        has_schema_privilege('anon',n.oid,'CREATE') AS anon_create,
        has_schema_privilege('authenticated',n.oid,'CREATE') AS authenticated_create,
        has_schema_privilege('anon',n.oid,'USAGE') AS anon_usage,
        has_schema_privilege('authenticated',n.oid,'USAGE') AS authenticated_usage
 FROM pg_catalog.pg_namespace n
 WHERE n.nspname IN ('public','semantic_atlas')
)
SELECT jsonb_build_object(
 'schema','BT2_MEMORY_PROVIDER_ACCESS_INPUT_V1',
 'observed_at',to_char(now() at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'),
 'source_ref','connected-provider-metadata-only-no-private-rows',
 'independently_authenticated',false,
 'tables',(SELECT coalesce(jsonb_agg(to_jsonb(tab)),'[]'::jsonb) FROM tab),
 'functions',(SELECT coalesce(jsonb_agg(to_jsonb(fn)),'[]'::jsonb) FROM fn),
 'schema_rights',(SELECT coalesce(jsonb_agg(to_jsonb(sch)),'[]'::jsonb) FROM sch)
) AS snapshot;