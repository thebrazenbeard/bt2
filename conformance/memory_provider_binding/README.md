# BT2 Memory Provider Catalog Conformance V1

Status: READ-ONLY SOURCE INTEGRATION CANDIDATE. This is a subordinate
verification seam for BT2 Memory Lifecycle Draft PR #124. It does not connect
to live memory tables, authorize recall, admit historical evidence, or activate
a daemon.

Offline (Python 3.11+):

~~~bash
python -m unittest discover -s conformance/memory_provider_binding/tests -p 'test_*.py' -v
python conformance/memory_provider_binding/provider_catalog.py conformance/memory_provider_binding/fixtures/vera_synthetic.json
python conformance/memory_provider_binding/provider_catalog.py conformance/memory_provider_binding/fixtures/tattler_synthetic.json
~~~

## Versioned interface

Input BT2_MEMORY_PROVIDER_CATALOG_INPUT_V1 is bounded metadata only:
provider_role, observation_time, source_ref, relations (schema, name, kind,
rls_enabled), routines (schema, name), and an optional UNTRUSTED claim of
independent authentication. No private rows, secrets, credentials, account
identifiers, model instructions, RPC calls, or action requests are accepted.
CONTRACT_V1.json documents the input.

Output BT2_MEMORY_PROVIDER_CATALOG_OUTPUT_V1 is deterministic.
For Vera, seven named RLS-enabled relations and two named functions must be
present for CATALOG_PRESENT_UNQUALIFIED. Missing objects or disabled RLS
yield MISSING_REQUIREMENTS. For Tattler, unrelated review tables yield
NOT_APPLICABLE_REVIEW_PROVIDER, and unexpected Vera memory objects produce
CROSS_PROJECT_SCOPE_CONFLICT.

Output always carries UNKNOWN_NOT_INDEPENDENTLY_VERIFIED provider identity,
UNKNOWN_NOT_PROBED runtime currentness, UNKNOWN_NOT_VERIFIED source heads,
UNKNOWN_NOT_INSPECTED public grants, false authenticated, NONE memory
admission/read/release and empty side effects. A serialized JSON snapshot
cannot authenticate itself regardless of the claimed actor.

## Source owners and compatibility

SOURCE_BINDINGS_V1.json pins exact previously inspected source heads for
STM session memory, DeepMemoryStorage historical overlays, vera-mono CAS
governed admission, and BT2 conformance. These are dated source labels,
not fresh operational state or identity readback. The Supabase Vera project
already owns R9B0 and Semantic Atlas; no competing schema was created.
Tattler has a different webhook/review purpose.

No Supabase migration, DDL/DML, branch, API grant, credential change,
protected memory read, GitHub merge, host service or new paid backend is
implemented or required by this component.

## Evidence and error correction

First RED: missing Semantic Atlas currentness function wrongly reported
CATALOG_PRESENT_UNQUALIFIED; the exact assertion passed after mandatory
function and RLS checks. Second RED: regex-only UTC accepted an impossible
February 31 date; strict calendar parsing fixed it. Hostile tests cover
missing objects, disabled RLS, duplicate identities, wrong object kind,
spoofed verification, private row smuggling, source-ref redaction, wrong
project role, deterministic output and prohibited side effects.

The connected Supabase provider was inspected read-only on 2026-11-20:
Vera had all seven required RLS-enabled catalog relations and two named
functions; Tattler had none of those Vera memory objects or functions.
That is metadata observation ONLY, not successful private memory retrieval
or authenticated access qualification. Project IDs and raw private
provider envelopes do not appear in this report.

Next independently qualify provider principal and grants, exact repo head
readback, memory epoch CAS and separate privacy/admission authorization,
latency/cost and negative replay, then owner-approved integration. This
does not modify BT2 decision policy, STM, DMS, vera-mono or Supabase.
## V1 privilege-surface qualification (separate from catalog presence)

The source-only provider_access.py accepts a bounded
BT2_MEMORY_PROVIDER_ACCESS_INPUT_V1 JSON snapshot and returns
BT2_MEMORY_PROVIDER_ACCESS_OUTPUT_V1. The companion
provider_access_probe.sql is SELECT-only and queries pg_catalog grants,
RLS flags, function SECURITY DEFINER status, constrained search-path
indicator, and schema CREATE/USAGE privileges. It never reads memory rows.

The evaluator fails closed for missing required tables/functions/schema
rights, public-role grants on expected sensitive memory objects, unsafe
security-definer search-path configuration, or new callable memory endpoints.
It now distinguishes an unlisted SECURITY INVOKER function with EXECUTE
but *without schema USAGE* from a proven exposed callable endpoint:
REVIEW_UNLISTED_SURFACES, not HOLD_PRIVILEGE_EXPOSURE. Review is still
required. It does not imply safe API routing, function body review, present
authentication, production authorization, or read access.

Real provider observation, November 20, 2026: Vera contains 8 relevant
memory/atlas relations and 22 matching functions under the wider probe.
All seven exact required tables have RLS and no direct anon/authenticated
DML grants. No CREATE grant for those roles on public or semantic_atlas.
One additional semantic_atlas runtime_manifest_stream_v4 function has
inherited EXECUTE for both client roles, but is SECURITY INVOKER and both
roles lack semantic_atlas USAGE. This is a latent grant/review item, not
a verified current disclosure. Do not revoke or expand grants without a
function caller/dependency and API schema review.

A JSON snapshot produced by this query can be edited or replayed. The
source-only program ALWAYS reports independently_authenticated=false,
runtime_currentness UNKNOWN, memory admission/read/release NONE. Live
provider receipt authentication, principal-bound privacy authorization,
readback and action decisions remain separate held work.

## November 20–21, 2026: complete function namespace and bounded inventory

Later read-only Supabase metadata established **50** relevant routines: 8
public vera_memory_* and 42 semantic_atlas routines. The prior function
filter skipped differently named Atlas routines, and the old LIMIT 33 SQL
sentinel combined with a 32-entry validator rejected the now-complete result.
Both deficiencies were reproduced with synthetic negative tests before repair.

The source probe now includes every function in the dedicated semantic_atlas
schema (not merely known name prefixes), and accepts up to 128 function
metadata entries. The SQL emits a 129th overflow sentinel, rejected by the
evaluator; the independent table cap remains 32 with its 33rd sentinel.
This is still a finite, fail-closed source inventory, not pagination,
permission widening or authentication.

The revised **actual** read-only provider query at 2026-11-21T02:04:47Z
returned 14 table/view metadata entries, all 50 function entries and
2 schema-rights entries. It passed the updated validator with
REVIEW_UNLISTED_SURFACES and reason codes for unlisted functions, tables
and EXECUTE grants without client-role schema USAGE. No required object
was missing. A separately checked Tattler snapshot had zero matching
tables/functions and remains UNKNOWN_INCOMPLETE_CATALOG for the Vera-only
access contract; Tattler is not a Vera memory provider.

Live metadata is a point-in-time observation, not an independent role
attestation. Private data rows, function bodies, policy predicates,
authoritative producer identity, Data API exposure and provider memory
admission were NOT examined or authorized. Full raw metadata receipts
remain outside the repository on the private authorized host.
