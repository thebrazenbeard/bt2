# BT2 Project Lantern L-D2 Authorized Admission Qualification — Two V1

Status: SINGLE-SESSION AUTHORIZED ADMISSION PASS / TRUE CONCURRENCY UNKNOWN / PRODUCER-BOUNDARY MIGRATION SOURCE-READY NOT LIVE
Date: 2026-09-12
Systems Architect: Two
Coordinator / execution owner: One
Execution boundary: One + Two only

## Scope

This qualification addresses future governed Lantern writes on the WoWSQL successor without creating any real `PROJECT_LANTERN` producer authority or durable synthetic material.

Patrick authorized a bounded synthetic qualification only. That authority did not include applying persistent producer-boundary DDL, creating a real producer permit, changing Project instructions, cutover, or Supabase retirement.

## Source and target admission equivalence

The source Supabase `lantern_material.append_material_v1` and target `bt2.append_material_v1` use the same material admission model in the materially relevant areas:
- READ COMMITTED requirement;
- duplicate JSON-key rejection;
- schema-policy lookup;
- accepted-profile lineage validation before and after serialization;
- current producer authorization lookup bound to project scope, producer principal, schema version, profile digest, policy digest, and validity interval;
- semantic projection from `semantic_role` + `subject_key`;
- canonical digest computation;
- atomic material + receipt creation;
- one material per `(project_scope, schema_version, semantic_key)`;
- one receipt per material;
- receipt foreign-key binding to the exact producer authorization tuple.

Current real state on both providers at qualification time:
- accepted Lantern profiles: 1;
- current valid producer grants/permits: 0;
- materials: 2;
- receipts: 2.

## Effective access-boundary observation

Source Supabase admission function is `SECURITY DEFINER`, owner `postgres`, fixed search path `pg_catalog, lantern_material`, and EXECUTE restricted to `postgres`.

Current live WoWSQL function is owner `postgres`, invoker-security, no function-local search path, and default function ACL. However, all observed non-postgres login roles are denied connection to this database and have no `bt2` schema usage, permit reads, or material/receipt insert rights. Therefore no broader effective write path was established from the current hosted state.

This is an observation about the hosted boundary, not proof that the DDL forms are identical.

## Source-controlled producer-boundary hardening

`database/migrations/0018_lantern_producer_boundary_v1.sql`
- blob: `2b1dbd64c3cecc47365c84dcca34c2161e5ab935`
- source effect: owner `postgres`, `SECURITY DEFINER`, fixed `search_path = pg_catalog, bt2`, revoke PUBLIC execute, grant execute to `postgres`;
- authority effect: NONE; it grants no producer permit and creates no material rows.

Live readback after source creation confirms migration 0018 is NOT APPLIED on WoWSQL. The live function remains `prosecdef=false`, `proconfig=NULL`, `proacl=NULL`.

## Bounded live qualification executed by Two

Two first source-controlled a one-statement rollback-sentinel admission test at commit `b11b1a0600413743a0237264a0f1a11d7a6da126`, blob `0ca14e58563f51e3bb9c017bc74352ce34b97041`.

The exact checked-in statement was executed against `bt2-479e4ad9`. It reached the deliberate terminal exception:

`LANTERN_AUTHORIZED_ADMISSION_ROLLBACK_PASS`

Before that sentinel, the statement established all of the following inside one atomic statement:
- one synthetic schema policy/profile/current permit could authorize admission;
- `bt2.append_material_v1` created one material and one receipt;
- receipt exactly cross-bound material, producer principal, permit, profile, policy, schema, semantic key, canonical digest, and source digest;
- a second material with the same semantic subject was rejected by the unique semantic-key boundary;
- an unpermitted producer was rejected;
- real `PROJECT_LANTERN` profile/permit/material/receipt counts did not change.

The deliberate exception rolled the entire statement back.

