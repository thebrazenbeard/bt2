# BT2 memory provider catalog V1 — source-only evidence report

Source branch: engineer-b/memory-provider-conformance-20261120
Parent: BT2 Draft PR #124, exact head a832363060b9cc6fd457ca1c3a9686a6a7da03b0.
No main merge or provider mutation is authorized or performed.

## Source inspection

Pin only exact source heads separately as of this investigation:
- STM main c40431c77e00a9b6b817641d07768d95bdd9c238: bounded, tenant/session-scoped working records.
- DeepMemoryStorage main dc4cf8ce6251a3b19d9c098c2807898a59429eba: append-only historic evidence, correction overlays, privacy.
- vera-mono main 49a779017ded184c22712ec1a0dc7a8b558faf71: SQLite governed memory CAS and historical read-only boundary.
- BT2 PR #124 head a832363060b9cc6fd457ca1c3a9686a6a7da03b0: source-only conformance contract, not yet main.

## Connected provider metadata (read-only)

Connected Supabase Vera project: ACTIVE_HEALTHY. Direct SELECT on pg_catalog
returned four public.vera_memory_epoch_* tables and three semantic_atlas
tables with RLS true for each. A separate SELECT from pg_proc returned
public.vera_memory_epoch_get_status_v1 and
semantic_atlas.search_current_runtime_objects_v11.

Connected Supabase Tattler project: ACTIVE_HEALTHY. Same targeted SELECTs
returned zero Vera memory tables or functions. Tattler is review/webhook
infrastructure; its nonmatching catalog is NOT a failed Vera memory backend.

The metadata is real connected-provider observation but its transcription to
this source-only fixture is NOT a cryptographic or permission-bound readback.
No table row contents, keys, account identifiers, journal, training material
or identity data were queried or published. No DDL, DML, RPC invocation,
migration, branch, budget/spend or external effect.

## Tests and correction

1. Real RED: initial stub incorrectly accepted absent Semantic Atlas currentness
   function as catalog present, assertion expected MISSING_REQUIREMENTS,
   exit 1. Green after strict required function and RLS checks.
2. Real RED: UTC shape regex accepted impossible calendar day
   2026-02-31, exit 1; green after parsing calendar date.
3. Real RED: BT2 main SHA incorrectly pinned as location of PR124-only
   memory conformance source, exit 1; corrected to exact PR124 source head.
4. Full offline synthetic tests check project scope, spoofed authentication,
   RLS, missing functions, duplicate objects, private row/secret avoidance,
   timestamp validity, source-ref privacy and deterministic CLI.

## Security ceiling

A JSON envelope can be forged. Matching these names and RLS flags only
establishes conformity to a supplied catalog snapshot. It cannot assert
that the connector principal is authorized, RLS policies are correct,
source heads are current, memory is admitted, runtime is qualified, or
a merge/release may proceed. The component does not add a Supabase
client or expose a new endpoint. All currentness and permission fields
remain unverified or NONE.

Independent owner review is required before admission bridges or any
Supabase/GitHub main mutation. This work is separate from BT2's
insight governor and signal_ingest Draft PR #123.