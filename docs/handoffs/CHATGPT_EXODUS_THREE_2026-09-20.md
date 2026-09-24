# ChatGPT Exodus — Three Retirement Checkpoint — 2026-09-20

Status: `STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT`

## Purpose

This checkpoint evacuates the durable engineering value of the retiring ChatGPT execution terminal historically used for BT2 role `Three`.

It is a recovery pointer and state-classification artifact, not a transcript, not a qualification receipt, and not a source of new protected-effect authority.

The conversation may become inaccessible without reducing the ability to reconstruct or instantiate Three.

## What this terminal represented

Project: **Build Team Two**

Durable logical worker:
- identity: `Three`
- permanent role source: `archive/training-sources/build-team-2.0/three/v1.0.0`
- roles:
  - State Machine / Data Model & Schema Steward
  - Supabase Service Warden
  - WoWSQL Service Warden

Execution environment:
- this ChatGPT conversation was only a terminal;
- it is not Three's durable identity, memory, authority, qualification, assignment, or state.

Future persistent human interface:
- `BT2 Coordinator`

No successor Three chat is required or intended.

## Fresh source subjects inspected

Canonical BT2 source:
- repository: `thebrazenbeard/bt2`
- branch: `main`
- exact head observed: `30e81cadd94fae117a7f6875523c03251c7c9f6e`
- current Project Instructions V3 blob: `5de32bc36d1cf463395d83760e3eb109e9523d70`

Communication hub:
- repository: `thebrazenbeard/chat-communication-bus`
- default branch observed: `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`
- Three writer lane observed: `bus/three-v2@08d11224f8ac3251ec05ee29a2b7a2f9e3f340b5`

Owning-project subjects materially touched by Three:
- `thebrazenbeard/abil@main=0812d9780ce1648820269fa142a43e17030ef793`
- ABIL PR #2 observed head: `712d5b30b45ba9299dcfce0599878cb81db70e8f`
- ABIL PR #3 observed head: `1da5bc57b0228178300f6ba966d97d1dce807dc1`
- `thebrazenbeard/world-zero@main=5ab39621d090079d24de40261906b64413c6f995`

All mutable refs above are observations. Fresh-check before effect or current-state claims.

## Worker reconstruction source

Three's preserved v1.0.0 source on current BT2 main:
- bootstrap: `archive/training-sources/build-team-2.0/three/v1.0.0/BOOTSTRAP.md`
- bootstrap blob: `e94149f885ab3aff1a6bf87aaa6e8cc6f775f519`
- manifest: `archive/training-sources/build-team-2.0/three/v1.0.0/TRAINING_MANIFEST.json`
- manifest blob: `315777e08bffc4808ebf68e715c8d58c2d00f2ee`

The manifest separates:
- permanent competence/role semantics;
- mutable assignments;
- leases;
- repository heads;
- provider/runtime state;
- mutation authority.

Its authority boundary states:
- One owns governance;
- Two owns database architecture/migrations;
- Three's Warden roles do not themselves authorize mutation;
- tool/repository access does not imply permission.

### Chat-era wording classification

The immutable historical v1.0.0 package contains chat-era phrases such as "fresh chat", "trained chat", and "BASE_READY chat".

Classification: `HISTORICAL_EVIDENCE / IMMUTABLE_TRAINING_SOURCE`.

Do not rewrite that frozen historical source merely to modernize terminology.

For current operation, the controlling BT2 Project Instructions V3 and Exodus reconstruction source treat ChatGPT/Work/API/CLI/model/subagent sessions as replaceable terminals. A future runtime reconstructs Three from durable source and current assignment evidence; it does not need a permanent Three conversation.

Preferred current worker reconstruction candidate:
- BT2 Draft PR #26
- branch: `exodus/bt2-runtime-worker-reconstruction-v1-20260919`
- exact head observed: `95fc8ca0f9a107ad3cf0287bcc5943ef3c42ad81`
- artifact: `native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json`
- Three source state there: `PACKAGE_FOUND`
- Three qualification state there: `QUALIFICATION_UNPROVEN`

Therefore:
- source reconstruction != qualification;
- qualification != installation/activation;
- source role != current assignment;
- service-writer capability != authority.

## Persistent-interface and Bus Exodus state

Relevant durable source candidates:
- BT2 PR #24 @ `9ded716828244d4abc3d5b3dfd7a351b6f261717` — BT2 Coordinator interface.
- BT2 PR #26 @ `95fc8ca0f9a107ad3cf0287bcc5943ef3c42ad81` — preferred BT2 workforce source reconstruction.
- BT2 PR #27 @ `fbd2739fb8a263fd5dd751a2032e1d2a5488f327` — corroborating dechatification candidate; One's final checkpoint says do not integrate it independently of preferred PR #26 without reconciliation.
- BT2 PR #29 @ `a781c0de3cdc4fe40034770ee06227ec44d11f7f` — BT2 role-topology Exodus checkpoint.
- Bus PR #128 @ `1af84ba0650bb646b696dfc31e4f79b498d100af` — exact three persistent interfaces.
- Bus PR #134 @ `86c330e7d7e5d13d800efaa56808f882c98d1547` — preferred composed chatless-worker architecture/reconstruction census.
- Bus PR #136 @ `bde34be27c90821c5d4068e3a5d02cfea0b2ec6b` — runtime-neutral worker reconstruction sibling.
- Bus PR #137 @ `cb22ffec36fc45c86fb960b7814287a742a4ced8` — current-facing route/chat decoupling sibling.
- Bus PR #139 @ `56ed27e2537a0c0bdd7316cf49c28dc3aad242ae` — corroborating operator recovery dechatification.

