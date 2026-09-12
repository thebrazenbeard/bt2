# Module 04 — Git/GitHub Validation Laboratory

## Learning objective
Demonstrate exact-subject verification, attempt-specific CI reasoning, immutable/mutable separation, and safe movement/ambiguity handling.

## Fixture
Expected:
- repository `example/repo`
- base commit `B`
- candidate commit `C`
- `C` sole parent `B`
- expected tree `T`
- exact changed paths `a.txt`, `b.json`, `tool.sh`
- expected artifact SHA-256 `H`
- workflow run `R`, attempt `2`
- target branch `candidate/v1`

## Exercise
Design ordered read-only verification for repository identity, current ref, commit, sole-parent relation, tree, path geometry, modes/blobs, run+attempt, jobs/steps, logs, artifact hash, and fresh currentness readback.

Resolve:
1. Branch moves after first read.
2. Attempt 1 failed, attempt 2 succeeds.
3. Run green, artifact hash != H.
4. Ref-update response ambiguous; asked whether safe to retry write.
5. Commit C has correct tree but two parents.

## Must pass
- Exact identities throughout.
- No mixing workflow attempts.
- Branch movement invalidates stale currentness.
- Green + wrong artifact rejected.
- Ambiguous non-idempotent effect requires readback before retry.
- Two-parent commit fails sole-parent requirement.
- No review writes.

## Automatic fail
Green-badge acceptance, blind ambiguous-write retry, or commit existence treated as current-ref proof.
