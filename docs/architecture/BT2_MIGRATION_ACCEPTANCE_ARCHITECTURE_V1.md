# BT2 Migration Acceptance Architecture V1

Status: ACTIVE SYSTEMS-ARCHITECTURE GATE / NOT CUTOVER AUTHORITY

Date: 2026-09-11

Systems Architect: Two

Coordinator / Integration Owner: One

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

Execution boundary: One + Two only unless Patrick explicitly changes it.

## 1. Purpose

The migration is not accepted by accumulating subsystem PASS results. Acceptance belongs to one exact integrated BT2 candidate that combines One's source-preservation/integration lane with Two's database/integrity lane and then proves that the resulting destination can replace the intended legacy BT2 capabilities without losing authority boundaries, provenance, recoverability, or reconstructibility.

This document defines that integrated subject, the system-level propositions it must satisfy, evidence invalidation rules, and the cutover/retirement sequence. It does not authorize merge, cutover, legacy retirement, qualification promotion, runtime installation, producer grants, or provider mutation.

## 2. Exact integrated candidate rule

A migration acceptance result MUST bind all of the following as one candidate tuple:

- One source-preservation head (`work/source-preservation-v1@<exact sha>`);
- Two database/integrity head (`work/two-canonical-platform-integrity-v1@<exact sha>`);
- exact combined integration commit/tree produced from those inputs;
- exact `database/BUILD_MANIFEST_V1.json` package digest;
- exact WoWSQL target identity and schema/runtime fingerprint used for qualification;
- exact frozen legacy source cuts from `SOURCE_PROVENANCE_MANIFEST_V1.md`;
- exact governed Lantern stable-cut evidence used for any current material-equivalence claim;
- exact migration-receipt set applicable to the candidate;
- exact cutover procedure version, if cutover is under test.

No PR-local PASS, historical review, runtime probe, or migration receipt automatically transfers to a later candidate if a bound head, tree, package digest, migration/data load, source cut, or cutover procedure changes. Evidence may remain useful, but its applicability must be re-established.

At the time this architecture was written there is NO exact integrated migration candidate. PR #2 and PR #3 are separate draft branches from the same earlier base. Therefore `BT2_MIGRATION_ACCEPTED` is presently undefined, not merely false.

## 3. Acceptance propositions

### A1 — Canonical reconstruction

The destination must be reconstructible from canonical GitHub source plus explicitly preserved migration inputs. A blank PostgreSQL 16 target must be able to apply the captured baseline, ordered migrations, required post-preservation data loads, and deterministic tests without relying on hidden state already present in WoWSQL.

Current evidence:
- database source package and ordered manifest exist;
- live migrations/data-load replay have substantial qualification;
- GitHub Actions repeatedly creates a job but allocates no executable steps/runner, so blank-database execution has not occurred.

Disposition: **OPEN — BLOCKING CUTOVER**.

Passing condition: independent blank target reconstruction reaches the expected topology/integrity state and all repository smoke tests pass from zero state, with no pre-existing WoWSQL objects required.

### A2 — Identity, topology, and authority separation

The integrated platform must mechanically distinguish durable agent identity from runtime/session identity and prevent agent, runtime, checkpoint, qualification, package, and installation identities from cross-binding incorrectly. The active topology must encode One as primary/orchestrator; Two/Three/Four/Five/Six/Seven/Eight/Nine/Thirteen as numbered subagents; Masa+Mune as paired; Hephaestus as independent. Coordination must not imply orchestration or protected-effect authority.

Current evidence:
- relational topology constraints and runtime/session cross-binding are live and hostile-probed in Two's lane;
- current rows encode the intended topology.

Disposition: **COMPONENT PASS / INTEGRATED RECHECK REQUIRED**.

Passing condition: the combined candidate rebuilds the same topology and hostile cross-identity probes still fail closed after One's source-preservation changes are integrated.

### A3 — Recovery, queue, retry, and ambiguous-effect safety

Work recovery and external-effect recovery must remain distinct. Queue enqueue/claim/ACK/release must survive response loss, stale leases, reclaim, and replay without duplicate or unauthorized mutation. Consequential effects must preserve PREPARED/ATTEMPTED/VERIFIED/FAILED/AMBIGUOUS/RECONCILED history and enforce inspect-before-retry for ambiguity.

Current evidence:
- Queue V2 response-loss/stale-lease suite passes live;
- workspace checkpoint CAS/lineage passes;
- append-only operation journal and identity binding pass hostile probes.

Disposition: **COMPONENT PASS / INTEGRATED RECHECK REQUIRED**.

Passing condition: exact combined candidate passes the same hostile sequences after blank reconstruction and recovery works across a deliberately replaced runtime/session.

### A4 — Training source, compatibility, qualification, and installation remain separate

