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
## Follow-up: real role privilege matrix and new false assurance corrections

Fresh read-only catalog SQL on November 20 examined direct role grants,
schema rights, search-path configuration and function execution mode,
in addition to mere table/function presence. No content rows were read.

Observed 8 matching relations, 22 matching routines, and two schemas.
For the seven required memory tables, anon and authenticated had no
SELECT/INSERT/UPDATE/DELETE object grants. Neither role could CREATE
in public or semantic_atlas. The two required functions were
SECURITY DEFINER, had pinned search_path settings, and neither client
role could EXECUTE them. Wider function inventory found one unrelated
immutable SECURITY INVOKER manifest-format routine with inherited EXECUTE
rights but no client schema USAGE. That observation does NOT establish an
exploitable exposure; classify as review/latent permission until schema
API exposure and function semantics are independently qualified.

Observed source RED -> GREEN cases: baseline privilege checker marked a
public SELECT grant as catalog present; failed exact assertion before
new access gate. An unlisted newly granted memory table/function was
ignored and produced a misleading restricted result (two real FAILs),
now fails closed. Missing schema write-grant evidence had falsely
qualified the source surface; now UNKNOWN. An unlisted invoker routine
with no schema USAGE was mislabeled proven exposure; source check now
returns review rather than a breach claim. All tests use synthetic data
and the live metadata snapshot remains private; no credential or row data
is committed.

## Connected provider access snapshot — exact local source evaluation

The committed SELECT-only provider_access_probe.sql was executed against
the connected Vera Supabase project. The returned metadata snapshot contained
8 memory/Atlas relations, 22 matching functions and rights for 2 schemas.
The snapshot was privately transferred to an isolated local Lappy file and
read back by provider_access.py (no database client, credential, or write in
the evaluator). The independent SHA256 of the private JSON fixture was
A8634C2A21D4D7516FD4F4CB9610803C27BD984299564548F51B57754750DE0C.

Observed evaluator output at 2026-11-20T21:20:38Z:
verdict REVIEW_UNLISTED_SURFACES, missing tables/functions/schemas all zero,
reason codes UNLISTED_EXECUTE_GRANT_NO_SCHEMA_USAGE,
UNLISTED_MEMORY_FUNCTION_REVIEW, UNLISTED_MEMORY_TABLE_REVIEW.
There was no role grant to CREATE in either inspected memory schema.
One public inherited EXECUTE belongs to an invoker manifest formatter
in a schema the client roles cannot USE. This is a follow-up review item,
not a confirmed unauthorized invocation or data leak.
Provider authenticity and present memory permission remain UNVERIFIED;
memory read, write, admission, release and other effects remain NONE.

The private provider snapshot is deliberately not copied to public GitHub.
The source evaluator makes no Supabase network request. The provider
execution and local evaluation are real observations, but the JSON
transfer is not an independently signed identity receipt.
