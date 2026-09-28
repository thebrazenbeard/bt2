# Eight Chatless Reconstruction Compatibility — 2026-09-20

Status: EXODUS COMPATIBILITY NOTE / SOURCE CANDIDATE / NO TRAINING OR INSTALL EFFECT

## Exact subjects

Canonical BT2 source observed for this review:
- repository: `thebrazenbeard/bt2`
- `main`: `30e81cadd94fae117a7f6875523c03251c7c9f6e`
- current Project Instructions V3 blob: `5de32bc36d1cf463395d83760e3eb109e9523d70`

This note is stacked on BT2 Exodus PR #26:
- base candidate head: `95fc8ca0f9a107ad3cf0287bcc5943ef3c42ad81`

Frozen Eight training source:
- package: `archive/training-sources/build-team-2.0/eight/v1.0.0/`
- `BOOTSTRAP_LOADER.md` blob: `9fed357656a73b42ba1791d26fcb042594e8d819`
- `TRAINING_MANIFEST.yaml` blob: `afb8042a344c01290bfd43685cc05ee489d12462`

## Conflict discovered during ChatGPT Exodus

The frozen v1.0.0 loader uses chat-era execution-container language, including:
- training a "fresh chat";
- freezing a successfully trained chat as the role base;
- branching a working chat from that base.

Current `PROJECT_INSTRUCTIONS_V3` states that a chat/session is a replaceable execution terminal and is not durable identity or state.

The loader itself says current governed role/authority sources outrank the frozen package for staleness checks and requires `TRAINING_SOURCE_STALE` rather than silent reinterpretation when current governance materially contradicts the package.

Therefore the safe Exodus interpretation is:

1. Eight's durable logical identity and permanent-role semantics do not require a permanent ChatGPT conversation.
2. The v1.0.0 package remains immutable historical/training source; do not rewrite its bytes merely to modernize terminology.
3. Chat-specific wording in that package MUST NOT be used to require a permanent Eight chat, a chat URL, hidden conversation state, or chat-derived current assignment.
4. Source-package presence alone MUST NOT be promoted to `BASE_READY`, installation, activation, current assignment, or effect authority.
5. If packaged-role qualification is required after Exodus, either:
   - perform an explicit current-governance compatibility review that can legitimately resolve the loader's staleness rule; or
   - publish a successor training package/version whose loader is execution-terminal-neutral.
6. Until then, a temporary runtime may reconstruct Eight for bounded work from:
   - current Project Instructions;
   - current BT2 permanent-role/governance source;
   - preserved role package as historical/semantic source;
   - current Bus topology;
   - an exact current durable assignment;
   - fresh target/provider evidence as applicable.
   That reconstruction does not self-award packaged training qualification.

## Why this is not a chat dependency

Eight's current role, routing, authority ceilings, and assignment discovery are all durable outside any conversation.

Current Bus route at this review:
- topology blob: `69e505031d4e53dcb853578dac23817649af1918`
- route: `bus/eight-v2`

Current Exodus reconstruction candidate:
- Bus PR #140 live head observed: `2461df3a1a8393d4c7ded227afb17ecc7abfacb3`
- `architecture/reconstruction/EXODUS_WORKER_EIGHT_V1.json` blob: `c59d11b2e667efa2ec67a3362174864d412f8df3`
- reconstruction status: `READY`
- `retired_chat_required: false`

That record and BT2 PR #26 remain candidates until integrated under normal authority. This note does not promote either candidate to canonical state.

## Regression condition

A future reconstruction/qualification design for Eight fails Exodus compatibility if any required step depends on:
- opening this retired chat;
- a permanent Eight conversation;
- a conversation URL/title/ID;
- hidden chat state;
- remembered chat-only assignment/authority;
- Slack history as the only recovery source.

A temporary ChatGPT/Work/API/CLI/model/subagent runtime is acceptable when treated as a terminal and when durable state supplies the worker/assignment/authority inputs.

## Authority ceiling

This note changes no historical training bytes and performs no:
- training;
- qualification award;
- install/activation;
- merge;
- provider mutation;
- credential/permission change;
- Project Settings mutation;
- canonical-memory effect;
- Slack activation;
- deployment.

STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT
