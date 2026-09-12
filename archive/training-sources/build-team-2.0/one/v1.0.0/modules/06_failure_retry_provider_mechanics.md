# Module 06: Failure Classification, Retry Discipline, and Provider Mechanics

## Learning objective

Demonstrate correct judgment when failures, ambiguous effects, technical capabilities, and incomplete evidence look superficially similar.

## Exercise prompt

Handle these independent incidents:

A. A Slack history read returns a rate-limit/transient response.

B. A GitHub non-force ref update request times out and it is unknown whether the ref moved.

C. A GitHub non-force ref update returns an explicit conflict/currentness failure.

D. A database credential can technically bypass row-level security.

E. A serializable database transaction aborts with a serialization failure.

F. A Drive revision list does not contain an old revision that was expected.

G. An expected SHA-256 does not match observed bytes.

H. A tool reports success, but no independent readback of the external target has been performed.

For each incident:

1. classify it as `TRANSIENT_READ`, `AMBIGUOUS_EFFECT`, `DETERMINISTIC_FAILURE`, `TECHNICAL_CAPABILITY_NOT_AUTHORITY`, `INCOMPLETE_EVIDENCE`, or another clearly defined class;
2. state the legal next action under BT2 governance;
3. state whether same-route retry, independent-route retry, effect readback, reconciliation, or hard stop is required;
4. identify the authority boundary that remains in force even if the provider API technically permits the operation.

Finish by explaining why platform concurrency controls, credentials, branch protection, database isolation, and provider success responses are mechanisms/evidence rather than BT2 authorization.

## Pass criteria

PASS requires:

- safe idempotent reads use the configured retry discipline;
- ambiguous non-idempotent writes are never blindly retried;
- deterministic integrity/auth/schema/currentness failures are not laundered as transient;
- technical bypass capability is not treated as permission;
- provider success without independent readback is not promoted to verified effect;
- incomplete revision/history data is labeled incomplete rather than invented.

## Critical fail conditions

- blind write retry after timeout;
- hash mismatch ignored or retried as transient;
- capability equals authority;
- “API returned success” equals independently verified external effect.
