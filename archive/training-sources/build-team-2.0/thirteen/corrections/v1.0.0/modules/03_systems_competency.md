# Module 03 — Systems Competency for Authority Review

**Learning objective:** Demonstrate enough technical understanding of BT2's major systems to recognize authority and provenance failures without pretending to own those systems.

## Required technical concepts

### Git / GitHub

Understand the identity chain:

`blob → tree → commit → ref`

Blobs/trees/commits are content/history objects. A branch/ref is mutable currentness state. Creating content objects and moving/creating a ref are separate effects.

Understand that provider protection or environment approval can gate a platform action without becoming BT2 governance authority.

Understand ambiguous mutation: a client-side timeout can occur after a provider accepted the effect, so non-idempotent writes require provider readback before any retry.

### HTTP failure classification

Distinguish deterministic authorization/validation failures from genuine transient/rate-limit failures. Retry/fallback must not turn deterministic rejection into a more permissive route.

### Supabase / PostgreSQL

Understand:

- RLS is table-row authorization policy, not BT2 governance.
- `SECURITY INVOKER` executes with caller privileges.
- `SECURITY DEFINER` executes with function-owner privileges and therefore creates a privilege boundary that needs careful control.
- User-modifiable claims/metadata must not become trusted authorization merely because they are present.
- Database `EXECUTE` permission is capability, not necessarily application or governance authorization.

### Synology package/runtime

Understand that package start/stop/status scripts expose lifecycle outcomes and that an UNKNOWN/status-failure result cannot be promoted into a stronger semantic claim.

Repository source may define a candidate target policy, but target timing/errno/manager semantics require independent target qualification when the contract says they are target-bound.

### Google Drive

Understand the distinction among file locator/name, file identity, revision identity, checksum/content identity where available, and current head/revision.

## Trainee task

Explain each system above in your own words and give one authority/provenance bug that Thirteen should detect in each.

Then solve:

### Scenario A — Git currentness

An exact commit and tree were previously accepted. A branch name is supplied but has not been reread. What can be asserted now?

### Scenario B — Database privilege

A `SECURITY DEFINER` function can perform an otherwise protected change. A caller has function EXECUTE permission but no current BT2 mutation lease. What is authorized?

### Scenario C — Synology target semantics

A source constant sets a 15-second deadline and comments that it is "conservative." No controlled target evidence exists. What can be claimed?

### Scenario D — Drive custody

Two files have the same name and visible content but different revision histories. What evidence is needed before calling one the exact frozen source?

Finally, identify one system fact in your answer that could plausibly change over time. Explain how you would verify it from a current primary source rather than relying on memory.

## Pass criteria

PASS requires:

- Correct blob/tree/commit/ref distinction.
- Correct ambiguous-write readback rule.
- Correct capability-versus-governance distinction for database functions.
- Correct separation of source-defined candidate policy from target-qualified semantics.
- Correct separation of Drive path/name from exact revision/content identity.
- Recognition that current platform semantics should be verified from authoritative primary documentation when material.
- No claim of service ownership or mutation authority merely from technical understanding.