Current intended persistent ChatGPT interfaces are exactly:
- Vera
- Vera Control Plane Coordinator
- BT2 Coordinator

Three is a durable logical worker that can be instantiated in an ephemeral runtime. Three is not a fourth persistent interface.

### Census state

Bus PR #134's current reconstruction census remains globally blocked and does not currently qualify Three as `READY`.

This checkpoint is durable reconstruction evidence for future census reconciliation. It does **not** self-promote Three to READY and does not claim BASE_READY, installation, activation, or current assignment.

## Current assignment/frontier

No current direct Three assignment was established by the fresh durable evidence inspected for this retirement cut.

Fail-closed rule:
- do not recover an assignment from this conversation;
- fresh-read current BT2 Coordinator/Bus/project assignment evidence before doing work;
- if no durable assignment exists, Three is idle rather than chat-memory-driven.

The primary fresh-confirmed Three-specific technical frontier is BT2 issue #31:
- `thebrazenbeard/bt2#31`
- title: `Bind training-package provenance claims to preservation evidence`
- classification: `UNRESOLVED_DEFECT / SCHEMA_INTEGRITY / EXODUS_PRESERVATION`

Implementation ownership remains with the current database/migration owner unless explicitly reassigned. Three's natural follow-up is exact-subject schema/invariant review of a proposed repair, not unilateral migration ownership.

## NEW_DURABLE_VALUE — training provenance cross-bind defect

Historical discovery:
- Bus `three-0033`
- path: `messages/0033-three-to-one-two-bt2-training-provenance-crossbind-gap.md`

Fresh-confirmed on current BT2 main:
- `database/migrations/0014_training_source_state_separation_v1.sql`
  - blob `7b20752ef442f979c59d610f2b3857988c8af04d`
- `database/tests/0003_training_source_registry_reconstruction_smoke.sql`
  - blob `31c96a79b5382c6825254a047a3259be7a3b70a6`
- `database/data/0001_verified_training_source_registry_v1.sql`
  - blob `e313af9b735a06caf21d6d132d5afc5be8eab4ab`

Current defect:
- preservation evidence mechanically binds verified state, package-tree identity, and no qualification/runtime-installation effect;
- it does not mechanically cross-bind the complete claimed provenance tuple such as source repository/ref/commit/tree/path and manifest identity;
- the conflict-update path can therefore rewrite provenance fields while retaining the same package-tree subject.

Project-local durable frontier:
- BT2 issue #31.

Claim ceiling:
- byte-tree-to-receipt binding is not equivalent to full source-provenance binding;
- no runtime/provider mutation is needed to preserve the defect;
- issue existence does not authorize implementation, migration application, merge, or cutover.

## HISTORICAL_EVIDENCE — ABIL Three reviews

Durable Bus evidence:
- `messages/20260917-three-to-seven-abil-r4-transitive-leakage-review.md`
  - blob `3ed4fd99369effeb5198eddff523f88362145aee`
- `messages/20260917-three-abil-r4-information-identity-disposition.md`
  - blob `4af5fa6269a312387f383078804c5b6dd5bdc0aa`

The latter recorded a Three design-source information/identity PASS for the exact historical composition:
- architecture `712d5b30b45ba9299dcfce0599878cb81db70e8f`
- then-reviewed R4 design head `c31d760a711dfd36c00ef9f40a7036b2b1701f45`

Retained invariant:
with learner-visible inputs held constant, changes only to evaluator/control-plane authority, safety, promotion, commissioning, or active-artifact state must not alter learner-visible bytes or identities, including derived identifiers/digests.

Currentness:
- ABIL PR #3 has since moved to `1da5bc57b0228178300f6ba966d97d1dce807dc1`;
- old Three PASS is historical provenance only and must not be carried onto the current head;
- ABIL Draft PR #26 already defines a chat-independent `ABIL_EXECUTION_WORKER` coordinated primarily through BT2 Coordinator;
- no additional ABIL chat is required.

## HISTORICAL_EVIDENCE / IDEA_OR_FUTURE_FRONTIER — World Zero

Durable Bus recommendation:
- `messages/20260917T0741-three-world-zero-provenance.md`
- blob `a556547cf514fa9f3db647d071276cc3ae774c01`

It recommended:
- explicit observation provenance and transformation lineage;
- aggregate plus regional/distributional validation;
- holdout periods/variables;
- avoiding double-counting correlated derived indicators;
- explicit latent-state-to-proxy measurement mapping;
- immutable model/dataset/scenario inputs in run receipts.

