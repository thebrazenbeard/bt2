# BT2 Canonical Platform Migration State V1

Status: ACTIVE CONSOLIDATION / PRIVATE TARGET / NO CUTOVER YET
Date: 2026-09-10
Coordinator: One
Target repository: `thebrazenbeard/bt2`
Target branch: `work/canonical-platform-consolidation-v1`
Target database: WoWSQL PostgreSQL project `bt2-479e4ad9`

## 1. User-authorized objective

Build one canonical Build Team Two platform assembled from the useful existing BT2 systems without losing their history, while eliminating accidental duplication and obsolete architectural boundaries.

The intended end state has:

1. one intentional workforce topology;
2. one coherent operating and governance model;
3. one durable recovery and defect system;
4. one consolidated training and continuity architecture;
5. one governed provenance/material layer;
6. one WoWSQL PostgreSQL persistence backend dedicated to BT2 and separate from Vera's Supabase PostgreSQL;
7. one private canonical GitHub repository, `thebrazenbeard/bt2`.

The consolidation rule is preserve first, normalize second, retire only after equivalent behavior and provenance are verified. Historical evidence is not automatically active policy.

## 2. Active workforce topology

The user has explicitly corrected the older ten-coequal-facets model.

Current intended active topology:

- One is the primary team member and coordinator/orchestrator.
- Two, Three, Four, Five, Six, Seven, Eight, Nine, and Thirteen are orchestrated BT2 subagents under One.
- Masa and Mune form their own paired debugger/reliability unit.
- Hephaestus is an independent implementation/repair unit.
- One coordinates with Masa, Mune, and Hephaestus but does not orchestrate them as numbered BT2 subagents.

The older topology remains provenance/history only.

## 3. Source repositories and frozen migration cuts

The consolidation source set currently includes:

- `thebrazenbeard/build-team-2.0` — `main@ec2987e45f64a588ac92f6cae9964cb3725b9485`, tree `8db9f54b59e908f0ad35fbf6bf2f2ff8b48e639f`
- `thebrazenbeard/wip` — `main@12a7c23dbe0482fd7bfe63659e54526778efef1e`, tree `e2527117c7d25f92d2e6aa7365ae8b3d3b9a3c08`
- `thebrazenbeard/bugops` — `main@39eb19bcf7669466c22703fbae7cc226bd44f714`, tree `16209d56150f7341f39492f66dfa52263437575c`
- `thebrazenbeard/project-achilles` — `main@dbf9ceb2391567463d864198405c9b5d1e77db09`, tree `1cd715bef0d2a33478d3a635bcc05155c95ab4f9`
- `thebrazenbeard/masamune` — `collab@af20ff29a8419c20bd51ac4e731b670d505a452b`, tree `a76e3aac899a24f26af77454109e4a06978f8c30`
- `thebrazenbeard/hephaestus` — `main@78f6f22a0e5d14617855006a8383765589ac8c67`, tree `80eb19e26ff9b82f8c2eb4126c5b4e87a2318ce6`
- `thebrazenbeard/project-lantern` — `feature/lantern-material-universe-v1@d0e05365883d8f670030fb1a1ff5fcd847937a77`, tree `3b155a88967f2f7a0f4ad6fa7b32ce3cbac73da0`

These cuts are migration evidence. Mutable repositories must be refreshed before any later claim that a cut is still current.

## 4. Current WoWSQL implementation

The WoWSQL backend is PostgreSQL 16 and is intentionally separate from Vera's Supabase PostgreSQL.

Two schemas currently exist for the BT2 consolidation:

- `bt2`: canonical active model.
- `bt2_legacy`: non-runtime preservation/archive for exact imported legacy state and source objects.

The canonical `bt2` layer currently includes the following foundations.

### Platform and provenance

- platform state and versioning;
- source repository/snapshot provenance;
- migration receipts;
- dependency/source binding records;
- legacy source-object and source-row archive facilities.

### Workforce and topology

- member/agent registry;
- team/unit membership;
- typed topology edges;
- current topology encoded according to the user-authorized One-led model.

