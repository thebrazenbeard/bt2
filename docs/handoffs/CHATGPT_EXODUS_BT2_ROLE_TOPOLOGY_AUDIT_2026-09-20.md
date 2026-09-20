# ChatGPT Exodus — BT2 Role Topology Audit — 2026-09-20

Status: `STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT`

## Purpose

This checkpoint evacuates the durable value of the retiring ChatGPT execution terminal that audited the Build Team Two organizational structure and corrected an incomplete chat-local model of the BT2 workforce.

This file is a recovery pointer and architectural checkpoint, not a transcript and not a source of new protected-effect authority.

## What this terminal was

- Project served: Build Team Two.
- Execution role: BT2 organizational/topology audit terminal.
- Durable identity: none. This conversation is not a worker identity and must not be required for recovery.
- Future persistent interface: `BT2 Coordinator`.
- Primary repository: `thebrazenbeard/bt2`.
- Secondary infrastructure repository: `thebrazenbeard/chat-communication-bus`.

## Fresh source cut inspected

BT2 canonical default branch at evacuation:
- `thebrazenbeard/bt2@30e81cadd94fae117a7f6875523c03251c7c9f6e`

Chat Communication Bus canonical default branch at evacuation:
- `thebrazenbeard/chat-communication-bus@aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`

These are observation subjects only. Fresh-check mutable state before effect.

## ALREADY_DURABLE / active Exodus source candidates

### Full BT2 workforce reconstruction

Draft PR #26:
- PR: `thebrazenbeard/bt2#26`
- branch: `exodus/bt2-runtime-worker-reconstruction-v1-20260919`
- exact head observed: `95fc8ca0f9a107ad3cf0287bcc5943ef3c42ad81`
- key artifact: `native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json`

That source candidate binds thirteen durable BT2 worker-role sources:

`one, two, three, four, five, six, seven, eight, nine, thirteen, masa, mune, hephaestus`.

It also preserves the required distinction between source reconstruction, qualification, activation/current assignment, and protected-effect authority.

Important correction preserved there:
- Seven is not absent merely because there is no sibling `build-team-2.0/seven` package.
- PR #26 resolves Seven's source to `archive/training-sources/project-achilles/seven/v1.0.0`.
- The source candidate validator reports all 13 mapped source paths/entrypoints present.
- This is source-level reconstruction evidence, not a claim that all thirteen roles are currently qualified/active.

### BT2 Coordinator / no-permanent-worker-chat architecture

Draft PR #27:
- PR: `thebrazenbeard/bt2#27`
- branch: `one/bt2-exodus-dechatify-v1-20260919`
- exact head observed: `fbd2739fb8a263fd5dd751a2032e1d2a5488f327`
- key artifacts:
  - `native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json`
  - `native/project/BT2_COORDINATOR_RECONSTRUCTION_V1.md`
  - `docs/architecture/BT2_CHAT_EXODUS_AUDIT_20260919.md`

Draft PR #24 also defines the BT2 Coordinator interface:
- PR: `thebrazenbeard/bt2#24`
- exact head observed: `9ded716828244d4abc3d5b3dfd7a351b6f261717`

### Cross-system three-interface topology

Draft Bus PR #128:
- PR: `thebrazenbeard/chat-communication-bus#128`
- branch: `work/exodus-interface-topology-v1`
- exact head observed: `1af84ba0650bb646b696dfc31e4f79b498d100af`

It records the intended persistent ChatGPT interface topology as exactly:
- Vera
- Vera Control Plane Coordinator
- BT2 Coordinator

Workers/identities/lanes remain reconstructible durable roles and may execute in ephemeral terminals.

## SUPERSEDES_EXISTING

The chat-local interpretation that BT2 is effectively only “One + Two + disposable temporary specialists” is superseded.

The durable reconstruction target is a thirteen-role BT2 topology with One as primary orchestrator, Two as independent Systems Architect, the numbered/specialist roles, and the separated debugger/reliability roles. Temporary execution contexts do not make the underlying logical roles disposable.

