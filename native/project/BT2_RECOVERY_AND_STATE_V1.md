# BT2_RECOVERY_AND_STATE_V1

## Fresh-session recovery
A fresh BT2 session should recover state in this order:
1. current live user request and Project Instructions;
2. `thebrazenbeard/bt2@main` and any named target repository;
3. live WoWSQL `bt2-479e4ad9` state relevant to the task;
4. Chat Communication Bus messages relevant to current work;
5. installed Project files;
6. memory/inference only as non-authoritative context.

## Worker reconstruction
`native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json` is the current source map for reconstructing One, Two, numbered specialists, Masa/Mune, and Hephaestus without a permanent worker chat. Read the mapped source package and current assignment separately. Source-package recovery is not qualification, installation, activation, current assignment, or protected-effect authority.

## Minimum orientation record
Before resuming durable work, establish when relevant:
- canonical source head/ref;
- active branch/PR/worktree subject;
- exact target environment;
- last verified effect/receipt/test result;
- authority boundaries that still apply;
- next executable action.

Do not require all fields for trivial tasks. Do require them before destructive, cross-system, or continuation-sensitive work.

## Continuation checkpoint
When work remains across sessions, persist a concise checkpoint in a durable surface. It should state the exact subject, completed effects, unresolved blockers, current tests/evidence, authority ceiling, and next action. Never store passwords, API keys, or database credentials in checkpoints.

## Ambiguous effects
If an external write may have succeeded but its response was lost, read back before retrying. Do not blindly replay non-idempotent effects.

## Currentness
Fresh live evidence outranks older receipts, memory, screenshots, or prior-chat claims. A historical PASS does not automatically qualify a changed source/runtime subject.

## Failure mode
If durable state cannot establish a required current fact, report UNKNOWN or the bounded known state and continue only where safe. Do not fabricate continuity.
