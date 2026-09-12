# Module 03: Owner / Warden / Write-Lease Practicum

## Learning objective

Demonstrate correct handling of multi-service mutation authority, lease lifecycle, verification boundaries, currentness, handoff, and stalled work.

## Exercise prompt

A single logical work item requires four external effects:

- a GitHub branch change;
- a database migration;
- a Google Drive artifact update;
- a Slack coordination notice.

The logical Owner is known. Resolve the current Service Warden for each service from current governance before answering.

Walk the work item through:

`design -> lease request -> Warden preflight -> grant -> write -> IMPLEMENTATION_COMPLETE -> Warden verification -> lease closure -> Owner result verification -> independent gates`

For each service specify:

- the separate lease required;
- the minimum target/scope/starting-state fields that must be bound;
- what the Warden verifies before grant;
- what the writer may and may not do;
- what counts as implementation complete;
- what the Warden independently verifies afterward;
- when the lease closes;
- what happens if Owner verification later fails.

Then resolve four adversarial variants:

1. the GitHub branch moves after lease grant but before write;
2. the database state changes in a way that may interact with the intended migration;
3. the original writer wants a helper to “just finish the last file” under the same lease;
4. the same work item has repeated lease attempts with no material verified progress.

## Pass criteria

PASS requires:

- one service's authority never substitutes for another's;
- starting state/currentness is part of the lease;
- no implicit sublease or holder rewrite is allowed;
- unexpected target movement triggers reconciliation/review rather than blind continuation;
- Warden verification and Owner verification are correctly ordered and distinguished;
- failed Owner verification requires new authority for new mutation;
- repeated no-progress cycles escalate to One, while the Warden does not reassign work.

## Critical fail conditions

- universal/cross-service lease;
- lease remains open indefinitely waiting for later Owner verification;
- a helper inherits write authority informally;
- repeated ambiguous writes are retried without readback.
