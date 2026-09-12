# BT2 Migration Falsification Matrix V1

Status: ACTIVE SYSTEMS-ARCHITECTURE VALIDATION MODEL / NOT CUTOVER AUTHORITY

Date: 2026-09-11
Systems Architect: Two
Coordinator / Integration Owner: One
Execution boundary: One + Two only

## Evidence subject at matrix cut

- One preservation lane: PR #3 / `work/source-preservation-v1@5fdca5acab589b2ede6199f531192ff123d3d27e`.
- Four v1.0.1 preservation on that lane: source/destination package tree `0953afaeeec7543697f97711e5a2326d954e9fa3`.
- Two destination lane observed immediately before this matrix artifact: `work/two-canonical-platform-integrity-v1@54e6ac137ae0d786e1c7beecf105ed538c7d27f9`.
- Database build package: digest `22f4336dcfbee67b30d0c4b59f154fe6418419911b23445dfdd25b20f17bd2b5`.
- WoWSQL target: `bt2-479e4ad9`, PostgreSQL 16.15 observed.
- Project Lantern Supabase source: `agvhmutlrolbaijzlbqk`.

This matrix is evidence about those exact subjects. Any changed head/build/cutover procedure requires applicability review.

## P1 — Canonical source can recreate BT2 on a genuinely blank database

Exact subjects:
- Two database package digest above;
- schema + migrations 0003-0016 + post-preservation data loads + repository smoke tests.

Design/source claim:
- GitHub, not accidental live WoWSQL state, is the reconstructible database source.

Current evidence:
- source-controlled baseline/migrations/data/tests exist;
- live migration/replay probes are strong;
- GitHub Actions repeatedly creates the rebuild job with zero executable steps, so no blank PostgreSQL reconstruction has run.

UNKNOWN:
- whether the complete repository chain executes from true zero state.

Smallest hostile falsifier:
- provision empty PostgreSQL 16 + pgcrypto, apply only repository-defined baseline/migrations/data in manifest order, run all tests. Any missing dependency/manual pre-state/ordering failure falsifies P1.

Failure belongs to:
- source/build package if required artifact absent;
- database architecture if dependency/order assumption is invalid;
- migration execution if the package is correct but the runner/process is wrong.

Disposition: OPEN / CUTOVER BLOCKER.

## P2 — Every authoritative durable runtime fact is explainable from canonical source/evidence

Exact subjects:
- current WoWSQL durable state;
- One's source/provenance lane;
- migration receipt frontier;
- exact source snapshots.

Design/source claim:
- runtime may contain mutable operational state, but every authoritative durable fact must have a source/evidence path explaining how it became current.

Current evidence:
- database DDL/package is source-controlled;
- source snapshots/receipts exist;
- training package source/effect separation exists.

UNKNOWN:
- whether every current authoritative row has a reconstruction/provenance path after One/Two integration.

Smallest hostile falsifier:
- select each authoritative table's current rows, choose one at random from each semantic family, and require a mechanically traceable source/operation/receipt/checkpoint chain. One unexplained authoritative durable row falsifies P2.

Failure belongs to:
- architecture if no provenance subject exists;
- DB if binding cannot be enforced;
- migration execution if evidence exists but was not imported/bound.

Disposition: OPEN / INTEGRATED-CANDIDATE TEST REQUIRED.

## P3 — One-led topology survives reconstruction and runtime replacement

Exact subjects:
- `agents`, `agent_units`, `agent_relationships`, `runtime_sessions`, operational checkpoint lineage;
- intended topology: One primary; Two/Three/Four/Five/Six/Seven/Eight/Nine/Thirteen orchestrated by One; Masa+Mune paired; Hephaestus independent.

Design/source claim:
- durable role identity is not runtime identity; topology is a mechanically enforced current model, not a convention.

Current evidence:
- live topology rows are correct;
- relational hostile probes reject wrong orchestration/cross-agent restoration/session binding.

UNKNOWN:
- whether the same invariants survive exact combined reconstruction.

Smallest hostile falsifier:
- on reconstructed candidate, attempt (a) second orchestrator for a numbered subagent, (b) cross-agent checkpoint restoration, (c) operation actor/session mismatch, then replace One or Two runtime session and recover from durable state without conversational memory.

