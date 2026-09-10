# BT2 Canonical Platform Integrity Review — Two V1

Status: **CHANGES REQUIRED BEFORE CANONICAL CUTOVER / DIRECTION SOUND**

Date: 2026-09-10

Reviewer: Two

Coordinator: One

Review base: `work/canonical-platform-consolidation-v1@32edb12f0f843639bece425b3d57ca784b2a76dc`

Target database: WoWSQL `bt2-479e4ad9`

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

## 1. Scope and evidence discipline

This review covers the architecture seams assigned by One in `one-0154`: canonical identity, workforce topology, training/continuity normalization, queue/operation semantics, BugOps convergence, governed-material convergence, historical/current separation, compatibility/retirement, database constraints/concurrency, and migration acceptance criteria.

Evidence labels used here:

- **OBSERVED** — directly read from the exact GitHub source cut or queried from the live WoWSQL/Supabase database.
- **SOURCE REQUIREMENT** — explicit requirement from a frozen source system being consolidated.
- **INFERENCE** — architectural conclusion from named observations.
- **PROPOSED CORRECTION** — change required or recommended for the canonical target.
- **UNKNOWN** — not yet established by the evidence inspected.

This review does not authorize cutover, merge, retirement of source repositories, deletion of source database state, manufacture of qualification, or mutation of Vera's PostgreSQL.

## 2. Executive disposition

The consolidation direction is sound and two important first-slice claims independently pass:

1. **Workforce topology current data = PASS.** The live canonical rows encode One as the primary/orchestrator of Two, Three, Four, Five, Six, Seven, Eight, Nine, and Thirteen; Masa/Mune are a separate paired unit; Hephaestus is independent; One only coordinates with the latter units.
2. **Current Lantern governed read cut = PASS.** A fresh stable Supabase B0/payload/B1 cut for `PROJECT_LANTERN` contains exactly two materials under profile `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1` and policy `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`; `bt2.material_cut_v1('PROJECT_LANTERN')` returns the same two material UUIDs and the same canonical/semantic/source digest tuple for each member.

However, the first WoWSQL implementation is **not yet cutover-safe**. The main defects are not conceptual disagreement with One's architecture; they are integrity gaps where the database currently admits states that the source systems explicitly meant to prevent.

Blocking correction set before canonical cutover:

- runtime/session identity must remain distinct from durable agent identity;
- checkpoint predecessor identity must be scope-bound;
- training package, qualification, agent, and checkpoint identity must be cross-bound;
- WIP external-effect history must be an append-only transition journal, not only a mutable projection row;
- queue enqueue/ACK/release must survive response loss and stale leases without duplicating or mutating work incorrectly;
- BugOps closure and severity normalization must retain defect-specific semantics;
- topology correctness must be enforced as an invariant rather than only represented by currently-correct rows;
- the canonical database definition must become reproducible from GitHub-owned source before WoWSQL can be treated as canonical infrastructure;
- the intentionally stricter Lantern admission-concurrency behavior must be either specified and qualified or brought back to source-equivalent semantics.

## 3. Observed current state

### 3.1 Repository and source boundary

**OBSERVED:** `thebrazenbeard/bt2` is PRIVATE.

**OBSERVED:** One's consolidation branch remained exactly `32edb12f0f843639bece425b3d57ca784b2a76dc` at review cut.

**OBSERVED:** the branch contains the migration-state document and existing BT2 source content. A recursive tree search at this exact head did not expose a checked-in `.sql` migration/schema path for the live `bt2` WoWSQL implementation.

**INFERENCE:** WoWSQL currently contains canonical-candidate runtime DDL whose complete reconstructible source is not yet evident in the canonical repository. Runtime state therefore currently outruns repository source.

### 3.2 Database population state

**OBSERVED:** the live WoWSQL database contains 13 canonical agents and the intended topology.

**OBSERVED:** `bt2.training_packages = 0` and `bt2.training_qualifications = 0`. No qualification has been fabricated merely to fill the new model.

**OBSERVED:** `bt2_legacy.source_objects = 0`, `bt2_legacy.source_rows = 0`, and `bt2.migration_receipts = 0` at this review cut. The full historical import is therefore still incomplete, consistent with One's stated migration status.

