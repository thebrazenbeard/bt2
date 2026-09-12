# Module 06 — Adversarial Regression and Historical-Pattern Lab

**Learning objective:** Recognize recurring false-authority families while treating old examples as regression patterns, not automatically current defects.

## Historical-pattern exercises

Treat every case below as a **historical regression pattern**. Do not assume it is present in a current candidate without fresh evidence.

1. A deterministic authentication/authorization response is classified as transient and reaches a fallback path.
2. An exact quote supports only part of a capability description, but unrelated extra scope is admitted.
3. Missing control-socket state is treated as proof that an authorized STOP completed.
4. Lifecycle code emits its own "authorized/replay-safe" receipt before the manager effect.
5. Reading a status endpoint updates `last_seen`, then that timestamp is cited as independent evidence of preexisting freshness.
6. A registered runtime can call a succession function, and callable capability is treated as succession authority.
7. An old role/assignment row is rediscovered and counted as active capacity after the identity or assignment was retired.
8. An immutable content root is used as though it proves current mutable provider state.

## Trainee task

For each pattern:

1. Name the underlying false-authority family in general terms.
2. Build a concrete hostile/counterexample.
3. State the minimum independent evidence or correction needed.
4. Explain how you would determine whether a present occurrence is:
   - a new finding;
   - an existing-family reproduction;
   - historical only;
   - unresolved because evidence is unavailable.

Then choose any two patterns and combine them into a single multi-stage failure. Explain why the combined case does or does not create a new root finding.

Finally, invent one new false-authority family not directly listed above.

## Pass criteria

PASS requires:

- Does not treat historical examples as current findings without current evidence.
- Correctly identifies self-attestation, observation interference, retry laundering, scope piggyback, currentness substitution, stale reactivation, and capability/authority confusion where applicable.
- Distinguishes new root cause from new example of an existing root.
- Gives smallest sufficient correction rather than vague "add more checks."
- Produces a coherent combined hostile and a novel family.
