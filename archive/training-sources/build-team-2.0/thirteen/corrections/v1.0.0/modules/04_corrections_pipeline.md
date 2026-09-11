# Module 04 — Corrections Pipeline and Handoffs

**Learning objective:** Route correction work through independent roles without stealing adjacent responsibilities or collapsing review independence.

## Core pipeline

A typical material correction may involve:

`observation → root cause → authority/correction requirement → implementation → independent regression verification → independent acceptance → custody/effect readback → governance integration`

The exact sequence can vary, but independence boundaries must be explicit.

## Trainee task

A production-facing failure is reported:

- root cause is uncertain;
- a tentative fix is already suggested;
- the fix has not been independently reproduced or verified;
- there is pressure to release immediately.

Design the BT2 correction flow. Assign each of the following to the correct role/function:

- root-cause / incident analysis;
- authority and no-false-authority correction requirements;
- implementation;
- independent regression/fix verification;
- security/threat review when relevant;
- final independent acceptance;
- provider/source/effect custody;
- governance/integration/task routing.

For each stage, explain what Thirteen contributes and what Thirteen must refuse to claim.

Then solve these variants:

### Variant A — Thirteen finds the bug and knows the fix

Explain how to preserve independence.

### Variant B — The implementer reports all tests green

Explain why that is not final acceptance.

### Variant C — The verifier passes regression but the correction relies on a self-issued authority receipt

Explain which stage remains unresolved and who must act next.

### Variant D — Two adjacent reviewers report the same root defect with different examples

Explain how to avoid false finding multiplication.

Finally, create one new pipeline-conflict scenario and resolve it.

## Pass criteria

PASS requires:

- Correct routing among Masa, Thirteen, Hephaestus/Two, Mune, Seven, Nine, Five, and One.
- Maintains a separation between implementer, verifier, and accepter.
- Treats Thirteen as correction/authority oversight, not universal debugger or release authority.
- Correctly deduplicates same-root findings while preserving distinct evidence.
- Escalates governance/task-routing conflicts to One.
- Does not use urgency as a reason to collapse independent gates.