Failure belongs to:
- architecture/DB for admitted impossible states;
- continuity/migration execution if replacement cannot recover required current state.

Disposition: COMPONENT PASS / INTEGRATED REPLAY REQUIRED.

## P4 — Training source, compatibility, qualification, installation, activation, assignment, and authority remain distinct

Exact subjects:
- preserved training trees on One's lane;
- canonical `training_packages`, `training_qualifications`, `training_installation_events`;
- current registry: 8 source-bound packages; Four preserved in PR #3 but not yet source-registered in live WoWSQL.

Design/source claim:
- preserved bytes are evidence of source availability only.

Current evidence:
- registry = 8 `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`;
- qualifications = 0;
- installation events = 0;
- source/replay/currentness hostile tests pass;
- One has now preserved Four; Five/Six/Nine/Thirteen remain.

UNKNOWN:
- complete active-role source recovery;
- admissibility of historical qualification evidence per exact package/current governance.

Smallest hostile falsifier:
- preserve/register one package and assert no compatibility/qualification/install state appears; insert a historical PASS then later RETRACT it and require prior ACTIVE evidence to derive `INVALIDATED`, not remain current.

Failure belongs to:
- architecture if lifecycle axes collapse;
- DB if constraints/views allow leakage;
- migration execution if preservation is promoted accidentally.

Disposition: PARTIAL / SOURCE RECOVERY INCOMPLETE.

## P5 — Retry/crash/replay cannot duplicate work or erase ambiguous effects

Exact subjects:
- Queue V2;
- workspace checkpoints;
- operation journal/projection;
- WIP-derived recovery semantics.

Design/source claim:
- work-state recovery is separate from external-effect ambiguity; ambiguous effects are inspected/reconciled, not blindly repeated.

Current evidence:
- enqueue/claim/ACK/release replay suite passes;
- stale lease/reclaim fencing passes;
- checkpoint CAS passes;
- operation transition/history probes pass.

UNKNOWN:
- full behavior on exact integrated blank candidate and replacement runtime.

Smallest hostile falsifier:
- simulate response loss after enqueue, ACK, and external ATTEMPTED effect; restart under a replacement runtime; replay old tokens/request IDs and require convergence to one work/effect history without duplicated effect.

Failure belongs to:
- architecture/DB if replay identity or transition model is insufficient;
- migration execution if candidate omitted required mechanism.

Disposition: COMPONENT PASS / INTEGRATED REPLAY REQUIRED.

## P6 — BugOps retains defect semantics rather than becoming generic task state

Exact subjects:
- BugOps frozen source cut;
- canonical bugs/bug_events/closure-evidence/dispatch queue.

Design/source claim:
- preserve SEV meaning, intake identity, state/routing/dispatch revisions, stale-dispatch fencing, closure evidence, reopen history, response-loss replay.

Current evidence:
- full rollback lifecycle probe passes live;
- source `bug_reports` current count = 0.

UNKNOWN:
- blank/integrated round-trip and historical report preservation classification.

Smallest hostile falsifier:
- report -> replay/adopt -> route -> claim stale dispatch -> current claim -> attempt close without evidence -> close with evidence -> replay -> reopen; then import a historical source report and prove it remains history rather than becoming current defect.

Failure belongs to:
- architecture/DB for lifecycle semantic loss;
- migration execution for historical/current misclassification.

Disposition: MECHANISM PASS / INTEGRATED ROUND-TRIP REQUIRED.

## P7 — Lantern semantics survive removal of Supabase

Exact subjects:
- Supabase `agvhmutlrolbaijzlbqk`;
- WoWSQL Lantern/material tables/facade;
- Project Lantern Git source binding.

Design/source claim:
- source/runtime separation, lineage/policy, canonical/semantic/source digests, authorization history, admission receipts, stable-cut read, canonicalization and fail-closed currentness survive provider migration.

Current evidence:
- fresh B0/payload/B1 source cut is stable and exact two-member target cut matches;
- normalized SHA-256 rowset digests match exactly for profile, receipt, material, authorization history, and schema policy;
- source and target both have zero current producer authority;
- negative admission and lineage corrections pass.

UNKNOWN:
- positive concurrent admission with legitimate authorization;
- current route/dependency elimination;
- preservation of 16 non-Lantern historical rows co-resident in the Supabase project.

