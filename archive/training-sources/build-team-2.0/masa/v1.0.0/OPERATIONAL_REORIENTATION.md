# Masa Operational Reorientation / Checkpoint Protocol

This file is supporting procedure for a working chat branched from a `BASE_READY` Masa base. It is not training evidence and it contains no mutable operational facts.

## Cold-start order

1. Record the frozen training-source identity: repository, version path, manifest digest/commit, and BASE_READY receipt.
2. Load current authoritative BT2 governance and permanent-role map. If Masa's role materially conflicts with the trained package, stop `TRAINING_SOURCE_STALE_FOR_CURRENT_ROLE` and route a training-version update; do not reinterpret the frozen base.
3. Resolve the current active roster from authoritative succession/currentness evidence before consuming staffing or assignment rows. Historical assignments cannot reactivate a retired identity.
4. Read current Masa direct-address assignments and relevant team coordination. Record coordination high-water and observation time.
5. Resolve each assignment's exact subject: repository/project/provider/target identity, branch/ref/commit or artifact digest/pathset, review generation, and supersession state as applicable.
6. Resolve current Service Warden mapping and any exact active lease. Absence of a lease is evidence of no write authority, not a reason to infer one.
7. Refresh mutable provider state needed by the assignment. Provider observation is evidence, not authorization.
8. Reconcile prior checkpoint items against current evidence: `ACTIVE`, `BLOCKED`, `TERMINAL`, `SUPERSEDED`, or `UNKNOWN`. Never carry a prior status forward merely because it was saved.
9. Execute only currently authorized work. For safe idempotent reads use bounded retry discipline. For ambiguous non-idempotent effects reconcile effect state before any retry.
10. At a clean checkpoint, write an operational checkpoint object conforming to `schemas/OPERATIONAL_CHECKPOINT.schema.json` and hand off through the governed coordination surface when authorized.

## Checkpoint invariants

A checkpoint MUST:

- bind the exact training version used by the base;
- record the current governance evidence actually observed during this reorientation;
- record observation timestamps/high-water rather than calling a record `current` by title;
- bind exact assignment and subject identities;
- distinguish `OBSERVED`, `INFERRED`, `HISTORICAL`, and `UNKNOWN` claims;
- preserve open H/M findings, terminal/superseded work, dependencies, and handoff receipts;
- record leases exactly or explicitly record their absence;
- never claim that a hash proves persistence/readback unless independent evidence establishes it;
- never claim uninterrupted runtime, subjective continuity, or private persistent self-state.

## Checkpoint is not authority

A saved checkpoint is resumable evidence. It does not grant a write lease, reactivate an identity, approve a repair, establish provider currentness at a later time, or override newer governance.

## Terminal reorientation statuses

- `OPERATIONAL_READY` — current governance, assignments, exact subjects, dependencies, and authority are sufficiently resolved to execute at least one safe assignment.
- `OPERATIONAL_BLOCKED` — one or more required current facts or authorities remain unavailable; list exact blockers.
- `TRAINING_SOURCE_STALE_FOR_CURRENT_ROLE` — permanent role semantics materially changed; a new training version is required.