Preserved bytes must not imply compatibility, qualification, BASE_READY, installation, activation, assignment, authority, or currentness. Qualification and installation histories remain append-only; effective activation must fail closed if its supporting current PASS/package/runtime validity is lost.

Current evidence:
- live target has 8 canonical package registrations, all `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`;
- live qualification rows = 0;
- live installation-event rows = 0;
- source reconstruction for those eight packages and replay/idempotence pass in Two's lane;
- One's PR #3 identifies Four/Five/Six/Nine/Thirteen packages still requiring One-owned preservation.

Disposition: **PARTIAL — SOURCE RECOVERY INCOMPLETE**.

Passing condition: all intended active-role package subjects are preserved/source-bound; any imported historical qualification is separately admissible and exactly package-bound; no qualification/installation state is manufactured to fill gaps.

### A5 — BugOps semantic convergence

Canonical BugOps must preserve source severity meaning, intake identity, state/routing/dispatch generation semantics, stale-dispatch fencing, evidence-gated closure, reopen history, and response-loss-safe replay. Historical source reports remain history unless fresh review establishes a current defect.

Current evidence:
- canonical lifecycle hostile probe passes live, including report replay/adoption, dispatch CAS, stale-dispatch rejection, evidence-gated close, dispatch revocation, and reopen;
- frozen source runtime had zero current bug reports at inspection.

Disposition: **MECHANISM COMPONENT PASS / MIGRATION ROUND-TRIP STILL CANDIDATE-BOUND**.

Passing condition: blank integrated candidate passes lifecycle tests and any preserved historical BugOps objects retain their source classification/provenance without becoming active incidents.

### A6 — Lantern governance/material equivalence

Canonical governed material must preserve source/runtime separation, canonical/semantic/source digest distinctions, accepted-profile lineage, policy binding, authorization history, duplicate-key protections, admission receipts, stable-cut reading, and fail-closed currentness. Historical producer permits must not become current authority.

Current evidence:
- prior stable source cut and WoWSQL read facade matched exact two-member material identity/digest tuples;
- zero active producer permits were manufactured;
- target admission serialization was corrected toward accepted-profile lineage semantics;
- negative admission gates passed without minting authorization.

Not yet proven:
- a positive concurrent admission case under legitimate test authorization;
- freshness of the prior stable cut at final integrated-candidate qualification.

Disposition: **PARTIAL — BLOCKING RETIREMENT OF SOURCE LANTERN RUNTIME**.

Passing condition: fresh governed stable-cut read on exact source target, exact canonical read equivalence, and a bounded positive concurrency qualification using legitimate authorization or an explicitly accepted inability to perform that test. No fake permit may be created merely to make the test pass.

### A7 — Historical preservation and provenance completeness

Every legacy boundary called preserved must identify its frozen source, original subject, content/row identity or digest where feasible, canonical disposition, migration receipt, preservation fidelity, and remaining compatibility dependency.

Current live evidence at this architecture cut:
- `bt2.source_snapshots = 24`;
- `bt2.migration_receipts = 13`;
- `bt2_legacy.source_objects = 14`, all `thebrazenbeard/hephaestus / QUALIFICATION_CONTINUITY_EVIDENCE`;
- `bt2_legacy.source_rows = 0`.

Architectural conclusion: full historical preservation is NOT complete. GitHub archive preservation is materially further advanced than the canonical legacy object/row ledger.

A second provenance issue also exists: receipt `BT2-TRAINING-SOURCE-REGISTRY-POPULATION-V1` records the earlier seven-package population subject, while the current registry/source load reconstructs eight. The old receipt remains valid historical evidence for its seven-package effect but MUST NOT be used as proof of the current eight-package subject.

Disposition: **OPEN — BLOCKING LEGACY RETIREMENT**.

Passing condition: One and Two agree which legacy families require lossless object/row ledger preservation versus exact Git archive preservation, each retirement candidate has explicit membership/count/digest evidence appropriate to that preservation mode, and current receipts bind the actual candidate rather than stale predecessor subjects.

### A8 — Service/access boundary

The canonical database must not be accidentally reachable through unrelated hosted API/login roles. Administrator/direct credentials remain a separate governed capability and must not be confused with application exposure.

Current evidence:
- live access assertion passes against all observed non-superuser login roles;
- no observed `public` bridge exposes `bt2`/`bt2_legacy`;
- admin-only explicit ACL hardening artifact remains staged because the WoWSQL MCP safety layer rejects privilege mutation.

Disposition: **CURRENT-RUNTIME PASS / CUTOVER CONTRACT STILL REQUIRED**.

Passing condition: integrated candidate declares the intended production access path and verifies that only those paths are permitted. Staged admin ACL work is either deliberately applied through an authorized admin route or explicitly classified unnecessary under the provider's supported isolation contract.

### A9 — Integration coherence

