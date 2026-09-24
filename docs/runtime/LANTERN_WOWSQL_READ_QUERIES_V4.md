# LANTERN_WOWSQL_READ_QUERIES_V4

Status: CANONICAL-CANDIDATE WOWSQL READ CONTRACT / FREE-SHARED COMPATIBILITY ROUTE

Target WoWSQL project: `bt2-479e4ad9`
Project scope: `PROJECT_LANTERN`

The canonical internal Lantern state remains in schema `bt2`. On WoWSQL free-shared PostgreSQL, the Project login is intentionally denied `USAGE` on `bt2`, and the platform does not expose the Direct/owner connection route. Project currentness reads therefore use the source-controlled `bt2_project_read` projection.

The projection is read-only by contract and is valid only in `FROZEN_ZERO_PRODUCER` mode. It grants no producer authority. Any future producer authorization or material admission requires the projection to be republished or superseded before Lantern currentness may be claimed.

## Preflight — projection binding

```sql
SELECT projection_id, project_scope, target_project, source_state_digest,
       source_seed_git_blob, producer_mode, material_count,
       profile_digest, policy_digest
FROM bt2_project_read.lantern_projection_meta_v1
WHERE projection_id='BT2_LANTERN_FREE_SHARED_READ_V1'
  AND project_scope='PROJECT_LANTERN';
```

Require exactly one row with:
- `target_project = bt2-479e4ad9`;
- `source_state_digest = 29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5`;
- `source_seed_git_blob = afe33f1eae5322b18264efa9ed3502f9fe37c10d`;
- `producer_mode = FROZEN_ZERO_PRODUCER`;
- `material_count = 2`.

Any mismatch means `UNKNOWN`; do not fall back to Supabase, memory, or an inaccessible internal schema.

If the connector/target fails before this row can be established, return `UNKNOWN` for Lantern currentness without looping on equivalent calls.

## B0 / B1 — governed material cut

```sql
SELECT facade_id, profile_digest, predecessor_digest, policy_digest,
       exact_members, material_count
FROM bt2_project_read.lantern_cut_v1
WHERE project_scope='PROJECT_LANTERN';
```

Expected shape: exactly one row containing:
- `facade_id = BT2_MATERIAL_CUT_V1`;
- the accepted profile/policy digests from preflight;
- `exact_members` sorted by material ID;
- `material_count = 2`.

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
FROM bt2_project_read.lantern_materials_v1
WHERE project_scope='PROJECT_LANTERN'
ORDER BY material_id;
```

Cross-bind payload to B0:
1. payload row count == B0 `material_count`;
2. sorted `[material_id, canonical_digest, semantic_key, source_digest]` tuples exactly equal B0 `exact_members`;
3. every payload row has B0 `profile_digest` and `policy_digest`.

Then execute B1 using the same cut query.

## Stability rule
B0 and B1 must match exactly. On snapshot mismatch, retry the complete preflight -> B0 -> payload -> B1 sequence once. A second mismatch yields `UNKNOWN`.

This snapshot retry rule is not an instruction to repeatedly re-probe an unavailable connector.

## Free-shared freshness ceiling
`FROZEN_ZERO_PRODUCER` is a deliberate hosted-mode ceiling, not a permanent Lantern design. While this mode is active:
- Project reads are valid against the exact source-bound projection above;
- no producer grant or material admission may be treated as current unless this projection is republished or superseded in the same authorized change;
- the internal `bt2` schema remains inaccessible to the Project role;
- inability to read internal `bt2` directly is not permission to use another provider or memory as current state.

## Evidence ceiling
A stable projected read proves current governed material for the exact frozen WoWSQL projection only. It does not grant producer authority, material-admission authority, database write authority, Project-settings authority, merge/deploy authority, runtime identity continuity, or general BT2 source availability.