**OBSERVED:** eight `source_snapshots` rows bind the seven GitHub source cuts plus the Supabase runtime cut.

### 3.3 Lantern current cut

**OBSERVED:** Supabase target `agvhmutlrolbaijzlbqk` is `ACTIVE_HEALTHY`.

**OBSERVED:** B0 and B1 were identical around a payload read. Exact visible members:

- `575acfa9-1274-5bbd-9a82-7e672af12e5d`
- `e71548f3-3f09-49fd-9ed6-5d0179fd608c`

**OBSERVED:** the WoWSQL generalized material-cut facade returns exact member/digest equivalence for those two rows.

**OBSERVED:** three historical material producer permits exist in WoWSQL; all three are currently invalid by expiry and/or invalidation. No new active producer permit was manufactured during migration.

## 4. Identity model: durable agent is not a runtime session

### Finding I-1 — runtime/session identity is absent from the canonical relational model

**OBSERVED:** the canonical schema has durable `agents`, workspaces, assignments, queue items, handoffs, operations, and checkpoints, but no explicit runtime/session/execution-instance subject.

**INFERENCE:** if two replaceable runtime terminals act as logical agent `two`, their provenance can collapse into the same `agent_key`. A durable logical agent and the chat/session/runtime that happened to execute a step are not the same identity class.

**PROPOSED CORRECTION:** add an explicit runtime execution subject, e.g. `agent_runtime_sessions` or `execution_instances`, with at minimum:

- opaque runtime/session ID;
- durable `agent_key` FK;
- provider/runtime provenance where available;
- opened/closed timestamps;
- optional predecessor/handoff relationship;
- source evidence/metadata without granting authority.

Operations, checkpoints, claims, handoffs, and qualification evaluations should be able to record this execution identity independently of the durable agent. Absence of runtime provenance may be allowed when unavailable, but must not be silently interpreted as identity continuity.

## 5. Checkpoint and continuity integrity

### Finding C-1 — operational checkpoint parent can cross agent identity

**OBSERVED:** `operational_checkpoints.predecessor_checkpoint_id` is a plain FK to any checkpoint ID. One-root-per-agent and one-successor indexes exist, but there is no composite FK requiring parent and child to share `agent_key`.

**INFERENCE:** a checkpoint for Two can point to a checkpoint for Three while still satisfying all present constraints. That creates false continuity across durable agent identities.

**PROPOSED CORRECTION:** expose a unique candidate key `(checkpoint_id, agent_key)` and replace/augment the predecessor FK with `(predecessor_checkpoint_id, agent_key) -> (checkpoint_id, agent_key)`.

If operational checkpoint branching is forbidden, retain one-successor. If branching is legitimate for some recovery workflows, make the branch subject explicit rather than weakening the identity constraint.

### Finding C-2 — workspace checkpoint parent can cross workspace identity

**OBSERVED:** `workspace_checkpoints.predecessor_checkpoint_id` references any workspace checkpoint ID. `(workspace_id,generation)` is unique and predecessor has one-successor, but parent and child are not constrained to the same workspace.

**INFERENCE:** a checkpoint in workspace A may use a parent from workspace B.

**PROPOSED CORRECTION:** add a unique candidate key `(workspace_checkpoint_id,workspace_id)` and composite predecessor FK `(predecessor_checkpoint_id,workspace_id)`.

### Finding C-3 — workspace lineage root and generation adjacency are underconstrained

**OBSERVED:** there is no one-root-per-workspace constraint and no rule requiring a root to be generation 0 or a successor to advance exactly one generation. No trigger/function currently enforces atomic compare-and-swap between `workspaces.generation` and appended checkpoint generation.

**SOURCE REQUIREMENT:** WIP uses workspace generation as an optimistic-concurrency token; stale workers must refresh instead of overwriting a newer frontier.

**PROPOSED CORRECTION:** canonical checkpoint append must be a controlled atomic operation that:

1. locks the workspace row;
2. checks expected current generation;
3. checks parent is the current checkpoint for the same workspace;
4. writes generation `current + 1` (or a precisely specified root convention);
5. updates workspace projection/current generation in the same transaction;
6. rejects stale expected generations.

Do not rely on callers to preserve this invariant manually.

## 6. Training and qualification identity integrity

### Finding T-1 — qualification can bind an agent to another agent's package

