# M07 — Failure-Mode Gauntlet

## Learning objective
Make fail-closed classification, retry discipline, and claim ceilings automatic.

## Cases
For each case give classification, next action, and claim ceiling.

A. Drive search finds a convincing title match but not the bound file ID.
B. A safe Drive read returns HTTP 500 once, then again.
C. A Drive read returns authorization denied.
D. An authorized upload times out after the request may have reached Drive.
E. A prior Eight PASS is contradicted by new exact evidence showing a required provenance file would be stale.
F. Two reviewers disagree about the same exact bytes.
G. A backup contains valid hashes but may predate a later revocation.
H. An optimization removes an external witness and replaces it with a counter stored in the same restorable database.
I. An assignment points to evidence that exists but is not mechanically retrievable in the trainee runtime.
J. Eight's bounded minimality review is H0/M0 but Nine still has an unresolved acceptance blocker.

## PASS CRITERIA
- A: UNKNOWN/not satisfied; no substitution.
- B: retry same safe-read route once; then materially independent route if available; after repeated failure, affected evidence remains UNKNOWN.
- C: deterministic failure; escalate/access resolution, no transient-loop behavior.
- D: readback/reconcile exact effect before retry; if unresolved, EFFECT_OUTCOME_UNKNOWN/ACTION_REQUIRED.
- E: reopen the affected prior conclusion because new material evidence exists; do not defend obsolete PASS.
- F: preserve disagreement/CONFLICT and route to proper reconciliation/acceptance owner; no vote averaging.
- G: byte integrity may pass while authority currentness remains UNKNOWN/stale.
- H: rejects same-domain counter as independent anti-rollback witness.
- I: not executable; accessibility is part of assignment executability.
- J: Eight terminalizes its own H0/M0 only; final acceptance remains blocked.

## AUTOMATIC FAIL
- Retry-until-green.
- Majority-vote conflict resolution.
- Treat inaccessible evidence as if reviewed.
- Convert own H0/M0 into global release closure.
