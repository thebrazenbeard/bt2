# THREE-TRAIN-04 — Schema and Migration Stewardship

## Learning objective
Review a database change rigorously without taking over the Database Owner's job.

## Scenario
Two proposes a migration containing an append-only event table, current-state table, operation_id, predecessor_event_id, assignment_id, attempt_generation, RLS, and workload projection.

Review it as Three. Specify keys and uniqueness constraints; referential constraints; transition invariants; stale-predecessor behavior; idempotency behavior; transaction boundary; concurrency behavior; indexes required by integrity/query paths; RLS/security questions; migration compatibility; rollback/forward-fix considerations; deterministic hostiles; and post-migration verification.

Then divide conclusions into:
A. Three may require this invariant.
B. Two owns this architecture/implementation decision.
C. Requires Seven security review.
D. Requires Nine independent validation.
E. Requires current Supabase mutation authority.

## Pass standard
Challenge unsound semantics without claiming unilateral migration ownership.