# Mune Operational Checkpoint Protocol

Schema: `BT2_MUNE_OPERATIONAL_CHECKPOINT_V1`

## Purpose

A working Mune branch uses this protocol to save enough **mutable operational state** for a later branch to resume verification correctly. Checkpoints are not training source, do not alter the frozen role base, and do not establish hidden or subjective continuity.

## When to checkpoint

Create or refresh a checkpoint at a clean handoff boundary, including:
- after a material review verdict or correction;
- before branching, context exhaustion, or deliberate work transfer;
- after an ambiguous external effect has been reconciled;
- when the controlling assignment or exact immutable subject changes;
- when requested by current governance.

Do not generate checkpoint churn merely because a turn occurred.

## Required fields

Use `operational-checkpoint-template.json`. Populate:
- package/trained-base identity;
- role;
- checkpoint creation time and provenance;
- controlling current assignment/event;
- exact immutable review subject and custody locator;
- material current Git/provider/target identities;
- completed tests/hostiles and verdict/claim ceiling;
- unresolved blockers/conflicts;
- debugger-lead, repair-implementer, governance, and relevant Owner/Warden escalation interfaces;
- next executable frontier;
- external effects actually performed;
- explicitly unperformed or unauthorized effects;
- superseded/historical subjects;
- retry/ambiguous-write state;
- source locators needed to refresh currentness.

## Truth boundary

A checkpoint is a historical operational record. On resume:
1. verify checkpoint structure;
2. refresh current governance and roster;
3. refresh assignment and authority;
4. reacquire exact review subject/current head/provider/target;
5. compare fresh evidence to checkpoint;
6. treat mismatches as currentness changes, not as errors to overwrite silently.

A checkpoint may say what was verified at checkpoint time. It may not self-authorize a current action.

## Base separation

The frozen Mune base stores permanent competence:
- role boundaries;
- verification method;
- evidence discipline;
- retry/write safety;
- escalation and handoff method.

The operational checkpoint stores temporary work state:
- assignments;
- heads;
- hashes;
- provider observations;
- blockers;
- unfinished work;
- leases and currentness.

Never copy mutable checkpoint data into the versioned training modules to make it “remembered.”

## Resume output

After refresh, report one:
- `RESUME_READY`
- `RESUME_READY_WITH_SUPERSESSION`
- `BLOCKED_CURRENTNESS`
- `BLOCKED_AUTHORITY`
- `BLOCKED_EVIDENCE`

State the exact next frontier and the evidence supporting it.
