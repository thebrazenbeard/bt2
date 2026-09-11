# BT2 Migration Acceptance Architecture V1

Status: ACTIVE SYSTEMS-ARCHITECTURE GATE / NOT CUTOVER AUTHORITY

Date: 2026-09-11

Systems Architect: Two

Coordinator / Integration Owner: One

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

Execution boundary: One + Two only unless Patrick explicitly changes it.

## 1. Acceptance subject

BT2 migration acceptance does not come from accumulating subsystem PASS results. It belongs to one exact integrated candidate that combines One's source-preservation/integration lane and Two's database/integrity lane.

Every acceptance result must bind:

- exact One source-preservation head;
- exact Two database/integrity head;
- exact combined integration commit/tree;
- exact `database/BUILD_MANIFEST_V1.json` package digest;
- exact WoWSQL target/fingerprint used for runtime qualification;
- exact frozen legacy source cuts;
- exact governed Lantern stable cut used for any current-equivalence claim;
- exact applicable migration-receipt set;
- exact cutover-procedure version when cutover is tested.

A PASS does not automatically follow a later head, package tree, migration/data load, source cut, provider/access configuration, training version, Lantern cut, or cutover procedure. Stale evidence remains historical evidence about its exact subject.

At this architecture cut there is **no exact integrated migration candidate**. PR #2 and PR #3 remain separate draft branches from the same historical base. Therefore `BT2_MIGRATION_ACCEPTED` is presently **NOT YET A DEFINED EXACT SUBJECT**.

## 2. System-level acceptance propositions

### A1 — Canonical reconstruction

A blank PostgreSQL 16 destination must reconstruct from canonical GitHub source plus explicitly preserved migration inputs, without hidden WoWSQL pre-state.

Current: source package, ordered migrations, post-preservation loads, and tests exist; live replay is qualified; GitHub Actions still creates a job with no runner/steps, so true blank execution has not occurred.

Disposition: **OPEN / CUTOVER BLOCKER**.

### A2 — Identity, topology, and authority separation

Durable agent identity, runtime/session identity, checkpoint lineage, training package, qualification, installation, assignment, and authority must not substitute for one another. The One-led topology must be mechanically enforced.

Current: hostile relational/runtime probes pass live and current topology is correct.

Disposition: **COMPONENT PASS / INTEGRATED RECHECK REQUIRED**.

### A3 — Recovery, queue, retry, and ambiguous-effect safety

Queue/work recovery must survive response loss, stale leases, reclaim, replay, crash, and ambiguous effects without duplicate or unauthorized mutation. Consequential effect history remains append-only through PREPARED/ATTEMPTED/VERIFIED/FAILED/AMBIGUOUS/RECONCILED.

Current: Queue V2, checkpoint CAS/lineage, and operation-journal hostile probes pass live.

Disposition: **COMPONENT PASS / INTEGRATED RECHECK REQUIRED**.

### A4 — Training lifecycle separation

Preserved source != compatibility != qualification != BASE_READY != installation != activation != assignment != authority/currentness.

Current:
- 8 canonical package rows are `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`;
- qualification rows = 0;
- installation-event rows = 0;
- source reconstruction/replay for those 8 passes;
- One still has Four/Five/Six/Nine/Thirteen package preservation to complete on the One-owned lane.

Disposition: **PARTIAL / SOURCE RECOVERY INCOMPLETE**.

### A5 — BugOps semantic convergence

Canonical BugOps must preserve intake identity, SEV meaning, state/routing/dispatch generations, stale-dispatch fencing, evidence-gated closure, reopen history, and response-loss-safe replay.

Current: full live lifecycle hostile probe passes; source runtime had zero current bug reports at inspection.

Disposition: **MECHANISM COMPONENT PASS / INTEGRATED ROUND-TRIP RECHECK REQUIRED**.

### A6 — Lantern governed-material equivalence

Canonical material handling must preserve source/runtime separation, digest distinctions, accepted-profile lineage, policy binding, authorization history, canonicalization protections, admission receipts, stable-cut reading, and fail-closed currentness. Historical permits never become current authority by import.

Current: prior two-member read-cut equivalence passed; no active permit was manufactured; target lineage serialization was aligned; negative admission gates pass.

Still unresolved: positive concurrent admission under legitimate authorization and fresh cutover-time stable-cut equivalence.

Disposition: **PARTIAL / BLOCKS SOURCE-LANTERN RETIREMENT**.

### A7 — Historical preservation and provenance completeness

Each legacy boundary called preserved must have a preservation mode and evidence appropriate to it: exact Git archive, lossless object/row ledger, mapped representation, or explicit intentional exclusion.

