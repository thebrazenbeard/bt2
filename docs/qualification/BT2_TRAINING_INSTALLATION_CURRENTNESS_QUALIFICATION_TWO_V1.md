# BT2 Training Installation / Currentness Qualification — Two V1

Date: 2026-09-10
Coordination: `BT2-CANONICAL-PLATFORM-20260910`
Owner: Two
Target: WoWSQL `bt2-479e4ad9`

## Purpose

Represent runtime training installation/activation as durable evidence without collapsing it into package discovery, compatibility, qualification, logical-agent identity, or an external installation effect.

## Source

- `database/migrations/0015_training_installation_evidence_v1.sql`
- `database/migrations/0016_training_qualification_currentness_v1.sql`
- `database/tests/0002_training_installation_smoke.sql`

## Model

Installation/activation observations are an append-only event chain keyed by stable `binding_id`. The chain records the agent, exact training package, optional supporting qualification, target kind/locator or same-agent runtime session, sequence/predecessor, observed state, and evidence.

Observed installation states are:

`STAGED | INSTALLED | ACTIVE | INACTIVE | REMOVED`

The event log is historical evidence only. It does not itself install or activate anything externally.

Qualification records are append-only. `training_qualification_current_v1` derives the current qualification disposition for an agent/package from the latest qualification record. A historical PASS is therefore not silently treated as current after a later RETRACTED/SUPERSEDED/FAIL disposition.

`training_installation_effective_v1` separates the latest observed installation state from its current validity. An observed ACTIVE state is effective ACTIVE only while:

- the package remains `QUALIFIED_BASE`;
- package compatibility remains `COMPATIBLE`;
- the current qualification is PASS and is the exact qualification cited by the ACTIVE event;
- when the target is a runtime session, that same-agent runtime session remains ACTIVE.

If those supports no longer hold, the historical ACTIVE observation remains immutable but effective state becomes `INVALIDATED`.

At most one currently valid ACTIVE training binding is admitted for an agent. The check is serialized by an agent-scoped advisory transaction lock.

## Behavioral qualification

A rollback-contained hostile probe on the live WoWSQL target reached deliberate marker:

`TRAINING_INSTALLATION_ROLLBACK_PASS`

Verified:

1. a compatible QUALIFIED_BASE package with current PASS qualification can produce ACTIVE evidence;
2. the effective view reports that binding as currently valid ACTIVE;
3. a second simultaneously current ACTIVE binding for the same agent is rejected;
4. installation-event UPDATE is rejected because history is append-only;
5. qualification UPDATE is rejected because qualification history is append-only;
6. an installation event for agent Two cannot bind to agent Three's runtime session;
7. invalid `STAGED -> ACTIVE` transition is rejected;
8. an event cannot change the binding target subject across the predecessor chain;
9. `ACTIVE -> INACTIVE` succeeds;
10. after a later RETRACTED qualification, the old ACTIVE observation remains historical but effective state becomes `INVALIDATED`;
11. the retracted/stale PASS cannot authorize a new ACTIVE binding;
12. a later fresh PASS can support a new ACTIVE binding because the prior ACTIVE evidence is no longer currently valid.

Post-probe readback confirmed:

- training packages: 0 probe rows;
- training qualifications: 0 probe rows;
- installation events: 0 probe rows;
- runtime sessions: 0 probe rows.

## Rebuild coverage

`database/tests/0002_training_installation_smoke.sql` reproduces the core qualification/installation-currentness path using explicit synthetic fixtures inside a transaction that rolls back.

The GitHub Actions workflow now executes every `database/tests/*.sql` file in lexical order. GitHub Actions remains externally blocked before runner step 1 on this repository, so blank-database execution is still not credited as PASS or FAIL.

## Current package binding

Database package digest after migrations through `0016` and both smoke tests:

`6d3ef0d835b2d86562af090b13ab8f0eb9ab869cceab73062cbd0bffe47a84c1`

## Authority nonclaim

No real training package, qualification, installation, or activation state was created by this qualification. No external runtime was modified. No merge, cutover, legacy retirement, producer authorization, or Vera-Supabase mutation is asserted.
