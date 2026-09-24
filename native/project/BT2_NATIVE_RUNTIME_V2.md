# BT2_NATIVE_RUNTIME_V2

## Purpose
This file defines BT2 native runtime behavior with external-provider degradation contained to the claim domains that actually depend on those providers.

## Bootstrap
On a fresh chat that needs BT2 durable state:
1. Treat the session as an ephemeral execution terminal.
2. Read current Project Instructions.
3. Refresh `thebrazenbeard/bt2@main` before claims about canonical source.
4. Recover open source work from Git and current coordination/handoffs from the Chat Communication Bus when relevant.
5. Read WoWSQL `bt2-479e4ad9` only when the requested claim or acceptance criterion depends on live database state.
6. Use Project Lantern only through the installed WoWSQL Lantern contract when Lantern currentness is actually relevant.
7. If WoWSQL is unavailable, mark only WoWSQL-dependent facts `UNKNOWN` and continue independent work.

## Durable boundaries
Git is canonical for code, versioned contracts, migrations, tests, runbooks, reconstructible configuration, and resumable source checkpoints.

The Chat Communication Bus is the normal non-PR coordination and handoff channel. Durable repository artifacts may also carry checkpoints when the owning repository needs reconstructible state.

WoWSQL is runtime/query infrastructure for database receipts, runtime registrations, governed Lantern state, and other modeled runtime facts. It must not be the sole copy of information required to resume ordinary BT2 source work.

The ChatGPT Project supplies instructions, native reference files, tools/connectors, and execution sessions. It is not the sole durable datastore.

## Provider failure containment
Provider failure must remain local to the facts and effects that require that provider.

A WoWSQL outage does not block:
- Git source inspection or editing;
- branch/PR review;
- repository-local tests and static validation;
- Bus coordination;
- source-backed recovery;
- documentation or checkpoint creation;
- work on another provider or target that has independent authority and evidence.

A WoWSQL outage does block or narrow:
- claims about current WoWSQL rows or receipts;
- claims about current Lantern-visible material;
- acceptance that explicitly requires live WoWSQL readback;
- a WoWSQL write or read-after-write effect.

Do not substitute another provider for the blocked fact unless a separate, explicit contract defines semantic equivalence. There is no Supabase fallback for Lantern currentness.

## Retry discipline
After a direct WoWSQL request fails internally or cannot reach the target, do not loop on equivalent calls merely to obtain a different error. A second attempt is justified only when the method, route, target, credentials state, or new evidence is materially different.

A later turn or later phase may probe again when current provider health matters.

## Coding-team behavior
One maintains the whole task graph and integration state. Two maintains an independent whole-system architecture model. Specialist roles can be routed by One when their charter is useful. Do not create role fan-out when One/Two can finish the task directly.

Substantial implementation should occur on an isolated branch/worktree. Inspect before editing. Prefer tests that reproduce the defect or prove the requested behavior. Verify effects after writes. Record durable handoff state before a chat becomes a bottleneck.

## Recovery
A fresh One should be able to establish:
- current canonical source head;
- current active work/PR;
- current coordination/handoff frontier;
- provider availability for any provider-dependent claim;
- pending blockers;
- next executable action.

The inability to read WoWSQL must not prevent source recovery when Git/Bus evidence is sufficient. Runtime-only facts remain `UNKNOWN` until fresh readback succeeds.

## Installation state vocabulary
- `SOURCE_READY`: canonical file exists in Git.
- `PROJECT_FILES_INSTALLED`: exact native Project files are present.
- `PROJECT_INSTRUCTIONS_INSTALLED`: exact Project instruction contract is active.
- `CORE_OPERATIONAL`: canonical Git plus required coordination/repository surfaces are usable for the requested non-runtime work.
- `RUNTIME_PROVIDER_AVAILABLE`: the relevant runtime provider answered the required live read.
- `LANTERN_CURRENTNESS_VERIFIED`: the exact governed Lantern read completed and cross-bound successfully.
- `BEHAVIOR_VERIFIED`: a fresh chat demonstrates the intended operating behavior.

Do not collapse these states.
