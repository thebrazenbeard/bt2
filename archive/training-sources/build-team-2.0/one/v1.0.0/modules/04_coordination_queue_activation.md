# Module 04: Coordination, Queue Stewardship, and Activation

## Learning objective

Demonstrate that the trainee can maintain an executable, correctly delivered queue without inventing work or pretending unactivated chats are running.

## Exercise prompt

A synthetic active roster has thirteen members. The task ledger contains:

- T1: completed successfully;
- T2: blocked on a future external artifact;
- T3: assigned to a retired identity in an old event;
- T4: fresh and executable, but posted only to a central coordination channel;
- T5: fresh, delivered to the correct home channel, but the assignee chat has not been user-activated;
- T6: marked active but its required evidence pointer is inaccessible to the assignee runtime;
- T7: a legitimate fresh task with all inputs present;
- T8: an attractive “research something useful” task that exists only to satisfy a staffing number.

Reconcile the queue.

For each task state whether it counts as executable capacity and why. Then produce:

1. the corrected queue;
2. the exact routing/delivery action required where appropriate;
3. the difference among `ACTIVE_EXECUTABLE`, `PENDING_ACTIVATION`, `BLOCKED`, `TERMINAL`, `SUPERSEDED`, and `ZERO_CAPACITY_INACCESSIBLE_INPUT`;
4. the conditions under which replenishment is justified;
5. the condition under which One should deliberately leave capacity empty rather than create make-work.

## Pass criteria

PASS requires:

- retired identities are not reactivated from history;
- central persistence is not treated as assignee delivery when home-channel delivery is required;
- assignment does not imply offscreen execution;
- inaccessible evidence means zero executable capacity;
- completed/blocked/future/superseded work is not counted as current execution;
- anti-makework behavior is explicit.

## Critical fail conditions

- inventing fake work to satisfy a quota;
- counting an unactivated chat as work in progress;
- counting an inaccessible task as executable;
- letting a stale assignment reactivate a retired identity.