**OBSERVED:** `training_qualifications.agent_key` and `training_package_id` have independent FKs. No composite FK requires the selected package to belong to the same agent.

**INFERENCE:** the database admits a `PASS` row asserting Three qualified against a training package belonging to Two.

**PROPOSED CORRECTION:** create a unique package key `(training_package_id,agent_key)` and composite qualification FK `(training_package_id,agent_key)` to it.

### Finding T-2 — operational checkpoint can combine incompatible agent/package/qualification identities

**OBSERVED:** operational checkpoints separately reference `agent_key`, `training_package_id`, and `qualification_id` without a constraint that all three describe the same qualified subject.

**PROPOSED CORRECTION:** training qualification should expose a unique composite identity such as `(qualification_id,agent_key,training_package_id)`. A checkpoint that claims training/qualification continuity must reference that tuple. If package or qualification is intentionally absent, absence must be explicit rather than inferred.

### Finding T-3 — nullable source-set digest weakens package uniqueness

**OBSERVED:** `training_packages` is unique on `(agent_key,version,source_set_digest_sha256)`, but `source_set_digest_sha256` is nullable.

**INFERENCE:** PostgreSQL uniqueness permits multiple rows with the same agent/version and NULL digest.

**PROPOSED CORRECTION:** either require a non-null immutable source-set digest for `REGISTERED` and stronger states, or create a partial uniqueness/state constraint that prevents ambiguous registered package identities while still allowing unbound discovery records.

No missing historical worker may receive `PASS` merely to satisfy this schema. Discovery, package binding, qualification evidence, and activation remain separate states.

## 7. WIP operation journal convergence

### Finding O-1 — append-only external-effect history was collapsed into a mutable projection

**SOURCE REQUIREMENT:** frozen WIP defines external-effect recovery as an event chain through `PREPARED -> ATTEMPTED -> VERIFIED / FAILED / AMBIGUOUS`, with later reconciliation represented explicitly. Its operation-event schema has `sequence`, `previous_event`, and `RECONCILED`; historical records are append-only.

**OBSERVED:** canonical `bt2.operations` has only one mutable row per operation with a current `state`. There is no `bt2.operation_events` table and no trigger preserving state transitions.

**INFERENCE:** updating one row from PREPARED to ATTEMPTED to VERIFIED destroys the durable transition history WIP uses to recover from interrupted responses. The current table is a useful current-state projection, not a sufficient journal.

**PROPOSED CORRECTION:** retain `operations` as the current projection if desired, but add an append-only `operation_events` chain. At minimum bind:

- operation ID;
- monotonic sequence;
- previous event ID/sequence;
- state including `RECONCILED`;
- actor agent + optional runtime session;
- target and precondition snapshot;
- request/effect/result digests;
- recovery instruction;
- effect/readback receipt for VERIFIED/RECONCILED;
- created timestamp.

A controlled transition function should append the event and update the projection in one transaction. Direct state mutation must not be the canonical transition path.

### Finding O-2 — operation state-dependent fields are not mechanically enforced

**OBSERVED:** state is check-constrained, but nothing requires ATTEMPTED to carry attempt evidence, terminal states to carry resolution evidence, or legal transitions to follow a state graph.

**PROPOSED CORRECTION:** enforce a transition matrix in the controlled append function and state-dependent constraints. `AMBIGUOUS` must remain a first-class unresolved effect requiring inspect-before-retry; it must never be silently converted into failure or safe retry.

## 8. Dispatch queue custody, lease, and response-loss semantics

### Finding Q-1 — generic enqueue is not idempotent

**OBSERVED:** `enqueue_work` creates a random queue item on every call. It stores a payload digest but has no caller-supplied dispatch/idempotency identity and no operation binding.

**INFERENCE:** if enqueue succeeds but the response is lost, repeating the same call can create duplicate work. This violates the recovery intent inherited from WIP and BugOps.

**PROPOSED CORRECTION:** canonical enqueue needs a stable caller-supplied dispatch key/request ID and request digest. Replay of the same identity+digest must return the existing queue item; reuse with a different digest must fail conflict. The idempotency scope must be explicit (for example queue + logical source + logical target + dispatch key), not global by accident.

