# BT2_RECOVERY_AND_STATE_V2

## Fresh-session recovery
A fresh BT2 session should recover state in this order:
1. current live user request and Project Instructions;
2. `thebrazenbeard/bt2@main` and any named target repository;
3. Chat Communication Bus messages relevant to current work;
4. installed Project files needed to interpret the active contract;
5. live WoWSQL `bt2-479e4ad9` only for runtime-only or Lantern-currentness facts needed by the task;
6. memory/inference only as non-authoritative context.

This ordering is about availability and reconstruction, not authority promotion. A lower source never substitutes for a missing higher-authority fact in the same claim domain.

## Recovery domains
Classify each missing fact:
- source/repository fact -> Git;
- coordination/handoff fact -> Bus or owning repository checkpoint;
- installed-project fact -> current Project files/instructions;
- WoWSQL runtime fact -> live WoWSQL readback;
- Lantern currentness fact -> governed Lantern read sequence;
- remembered context -> non-authoritative aid only.

If a provider is unavailable, fail closed only for facts in that provider's domain. Continue recovery in independent domains.

## Minimum orientation record
Before resuming durable work, establish when relevant:
- canonical source head/ref;
- active branch/PR/worktree subject;
- exact target environment;
- current coordination/handoff frontier;
- provider availability for any provider-dependent requirement;
- last verified effect/receipt/test result that is actually available;
- authority boundaries that still apply;
- next executable action.

Do not require all fields for trivial tasks. Do require the applicable fields before destructive, cross-system, or continuation-sensitive work.

## Continuation checkpoint
When work remains across sessions, persist a concise checkpoint in Git and/or the Chat Communication Bus before treating the session as safely resumable. It should state the exact subject, completed effects, unresolved blockers, current tests/evidence, authority ceiling, provider limitations, and next action.

WoWSQL may mirror or enrich a checkpoint, but it must not be the only place needed to resume ordinary source work.

Never store passwords, API keys, database credentials, or other secrets in checkpoints.

## Ambiguous effects
If an external write may have succeeded but its response was lost, read back from that same authoritative system before retrying. Do not blindly replay non-idempotent effects and do not infer write success from source intent.

If the provider cannot be read, classify the effect as `UNKNOWN` and continue only work that does not require resolving that ambiguity.

## Currentness
Fresh live evidence outranks older receipts, memory, screenshots, or prior-chat claims within the same claim domain. A historical PASS does not automatically qualify a changed source/runtime subject.

Git currentness and runtime currentness are separate. A current Git head can be established while WoWSQL currentness is unknown, and vice versa.

## Provider outage behavior
When WoWSQL is unavailable:
- record the bounded failure;
- do not fall back to Supabase for Lantern/current-runtime truth;
- do not repeatedly retry an unchanged failing route in the same bounded operation;
- keep source, review, test, Bus, and checkpoint work moving where semantically independent;
- require a fresh read when WoWSQL-dependent work resumes.

## Failure mode
If durable state cannot establish a required current fact, report `UNKNOWN` or the bounded known state. Do not fabricate continuity and do not broaden one provider outage into a claim that the whole BT2 system is unavailable.