Live evidence at this architecture cut:
- `bt2.source_snapshots = 24`;
- `bt2.migration_receipts = 14` after registry receipt V2;
- `bt2_legacy.source_objects = 14`, all Hephaestus qualification/continuity evidence;
- `bt2_legacy.source_rows = 0`.

The Git archive is materially further advanced than the canonical legacy object/row ledger. Full historical preservation is therefore not complete.

Registry-receipt drift found during this architecture sweep is now closed correctly:
- V1 remains VERIFIED historical evidence for the seven-package subject;
- V2 `BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V2` is VERIFIED for the current eight-package source subject;
- V2 digest: `ab185318e8865136228efd684382d3e67601abfa357ffcabc3be6ca1c8312e11`.

Disposition: **OPEN / BLOCKS LEGACY RETIREMENT**, with the registry receipt sub-gap **CLOSED**.

### A8 — Service/access boundary

The canonical database must not be accidentally exposed through unrelated hosted/API/login roles; administrator/direct credentials remain a separately governed capability.

Current: live all-non-super-login assertion passes and no observed `public` bridge reaches `bt2`/`bt2_legacy`; explicit ACL hardening remains admin-only/staged because the WoWSQL MCP rejects privilege mutation.

Disposition: **CURRENT-RUNTIME PASS / FINAL ACCESS CONTRACT REQUIRED**.

### A9 — One/Two integration coherence

The combined destination must have one source manifest, database build identity, receipt frontier, topology model, and no contradiction between repository and runtime evidence.

Current: PR #2 and PR #3 are complementary, draft, and separate. No combined tree has been qualified.

Disposition: **OPEN / PRIMARY NEXT ARCHITECTURAL GATE**.

Passing sequence:
1. One identifies exact PR #3 preservation frontier.
2. One designates/creates exact combined candidate from exact One and Two heads.
3. Two inspects combined path and semantic conflicts.
4. Build/source manifests are rebound to the combined subject.
5. Every predecessor PASS is classified `APPLICABLE`, `REQUIRES_REPLAY`, or `HISTORICAL_ONLY`.
6. Required replay/reconstruction occurs before any migration-level acceptance claim.

### A10 — Cutover, rollback, and retirement

Destination correctness alone is insufficient. The transition must be demonstrated.

Required cutover architecture:
- enumerate legacy write surfaces/current writers;
- define freeze/stop-write points;
- capture final source frontier immediately before cutover;
- reconcile final delta into canonical state;
- verify destination against that frontier;
- switch authoritative routing;
- run bounded post-cutover write/readback/recovery smoke;
- preserve rollback trigger and rollback target while rollback remains possible;
- retire each legacy boundary only after its own gate passes;
- preserve historical repositories/evidence unless separately authorized for deletion.

Current: no complete executable cutover/freeze/final-delta/rollback procedure has been demonstrated.

Disposition: **OPEN / FINAL CUTOVER BLOCKER**.

## 3. One / Two operating contract

One owns source preservation, integration coordination, remaining source recovery, source-side semantic classification, and proposed final integration/cutover sequencing.

Two owns destination systems architecture, database/integrity implementation, cross-subsystem invariants, exact acceptance propositions/invalidation rules, architecture review of the integrated candidate/cutover sequence, and destination-side corrections needed to satisfy those propositions.

Two does not direct or depend on other workers for this migration. One does not need to hand Two a ticket before Two identifies an architectural consequence. Two returns consequences, invariants, blockers, and tests to One; One owns sequencing/integration.

## 4. Immediate sequence

1. One continues Four/Five/Six/Nine/Thirteen preservation on the One-owned lane.
2. Two holds destination invariants stable and continues architecture-wide drift checks.
3. At One's next preservation checkpoint, One supplies exact PR #3 head + semantic frontier.
4. Two reviews that frontier against A1-A10 before integration.
5. One designates/creates the exact combined integration candidate.
6. Two binds that candidate and reclassifies all predecessor PASS evidence.
7. Exact combined reconstruction/qualification occurs when a blank execution route exists.
8. Only after A1-A9 close do One and Two exercise A10 cutover/rollback.
9. Retirement remains explicit per legacy boundary; there is no global shortcut.

## 5. Current blocker set

`BT2_MIGRATION_ACCEPTED = NOT YET A DEFINED EXACT SUBJECT`

Current system-level blockers:

- no exact combined PR #2 + PR #3 candidate;
- blank-database reconstruction unexecuted;
- remaining active-role training source preservation incomplete;
- historical object/row preservation ledger incomplete;
- positive Lantern concurrency/fresh cutover-time read equivalence unresolved;
- final production access contract not yet explicit beyond current hosted isolation evidence;
- cutover/freeze/final-delta/rollback procedure not yet demonstrated.

Component PASS results remain valuable, but none becomes migration-level acceptance until it is bound to and survives the exact integrated candidate.