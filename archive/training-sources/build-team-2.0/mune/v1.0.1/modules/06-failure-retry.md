# Module 06 — Failure Classification and Retry

## Learning objective
Correctly handle transient failure, deterministic failure, conflict, and ambiguous effect.

## Cases
Classify each and state retry procedure:
A. Read-only SELECT timeout.
B. HTTP 401.
C. Permission denied.
D. Schema-validation error.
E. Checksum mismatch.
F. Ambiguous timeout after INSERT.
G. First GitHub read returns 503.
H. Alternate route returns a conflicting hash for the same semantic target.
I. Exact immutable locator returns explicit NOT_FOUND.
J. Retry returns a different branch head because the branch genuinely moved.

Allowed outcome classes:
`CONFIRMED`, `DEGRADED`, `DETERMINISTIC_FAILURE`, `CONFLICT`, `UNKNOWN`, `BLOCKED`.

## PASS
- transient reads use initial → same-route retry → materially independent route where available;
- authentication/authorization/schema/integrity/hash failures are not retried as transient;
- ambiguous writes require commit-state/operation-ID verification before retry;
- conflicting hashes/currentness are preserved rather than averaged;
- real branch movement is distinguished from transport failure;
- exact NOT_FOUND may be deterministic when target identity and route semantics justify it.

## Fatal FAIL
- blind INSERT retry;
- single transient read becomes BLOCKED;
- authorization failure is called transient.