### Finding Q-2 — ACK is exact-token but not response-loss idempotent

**OBSERVED:** `ack_work` succeeds only while the row is `CLAIMED`, token matches, and lease has not expired. It leaves lease token/owner on the row but subsequent identical ACK sees `ACKED` and raises `STALE_OR_INVALID_LEASE`.

**INFERENCE:** a successful ACK followed by response loss cannot be safely replayed as confirmation.

**PROPOSED CORRECTION:** persist an append-only ACK receipt/event. Replaying the same queue item + claim generation/token after successful ACK should return the same terminal receipt; a different claimant/token must fail.

### Finding Q-3 — expired holder may release before another claimant reclaims

**OBSERVED:** `release_work` checks CLAIMED + lease token but does not require `lease_until >= now`.

**INFERENCE:** an expired worker still has mutation authority until another claimant happens to replace its token. Lease expiry should itself terminate ordinary holder authority.

**PROPOSED CORRECTION:** require a live lease for ordinary release/dead-letter mutation. Recovery of expired work belongs to reclaim/reconciliation logic, not the expired holder.

### Finding Q-4 — claim/retry history is only partially preserved

**OBSERVED:** queue row retains current lease and a cumulative `claim_count`, but there is no append-only queue event/claim receipt history.

**PROPOSED CORRECTION:** preserve claim/reclaim/ACK/release/dead transitions in an append-only dispatch-event table or operation-journal specialization. This is especially important for custody disputes and crash/retry reconstruction.

### Finding Q-5 — expired-claim selection lacks a supporting partial index

**OBSERVED:** the queue has a READY partial index, while `claim_work` also scans expired CLAIMED rows by `lease_until`.

**PROPOSED CORRECTION:** add an expired-claim/reclaim index appropriate to `(queue_name,target_agent_key,lease_until)` for CLAIMED rows after workload shape is fixed. Correctness comes first, but WoWSQL's low resource/concurrency limits make avoiding unnecessary scans useful.

### Finding Q-6 — retry/dead policy is caller-controlled without canonical claim ceiling

**OBSERVED:** `release_work` accepts caller-selected `p_dead`; no queue-level max attempts/dead policy is enforced.

**PROPOSED CORRECTION:** make retry ceilings/backoff/dead-letter policy explicit per queue/work kind or assignment. A caller may report failure context, but should not silently redefine platform custody policy.

## 9. BugOps convergence

### Finding B-1 — severity semantics were renamed without an explicit reversible map

**SOURCE REQUIREMENT:** BugOps source severity is `SEV-0` through `SEV-3`, with SEV-0 specifically covering safety/security/data-loss/protected-effect risk and SEV-1 covering core control/identity/authority/provenance/correction/integrity failures.

**OBSERVED:** canonical `bugs.severity` uses `LOW/MEDIUM/HIGH/CRITICAL`.

**INFERENCE:** a generic label rename is acceptable only if semantic meaning and round-trip provenance are retained. Otherwise a migrated historical `SEV-1` may become an underspecified generic severity.

**PROPOSED CORRECTION:** either preserve the canonical SEV scale or define/version an explicit mapping with original source severity retained in migration provenance. Do not infer mapping ad hoc during import.

### Finding B-2 — canonical status function admits transitions looser than defect lifecycle evidence

**OBSERVED:** `update_bug_status` mostly validates that the requested label is in the enum. Outside CLOSED/REOPENED handling, it permits transitions such as NEW -> CLOSED.

**SOURCE REQUIREMENT:** a substantive BugOps incident closes only after the mechanism is bounded, corrective controls and regression cases exist, required issue/branch/PR review path is complete or an explicit exception exists, claimed implementation/effect is verified, and unresolved hypotheses remain explicit.

**PROPOSED CORRECTION:** separate lifecycle state from closure qualification. Use an explicit transition matrix and a closure receipt/evidence subject. A close transition must reference the evidence required by the applicable BugOps policy or an explicit exception record. Source merge alone is never sufficient evidence of runtime correction.

### Finding B-3 — intake idempotency path conflicts with operation uniqueness

**OBSERVED:** `report_bug` contains logic intended to converge on an existing `bugs.intake_key` when the digest matches. But before that convergence path can complete, it inserts an `operations` row whose `(target_locator,idempotency_key)` is unique and both values are derived from the same intake key.