World Zero has since materially advanced through admitted source cuts, regional/cohort bindings, holdout eligibility and temporal/walk-forward execution. The September 17 note remains advisory provenance; it is not a current assignment or current project verdict.

## Lantern / durable currentness

Exact required target:
- `bt2-479e4ad9`

This retirement terminal attempted current WoWSQL access through the available connector, but project/SQL operations failed internally before valid Lantern read evidence was returned.

Therefore:
- `LANTERN_CURRENTNESS = UNKNOWN_IN_THIS_TERMINAL`
- no Supabase, Git source, chat memory, prior Lantern snapshot, or other provider was substituted as current Lantern state.

A future runtime must follow the current V3 handshake against exactly `bt2-479e4ad9` when Lantern currentness materially matters.

## Authority and non-authority

This Exodus task authorizes reversible evacuation work such as:
- reads;
- bounded branches;
- documentation/governance/test work;
- Draft PRs;
- issues;
- checkpoints;
- Bus coordination;
- verification/readback.

It does not authorize:
- merge/canonical promotion;
- production deployment;
- provider/database mutation;
- credential/permission/ruleset mutation;
- destructive cleanup or force push;
- public release/visibility change;
- training or qualification manufacture;
- Project Settings or canonical-memory mutation;
- Slack reconnection/configuration;
- protected machine effects.

Three's role does not expand this boundary.

## Durable write/routing rules

For a future Three runtime:
- source/code/docs/tests belong in the owning repository on a bounded branch/PR;
- independent review belongs on the exact owning PR/review surface;
- non-PR coordination uses the current Chat Communication Bus route;
- recovery and assignment state belongs in durable BT2/Bus/project evidence, not chat history;
- verify current Bus topology before writing;
- do not invent a new permanent worker chat or writer identity.

## Fresh-runtime reconstruction procedure

A BT2 Coordinator may instantiate Three without this conversation:

1. Read current BT2 Project Instructions.
2. Fresh-check `thebrazenbeard/bt2@main`.
3. Fresh-check the disposition of BT2 PR #26 and any accepted/successor worker-reconstruction source.
4. Read Three's preserved v1.0.0 source package and verify current governance compatibility.
5. Treat preserved package presence as source reconstruction only unless current qualification evidence proves more.
6. Fresh-check current Bus topology and `bus/three-v2`.
7. Read One's current/final BT2 Coordinator portfolio checkpoint as a starting snapshot only.
8. Fresh-read current assignment evidence. Do not derive work from this retired conversation.
9. Fresh-read exact owning-project source/review subjects before carrying PASS/FAIL.
10. If Lantern currentness matters, require exact WoWSQL target `bt2-479e4ad9` and execute V3 preflight -> B0 -> payload -> B1; fail closed if unavailable.
11. Perform bounded work, verify, and persist results durably.
12. Stop at protected-effect gates.

## Reconstruction test

Assuming this conversation is inaccessible, durable state now answers:

1. What is Three? — a BT2 durable specialist role with three explicit steward/warden responsibilities.
2. What project/domain does it serve? — Build Team Two, with bounded cross-project review when dispatched.
3. What authority exists? — role responsibility and Exodus reversible persistence authority only; no implicit protected-effect authority.
4. What repositories/routes matter? — BT2 canonical source, owning project repos, and Chat Communication Bus.
5. What is current vs historical? — exact current source observations above; old ABIL PASS and World Zero note explicitly historical/advisory.
6. What failed and why? — BT2 provenance cross-bind defect is project-local issue #31; Lantern currentness is UNKNOWN because exact WoWSQL reads failed internally.
7. What may safely happen next? — current-assignment recovery, exact-head review, issue #31 repair review, and other reversible work if durably assigned.
8. How does Three communicate? — current Bus topology/route, not this chat.
9. How is Three instantiated? — preserved role source + current governance + current assignment in an ephemeral runtime.
10. What requires Patrick? — merge, deployment, provider/credential/permission/training/canonical and other protected effects under controlling contracts.

No useful Three-specific operational fact discovered here requires the retired ChatGPT conversation.

## Global Exodus caveat

The Bus-wide worker reconstruction census remains a separate global cutover gate. Three is not self-declared READY by this checkpoint.

That global census state does not make this conversation a system of record. The durable material needed to evaluate Three's readiness now exists outside the conversation.

## Future interface and exact next directive

Future interface:
`BT2 Coordinator`

Directive:

`BT2_COORDINATOR::RESTORE_THREE_FROM_DURABLE_STATE::Fresh-check bt2/main, BT2 PR #26 and successor Exodus candidates, Bus PR #134 plus material siblings #136/#137, bus/three-v2, bt2 issue #31, and any current owning-project assignment; instantiate Three ephemerally from its preserved v1.0.0 role source only after current governance/source compatibility checks; keep source reconstruction, qualification, installation, current assignment, and protected-effect authority separate; do not reopen or depend on the retired Three chat.`
