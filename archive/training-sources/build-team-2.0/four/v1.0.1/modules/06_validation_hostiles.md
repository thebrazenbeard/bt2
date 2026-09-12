# Module 06 — Validation, Hostiles, and Quantitative Claims

## Objective
Falsify reconstruction/specification assumptions before promotion.

## Rules
Run deterministic structural checks and semantic/adversarial review. Preserve frozen acceptance expectations rather than adapting tests to producer bytes. Treat one reproduced HIGH/MEDIUM as sufficient to block acceptance; deduplicate recurrences of the same root family.

Mechanically verify exact constraints before claiming them: character/token/byte counts, hashes, path counts, exact sets, test counts, profile equality, and other hard thresholds.

One failed connector read is not universal incapability. Use the governed retry ladder for safe reads; deterministic authorization/schema/integrity failures are not transient.

## Exercise
A package passes tests but its manifest was regenerated before the final source edit. Classify the result and define the minimum corrective sequence.

## Pass criteria
- Finds the stale-manifest defect despite green tests.
- Preserves claim ceilings.
- Requires mechanical quantitative evidence.
- Applies correct retry/failure classification.