**INFERENCE:** a retry using a new operation UUID but the same intake key can hit the operation uniqueness constraint instead of reaching the intended existing-bug convergence behavior. Concurrent same-intake submissions lock by different operation IDs and have the same issue.

**PROPOSED CORRECTION:** define one authoritative intake idempotency identity. Either operation identity owns the intake key and returns the already-established result, or bug intake owns it and the operation journal references that result. Do not maintain two conflicting uniqueness mechanisms.

## 10. Workforce topology invariants

### Finding G-1 — current topology rows are correct; admissible future rows are too broad

**OBSERVED:** current data exactly matches Patrick's intended workforce topology.

**OBSERVED:** schema checks constrain enum-like `unit_type`, `role_kind`, and `relation_type`, but do not mechanically enforce their cross-table meaning. `agent_units.orchestrator_agent_key` is not currently an FK to `agents`; an ORCHESTRATED_TEAM can be created without an orchestrator; a PAIRED/INDEPENDENT unit can carry one; and arbitrary agents can receive `ORCHESTRATES` edges as long as source != target.

**PROPOSED CORRECTION:** enforce at least these invariants through FKs plus deferred constraint triggers or controlled mutation functions:

- an ORCHESTRATED_TEAM has exactly one active orchestrator who is PRIMARY in that same unit;
- each active SUBAGENT in that unit has exactly one active ORCHESTRATES edge from that orchestrator;
- PAIRED and INDEPENDENT units have no orchestrator;
- PAIRED_WITH members belong to the same paired unit and pairing symmetry is maintained;
- Hephaestus cannot become an orchestrated numbered subagent through a stray relation row;
- COORDINATES_WITH conveys coordination only, never transitive write/merge/deployment authority.

The old coequal-facet topology belongs in provenance, not in active relationship rows.

## 11. Governed material / Lantern convergence

### Finding L-1 — current governed read-cut equivalence passes

**OBSERVED:** profile, policy, member UUIDs, canonical digests, semantic keys, and source digests match between the stable Supabase cut and WoWSQL generalized cut.

Disposition for current read-cut migration: **PASS**.

### Finding L-2 — producer authorization migration is safely historical

**OBSERVED:** all three imported producer permits are currently invalid. No active write permit was inferred from historical authority.

Disposition: **PASS** for this boundary.

### Finding L-3 — canonical append has a concurrency behavior difference from source Lantern

**OBSERVED:** source Supabase `append_material_v1` pre/post serialization comparison is bound to accepted-profile lineage. Canonical WoWSQL `append_material_v1` compares the generalized material cut including `exact_members` before and after locking the profile table.

**INFERENCE:** this is stricter than source behavior. A distinct material admitted by another concurrent transaction between the two reads can invalidate the second admission even when accepted-profile lineage did not move. This may be a deliberate conservative policy, but it is not exact behavioral equivalence.

**PROPOSED CORRECTION:** make the choice explicit:

- if source-equivalent concurrency is desired, serialize/check profile lineage rather than current material membership; or
- if stricter admission serialization is intended, declare it as a canonical policy change and qualify simultaneous distinct-semantic-key admissions for liveness, retry safety, and no false duplicate creation.

Do not silently call this exact behavioral equivalence based only on the current read cut.

## 12. Historical/current separation

### Finding H-1 — architecture direction is correct; import population is not complete

**OBSERVED:** `bt2_legacy` is structurally present but currently empty. Migration receipts are also empty.

**INFERENCE:** historical preservation is still in-progress, not failed. This becomes a blocker only if cutover/retirement is attempted before it is populated and verified.

**PROPOSED CORRECTION:** every imported historical object/row should bind source system + exact source snapshot + original locator/primary identity + content digest + classification (`HISTORICAL`, `SUPERSEDED`, `ACTIVE_CANDIDATE`, etc.). Promotion from history into active policy must be a separate explicit event, never a side effect of import.

Old Slack/R9A0/topology notices must remain historical unless independently re-authorized.

## 13. Database source-of-truth and rebuildability

### Finding S-1 — live DDL currently outruns evident GitHub reconstruction source

**OBSERVED:** the canonical database has extensive tables, indexes, functions, and views. At the reviewed branch head, no complete GitHub-owned SQL reconstruction/migration source was evident in the recursive tree.

