# Project Lantern L-D2 Authorized Admission — One V1

Status: SEMANTIC ADMISSION QUALIFIED / REAL AUTHORITY UNCHANGED / ACL HARDENING SOURCE-READY / CONCURRENCY OPEN

## Scope

This qualification addresses Lantern retirement seam L-D2: preserve future governed write capability on WoWSQL without creating durable producer authority or material state.

Execution scope remains One + Two only.

## Source artifacts

- Producer-boundary migration: `database/migrations/0018_lantern_producer_boundary_v1.sql`
  - live branch blob: `2b1dbd64c3cecc47365c84dcca34c2161e5ab935`
  - source intent: owner `postgres`, `SECURITY DEFINER`, fixed `search_path=pg_catalog, bt2`, PUBLIC EXECUTE revoked, EXECUTE granted only to postgres.
  - creates no permit and no material row.
- Authorized-admission rollback smoke: `database/tests/0006_lantern_authorized_admission_rollback_smoke.sql`
  - corrected blob: `d10b1d9447a8a178eba84e94058e35145455bc55`
  - correction removed deliberate success exception and replaced it with normal `BEGIN ... ROLLBACK`, so a successful test is a successful SQL execution under `ON_ERROR_STOP`.
- Additional boundary/negative coverage source: `database/tests/0006_lantern_producer_boundary_rollback_v1.sql` blob `eadf05d0b568c6e3e8ba082ae6b79e4ae9d85574`.

## Source boundary comparison

Live Supabase source `lantern_material.append_material_v1(uuid,text,text,text,text,text)` was read directly and observed as:
- owner `postgres`;
- `SECURITY DEFINER`;
- `search_path=pg_catalog, lantern_material`;
- EXECUTE ACL `{postgres=X/postgres}`.

WoWSQL pre-migration live form remains:
- owner `postgres`;
- invoker-security (`prosecdef=false`);
- no local search path;
- default function ACL.

Two independently established that the hosted WoWSQL access boundary currently makes non-postgres PUBLIC EXECUTE operationally inert because inspected non-postgres login roles cannot CONNECT to the database, cannot USE schema `bt2`, and lack underlying table rights. Therefore no exploitable broader producer route is claimed.

## Live rollback-only semantic qualification

The corrected `0006_lantern_authorized_admission_rollback_smoke.sql` logic was executed as one transaction against `bt2-479e4ad9` and returned normal batch success.

Synthetic-only subject:
- scope `BT2_LANTERN_ADMISSION_SMOKE`;
- synthetic schema policy/profile/permit;
- no real `PROJECT_LANTERN` rows changed.

The test proved:
1. one valid synthetic permit can authorize one append;
2. the resulting material and receipt cross-bind to the exact permit/profile/policy/schema/principal;
3. a duplicate semantic subject is rejected by the uniqueness invariant;
4. an unpermitted producer is rejected;
5. real `PROJECT_LANTERN` profile/permit/material/receipt counts remain unchanged during the transaction;
6. the entire synthetic fixture rolls back.

Independent One supplemental rollback execution additionally proved:
- invalidated permit rejection;
- incomplete semantic payload rejection;
- duplicate semantic subject rejection;
- successful positive admission and receipt binding;
- zero synthetic residue after rollback.

Post-test live readback:
- synthetic permits = 0;
- synthetic materials = 0;
- synthetic receipts = 0;
- current valid `PROJECT_LANTERN` permits = 0.

## Operator limitation

The WoWSQL operator layer rejects `REVOKE` before PostgreSQL execution. Therefore the exact ACL mutation portion of migration 0018 could not be live-qualified through this operator path. This is an operator/tool limitation, not evidence that PostgreSQL would reject the DDL.

Accordingly:
- `AUTHORIZED_ADMISSION_SEMANTICS = PASS_ROLLBACK_ONLY`;
- `NO_REAL_AUTHORITY_EFFECT = PASS`;
- `NO_REAL_MATERIAL_EFFECT = PASS`;
- `PRODUCER_BOUNDARY_SOURCE_DESIGN = SOURCE_READY`;
- `PRODUCER_BOUNDARY_LIVE_ACL_APPLY = NOT_ESTABLISHED_THROUGH_CURRENT_OPERATOR`;
- `CONCURRENT_ADMISSION_SERIALIZATION = NOT_ESTABLISHED`.

## Claim ceiling

This evidence does not authorize or establish any real producer permit, real material admission, Project cutover, Supabase retirement, merge, or deployment.
