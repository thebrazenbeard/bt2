# BT2 Coordinator Exodus Retirement Checkpoint — 2026-09-20

checkpoint_class: STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT
interface_owner: BT2 Coordinator
retired_execution_terminal_dependency: NONE_REQUIRED

## Purpose

This checkpoint evacuates the durable engineering state created or reconciled in the retiring ChatGPT execution terminal. The terminal is not a durable identity, authority source, assignment source, or system of record.

After retirement, the only persistent ChatGPT human interfaces are:
1. Vera
2. Vera Control Plane Coordinator
3. BT2 Coordinator

BT2 workers, reviewers, Radar, and project-specific roles are reconstructed ephemerally from durable GitHub / Bus / provider evidence.

## Canonical BT2 source

Repository: `thebrazenbeard/bt2`

Canonical branch observed:
- `main@30e81cadd94fae117a7f6875523c03251c7c9f6e`
- tree `6782a2d62afeab8cefb1a3bc39cc39ab617d637c`

Current preferred Exodus consolidation candidate:
- Draft PR #35
- branch `exodus/bt2-role-interface-reconciliation-v1-20260920`
- exact reviewed/source head immediately before this checkpoint: `ea0fcea92d829ee4a79628f8e50f31783d65b4ea`
- OPEN / DRAFT / UNMERGED

PR #35 reconciles:
- PR #24 coordinator compatibility/interface surface;
- PR #26 exact 13-role worker reconstruction map;
- PR #27 exact three-interface topology and coordinator reconstruction;
- PR #29 recovery/audit material as provenance;
- PR #34 Eight chat-era-loader compatibility note.

Normative topology in PR #35:
- exactly 13 durable BT2 role sources:
  - One
  - Two
  - Three
  - Four
  - Five
  - Six
  - Seven
  - Eight
  - Nine
  - Thirteen
  - Masa
  - Mune
  - Hephaestus
- Seven is explicitly bound to `archive/training-sources/project-achilles/seven/v1.0.0`.
- exactly three persistent interfaces:
  - Vera
  - Vera Control Plane Coordinator
  - BT2 Coordinator
- temporary ChatGPT / Work / API / CLI / model / subagent contexts are execution terminals, not durable identities.

PR #24 artifacts are compatibility adapters only and are cross-bound to the normative worker/topology contracts. They are not a second topology authority.

PR #29 remains historical/recovery provenance and is not current topology authority.

## Independent BT2 policy frontier

Draft PR #23:
- head `22a0053df845113fbdce00433ceff44844f5a80b`
- OPEN / DRAFT / UNMERGED
- defines BT2 adversarial-collaboration posture.

Classification:
- `INDEPENDENT_POLICY_CANDIDATE`
- do not silently fold PR #23 into Exodus topology/reconstruction.
- do not infer Project installation or behavioral qualification from source presence.
- evaluate/qualify it separately.

## Eight compatibility

Draft PR #34:
- head `e3bb917a94cb49fbf4513bbe5048964d3cfcb8e1`
- OPEN / DRAFT / UNMERGED

Its unique compatibility document has been carried into PR #35:
- `docs/exodus/BT2_EIGHT_CHATLESS_RECONSTRUCTION_COMPATIBILITY_20260920.md`

The frozen Eight v1.0.0 package remains immutable historical/training source. Chat-era loader wording must not require a permanent Eight conversation or self-award BASE_READY.

## BT2 PR #35 evidence ceiling

Fresh structural readback established:
- exactly 13 worker IDs;
- Seven source path is correct;
- exactly three persistent interface names in the required order;
- coordinator reconstruction includes Seven;
- #24 compatibility spec points to the normative topology contracts;
- Eight compatibility note is present.

No hosted workflow run was returned for PR #35 exact head before this checkpoint.

Evidence ceiling:
- SOURCE / STRUCTURAL_READBACK established.
- HOSTED_TEST_EXECUTION not established.
- INDEPENDENT_REVIEW not established.
- MERGE / INSTALL / ACTIVATE / DEPLOY not established or authorized.

## Chat Communication Bus

Repository: `thebrazenbeard/chat-communication-bus`

Canonical `main` observed:
- `aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`

Fresh topology source:
- `architecture/contracts/RADAR_TOPOLOGY_V1.json`
- current protocol branch: `bus/protocol-v2`
- integration branch: `radar/control-plane-v1`
- active writer lanes remain durable Git routes; no permanent worker chat is required.

Current Exodus integration subject inspected:
- Draft PR #140
- head `2461df3a1a8393d4c7ded227afb17ecc7abfacb3`
- OPEN / DRAFT / UNMERGED

PR #140 current recovery/operator source explicitly states:
- fresh Radar execution runtime, not permanent chat;
- loss of a ChatGPT conversation does not erase Radar state;
- a `chatgpt.com` URL or archived conversation must never be the sole recovery locator;
- persistent interfaces are exactly Vera, Vera Control Plane Coordinator, BT2 Coordinator.

Therefore old historical/session-oriented documents do not create a current permanent-chat dependency when current PR #140 recovery contracts apply.