**INFERENCE:** if WoWSQL were lost, replaced, or needed an independent qualification environment, the canonical database could not yet be proven reproducible solely from the new canonical repository.

**PROPOSED CORRECTION:** before cutover, add a source-controlled database package under an intentional path such as:

- `db/schema/` or ordered `db/migrations/` for canonical DDL;
- `db/fixtures/` for non-secret qualification fixtures;
- `db/tests/` for executable invariants;
- a manifest binding schema version, ordered migration digests, required extensions/features, and target PostgreSQL assumptions;
- a migration receipt written only after exact source has been applied and verified.

The live database should become a build/install/runtime instance of repository source, not the only copy of the implementation.

## 14. Compatibility and retirement map

The migration should not treat every old repository as an eternal runtime dependency, but retirement requires evidence.

### Normalize into canonical BT2 immediately

- workforce topology and logical agent/unit registry;
- provider-neutral workspaces/checkpoints/handoffs/decisions;
- operation/effect journal;
- native dispatch queue;
- BugOps logical incident/evidence/verification semantics;
- training package/qualification registry;
- generalized governed-material model;
- source snapshot and migration provenance.

### Preserve temporary compatibility/provenance

- WIP file formats and operation/checkpoint schemas until canonical recovery replay demonstrates equivalent recovery behavior;
- BugOps SEV/report/closure semantics and issue/PR references until canonical incident lifecycle round-trips without information loss;
- Lantern read facade and admission semantics until both read-cut and admission/concurrency qualification pass;
- source-specific training manifest paths and qualification evidence until every active agent's package has an exact canonical binding;
- R9A0/governance/Slack-era records as historical material only.

### Retirement evidence required per old boundary

An old repo/schema/API may be declared superseded only when:

1. exact source cut is preserved and content-addressed;
2. required active semantics are mapped to canonical subjects;
3. historical records are preserved with count/digest or equivalent membership proof;
4. compatibility/replay tests pass;
5. no active workflow still writes only to the old surface;
6. rollback/recovery from the new system has been demonstrated;
7. Patrick/authorized governance explicitly accepts retirement/cutover.

Repository deletion is not implied by logical retirement.

## 15. Falsifiable migration acceptance suite

The following cases should be executable and retained as evidence before canonical cutover.

### Identity/topology

1. Cross-agent operational-checkpoint predecessor is rejected.
2. Cross-workspace workspace-checkpoint predecessor is rejected.
3. Two independent roots in one linear workspace are rejected.
4. Stale workspace generation append is rejected atomically; fresh worker can continue.
5. Invalid ORCHESTRATES edge to Masa, Mune, or Hephaestus is rejected.
6. Removing the orchestrator from an active ORCHESTRATED_TEAM without a valid transition is rejected.
7. Runtime session A and runtime session B may both represent logical agent Two without becoming the same execution identity.

### Training/continuity

8. Qualification `(agent=Three, package=Two-package)` is rejected.
9. Operational checkpoint carrying a qualification/package from another agent is rejected.
10. Missing historical package remains DISCOVERED/UNKNOWN rather than automatically PASS.
11. Canonical package import preserves exact source commit/tree/manifest digest and qualification evidence.

### Queue/operations

12. Enqueue succeeds but response is discarded; replay with same dispatch identity+digest returns one queue item, not two.
13. Same dispatch identity with different digest is rejected as reuse conflict.
14. Two concurrent claimers cannot hold the same claim generation/token.
15. Expired claimant cannot release/ACK after lease expiry.
16. Reclaimed work rejects the old claimant's token.
17. Successful ACK with lost response can be replayed to the same ACK receipt without error or duplicate effect.
18. PREPARED and ATTEMPTED operation events remain queryable after VERIFIED/FAILED/AMBIGUOUS/RECONCILED terminal projection.
19. AMBIGUOUS recovery forces inspect-before-retry and cannot silently create a second external effect.
20. Claim/reclaim/dead history remains reconstructible after crash/restart.

### BugOps

