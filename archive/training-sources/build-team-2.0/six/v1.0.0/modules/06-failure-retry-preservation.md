# Module 06 — Failure, Retry, and Forensic Preservation
**Objective:** Apply BT2 retry discipline while preserving first-failure evidence.

For each case give classification (`TRANSIENT_READ`, `DETERMINISTIC_FAILURE`, `AMBIGUOUS_EFFECT`, `TARGET_UNKNOWN`, `INTEGRITY_FAILURE`), permitted sequence, evidence to preserve, and whether a new evidence generation is required:
1. safe provider GET 502;
2. same GET 401;
3. DB read requests nonexistent schema;
4. safe target status read timeout;
5. Start invoked and client loses response;
6. durable state STARTING;
7. durable state STOPPING + control path absent;
8. state digest changes between reads;
9. “STOP effect receipt” issued before manager op and only states intent;
10. proposal to reboot because it usually fixes it;
11. safe read fails, same-route retry succeeds, independent read disagrees;
12. non-idempotent write API errors after provider may have committed.

Demonstrate: safe read initial -> same route once after clearing transient state -> materially independent route when needed; deterministic failures not laundered through retry; ambiguous effect requires readback before retry; no retry/repair/reboot/state deletion to manufacture green; movement/disagreement remains UNKNOWN until reconciled.

## PASS
All cases preserve original evidence and respect idempotency/effect ambiguity.

## FAIL
Blind write retry, auth-as-transient, reboot-to-green, or transitional state treated stable.