Independent post-execution readback:
- synthetic policy rows: 0;
- synthetic profile rows: 0;
- synthetic permit rows: 0;
- synthetic material rows: 0;
- synthetic receipt rows: 0;
- real `PROJECT_LANTERN` profiles: 1;
- real current permits: 0;
- real materials: 2;
- real receipts: 2.

Disposition: `AUTHORIZED_POSITIVE_ADMISSION_SINGLE_SESSION = PASS_ROLLBACK_CONTAINED`.

## CI reconciliation

The rollback-sentinel file was unsuitable for the generic GitHub workflow because `psql -v ON_ERROR_STOP=1` would treat the intentional sentinel as a failing test. It was therefore removed at commit `7de2440e1445b416c79f0e874c9f2b901bae726b` rather than leaving a known-false CI failure mode.

One concurrently added the canonical CI-shaped qualifier:

`database/tests/0006_lantern_producer_boundary_rollback_v1.sql`
- blob: `eadf05d0b568c6e3e8ba082ae6b79e4ae9d85574`
- transaction form: ordinary `BEGIN ... ROLLBACK`;
- includes temporary producer-boundary form, positive admission, no-permit rejection, invalidated-permit rejection, incomplete semantic payload rejection, duplicate-semantic rejection, intermediate cardinality oracle, and rollback.

This is the canonical source test going forward. Two's removed sentinel test remains execution evidence only, not part of the rebuild test set.

## True concurrency ceiling

True two-session admission concurrency is NOT ESTABLISHED.

`dblink` and `postgres_fdw` are available extensions but are not installed on the target. The connected WoWSQL tool does not guarantee two simultaneously live sessions, so Two did not substitute sequential calls for concurrency evidence and did not install new infrastructure under the bounded-test authority.

Disposition: `AUTHORIZED_ADMISSION_TRUE_CONCURRENCY = UNKNOWN`.

## Current package rebind inputs

After canonical test reconciliation at commit `7de2440e1445b416c79f0e874c9f2b901bae726b`:
- schema tree: `12e5e5846881f82845875ffe26644bbdeb0729c6`;
- migrations tree: `d00e657034646133590967e23b0588f2f63b5e7f`;
- tests tree: `261a5a1aada11d7fb9270571686e4e3fd010eac7`;
- admin tree: `6447503b9ab4f4613c657488742da88abea7cffa`;
- data tree: `6e82256a1bbfc9545f19b064594ca9df363ad742`;
- Lantern archive tree: `929ee632b6df04e6ee7324b1f955539e80f26258`;
- loaders tree: `d309e0d790dbc353faa0772b19247d1806732c30`;
- PostgreSQL major: 16;
- required extension: `pgcrypto`.

Digest input:

`schema:12e5e5846881f82845875ffe26644bbdeb0729c6|migrations:d00e657034646133590967e23b0588f2f63b5e7f|tests:261a5a1aada11d7fb9270571686e4e3fd010eac7|admin:6447503b9ab4f4613c657488742da88abea7cffa|data:6e82256a1bbfc9545f19b064594ca9df363ad742|archive:929ee632b6df04e6ee7324b1f955539e80f26258|loaders:d309e0d790dbc353faa0772b19247d1806732c30|postgres-major:16|required-extension:pgcrypto`

Candidate package SHA-256 after manifest rebind:

`b16753f504f0a1b9b2d1560aff3a89a8a5c0c2b4a07d22c42e4496dce7aae4c2`

Until `database/BUILD_MANIFEST_V1.json` is actually rebound, this digest is a computed candidate, not the current manifest-declared package identity.

## Claim ceiling

Established:
- future authorized admission algorithm works in a rollback-contained single-session synthetic qualification;
- no synthetic fixture or real producer authority remains from Two's live test;
- current hosted access boundary exposes no non-postgres executable write path;
- producer-boundary hardening and CI-safe rollback qualification are source-controlled.

Not established:
- migration 0018 applied live;
- true two-session concurrency behavior;
- a real producer permit;
- Project runtime write routing;
- blank GitHub-hosted rebuild execution;
- L-D3 route cutover;
- Supabase retirement/deletion.