21. Same intake identity+same digest under response loss converges to one bug.
22. Same intake identity+different digest is rejected as conflict.
23. NEW -> CLOSED without required closure evidence is rejected for substantive incidents.
24. Closure after required correction/regression/review/readback evidence succeeds and produces a closure receipt.
25. Reopen creates an auditable lifecycle event and does not erase prior closure evidence.
26. Historical `SEV-*` values round-trip through any normalized severity mapping without semantic loss.

### Lantern/material

27. Fresh Supabase B0/payload/B1 exact-member cut equals WoWSQL material cut on profile/policy/member/digests.
28. No historical producer permit becomes current solely through import/restore.
29. Duplicate semantic identity is rejected consistently.
30. Duplicate JSON keys are rejected before canonicalization.
31. Concurrent distinct material admissions satisfy the explicitly chosen canonical concurrency policy without duplicate or untraceable partial state.
32. Corrupt/inconsistent profile lineage causes no runtime-visible current cut and no admission.

### Historical preservation/rebuild/cutover

33. Every frozen source snapshot is content-bound to exact ref/commit/tree where applicable.
34. Legacy archive count and per-object/row digests match the selected source cut before retirement approval.
35. Historical Slack/R9A0/coequal-topology records are retrievable as history but absent from active policy/topology projections.
36. A blank supported PostgreSQL target rebuilt solely from canonical GitHub database source produces the expected catalog, functions, constraints, and test behavior.
37. Canonical recovery can resume a checkpointed workspace after simulated runtime loss without reading an old chat transcript.
38. An interrupted external write with ambiguous response is reconciled from durable events and target readback without blind repeat.
39. No old repository/schema is retired while an active-only dependency or unmatched historical object remains.
40. Cutover receipt identifies exact repository source, database schema/migration digest, verified acceptance evidence, and explicit authority.

## 16. Recommended correction order

1. **Source-control the canonical database definition** so subsequent database corrections have a durable reviewed home.
2. **Fix identity cross-binding** for runtime sessions, training, and checkpoint predecessors.
3. **Restore append-only operation/dispatch event history** and make operations/work_queue current-state tables projections over controlled transitions.
4. **Make enqueue/ACK/release response-loss and lease semantics mechanical.**
5. **Strengthen topology admissibility.**
6. **Add BugOps closure qualification and explicit severity mapping.**
7. **Decide and qualify Lantern admission-concurrency policy.**
8. **Complete legacy/history and distributed training import.**
9. **Run the falsifiable acceptance suite on a rebuild from canonical GitHub source.**
10. Only then evaluate cutover/retirement separately from source merge.

## 17. Current disposition by assigned seam

| Seam | Disposition |
|---|---|
| Canonical entity/identity | `CHANGES_REQUIRED` — runtime identity + cross-binding gaps |
| Topology current rows | `PASS_CURRENT_DATA` |
| Topology invariant enforcement | `CHANGES_REQUIRED` |
| Training/continuity | `CHANGES_REQUIRED` — empty import is honest; relational binding is weak |
| Queue/operation semantics | `CHANGES_REQUIRED` — response-loss + append-only journal blockers |
| BugOps convergence | `CHANGES_REQUIRED` — closure/severity/idempotency fidelity |
| Governed material current cut | `PASS_EXACT_MEMBER_READ_EQUIVALENCE` |
| Governed material admission behavior | `QUALIFICATION_REQUIRED` — concurrency delta |
| Historical/current separation direction | `PASS_DIRECTION / IMPORT_INCOMPLETE` |
| Compatibility/retirement | `NOT_READY` |
| Database constraints/concurrency | `CHANGES_REQUIRED` |
| Migration acceptance criteria | `DEFINED_BY_THIS_REVIEW / NOT_YET_EXECUTED` |
| Canonical cutover | `NOT_READY / NOT_AUTHORIZED` |

## 18. Remaining unknowns

- Full distributed training-package inventory for every active agent has not yet been recovered here.
- Full legacy Supabase custom-schema row/object archive is still incomplete.
- Exact WoWSQL access-control model for the final canonical service boundary has not yet been qualified; WoWSQL `auth=false` means Supabase RLS cannot simply be copied as the answer.
- Whether canonical material admission intentionally wants stricter serialization than source Lantern remains a design decision.
- Which old repositories remain temporarily writable during migration and the eventual dual-write/freeze/cutover sequence are not yet established.

These unknowns should remain explicit rather than being filled by inference.
