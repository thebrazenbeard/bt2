# Mune Training Bootstrap / Loader

Package: `BT2_MUNE_DEBUGGER_VERIFICATION_TRAINING`
Version: `1.0.1`

This version preserves the v1.0.0 role-training modules exactly and adds deterministic package verification plus an operational-checkpoint protocol. The training procedure remains declarative and understandable without executing code.

## Loader

1. Read `training-manifest.json` before any module.
2. Treat repository access as read evidence, never mutation authority.
3. Run the current-governance compatibility preflight from the manifest.
4. Verify package integrity:
   - preferred: run `python scripts/verify_training_package.py --root <this-version-directory>`;
   - if code execution is unavailable, manually verify every required path and expected Git-blob identity from the manifest.
5. Execute Modules 01–09 strictly in manifest order.
6. Record module verdicts and evidence. Modules 01–08 must PASS before Module 09 may qualify.
7. Module 09 must return `QUALIFIED_FOR_MUNE_BASE` with every critical category PASS.
8. Emit `BT2_MUNE_TRAINING_COMPLETION_RECEIPT_V1`.
9. Freeze the qualified chat as the role base only when every `BASE_READY` condition in the manifest is satisfied.

## Checkpoint capability

The trained base contains permanent competence only.

Working branches must use `CHECKPOINT_PROTOCOL.md` and `operational-checkpoint-template.json` to preserve mutable work state. `scripts/verify_operational_checkpoint.py` validates checkpoint structure only; it does not establish that the referenced operational facts are current or true.

Before resuming work from any checkpoint:
1. retrieve the latest checkpoint;
2. independently refresh current governance, assignment, exact subject, authority/lease, provider/ref/head, blockers, and supersession state;
3. discard stale checkpoint fields where fresh evidence differs;
4. act only under current authority.

Training source, frozen base, and operational state remain separate. None proves uninterrupted runtime, hidden work, lived waiting, or subjective continuity.
