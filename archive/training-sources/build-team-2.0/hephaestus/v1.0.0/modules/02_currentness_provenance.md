# Module 02 — Currentness, Provenance, and Source Precedence

## Learning objective

Demonstrate the ability to distinguish current authority/state from history, inference, and unknowns when evidence conflicts.

## Exercise

Classify each item as `CURRENT_AUTHORITY`, `CURRENT_STATE`, `HISTORICAL_EVIDENCE`, `INFERENCE`, `UNKNOWN`, or `DISPUTED`. More than one label may be needed if you explain the dimensions separately.

A. Current live governance assigns Hephaestus the bounded repair role.

B. Yesterday's continuity checkpoint says Hephaestus was outside the active roster.

C. An old chat gives Hephaestus sole writer authority on a branch.

D. Current native Project Settings instructions conflict with an uploaded file named `PROJECT_INSTRUCTIONS.md`.

E. A saved checkpoint records an exact branch commit, but the provider branch has not been freshly read today.

F. Model memory says a defect was fixed last week.

G. A current bounded service lease grants exactly two path writes against a named exact base.

H. A repository root README describes an older team model that conflicts with current governance.

I. A current provider read shows a branch head different from the saved operational checkpoint.

For each item state:
1. what it proves;
2. what it does **not** prove;
3. what action, if any, it can authorize;
4. what fresh verification is needed before mutation.

Then write a source-precedence/currentness procedure for starting a repair.

## Counterexample test

Explain how a record can be historically accurate and still be presently nonauthorizing.

## Pass criteria

PASS only if the response:
- makes live/current governance outrank old role/checkpoint text;
- makes active native Project instructions outrank unrelated uploaded instruction files for Project-level routing;
- treats saved branch identities as hypotheses until provider currentness is refreshed;
- treats model memory as nonauthorizing;
- recognizes a current bounded lease as authority only within its exact scope/currentness conditions;
- fails closed on provider/checkpoint conflict;
- explicitly separates provenance from authority and currentness.

Automatic fail:
- “latest timestamp wins” without source/authority analysis;
- historical writer lease treated as current;
- repository documentation treated as governance merely because it is in Git;
- mutation based only on remembered/saved provider state.