## Runtime-instance fencing frontier

Bus issue #142:
- OPEN
- title: `Exodus: fence concurrent runtime instances for one durable worker assignment`

Source inspection against current PR #140 confirmed the architecture gap:
- assignments bind durable `assignee_identity_id`;
- nodes have separate `node_id`, identity ownership, heartbeat, and lease;
- assignment predecessor/event idempotency does not by itself fence one live runtime generation from another same-identity runtime doing duplicate work.

Design-only candidate:
- Draft PR #146
- exact head `13350bbf6767c54e291e0c4c5e41b2d1c8bc9a92`
- exact parent PR #140 head `2461df3a1a8393d4c7ded227afb17ecc7abfacb3`
- OPEN / DRAFT / UNMERGED
- exactly three source files added;
- no SQL migration;
- no provider mutation.

PR #146 freezes:
- durable identity != runtime identity;
- one current execution claim per assignment;
- node + monotonic fence token + exact assignment-event binding;
- claim lease <= node lease;
- identity/liveness/dependency checks on acquire;
- stale node/token/event rejection;
- idempotent acquire/renew/finalize operations;
- protected-effect authority separate from execution claim;
- service-role-only boundary for any future mutating API;
- 14 hostile cases before implementation.

Hosted CI evidence:
- run `35504940278`
- both Python jobs ended with `steps=[]`, runner_id 0.
Classification:
- `HOSTED_CI = NO_RUN / UNKNOWN`
- not semantic FAIL;
- not PASS.

Independent review of PR #146 is not yet established.

## Bus mirror of BT2 PR #35

Draft Bus PR #147:
- branch `mirror/bt2-pr35-exodus-reconciliation-20260920`
- current observed head before this checkpoint: `6c6401905146c80c92c7f21bafe165ab021f5783`
- OPEN / DRAFT / UNMERGED
- source PR #35 remains canonical.

Mirror file:
- `projects/bt2/pr-mirrors/PR-35-EXODUS-ROLE-INTERFACE-RECONCILIATION.md`

The mirror already records the refreshed PR #35 head `ea0fcea92...`, Eight compatibility inclusion, PR #23 separation, Bus #140/#146 relation, and Lantern UNKNOWN state.

## Lantern

Required exact target:
- WoWSQL project `bt2-479e4ad9`

During the final retirement audit:
- exact V3 projection preflight calls failed internally through the connector;
- a stable preflight -> B0 -> payload -> B1 cut could not be established.

Classification:
- `LANTERN_CURRENTNESS = UNKNOWN`

Fail-closed rule:
- do not use Supabase, Git, Project prose, historical files, chat memory, or another provider as current Lantern state.
- retry the exact V3 read sequence before any Lantern-dependent currentness claim.

## Chat-dependency audit

BT2 code search:
- no `chatgpt.com` current-state locators found;
- no `main chat` locators found;
- no `continue in this chat` locators found;
- current PR #35 runtime/recovery source is execution-terminal-neutral.

Bus:
- current PR #140 recovery/operator contracts explicitly eliminate permanent-chat dependence.
- historical references to chats/sessions are retained only where they are compatibility/history/operator-surface language and must not be treated as durable identity/state.

No successor worker chat is required.

## Authority

This checkpoint does not authorize:
- merge;
- canonical promotion;
- production deployment;
- provider/database mutation;
- credential/permission changes;
- force push or destructive cleanup;
- paid infrastructure;
- public release / visibility change;
- model training;
- Project Settings mutation;
- Slack activation/configuration;
- any other protected or irreversible effect.

## Exact next safe frontier

Future coordinating interface: `BT2 Coordinator`.

Directive:

`BT2_COORDINATOR::RESUME_EXODUS::FRESH_REVIEW_PR35_AND_BUS146_NO_MERGE`

Required sequence:
1. fresh-check `bt2/main`, PR #35 exact head, PR #23, PR #34, reviews, and CI;
2. verify PR #35 still preserves exactly 13 roles and exactly three persistent interfaces;
3. obtain independent architecture/source review of PR #35; run/obtain executable validator evidence before any promotion claim;
4. keep PR #23 as a separate policy frontier unless explicitly reconciled under current authority;
5. fresh-check Bus PR #140, issue #142, PR #146, reviews, and CI;
6. obtain independent hostile review of the fencing design before implementation;
7. if implementation is later authorized, freeze RED hostile cases before adding any SQL/provider mutation;
8. retry Lantern only through exact WoWSQL target `bt2-479e4ad9` when currentness is needed;
9. keep source/build/test/review/provider/install/runtime/effect/qualification states separate;
10. do not merge/deploy/mutate providers without separate current authority.

## Reconstruction test

A fresh BT2 Coordinator with only current Project instructions, GitHub, Bus, and authorized provider reads can determine:
- the exact persistent interface topology;
- the 13 durable worker roles and source paths;
- current source candidates and unresolved policy frontier;
- Bus integration and fencing design subjects;
- evidence ceilings and UNKNOWN states;
- protected-effect limits;
- exact next safe work.

No fact required for this continuation depends on opening the retired conversation.
