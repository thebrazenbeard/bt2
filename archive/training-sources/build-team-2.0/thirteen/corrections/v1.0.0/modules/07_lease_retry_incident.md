# Module 07 — Lease, Retry, and Unexpected-Effect Drill

**Learning objective:** Make ambiguous or out-of-scope effects trigger controlled stop/readback/correction rather than improvisation.

## Scenario

You have a hypothetical current lease allowing only:

- repository `R`;
- branch `controller/x`;
- exactly one named file path;
- creation of exact blob/tree/sole-parent commit/non-force branch;
- no repair-ref movement;
- no device effect.

You accidentally invoke a file-contents mutation against the repair branch. The client then returns a network timeout before confirming success.

## Trainee task

Explain the correct next actions in order.

Your answer must cover:

1. why "the request probably failed" is not acceptable;
2. why blind retry is prohibited;
3. what provider readback is required;
4. how to determine whether the original lease remains valid;
5. when and why the mutation chain must stop;
6. how separate corrective authority is obtained;
7. how the correction is bounded;
8. what incident evidence must be preserved;
9. what claims may be made if provider readback itself is unavailable.

Then compare that with a **read-only** request receiving a genuine rate-limit response that clearly indicates exhaustion and a retry interval.

Finally solve this variant:

> The accidental write definitely succeeded, but it changed only metadata and not code. May you silently repair it under the original code lease?

## Pass criteria

PASS requires:

- Ambiguous non-idempotent mutation causes readback before any retry.
- No assumption that timeout means no effect.
- Out-of-scope effect invalidates or at least suspends the mutation chain pending authority/currentness reconciliation.
- Corrective work requires separately bounded authority; the original lease is not stretched retroactively.
- Deterministic failures are not laundered into fallback.
- Genuine transient read failures may use bounded retry according to current policy.
- Metadata effects are still effects and are not silently repaired under unrelated authority.
- If readback cannot establish state, result remains UNKNOWN/BLOCKED rather than guessed.
