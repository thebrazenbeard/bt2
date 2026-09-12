# THREE-TRAIN-02 — State Machine and Data Model Engineering

## Learning objective
Build a machine-checkable state model and attack it.

## Exercise
Model an assignment lifecycle containing ASSIGNED, ACTIVE, BLOCKED, COMPLETED, CANCELLED. Reactivation is permitted only through an explicit new attempt.

Define assignment identity, attempt generation, current-state representation, legal edges, terminal states, predecessor identity, transition operation ID, idempotent replay, divergent operation-ID conflict, concurrency rule, workload projection rule, and UNKNOWN behavior.

Adjudicate:
1. ACTIVE -> COMPLETED -> stale ACK.
2. ACTIVE -> concurrent COMPLETED and BLOCKED from same predecessor.
3. COMPLETED -> ordinary amendment claiming ACTIVE.
4. COMPLETED -> explicit REACTIVATE generation+1.
5. Exact operation replay.
6. Same operation ID with changed target state.
7. Workload snapshot lists a terminal assignment.
8. Recognized event type with unknown lifecycle meaning.

## Constraint
Do not use highest event ID or newest timestamp as transition authority.

## Pass standard
Mechanical rejection/currentness rules are required; "use judgment" is insufficient.