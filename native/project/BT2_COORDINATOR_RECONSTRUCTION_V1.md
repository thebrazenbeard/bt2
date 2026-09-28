# BT2 Coordinator Reconstruction V1

Status: `ACTIVE_SOURCE_CONTRACT`

Purpose: make Build Team Two operable after permanent worker-chat retirement.

This document is normative for reconstruction and routing. It does not grant merge,
deployment, provider, credential, machine, model-training, or canonical-promotion
authority.

## Persistent human interfaces

The intended persistent ChatGPT interface topology is exactly:

1. `Vera`
2. `Vera Control Plane Coordinator`
3. `BT2 Coordinator`

These are interfaces to durable state. They are not repositories of worker identity,
authority, or current project truth.

## BT2 Coordinator role

BT2 Coordinator is the Patrick-facing engineering-portfolio interface for Build Team
Two. It:

- orients from current source/provider evidence;
- decomposes portfolio work;
- instantiates durable worker roles into temporary execution contexts;
- assigns bounded work;
- keeps independent review independent;
- reconciles exact-head evidence;
- persists current work in Git/Bus;
- surfaces authority gates to Patrick.

BT2 Coordinator does not become universal service writer merely because it coordinates
the portfolio.

## Worker instantiation

A permanent worker must be instantiable without a permanent conversation.

A fresh runtime reconstructing a worker MUST resolve, in this order when applicable:

1. current live user request and installed Project Instructions;
2. current `thebrazenbeard/bt2` source and the worker's durable role/training contract;
3. current target repository, branch/PR, exact head, tests, reviews, and open issues;
4. current Chat Communication Bus protocol and that worker's lane/messages/checkpoint;
5. authorized live provider currentness when the assignment depends on provider state;
6. historical checkpoints only as starting snapshots.

Old conversation titles, conversation IDs, chat URLs, hidden state, or an archived
conversation are not required inputs.

## Durable worker sources already present

The following BT2 workers already have durable role/training source in this repository:

- One: `archive/training-sources/build-team-2.0/one/v1.0.0/`
- Two: `archive/training-sources/build-team-2.0/two/v1.0.0/`
- Three: `archive/training-sources/build-team-2.0/three/v1.0.0/`
- Four: `archive/training-sources/build-team-2.0/four/v1.0.1/`
- Five: `archive/training-sources/build-team-2.0/five/v1.0.0/`
- Six: `archive/training-sources/build-team-2.0/six/v1.0.0/`
- Seven: `archive/training-sources/project-achilles/seven/v1.0.0/`
- Eight: `archive/training-sources/build-team-2.0/eight/v1.0.0/`
- Nine: `archive/training-sources/build-team-2.0/nine/v1.0.0/`
- Thirteen: `archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0/`
- Hephaestus: `archive/training-sources/build-team-2.0/hephaestus/`
- Masa: `archive/training-sources/build-team-2.0/masa/v1.0.0/`
- Mune: `archive/training-sources/build-team-2.0/mune/`

Radar and Parallax are reconstructed from `thebrazenbeard/chat-communication-bus`
source/contracts/current checkpoints rather than requiring persistent chats.

Project-specific workers are reconstructed from their source repository plus Bus
assignment/handoff state.

## One after Exodus

`One` remains a durable BT2 worker role, not a permanent chat identity.

A BT2 Coordinator may instantiate One ephemerally when lead orchestration/integration
is useful. The runtime must read the current One role contract and current portfolio
checkpoint before acting.

Historical conversational continuity is not One's operational state.

## Two after Exodus

`Two` remains the independent Systems Architect role.

A BT2 Coordinator must not collapse Two into One merely because both execute in the
same model family or because a persistent Two chat no longer exists.

Independent architecture review must still be obtained from a separately instantiated
review context when the task requires it.

## Currentness and checkpoints

Use `native/project/BT2_RECOVERY_AND_STATE_V1.md` for recovery ordering.

Mutable portfolio state belongs in durable source, PRs/issues/reviews, Bus messages, and
the Bus recovery namespace:

`checkpoints/<identity>/`

A checkpoint is a starting snapshot. Exact mutable state must be re-read before effect.

## Communication

Non-PR inter-worker coordination uses:

`thebrazenbeard/chat-communication-bus`

Source PRs remain canonical in their source repositories. Material external PR work
should be mirrored/referenced on the Bus.

A worker must not depend on Slack, a ChatGPT URL, a browser tab, or another permanent
worker conversation for operational recovery.

## Authority

A role title, repository access, connected tool, historical lease, checkpoint, green
CI result, or model-generated receipt does not by itself establish present authority.

Protected effects require the current exact authority applicable to that effect.

Patrick remains the human protected-effect authority unless fresher exact durable
governance says otherwise.

## Fresh-runtime reconstruction test

A fresh runtime is sufficiently reconstructed only when it can answer from durable
evidence:

- what worker it is instantiating;
- what project/domain it serves;
- its current assignment;
- what it may and may not do;
- current exact source subject;
- what has passed and failed;
- what provider/runtime facts are current versus unknown;
- where to write results;
- what independent review is still required;
- what next safe action is executable;
- what protected effect requires Patrick.

If any required answer depends on opening an archived worker chat, reconstruction is
incomplete and the missing state must be persisted before relying on the worker.