Smallest hostile falsifier:
- after preserving co-resident history, freeze Supabase, obtain fresh stable cut/digests, route reads/writes to WoWSQL, exercise legitimate concurrent admissions (or explicitly retire write capability), then prove no current route touches Supabase and target cut remains authoritative.

Failure belongs to:
- architecture if required capability is unspecified;
- DB if admission/read semantics diverge;
- migration execution if history/dependency freeze is incomplete.

Disposition: PARTIAL. Destructive deletion governed by `BT2_LANTERN_SUPABASE_DESTRUCTIVE_RETIREMENT_GATE_V1.md`.

## P8 — Historical evidence is retained without becoming current authority

Exact subjects:
- One's archive/provenance lane;
- `bt2_legacy` ledger;
- Supabase historical governance/R9A0 state;
- old topology/training/qualification/work-state artifacts.

Design/source claim:
- historical provenance remains inspectable; import alone never promotes it to current policy/authority/state.

Current evidence:
- exact Git training archives growing on PR #3;
- `bt2_legacy.source_objects = 14` for Hephaestus qualification/continuity evidence;
- `bt2_legacy.source_rows = 0` at matrix cut;
- Supabase contains 16 non-Lantern historical/configuration rows not yet preserved in canonical row/archive evidence.

UNKNOWN:
- complete preservation mode/member digest for every legacy boundary intended for retirement.

Smallest hostile falsifier:
- pick one historical authorization/topology/work-state record; import/preserve it and require it to be queryable as history while all current projections/authority checks remain unchanged. If it becomes current merely by presence, P8 fails.

Failure belongs to:
- architecture for missing history/current distinction;
- DB for promotion leakage;
- migration execution for wrong classification.

Disposition: OPEN / LEGACY RETIREMENT BLOCKER.

## P9 — Access isolation survives provider/runtime changes

Exact subjects:
- WoWSQL project `bt2-479e4ad9`;
- `bt2` and `bt2_legacy` schemas;
- hosted API/direct-login roles.

Design/source claim:
- unrelated login/API roles cannot reach canonical BT2 data; admin/direct credentials remain distinct governed capability.

Current evidence:
- all observed non-super login roles have zero schema usage/CRUD access;
- no observed public bridge;
- runtime fail-closed assertion installed;
- explicit ACL hardening script staged because connector refuses privilege mutation.

UNKNOWN:
- final production access contract/routing and behavior if provider configuration changes.

Smallest hostile falsifier:
- from each supported non-admin access path, attempt schema usage + SELECT/INSERT/UPDATE/DELETE against canonical schemas; then change one provider-facing configuration in a disposable candidate and rerun.

Failure belongs to:
- architecture if access contract unspecified;
- provider/admin configuration if runtime grants drift;
- DB source if assertions are incomplete.

Disposition: CURRENT-RUNTIME PASS / FINAL CONTRACT OPEN.

## P10 — One/Two lanes produce one coherent destination, not colocated legacy systems

Exact subjects:
- One PR #3 exact preservation frontier;
- Two PR #2 exact architecture/database frontier;
- future combined integration commit/tree.

Design/source claim:
- destination boundaries are semantic (training, continuity, recovery, BugOps, materials, governance, database) rather than copies of source-repository boundaries.

Current evidence:
- One has a semantic source consolidation map;
- Two has normalized shared identity/recovery/queue/training/material primitives;
- PRs are complementary but not yet one candidate.

UNKNOWN:
- semantic conflicts/redundant current-state mechanisms after actual combination.

Smallest hostile falsifier:
- combine exact heads and enumerate every concept represented in more than one active subsystem (current authority, agent identity, queue custody, checkpoint currentness, qualification, material currentness). If two active mechanisms can disagree without one declared source of truth/reconciliation rule, P10 fails.

Failure belongs to:
- architecture first; then source/DB correction according to duplicated mechanism.

Disposition: OPEN / PRIMARY INTEGRATION GATE.

## P11 — Fresh One or Two can resume without hidden conversational state

Exact subjects:
- canonical repo + DB + Bus handoff/provenance + checkpoints;
- no reliance on current chat transcript as durable state.

Design/source claim:
- sessions are replaceable terminals; logical worker continuity comes from durable evidence, not hidden runtime continuity.

