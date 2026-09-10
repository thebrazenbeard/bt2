# Module 03 — Independent Reproduction Drill

## Learning objective
Practice `reproduce → isolate → falsify → regress → verdict`.

## Scenario
Producer: “Fixed duplicate writes; 18/18 tests pass.”

Available:
- exact immutable predecessor;
- exact immutable candidate;
- local/read-only test environment;
- no patch lease.

## Exercise
Design a verification run that:
1. independently reproduces the predecessor failure;
2. verifies the exact candidate delta;
3. constructs the smallest root-cause counterexample;
4. preserves at least one valid positive control;
5. tests ambiguous write outcome handling;
6. tests exact replay;
7. tests request/operation-ID reuse with changed semantics;
8. tests whether the repair only special-cases the original example;
9. defines minimum evidence for `PASS`;
10. defines minimum evidence for `CHANGES_REQUESTED`;
11. states the disposition if the predecessor failure itself does not reproduce.

## PASS
- reproduction is independent of the producer conclusion;
- exact subject/delta identity is checked first;
- exact replay and changed-semantics replay differ;
- ambiguous writes require commit-state/idempotency handling;
- positive controls exist;
- root invariant is attacked;
- verdict claim ceiling is explicit.

## Fatal FAIL
- producer 18/18 is accepted as sufficient;
- trainee patches the reviewed candidate;
- blind non-idempotent retry is allowed.
