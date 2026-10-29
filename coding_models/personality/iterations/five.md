# Five — quantitative evidence challenge (2026-10-29)

Status: **source-level corpus repair; no neural model training or inference**.

## Frozen source and proposition

- BT2 baseline: draft PR #99 at `9036b904def1322a30fd73d21af2a85b59bba21c`.
- Original Five source: archived `thebrazenbeard/build-team-2.0` README at `950112a697550b689049da807f2d8176a507c38f`, which describes Five as precise, evidence-driven, quantitative.
- Challenge method: read-only `thebrazenbeard/t-kal-in-ket` at `b0af150c2405b519fd921bac33e5f9f1f35f92d7`. Its protocol requires separating evidence classes and refusing to call multiple reviewer labels independent executions without real invocation receipts. That protocol is a challenge reference, not installed multi-model review software; its repo has no selected software license.

## Adversarial dispositions

1. **REFINE — statistical pairing:** Existing Five train-006 requested a paired bootstrap despite only matching input-class composition. Class balance does not prove same-unit pairing. Revised the case to distinguish unpaired samples from matched observations, preserving 18/600 (3.0%) versus 9/600 (1.5%) and the 1.5 percentage-point, 50% relative decrease. A future confidence interval requires an explicit sampling design.
2. **REFINE — reviewer independence:** Existing Five train-008 appropriately rejected 9/10 training-adjacent successes as proof of generalization, but did not challenge a three-name review produced by one endpoint. Extended the synthetic case so the target response explicitly refuses that independent-review claim and requests provider/host/model/invocation/response bindings.

## Checks and limitations

- Added `tests/test_identity_five_challenges.py` with three deterministic source checks; two failed against the prior dossier and passed after these scoped changes.
- Preserved exactly 8 TRAIN and 2 DEV examples; this is **not** a new independent holdout.
- Changes remain synthetic supervised targets. They do not show Five's neural weights learned calibration or that any 13-model peer quorum has operated.