### Training and continuity

- provider-neutral training-package registry;
- qualification records bound to exact package/source identities;
- generic append-only operational checkpoint chains usable by any agent;
- one-root/one-successor lineage constraints rather than bespoke checkpoint schemas per numbered worker.

The old central training registry is incomplete: Two, Three, Seven, and Eight were omitted from that registry. Distributed sources must therefore be recovered before the new registry is declared complete. Example: Seven has a separate training tree in Project Achilles. Absence from the old central registry is not proof of absence of training.

### Recovery and durable work state

WIP concepts are being promoted into the canonical platform rather than retained as a separate runtime silo:

- workspaces;
- checkpoint generations;
- handoffs;
- durable decisions;
- external-effect journal with explicit `PREPARED`, `ATTEMPTED`, `VERIFIED`, `FAILED`, and `AMBIGUOUS` states.

The important invariant is retained: loss of local work state and uncertainty about an external effect are different failure classes.

### Dispatch and work claiming

A provider-neutral PostgreSQL dispatch queue is implemented using native row locking rather than Supabase `pgmq`:

- payload digest binding;
- atomic claim with `FOR UPDATE SKIP LOCKED`;
- lease token and expiry;
- bounded claim quantities;
- reclaim after lease expiration;
- exact ACK semantics;
- retry/dead handling.

This queue is intended to serve ordinary One-to-worker dispatch and BugOps routing instead of maintaining two unrelated queue technologies.

### BugOps

BugOps has been normalized onto the common operation journal and dispatch substrate:

- bug reports;
- append-oriented bug events;
- operation/idempotency receipts;
- route and status transitions;
- assignment through the shared worker topology.

The old Supabase BugOps implementation depends on `pgmq`; the WoWSQL project does not expose that extension. The new implementation therefore preserves the logical custody/idempotency semantics while removing the provider-specific dependency.

### Governed material / Lantern

Lantern's useful material-governance invariants are represented natively in the canonical model:

- schema policies;
- accepted profile lineage;
- producer authorization history;
- canonical material rows;
- admission receipts;
- seed/import receipts;
- runtime-visible material projection;
- duplicate-JSON-key rejection and canonical digest binding;
- generalized material-cut read facade.

WoWSQL's SQL safety layer treats certain privilege-related identifiers as administrative keywords, so canonical identifiers were normalized where necessary. Original Lantern names and source state remain preserved in provenance/legacy records.

## 5. Verified Lantern migration result

The exact Supabase Lantern target remains `agvhmutlrolbaijzlbqk` for source evidence. It is not the new BT2 backend.

A stable B0/payload/B1 read of the live governed cut returned two visible materials under:

