# Lantern least-privilege read gateway — P0 architecture decision V1

Status: **PROPOSED / BLOCKED**. This file is a design and falsifier contract, not
an installed migration, qualified runtime, or permission to switch providers.

## Why the current V4 route cannot yet qualify a separate consumer

The canonical `database/migrations/0024_postgresql_v4_provider_neutral_owner_boundary_v1.sql`
rejects `USAGE`/`CREATE` on `bt2` or `bt2_legacy`, and direct internal-relation
permissions, for every nonsuperuser login other than the migration caller
(`current_user`). That is intentional protection of BT2's internal schema.

The present SQL Connectome facade calls `bt2.material_cut_v1(text)` and directly
reads `bt2.runtime_visible_materials_v1`; target admission also calls the
`bt2` function. PostgreSQL cannot resolve those schema-qualified objects for
a separate login lacking `bt2` schema `USAGE`. Granting that `USAGE` makes the
BT2 internal-access assertion fail. Running the consumer as the migration
owner avoids that particular assertion only by collapsing the operator and
consumer privilege boundaries. Its absence of superuser/createdb flags does
not prove that it is a narrowly granted reader; object ownership and ordinary
ACLs must be independently checked.

`database/tests/0012_lantern_read_role_conflict_rollback_v1.sql` is the
rollback-only, opt-in PostgreSQL falsifier for the current condition.

## Proposed resolution; forward-only after review

1. Preserve all existing V4 schema, canonical algorithms, migration checksums,
   source manifests, and `bt2.assert_internal_access_boundary_v1()` semantics.
   No `bt2` or `bt2_legacy` schema access for the consumer login.
2. Add a **new forward-only** BT2 migration declaring a dedicated API schema
   (working name `lantern_read`, **not** `public`). Disallow `PUBLIC` schema
   access and `CREATE`. Put one versioned, explicitly `STABLE`, carefully
   audited `SECURITY DEFINER` read function in it, with a constant safe
   `search_path` and schema-qualified internal references. Own it with a
   restricted, preferably `NOLOGIN` role that has only the internal read
   privileges required by its implementation. No dynamic SQL, write path,
   mutable GUC-derived authorization, or untrusted caller-controlled object
   names. The schema/function owner cannot be the consumer.
3. The function must return one *atomic* `PROJECT_LANTERN` cut and its ordered
   full payload under the caller's single `REPEATABLE READ READ ONLY`
   transaction. It must expose exact members, material count, canonical
   source/payload digests, profile and policy digests, facade/schema version,
   and explicit failure for missing/invalid scope. A Lantern-specific consumer
   credential must be restricted to the exact `PROJECT_LANTERN` scope; it must
   not become a cross-project read key. No status inference from a
   zero-material cut. Select payload **only from the current cut's profile and
   policy**, not merely all historically accepted materials sharing a project
   scope: the V4 `runtime_visible_materials_v1` view itself also includes
   prior-profile materials, whereas `material_cut_v1` current members do not.
   A two-profile lineage fixture must prove parity. Do **not** introduce a
   `public` view/function bridge.
4. Create a separate `LOGIN` reader role with `NOSUPERUSER NOCREATEDB
   NOCREATEROLE NOREPLICATION NOBYPASSRLS`; grant only API schema `USAGE`,
   the specific API function `EXECUTE`, and explicitly necessary SQL Connectome
   identity-ledger reads. Avoid broad `pg_read_all_data` and grants on `bt2`
   tables, functions or schemas. Revoke `PUBLIC` `EXECUTE` on the gateway.
5. Introduce the new gateway as a **dual-route, opt-in source candidate** in
   SQL Connectome: the old `bt2` direct route remains only for existing pinned
   rebuild qualifications; the least-privilege consumer and operator admission
   must use the new gateway. Both routes cross-check exactly the same
   canonical cut/payload contract, with route/version in their receipts.
   A gateway implementation must not silently fall back to owner/direct `bt2`
   or another provider on failure. Change routing only through an explicit
   pinned configuration; never infer from connection success.
6. Bound the new gateway migration/version/checksum to the accepted BT2
   package manifest, SQL Connectome release and registry subject. PostgreSQL
   16 and managed PostgreSQL 17 must separately prove migration ownership,
   `SECURITY DEFINER` owner identity and safe search path; provider-neutral
   source equivalence does not confer runtime parity. Keep environment role
   provisioning out of immutable historical migrations.

This is a *proposed* minimal secure API boundary, not approved SQL DDL. Exact
return type, API grants, caller-scope authorization and audit receipt must be
reviewed against both BT2 and SQL Connectome before a migration is written.

## Acceptance and hostile gate matrix

| Gate | Executable evidence required | Failure rule |
| --- | --- | --- |
| Rebuild and ownership | Fresh PostgreSQL 16 rebuild plus PostgreSQL 17 managed-owner compatibility; pinned migration/manifest digests | `UNKNOWN`; retain previous provider |
| Reader positive | Separate non-owner `LOGIN` reader calls only `lantern_read` API in one `REPEATABLE READ READ ONLY` snapshot; **nonempty** `PROJECT_LANTERN` cut and full payload exact-member and digest parity | `UNKNOWN` on empty, drift or inconsistent read |
| Profile lineage | One scope has accepted material from prior and current profiles; reader emits **only** current-profile/policy exact members, with matching count and digest | Abort on historical overread or underread |
| Reader negative ACL | Consumer denied `bt2` schema, direct views/relations, producer functions, writes, DDL, and unauthorized project scope; unrelated logins denied gateway | Abort acceptance on any unexpected grant |
| Gateway integrity | Review SECURITY DEFINER owner, `STABLE` body, fixed search path, no dynamic SQL, no public bridge, no unaudited grant chain | Abort on drift or privilege escalation |
| TLS/physical identity | Verify-full hostname and CA; observed TLS on registry and target; independent pinned physical cluster identity and expected role/database | `UNKNOWN` if inaccessible or mismatch |
| Transport/auth | Separate authenticated client against *deployed* HTTPS MCP endpoint; invalid/expired/wrong audience token denied; no in-process bypass | `UNKNOWN` without remote proof |
| Independent consumer | Project Lantern application itself reads from that endpoint, verifies currentness/receipts and fails closed when endpoint unavailable | No promotion without direct readback |
| Recovery | Quiesced blank restore proves data, ACL, ownership, functions, policies and recovery objective independently | Hold on any untested dependency |
| Governance | Recorded operator decision, provider selection, explicit read-only promotion, revocation/fallback plan | No implicit cutover |

Existing source tests that reconstruct a disposable PostgreSQL 16 instance and
invoke SQL Connectome MCP *in-process with authentication disabled* remain
valuable, but do not satisfy the live transport, role, provider or independent
consumer gates. SQL Connectome's read-only target-admission receipt correctly
reports `database_grants_state=UNKNOWN`, `facade_payload_qualified=false`, and
`cutover_authorized=false`, even when its narrower preflight status is PASS.

Until all listed gates are evidenced against a selected and owned target,
Project Lantern `active_currentness_backend` must remain `null` and
`lantern_currentness` must remain `UNKNOWN`. WoWSQL is retired; Supabase,
Git, Project prose, chat history and source candidates are not live fallbacks.
