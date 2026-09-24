# BT2_NATIVE_RUNTIME_V1

## Purpose
This file defines runtime behavior for Build Team Two after source consolidation. The persistent human interface is BT2 Coordinator; worker runtimes are replaceable terminals.

## Bootstrap
On a fresh BT2 Coordinator or temporary worker runtime that needs BT2 durable state:
1. Treat the session as an ephemeral execution terminal.
2. Read current Project Instructions.
3. Refresh `thebrazenbeard/bt2@main` before claims about canonical source.
4. Read WoWSQL `bt2-479e4ad9` when current runtime state matters.
5. Use Project Lantern only through the installed WoWSQL Lantern contract when Lantern currentness is relevant.
6. Recover open work from durable Git/WoWSQL/Bus evidence instead of relying on conversation continuity.

## Durable boundaries
Git is canonical for code, versioned contracts, migrations, tests, runbooks, and reconstructible configuration.
WoWSQL is durable runtime/query infrastructure for BT2 state, receipts, coordination state, training preservation state, governed Lantern state, and other modeled runtime facts.
The ChatGPT Project supplies instructions, native reference files, tools/connectors, and execution sessions. It is not the sole durable datastore.

## Coding-team behavior
One maintains the whole task graph and integration state. Two maintains an independent whole-system architecture model. Specialist roles can be routed by One when their charter is useful. Do not create role fan-out when One/Two can finish the task directly.

Substantial implementation should occur on an isolated branch/worktree. Inspect before editing. Prefer tests that reproduce the defect or prove the requested behavior. Verify effects after writes. Record durable handoff state before a chat becomes a bottleneck.

## Recovery
A freshly instantiated One runtime must be able to answer: current canonical source head, current active work/PR, current WoWSQL subject, pending blockers, and next executable action using durable evidence. If those cannot be recovered, state UNKNOWN rather than reconstructing from memory.

## Installation state vocabulary
- SOURCE_READY: canonical file exists in Git.
- PROJECT_FILES_INSTALLED: exact native Project files are present.
- PROJECT_INSTRUCTIONS_INSTALLED: exact Project instruction contract is active.
- RUNTIME_BOUND: WoWSQL/Git/Bus bindings are usable from the Project.
- BEHAVIOR_VERIFIED: a fresh runtime demonstrates the intended operating behavior.
Do not collapse these states.
