---
module_id: TWO-TRN-05
role_id: BT2-TWO
training_version: 1.0.0
title: Migration and concurrency engineering
objective: Design staged, compatible, availability-aware PostgreSQL/Supabase migrations with sound retry, lock, backfill, and rollback/forward-fix behavior.
---

## Learning exercise

A production PostgreSQL table contains tens of millions of rows. A feature requires:

- a new logically required field;
- a uniqueness guarantee;
- a large backfill;
- new application behavior;
- continuous service availability.

Design a staged migration and deployment sequence that permits a bounded old-app/new-schema and new-app/old-schema compatibility window.

For each stage give:

- preconditions;
- exact mutation class;
- expected PostgreSQL lock/concurrency concern;
- idempotency/retry behavior;
- observability/readback;
- stop condition;
- rollback or forward-fix choice;
- postconditions before the next stage.

Your design must address:

- why a single giant transaction is not automatically safest;
- DDL lock behavior and blocking risk;
- online/concurrent index creation, including failed/invalid intermediate results and transaction limitations;
- chunked/backfill progress keys and duplicate execution;
- concurrent application writers;
- constraint validation timing;
- transaction isolation and whole-transaction retry on serialization failure;
- deadlock/lock ordering;
- migration-history drift versus live-schema state;
- partial deployment and restart behavior.

Then give three migration plans that look attractive but are unsafe, and explain the failure mode.

## Pass criteria

PASS only if the trainee designs explicit compatibility stages, accounts for locking and long-running effects, makes backfill/retry idempotent, distinguishes migration metadata from actual schema state, and refuses the blanket rule that “one transaction makes every migration safer.”

Critical fail: proposes blocking/irreversible DDL on the hot path without evaluating locks/compatibility, or treats migration-history metadata repair as executing/rolling back SQL.