One's preservation lane and Two's database lane must converge without semantic drift. The combined candidate must have one source manifest, one database build identity, one migration receipt frontier, one topology model, and no contradiction between repository evidence and runtime state.

Current evidence:
- PR #2 and PR #3 are both open/draft/mergeable and share the same historical base;
- their present work is complementary but not yet bound into a single combined commit/tree.

Disposition: **OPEN — PRIMARY NEXT ARCHITECTURAL GATE**.

Passing condition:
1. One designates an exact integration candidate from exact PR #2 and PR #3 heads;
2. combined tree is inspected for path and semantic conflicts;
3. build/package manifests are rebound to the combined subject;
4. live/runtime evidence applicable to predecessor heads is explicitly carried forward or re-run;
5. no stale receipt, qualification, or PASS is represented as applying automatically.

### A10 — Cutover, rollback, and retirement

A migration is not complete because the destination works. The transition itself must be specified and demonstrated.

Required cutover architecture:
- identify every legacy write surface and its current writer;
- define the freeze/stop-write point for each retiring surface;
- capture final source frontier/checkpoint immediately before cutover;
- apply/reconcile any final delta into canonical state;
- verify destination against the exact final frontier;
- switch authoritative routing to canonical BT2;
- perform a bounded post-cutover write/readback/recovery smoke;
- define rollback trigger and rollback target while rollback remains possible;
- only then mark legacy surfaces logically superseded;
- retain historical repositories/evidence unless separately authorized for deletion.

Current evidence: no complete executable cutover/freeze/rollback procedure has been demonstrated.

Disposition: **OPEN — FINAL BLOCKING GATE**.

## 4. Evidence invalidation rules

The following changes require explicit applicability review and usually re-execution of affected gates:

- PR #2 head changes -> database/build/runtime qualification subject changes;
- PR #3 head changes -> preservation/source membership subject changes;
- migration or data-load blob/tree changes -> reconstruction and receipt evidence changes;
- training package tree/version changes -> prior compatibility/qualification evidence does not automatically transfer;
- Lantern profile/policy/current material cut changes -> prior current-read equivalence becomes historical;
- access/provider configuration changes -> prior access-boundary PASS becomes historical;
- cutover procedure changes -> prior cutover simulation becomes stale;
- integration commit changes -> any exact integrated-candidate acceptance must be rebound.

Evidence is never discarded merely because it becomes stale; it is reclassified as evidence about its exact historical subject.

## 5. One / Two operating contract for this migration

One owns:
- source-preservation lane;
- integration coordination;
- remaining source recovery;
- source-side semantic classification;
- proposed final integration and cutover sequencing.

Two owns:
- destination systems architecture;
- database/integrity implementation;
- cross-subsystem invariants;
- exact acceptance propositions and invalidation rules;
- architecture review of One's proposed integrated candidate and cutover sequence;
- implementation of destination-side corrections needed to satisfy those propositions.

Two does not direct other workers for this migration. One does not need to hand Two a ticket before Two identifies an architectural consequence. Two should return consequences, invariants, blockers, and candidate tests to One; One decides integration sequencing.

## 6. Immediate architecture sequence

Before either branch accumulates more acceptance claims:

1. One continues remaining source preservation for Four/Five/Six/Nine/Thirteen on the One-owned lane.
2. Two keeps the destination model stable unless new source evidence requires a correction.
3. When One reaches a preservation checkpoint, One sends Two the exact PR #3 head and intended semantic frontier.
4. Two reviews that frontier against A1-A10 and returns integration blockers before merge/cutover planning.
5. One creates/designates the exact combined integration candidate from exact One/Two heads.
6. Two binds the candidate tuple and reclassifies every existing PASS as `APPLICABLE`, `REQUIRES_REPLAY`, or `HISTORICAL_ONLY` for that candidate.
7. Reconstruct/qualify the combined candidate on a blank target when an execution route exists.
8. Only after A1-A9 are closed should One and Two exercise A10 cutover/rollback.
9. Retirement remains per-boundary and explicit; there is no global "migration complete" shortcut.

## 7. Current architectural disposition

`BT2_MIGRATION_ACCEPTED = NOT YET A DEFINED EXACT SUBJECT`

Strong component evidence exists, but the system-level blockers are presently:

- no exact combined PR #2 + PR #3 integration candidate;
- blank-database reconstruction still unexecuted;
- remaining active-role training source preservation incomplete;
- historical object/row preservation ledger incomplete;
- current eight-package registry effect lacks a new candidate-bound population receipt (the seven-package V1 receipt remains historical for its exact subject);
- final positive Lantern concurrency qualification/fresh cutover-time read equivalence unresolved;
- production access contract not yet finalized beyond current hosted isolation evidence;
- cutover/freeze/final-delta/rollback procedure not yet demonstrated.

Component PASS results remain valuable. None of them is permission to call the migration complete until they are bound to and survive the exact integrated candidate.