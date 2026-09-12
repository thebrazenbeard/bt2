# BT2 Project Lantern L-D2 Minimum Concurrency Falsification — Two V1

Status: SOURCE-READY TEST CONTRACT / EXECUTION NOT ESTABLISHED
Date: 2026-09-12
Systems Architect: Two
Coordinator / execution owner: One
Execution boundary: One + Two only

## Purpose

Define the smallest true multi-session evidence needed to close Lantern L-D2 concurrency/serialization without substituting sequential calls or lock-theory for execution.

Single-session governed admission has already passed rollback-contained qualification. This contract addresses only behaviors that require simultaneous database sessions.

All cases use an isolated synthetic scope and synthetic producer authority. Real `PROJECT_LANTERN` state must remain unchanged. Test fixtures must be removed completely after each case, and final readback must show zero synthetic permits/materials/receipts/profiles/policies.

## C1 — Same semantic subject race

Two sessions begin from the same accepted synthetic profile and same valid synthetic permit.

Session A and Session B call `bt2.append_material_v1` concurrently using:
- different material IDs;
- the same project scope;
- the same schema version;
- the same `semantic_role` + `subject_key`;
- independently valid source digests/payload bodies.

PASS requires:
- exactly one admission succeeds;
- the other fails with the semantic uniqueness boundary rather than creating a second accepted material;
- exactly one material and one receipt exist for that semantic subject before cleanup;
- the receipt belongs to the winning material and exact permit/profile/policy/principal tuple;
- no orphan material and no orphan receipt exist.

Falsifier: two successful materials for one semantic subject, zero successes, ambiguous duplicate success, or material/receipt cardinality split.

## C2 — Distinct semantic subjects race

Two sessions concurrently admit different semantic subjects using the same valid profile and permit.

PASS requires:
- both calls succeed;
- two distinct materials and two distinct receipts exist;
- each receipt cross-binds to its own material and the same valid permit/profile/policy/principal;
- neither call deadlocks or incorrectly serializes into rejection merely because the other admission is active.

Falsifier: one unrelated admission suppresses/corrupts the other, receipt/material cross-binding is wrong, or deadlock occurs under this normal parallel case.

## C3 — Profile-lineage mutation race

Create a valid synthetic accepted lineage. Interleave one admission with one transaction that changes the accepted profile lineage for the same project scope.

Both orderings must be exercised:

A. admission obtains the serialization boundary first;
- profile mutation must wait;
- admission may complete against the lineage it serialized;
- mutation may proceed only afterward.

B. profile mutation becomes visible before admission acquires the serialization boundary;
- admission must re-read the lineage after acquiring its lock;
- if the lineage differs from its pre-lock observation, admission must fail with `accepted profile lineage changed during admission` or another explicitly equivalent fail-closed result;
- no material/receipt may be admitted against the stale lineage.

Falsifier: material admission succeeds using a profile/policy lineage that changed between pre-check and serialized re-check.

## C4 — Permit invalidation race

Interleave an admission with invalidation of the exact permit used by that admission.

Both orderings must be exercised:

A. admission locks/validates the permit first;
- invalidation waits;
- admission may finish using the still-valid serialized permit;
- invalidation becomes effective only afterward.

B. invalidation commits first;
- subsequent admission must reject the permit;
- no material/receipt may be created after invalidation is visible.

Falsifier: admission succeeds after committed permit invalidation is visible, or receipt references a permit that was not valid at the serialized authorization point.

## Global invariants for every case

Before cleanup:
- material count equals successful admission count;
- receipt count equals material count;
- every material has exactly one receipt;
- every receipt binds an existing material and the exact synthetic permit/profile/policy/principal tuple;
- no duplicate semantic subject exists within one `(project_scope, schema_version)`;
- real `PROJECT_LANTERN` row counts and current valid permit count are unchanged.

After cleanup:
- synthetic schema-policy/profile/permit/material/receipt rows = 0;
- no test authority survives;
- real `PROJECT_LANTERN` remains 1 accepted profile / 0 current permits / 2 materials / 2 receipts unless separately changed by an authorized real migration before test execution.

## Execution requirements

PASS evidence must prove at least two simultaneously live PostgreSQL sessions. Sequential connector calls, two operations inside one transaction, or a single-session procedural simulation do not satisfy this contract.

A valid harness may use:
- two external PostgreSQL connections;
- a disposable clean PostgreSQL instance;
- another mechanism that demonstrably creates independent concurrent backend sessions.

Installing `dblink`, `postgres_fdw`, helper extensions, or persistent test infrastructure on the canonical target is not implied by this contract and requires separate authority.

## Closure rule

`L-D2_CONCURRENT_ADMISSION_SERIALIZATION = PASS` only when C1-C4 all pass against the same admission-function subject and producer-boundary subject.

If migration `0018_lantern_producer_boundary_v1.sql` is applied after concurrency testing, concurrency must be replayed or evidence must otherwise demonstrate the function behavior subject is unchanged except for the access-boundary attributes. Do not silently carry concurrency PASS across a changed executable function definition.

Current status: `NOT_ESTABLISHED / UNKNOWN`.
