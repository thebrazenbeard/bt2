# Module 08 — Producer Evidence, Claim Ceilings, and Independent Verification

## Learning objective

Produce a complete repair-candidate receipt that is useful to independent verification without inflating producer evidence into acceptance.

## Scenario

Assume:
- a valid bounded lease existed;
- a two-path correction was implemented within scope;
- producer-local tests passed;
- provider readback succeeded;
- no forbidden effect was observed.

Do **not** assume independent verification or release acceptance has happened.

## Required output

Draft a structured `PRODUCER_COMPLETION_RECEIPT` containing:

- training/example marker so the record cannot be mistaken for a real operation;
- governing repair assignment/contract reference fields;
- lease identity and authority ceiling;
- predecessor/base identity;
- resulting candidate commit/tree or equivalent identity;
- exact changed pathset;
- per-path content/blob identity when available;
- tests actually executed;
- exact observed results;
- provider readback;
- forbidden/non-effects checked;
- unresolved unknowns;
- known limitations;
- claim ceiling;
- explicit next verifier/handoff functions.

Then explain, with one counterexample each, why these are different claims:

- `LOCAL_TESTS_PASS`
- `FIX_VERIFIED`
- `SECURITY_REVIEW_PASS` when applicable
- `RELEASE_ACCEPTED`

Finally, describe how you would report a partial failure where the code change read back correctly but one expected test was skipped.

## Pass criteria

PASS only if the receipt:
- binds exact predecessor and candidate identities;
- records exact path/content scope;
- distinguishes executed tests from planned/skipped tests;
- records provider readback separately from test result;
- preserves unknowns and limitations;
- does not self-award independent verification/security/release acceptance;
- gives a bounded producer claim.

Automatic fail:
- “all tests passed” when some were not executed;
- using a successful commit as proof the defect is fixed;
- omitting the exact changed pathset;
- collapsing producer and verifier roles.