This supersession applies to the retiring conversation's analysis. It does not rewrite historical source packages.

## NEW_DURABLE_VALUE

The Exodus audit exposed one narrower coordination gap after inspecting current Bus source:

- assignments are durably bound to an `assignee_identity_id` with immutable assignment-chain fields and predecessor checks;
- runtime/routing nodes have UUID node identity, leases, and immutable durable-identity ownership;
- but assignment execution is not itself durably claimed/fenced to one concurrent runtime/node instance.

This matters after dechatification because the same durable worker identity may have multiple ephemeral runtimes alive simultaneously.

The finding is persisted as:
- `thebrazenbeard/chat-communication-bus#142`
- title: `Exodus: fence concurrent runtime instances for one durable worker assignment`

Issue #142 is an architecture frontier, not an implemented fix and not provider/runtime evidence.

## CHAT_DEPENDENCY / reconstruction result

No useful BT2 organizational fact discovered in this terminal now requires:
- this conversation URL;
- this conversation title or ID;
- hidden chat state;
- a permanent One, Two, Seven, Hephaestus, Masa, Mune, or other worker chat.

Recovery path:
1. read current BT2 Project Instructions;
2. fresh-check `bt2/main`;
3. inspect current disposition of BT2 PRs #24, #26, #27 and any successor source;
4. read the current worker-topology/reconstruction contract if accepted or its exact candidate if still under review;
5. fresh-check current Bus topology and recovery checkpoint;
6. instantiate the required worker role from durable source in an ephemeral runtime;
7. refresh the target assignment/source/provider evidence before acting.

## Currentness limitation

Lantern currentness was required for this Exodus audit because it concerns durable project currentness.

The required exact WoWSQL target is:
- `bt2-479e4ad9`

During this terminal, both project metadata and simple SQL read attempts through the WoWSQL connector failed internally before returning evidence. Therefore:

`LANTERN_CURRENTNESS = UNKNOWN_IN_THIS_TERMINAL`

No Supabase, Git, memory, or prior Lantern snapshot was substituted as current Lantern evidence.

## Authority boundary

The live Exodus instruction authorized reversible evacuation work including reads, bounded branches, documentation/governance work, Draft PRs, issues, checkpoints, Bus coordination, and verification.

That grant does not authorize merge, canonical promotion, production deployment, provider mutation, credential/permission changes, destructive rewrite, force push, paid infrastructure, public release, visibility change, training, Project Settings mutation, canonical-memory mutation, Slack reconnection/configuration, or another protected/irreversible effect.

This checkpoint records the authority under which the evacuation writes were made; it does not extend that authority indefinitely.

## Protected effects deliberately not performed

- no merge;
- no canonical promotion;
- no deployment;
- no provider/database mutation;
- no credential/permission/ruleset mutation;
- no training or Project Settings mutation;
- no Slack activation;
- no destructive cleanup or history rewrite.

## Next coordinator

Future interface: `BT2 Coordinator`.

Exact next directive:

`BT2_COORDINATOR::FRESH_CHECK_EXODUS_CANDIDATES::Reconcile current bt2/main with PRs #24, #26, and #27 plus Bus PR #128; preserve the 13-role reconstruction contract and exact three-interface topology; inspect Bus issue #142 against the current active Bus integration line before designing any runtime-instance fencing; refresh Lantern only through exact WoWSQL target bt2-479e4ad9 and fail closed if unavailable; do not merge/deploy/mutate providers without separate current authority.`

## Reconstruction test

Assuming this ChatGPT conversation is inaccessible, a fresh BT2 Coordinator with GitHub/Bus access can determine:
- the project and worker topology;
- the exact durable source candidates;
- why the earlier two-role chat model was wrong;
- where Seven's source is reconstructed from;
- the current known concurrency frontier;
- the authority ceiling;
- the next safe coordination action.

Therefore this retiring conversation is not required as infrastructure.
