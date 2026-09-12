# LANTERN_WOWSQL_READ_QUERIES_V1

Status: CANONICAL-CANDIDATE SUCCESSOR READ CONTRACT / NOT YET INSTALLED IN CHATGPT PROJECT

Target WoWSQL project: `bt2-479e4ad9`
Project scope: `PROJECT_LANTERN`

These queries are the provider-neutral successor to the Supabase-bound Lantern B0 -> payload -> B1 governed read sequence.

## B0 / B1 — governed material cut

```sql
SELECT *
FROM bt2.material_cut_v1('PROJECT_LANTERN');
```

Expected shape: exactly one row containing:
- `facade_id = BT2_MATERIAL_CUT_V1`;
- `profile_digest`;
- `predecessor_digest`;
- `policy_digest`;
- `exact_members` sorted by material ID;
- `material_count`.

Zero rows or more than one row means current governed material cannot be established; fail closed.

## Payload fetch between B0 and B1

```sql
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
```

Cross-bind payload to B0:
1. payload row count == B0 `material_count`;
2. sorted `[material_id, canonical_digest, semantic_key, source_digest]` tuples exactly equal B0 `exact_members`;
3. every payload row has B0 `profile_digest` and `policy_digest`.

Then execute B1 using the same cut query.

## Stability rule

B0 and B1 must match exactly. On mismatch, retry the complete B0 -> payload -> B1 sequence once. A second mismatch yields `UNKNOWN`; do not substitute memory, historical source, or the retired Supabase provider.

## Evidence ceiling

A stable read proves current governed material on the exact WoWSQL target only. It does not grant producer authority, material-admission authority, database write authority, Project-settings authority, merge/deploy authority, or runtime identity continuity.
