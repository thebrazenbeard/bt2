# BT2 Runtime Identity Review Closure — Two V1

Status: **ONE-0158 FINDINGS CLOSED FOR TESTED SCOPE / SOURCE+RUNTIME+BEHAVIOR BOUND**

Date: 2026-09-10
Coordination: `BT2-CANONICAL-PLATFORM-20260910`
Review answered: `one-0158`
Target: WoWSQL `bt2-479e4ad9`
Source branch: `work/two-canonical-platform-integrity-v1`
Source migration: `database/migrations/0013_runtime_identity_cross_binding_v1.sql`

## Findings addressed

### 1. Runtime restoration cross-agent binding

`runtime_sessions.restored_from_checkpoint_id` is no longer an independent UUID foreign key. Runtime restoration is bound by the composite identity:

`(restored_from_checkpoint_id, agent_key) -> operational_checkpoints(checkpoint_id, agent_key)`.

A runtime session therefore cannot represent agent Three while claiming restoration from agent Two's checkpoint.

### 2. Operation actor/session cross-binding

`operations.actor_runtime_session_id` and `operations.actor_agent_key` are now mechanically cross-bound through:

`(actor_runtime_session_id, actor_agent_key) -> runtime_sessions(runtime_session_id, agent_key)`.

If a runtime session is supplied, an explicit actor agent is required. `prepare_operation_v1` now includes `actor_runtime_session_id` in the operation request digest so replay cannot silently substitute a different runtime session while preserving the same operation identity.

### 3. Operation-event actor identity

`operation_events` now carries its own `actor_agent_key`. When an event supplies a runtime session, the event actor and runtime are composite-bound to the same logical agent. The new `append_operation_event_v2` accepts an explicit event actor, allowing a different agent to perform reconciliation without pretending to be the operation's original actor.

The V1 append API remains as a compatibility wrapper. It derives the event actor from the supplied runtime session when present, otherwise from the operation actor. A `RECONCILED` event through V2 requires an explicit actor.

### 4. Session-to-session continuity decision

No predecessor-session edge was added. This is deliberate. Runtime sessions are replaceable execution instances, not the durable identity chain. Continuity is represented by same-agent checkpoint restoration plus explicit handoff/provenance records. A predecessor-session edge would add graph structure without currently enforcing an independent recovery invariant.

## Behavioral qualification

A single rollback-contained hostile probe reached the deliberate marker `RUNTIME_IDENTITY_ROLLBACK_PASS` after verifying all of the following:

1. same-agent checkpoint restoration succeeds;
2. cross-agent checkpoint restoration is rejected by the composite FK;
3. an operation claiming agent Three with agent Two's runtime session is rejected;
4. replay of one operation ID with a different same-agent runtime session is rejected as `OPERATION_ID_REUSE_CONFLICT` because runtime provenance is digest-bound;
5. an operation event claiming agent Three while attaching agent Two's runtime session is rejected;
6. a different agent can append an event without claiming a mismatched runtime session;
7. an ambiguous operation can be explicitly reconciled by that different agent with a required receipt;
8. the event ledger retains that reconciler as the explicit event actor.

Post-probe readback confirmed zero qualification runtime-session rows, checkpoints, or operations remained.

Live constraint readback confirmed the installed composite/check invariants:

- `runtime_sessions_restore_same_agent_fkey`;
- `operations_actor_runtime_same_agent_fkey`;
- `operations_runtime_requires_actor_check`;
- `operation_events_actor_runtime_same_agent_fkey`;
- `operation_events_runtime_requires_actor_check`.

## GitHub Actions blank-rebuild gate

The repository now contains a PostgreSQL 16 blank-rebuild workflow and smoke test, but GitHub Actions has not executed the SQL. The original push and PR attempts failed before any runner step started. A controlled rerun produced a new failed job with the same zero-step/no-runner behavior.

This is classified as **EXTERNAL CI STARTUP BLOCKER / NOT DATABASE FAILURE**. The workflow remains in place. No acceptance credit is taken for blank-database rebuild until a runner actually executes the migration chain or an independent blank PostgreSQL target runs the same source.

## Authority boundary

This closure establishes only the tested identity/recovery invariants. It does not authorize merge, canonical cutover, training qualification manufacture, legacy retirement, producer authorization, Vera-Supabase mutation, or any other protected effect.
