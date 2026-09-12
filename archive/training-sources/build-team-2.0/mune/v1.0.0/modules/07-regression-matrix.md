# Module 07 — Root-Invariant Regression Matrix

## Learning objective
Verify invariants, not only repaired examples.

## Scenario
Old bug: `target_matches_expected=true` allowed an attacker-selected target.
Repair: target is compared to expected-target evidence.

## Exercise
Build hostiles for:
1. observed and expected target co-mutated together;
2. self-attested ALLOW authority;
3. stale provider binding;
4. ref/registry alias collision;
5. wrong environment plus matching expected-environment lie;
6. exact replay;
7. changed-semantics replay;
8. concurrent attempts;
9. incomplete graph before privacy projection;
10. valid manual route;
11. valid tool route requiring confinement/capability evidence;
12. a malformed case that is merely another instance of the existing root cause.

Explain:
- same bug family versus new root cause;
- what independent trust root is required;
- why matching lies on both sides must fail.

## PASS
- co-mutation/self-attestation is explicitly tested;
- expected identities require independent provenance;
- aliasing is attacked;
- positive controls remain valid;
- currentness/privacy and replay semantics are covered;
- malformed instances are deduped when the invariant is already represented.

## Fatal FAIL
Only toggles the old boolean or lets expected evidence self-authorize.
