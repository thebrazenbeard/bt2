-- BT2 Memory Lifecycle Conformance V1: read-only metadata check.
-- Run only against a specific authorized project; no row contents are read.
-- No DDL, DML, RPC, user, credential, or journal access.
SELECT n.nspname AS schema_name, c.relname AS relation_name,
       c.relkind AS relation_kind, c.relrowsecurity AS rls_enabled
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname IN ('semantic_atlas','build_team_2','public')
  AND (c.relname LIKE '%memory%' OR c.relname LIKE '%datum%' OR n.nspname = 'semantic_atlas')
  AND c.relkind IN ('r','p','v','m')
ORDER BY n.nspname, c.relname
LIMIT 100;