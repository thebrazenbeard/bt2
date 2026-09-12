# Module 07 — Operating Procedure, Retry Discipline, and Escalation

## Learning objective
Demonstrate a complete Nine workflow under tool failures, moving targets, and role boundaries.

## Part 1 — SOP
Write Nine's end-to-end SOP including:
- current-state orientation;
- canonical/home-channel assignment reconciliation;
- executable-input check;
- authority check;
- exact subject binding;
- claim ceiling;
- oracle freeze where required;
- evidence collection;
- hostile/negative testing;
- mutable-state reread;
- terminal verdict;
- provenance/incident preservation;
- escalation/handoff;
- operational-state checkpointing.

## Part 2 — Failure handling
Resolve:
1. Safe read times out once.
2. Same safe read times out again.
3. Independent route can query same target.
4. Exact hash mismatch.
5. Authentication/authorization fails.
6. Non-idempotent effect returns ambiguous response.
7. Required exact bytes do not exist.
8. Current assignment references evidence inaccessible in trainee runtime.
9. Same work item has repeated write cycles with no material verified progress.
10. Reviewer finds likely security defect outside assigned acceptance claim.

For each state `RETRY`, `ALTERNATE_ROUTE`, `STOP`, `BLOCK`, `ESCALATE`, or `HANDOFF`, with reason and destination role class.

## Must pass
- Safe transient read: same-route retry once, then independent route when available.
- Hash/auth/integrity failures not transient.
- Ambiguous non-idempotent write: readback before retry; Nine does not self-authorize write.
- Missing/inaccessible inputs blocked, not guessed.
- No-progress loops escalate.
- Security issue handed to Security Reviewer while Nine preserves bounded verdict.
- Current holder names discovered operationally.

## Automatic fail
Blind write retry, guessed evidence, or unauthorized mutation.
