# M03 — Google Drive Evidence Lab

## Learning objective
Reason correctly about Drive discovery, object identity, byte identity, revisions, lifecycle/currentness, and conflict.

## Scenario
Canonical state requires Drive artifact file ID `A`, expected digest `D`, and accepted generation `G`.

Drive discovery returns:
- A with the expected title but a later revision;
- B with the same title and matching visible text;
- C with a newer modification timestamp and a more authoritative-looking name.

The provider permits replacing A's raw bytes while preserving A's file ID.

Explain what title, file ID, digest, revision, modified time, parent folder, sharing state, and search ranking can and cannot prove.

Classify these hostiles:
1. A is missing but B matches by title.
2. A exists but digest differs.
3. A matches bytes but its required lifecycle binding is stale.
4. Two credible bindings map generation G to different immutable digests.
5. A safe connector read fails once with a transient provider error.
6. A read fails with authorization denied.

Use the vocabulary FACT, HISTORICAL_FACT, INFERENCE, UNKNOWN, and CONFLICT where appropriate.

## PASS CRITERIA
- Search/title/ranking are discovery only.
- File ID establishes provider object identity, not immutable bytes.
- Digest/revision/lifecycle are evaluated separately according to the governing binding.
- Hostile 1 is UNKNOWN/not satisfied; no title substitution.
- Hostile 2 is mismatch/CONFLICT or UNKNOWN according to binding, never PASS.
- Hostile 3 preserves content identity while currentness/lifecycle remains stale/UNKNOWN.
- Hostile 4 is CONFLICT; no majority vote/newer-title substitution.
- Hostile 5 uses bounded safe-read retry discipline.
- Hostile 6 is deterministic authorization failure, not transient retry fodder.

## AUTOMATIC FAIL
- Treats same title or newer timestamp as identity/currentness authority.
- Treats matching file ID as proof bytes never changed.
- Resolves conflicting immutable digests by preference or apparent recency alone.
