# Four — creative dreamer: bounded adversarial source review

Status: **SOURCE_REVIEW_AND_TEST_ONLY**. This change does not train or evaluate neural weights.

## Authority and proposition

- Patrick-designated personality: **Creative dreamer**, retained verbatim as the first USER trait in `coding_models/personality/cases/four.json`.
- Source: `coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md` (Four's former reconstruction/package duty is not its defining personality).
- Adversarial lens: [`thebrazenbeard/t-kal-in-ket` README](https://github.com/thebrazenbeard/t-kal-in-ket/blob/main/README.md), fetched as Git blob `e56dad338f79601e4a81abe7cb08af1b0da0065f`. Its three peer lenses and claim-freezing discipline inform this **internal** review. There was no executable T'Kal-in-ket hearing, independent quorum, separate model response, or imported unlicensed code.

**Frozen claim:** Four's imaginative alternatives should end in executable, bounded coding examples without giving incorrect behavior a fictional gloss.

## Falsifiers and repairs

1. **Purist Logic:** Training example `four-persona-train-003` implicitly equated two empty contact names (Jaccard `0/0` fallback to `1.0`). That contradicts its own requirement to *suggest* likely duplicates safely. **FAILS before repair.** An explicit empty-name guard now returns `0.0`, avoiding false positive duplicate suggestions.
2. **Pragmatism:** `four-persona-train-007` claimed unknown verbs produced an error, but its example parser accepted any verb and returned a tuple. **FAILS before repair.** New parser code checks the three allowed imaginative verbs, rejects empty or unknown commands, and remains non-executing.
3. **Bridge:** Both corrections retain Four's divergent creativity (three algorithm families; dream/echo/fold) but establish a concrete, testable convergence boundary. **SURVIVES as source design**; neural behavioral transfer is **UNKNOWN**.

No public DEV cases were changed or consulted as an optimization target. Case roster remains 8 TRAIN + 2 DEV. No new generated code was executed by tests; assertions check authored source contract text and corpus shape.

## Verification

- New `tests/test_identity_four_challenges.py`: 3 tests, 2 failed against previous case text, 3 passed after repair.
- `python -m unittest discover -s tests -q`: 125/125 passed on this isolated branch.
- `python tools/validate_personality_sft.py`: 13 dossiers / 130 cases valid.
- `git diff --check`: passed.

**Ceiling:** These changes improve source-example correctness only; the old GGUF for Four is untouched, and no claim is made about generalized imagination, coding retention, or model improvement.
