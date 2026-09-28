# LANTERN_POSTGRESQL_READ_QUERIES_V4

Status: SOURCE CANDIDATE / PROVIDER-NEUTRAL POSTGRESQL CURRENTNESS READ

Project scope: `PROJECT_LANTERN`

## Preferred SQL Connectome route

Call:

```text
lantern_cut(project_scope="PROJECT_LANTERN")
```

The tool must execute the cut and payload inside one PostgreSQL `REPEATABLE READ READ ONLY` transaction and return:
- exact database/runtime identity;
- one governed cut;
- ordered payload rows;
- a receipt binding the runtime identity, project scope, profile, policy, material count, and exact membership digest.

A successful MCP transport call is not enough. The returned cut/payload must satisfy the cross-binding rules below.

## Direct PostgreSQL equivalent

A governed direct-read implementation must preserve one transaction snapshot:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;

SELECT current_database() AS database_name,
       current_user AS database_user,
       current_setting('server_version_num') AS server_version_num,
       to_regclass('bt2.runtime_visible_materials_v1')::text AS materials_view,
       to_regprocedure('bt2.material_cut_v1(text)')::text AS cut_function;

SELECT facade_id, profile_digest, predecessor_digest, policy_digest,
       exact_members, material_count
FROM bt2.material_cut_v1('PROJECT_LANTERN');

SELECT material_id::text,
       project_scope,
       schema_version,
       semantic_key,
       canonical_digest,
       source_digest,
       canonical_payload,
       created_at,
       receipt_id::text,
       profile_digest,
       policy_digest
FROM bt2.runtime_visible_materials_v1
WHERE project_scope='PROJECT_LANTERN'
ORDER BY material_id;

COMMIT;
```

Do not emulate this sequence with separate auto-commit calls that can observe different snapshots.

## Cross-binding

Require:
1. the preflight names both canonical objects;
2. exactly one cut row;
3. `facade_id = BT2_MATERIAL_CUT_V1`;
4. payload row count equals `material_count`;
5. sorted `[material_id, canonical_digest, semantic_key, source_digest]` tuples equal `exact_members` exactly;
6. every payload row has the cut `profile_digest` and `policy_digest`.

Any mismatch yields `UNKNOWN`.

## Migration-baseline expectation

The migration target is the canonical BT2 PostgreSQL schema and migrations, not the historical `bt2_project_read` WoWSQL projection.

The accepted migrated Lantern state is expected to reconstruct the source-controlled `PROJECT_LANTERN` governed state before currentness can be claimed. Runtime qualification must bind the exact source subject and seed/data reconstruction evidence; do not infer parity merely because object names exist.

## Evidence ceiling

A valid V4 read proves current governed Lantern material for the exact qualified PostgreSQL runtime subject. It does not prove producer authority, write authority, provider permanence, Project installation, training activation, or merge/deploy authority.