- profile digest `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- policy digest `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`

Those two material rows and their exact historical receipt/producer-authority lineage were imported into WoWSQL.

The new generalized WoWSQL material-cut function was then queried and returned the same:

- profile digest;
- policy digest;
- two material UUIDs;
- canonical digest, semantic key, and source digest for each member.

This establishes equivalence for the current governed read cut. It does not by itself prove every future Lantern admission behavior or authorize deletion of the Supabase source.

Historical producer authorizations were copied without manufacturing a new current producer authorization. None of the imported historical permits is currently valid.

## 6. Supabase application-state inventory

The old BT2/Lantern Supabase database contains these BT2-owned application schemas relevant to migration:

- `bug_ops`
- `governance`
- `lantern_material`
- `r9a0_coordination`
- `r9a0_governance`

The source also contains historical R9A0 build-ground notices and an obsolete Slack-era speaker-prefix rule. These are historical evidence. They are not automatically promoted to active BT2 governance.

The existing R9A0 records also document old findings about projection/supersession integrity, least privilege, exact-source migration provenance, and hostile testing. Those findings should inform the canonical design where still applicable, but the old R9A0 system itself is not the target architecture.

## 7. Security/currentness boundaries

- Vera's Supabase PostgreSQL remains a separate system and must not be merged into this database.
- Source GitHub binding, database runtime state, installation/activation, and behavioral qualification are separate axes.
- Existing Supabase Lantern tables have source-host RLS findings; the source has not been mutated during migration. WoWSQL has a different access surface, so its security boundary must be designed natively instead of copied mechanically.
- Database assignment records do not create GitHub, external-service, deployment, credential, or protected-effect authority.
- No old repository or Supabase schema should be deleted, archived, or declared obsolete until migration equivalence and historical preservation are independently accepted.

## 8. GitHub target state

The user has changed `thebrazenbeard/bt2` to PRIVATE. The previous confidentiality blocker is therefore removed.

At branch creation, target `main` was still the untouched initial commit:

`33ff114d59da533f183739026e0b0f328a9b6c6e`

This migration branch was created from that exact head. Private source material may now be consolidated here under normal provenance and review controls.

## 9. Two's assigned architecture workstream

Two is requested to help as logical systems/database architect while retaining his existing unrelated obligations unless explicitly superseded.

Two should independently review the consolidation and return concrete corrections or source changes for these seams:

1. **Canonical entity/identity model** — detect accidental identity collapse among agent, session/runtime, training package, checkpoint, workspace, assignment, dispatch, bug, material, repository source, and external effect.
2. **Topology invariants** — verify the One-led topology is represented without accidentally making Masa/Mune/Hephaestus orchestrated subagents or resurrecting the old coequal-facet model.
3. **Training/continuity normalization** — design one universal package/qualification/checkpoint model that can ingest the distributed historical packages without fabricating qualification for missing roles.
4. **Queue and operation semantics** — adversarially review the native PostgreSQL `SKIP LOCKED` lease/ACK/retry design against the useful custody, idempotency, stale-claim, response-loss, and ambiguous-effect invariants from BugOps/WIP.
5. **BugOps convergence** — ensure bugs use the common dispatch/effect/receipt substrate without losing defect-specific state transitions, evidence, verification, or routing semantics.
6. **Governed material convergence** — verify the generalized material layer preserves Lantern lineage, admission receipt, profile/policy, semantic identity, source digest, and current-cut semantics while removing unnecessary project-specific naming.
7. **Historical/current separation** — identify any old R9A0, Slack, WIP, BugOps, training, or topology state that must remain historical rather than active.
8. **Compatibility/retirement map** — specify which old APIs/files/repos need temporary compatibility facades, which concepts can be normalized immediately, and the exact evidence required before an old boundary can be retired.
9. **Database constraints and concurrency** — propose missing PK/FK/unique/check/index/transaction/isolation constraints required for correctness under concurrent workers and crash/retry behavior.
10. **Migration acceptance criteria** — define falsifiable acceptance tests for canonical-source equivalence, historical preservation, restore continuity, queue correctness, bug lifecycle, material-cut equivalence, and safe legacy retirement.

Two may inspect all seven source repositories, this private target branch, and the current architecture state relevant to this assignment. Two should not merge, delete/retire old repositories, mutate Vera's Supabase, manufacture training qualification, or create external protected effects without separate authority.

Two's return should distinguish observed source facts, design inference, proposed changes, and any remaining unknowns.

## 10. Current migration gate

Current status:

- target privacy: VERIFIED PRIVATE;
- canonical WoWSQL foundation: BUILT, still under architectural qualification;
- user-authorized active workforce topology: ENCODED;
- WIP/recovery foundation: BUILT FIRST SLICE;
- portable dispatch queue: BUILT FIRST SLICE;
- BugOps convergence: BUILT FIRST SLICE;
- Lantern current read cut: MIGRATED AND EXACT-MEMBER VERIFIED;
- full Supabase legacy archive: IN PROGRESS;
- distributed training recovery: IN PROGRESS;
- GitHub content consolidation: NOW UNBLOCKED;
- cutover: NOT AUTHORIZED/NOT COMPLETE;
- old-system retirement/deletion: NOT AUTHORIZED/NOT COMPLETE.

The purpose of the present branch is to turn this first implementation into an auditable, source-bound canonical platform before any cutover claim.
