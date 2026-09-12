# Hephaestus Training Checkpoint Support v1

This directory contains **optional deterministic support tooling** for the versioned Hephaestus permanent-role training source.

It does not change the meaning of any already-versioned training package. The normative training lifecycle remains the package's `TRAINING_MANIFEST.yaml` and `BOOTSTRAP.md`.

## Purpose

- verify the exact file set and checksums of a retrieved training package;
- create resumable training-execution checkpoints;
- preserve failed module attempts instead of rewriting them away;
- enforce ordered module progress structurally;
- bind a training run to one exact package version and immutable repository source;
- verify that a checkpoint claiming `BASE_READY` is structurally consistent with recorded module results.

## Boundaries

A training checkpoint is derivative evidence about **training execution**. It is not:

- versioned training source;
- the frozen base itself;
- project operational state;
- evidence of current provider state;
- evidence of current assignment or lease authority;
- evidence of uninterrupted runtime or subjective continuity.

Running these scripts does not make ChatGPT execute repository code automatically and grants no GitHub, provider, database, device, deployment, release, or other mutation authority.

## Files

- `scripts/verify_package.py`: standard-library exact package verifier.
- `scripts/training_checkpoint.py`: standard-library checkpoint state utility.
- `tests/test_checkpoint_support.py`: deterministic regression tests.
- `SUPPORT_MANIFEST.json`: version and scope metadata.
- `CHECKSUMS.sha256`: exact support-file hashes, excluding itself.

## Suggested use

1. Retrieve an exact immutable training package source.
2. Run or manually reproduce `verify_package.py` semantics against that package.
3. Initialize a checkpoint with `training_checkpoint.py init`, binding repository/ref/immutable commit or tag/package version/manifest SHA-256/checksum-file SHA-256.
4. After every module attempt, call `record` with the evaluator's `PASS` or `FAIL`. The script does not decide semantic competence.
5. Preserve failures. A failure leaves the same module as next required.
6. Resume only from a checkpoint whose exact source binding has been independently reverified.
7. Finalize only after all ten module results are `PASS`, no unresolved training dependency remains, and the actual final qualification has satisfied the package's rubric.
8. Hash the final checkpoint and bind it into the BASE_READY receipt.

If arbitrary code execution is unavailable, follow the same state transitions declaratively. The scripts are conveniences, not magic scrolls.
