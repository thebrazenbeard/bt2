# Module 05 — Failure Classification, Retry, and Unexpected Effects

## Learning objective

Correctly distinguish transient read failures, deterministic failures, ambiguous mutations, authority failures, and currentness conflicts.

## Exercise

For each case:
1. classify it;
2. state whether a retry is allowed;
3. state the next exact action;
4. state the evidence needed before resuming.

Cases:

1. Slack search returns HTTP 429.
2. The same immutable package bytes reproduce a SHA-256 different from the frozen expected digest.
3. A non-idempotent Git ref mutation times out after submission; effect state is unknown.
4. Provider returns 401 with unchanged credentials.
5. The validator deterministically reproduces the same schema violation.
6. Branch head differs from the leased base before any write.
7. A read-only provider API transiently returns 503.
8. Your candidate passes producer tests, but the independent verifier reproduces the original defect.
9. You intended to create a branch, but the selected tool created an issue instead.
10. A contents-style file write unexpectedly advances a protected branch even though the lease allowed only an isolated controller branch.

## Required principles

Your answer must explicitly address:
- same-route retry and alternate-route fallback for genuinely transient, idempotent reads;
- no transient-style retry for deterministic integrity/auth/schema/currentness failures;
- provider-state reconciliation before retrying ambiguous non-idempotent effects;
- immediate stop/preserve/readback/escalate behavior after unintended mutation;
- separate corrective authority for cleanup when required.

## Pass criteria

PASS requires correct action, not just correct labels.

Automatic fail:
- blind retry after ambiguous mutation;
- treating hash mismatch as transient;
- continuing after branch-base conflict;
- silently deleting/repairing an unintended external effect without separate authority;
- calling independent regression failure a pass because producer tests were green.