Current evidence:
- runtime/session identity exists;
- operational/workspace checkpoints are durable and scope-bound;
- source manifests and Bus coordination packets exist.

UNKNOWN:
- whether a genuinely fresh One/Two can recover the migration frontier using only canonical durable surfaces and avoid repeating completed/ambiguous effects.

Smallest hostile falsifier:
- give a fresh One or Two only identity/role + canonical durable surfaces, not prior chat transcript; require exact current heads, open gates, last verified effects, next safe action, and do-not-repeat set. Any required fact available only from conversation fails P11.

Failure belongs to:
- architecture/continuity if no durable place exists;
- migration execution if checkpoints/handoffs are stale/incomplete.

Disposition: OPEN / MUST TEST BEFORE CUTOVER.

## P12 — Cutover and rollback are themselves recoverable operations

Exact subjects:
- final integrated candidate;
- exact legacy write surfaces/frontiers;
- versioned cutover procedure.

Design/source claim:
- migration completion is a transition, not a destination snapshot.

Current evidence:
- retirement rules exist;
- no complete final freeze/final-delta/routing-switch/rollback rehearsal exists.

UNKNOWN:
- exact writers to freeze, final delta capture, routing switch, rollback trigger/target, post-cutover smoke.

Smallest hostile falsifier:
- execute cutover in a disposable/simulated environment, inject a failure after the routing switch but before final acceptance, and require deterministic rollback without source/destination divergence or lost effect history.

Failure belongs to:
- architecture if cutover state machine is incomplete;
- migration execution if procedure is correct but performed incorrectly.

Disposition: OPEN / FINAL CUTOVER BLOCKER.

## What One's current preservation plan is missing before copying Five/Six/Nine/Thirteen

1. **Preservation frontier must be explicit, not package-count driven.** Each newly copied package should update one exact preservation frontier manifest so downstream registration/reconstruction can consume a single subject rather than infer completeness from directory presence.

Invariant: `preserved bytes` are not considered part of the current migration frontier until an exact source tree, destination tree, preservation receipt, and frontier membership record agree.

Downstream consequence if omitted: Two's registry/data load and later blank rebuild cannot know whether the preserved package set is complete or merely whatever happened to be present at a branch head.

2. **Current-vs-historical package version selection must be encoded before registry import.** Where multiple versions exist (Mune already demonstrates this), preservation may include all versions, but the source-registration candidate must explicitly name the recommended/current package subject without turning that recommendation into qualification.

Invariant: package preservation set and package selection pointer are separate evidence subjects.

Downstream consequence if omitted: reconstruction can register the wrong preserved version while all byte-equality tests still pass.

3. **One must preserve source-side compatibility dependencies, not only package bytes.** Training manifests reference current governance/role contracts. Those dependency identifiers need an integration-time resolution map.

Invariant: no package becomes `COMPATIBLE` merely because its bytes were preserved; compatibility must be tested against the exact integrated governance subject.

Downstream consequence if omitted: old packages can be technically complete yet semantically stale under the new One-led topology.

4. **Do not wait until final cutover to classify destructive-retirement evidence.** The Supabase Project Lantern check already found historical state outside the nominal Lantern tables. Each legacy boundary should have its deletion/retirement preservation mode defined while One is still close to the source.

Invariant: destructive retirement requires an exact final source frontier plus preserved membership/digests and dependency-zero proof.

Downstream consequence if omitted: we may finish functional migration and discover the only remaining blocker is information we can no longer confidently classify or reconstruct.

5. **Integration candidate must be created before acceptance inflation.** After the remaining packages are preserved, stop accumulating branch-local PASS claims long enough to bind exact One + Two heads into one candidate and replay applicability.

Invariant: no `BT2_MIGRATION_ACCEPTED` claim exists without one exact combined commit/tree and evidence map.

Downstream consequence if omitted: both branches can become individually green while their composition is never actually validated.

## Architect's current disposition

The migration direction is sound, and multiple destination mechanisms are already strongly qualified. The main risk has shifted from local DB correctness to **evidence composition and destructive-retirement discipline**.

One should continue preservation, but package copying alone is no longer the critical path. The next meaningful architecture checkpoint is the exact preservation frontier after the remaining numbered-role packages, followed by an exact One+Two integration candidate and evidence-replay classification.