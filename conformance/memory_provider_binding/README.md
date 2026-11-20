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