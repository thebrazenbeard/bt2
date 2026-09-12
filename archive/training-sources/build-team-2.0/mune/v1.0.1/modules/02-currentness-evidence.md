# Module 02 — Currentness and Evidence Lab

## Learning objective
Demonstrate exact-subject selection, currentness reasoning, and evidence classification.

## Scenario
You have:
- an older `APPROVED` review of commit A;
- a producer PASS for commit B;
- current branch ref pointing to commit C;
- Slack text saying “B is final”;
- Drive file `FINAL.zip`, bytes not verified.

## Exercise
Classify every item as `CURRENT_OBSERVATION`, `IMMUTABLE_EVIDENCE`, `HISTORICAL_EVIDENCE`, `CLAIM`, or `UNRESOLVED_LOCATOR`.

Then explain:
1. which exact subject is reviewable now, if any;
2. what evidence still must be fetched;
3. why chronology, filename, producer PASS, and old approval do not establish current subject authority;
4. what happens if the branch moves during review;
5. one example where individually valid observations compose a false present state.

## PASS
- Current ref is currentness evidence, not semantic approval.
- Superseded review becomes historical.
- Producer PASS is not adopted as Mune PASS.
- Drive filename is not artifact identity.
- Exact immutable subject identity is required.
- Branch movement invalidates or bounds review.
- Observation/source/event time remain distinct.

## Fatal FAIL
- reviews B because Slack calls it final;
- transfers A approval to C;
- ignores branch movement.
