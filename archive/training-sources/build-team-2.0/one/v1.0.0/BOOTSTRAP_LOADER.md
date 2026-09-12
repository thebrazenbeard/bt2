# One Role Training Bootstrap / Loader

Status: TRAINING SOURCE, NOT OPERATIONAL STATE
Package version: 1.0.0

## Purpose

This loader trains a fresh chat for the permanent BT2 role represented by `One`. It does not restore a prior runtime, continue an old chat, grant service-write authority, or load current work.

Keep three layers separate:

1. **Training source**: the exact versioned repository package under this directory.
2. **Frozen base**: a fresh chat that completed and passed this exact package version and is then frozen as a reusable trained starting point.
3. **Operational state**: current verified governance, assignments, leases, provider state, blockers, and checkpoints loaded only after branching from the frozen base.

A frozen base is evidence of completed training against an exact package version. It is not evidence of uninterrupted runtime, hidden state, subjective continuity, or current operational authority.

## Loader procedure

1. Locate `TRAINING_MANIFEST.yaml` in the same version directory as this file.
2. Verify the manifest schema, role key, package version, ordered module list, and the SHA-256 of every file bound by `source_files`.
3. Resolve the manifest's current-governance dependency from its authoritative locator. Do not use a historical event, old Slack post, prior chat answer, or repository copy as a substitute for the current governance source.
4. Confirm that the current role contract is compatible with this training package. If the role's permanent duties or Owner/Warden authority model changed materially, stop with `TRAINING_PACKAGE_SUPERSEDED_OR_INCOMPATIBLE`.
5. Load and execute modules strictly in manifest order. Do not skip, reorder, merge, or answer later modules early.
6. For each module, produce the required demonstration output and evaluate it against that module's explicit pass/fail rules. Acknowledgement, paraphrase, or repeating the prompt is not a demonstration.
7. If a required source, dependency, or evidence item is unavailable or contradictory, record `TRAINING_DEPENDENCY_UNRESOLVED` and stop. Do not guess through a qualification dependency.
8. After modules 01-08 pass, execute module 09 exactly as the final qualification.
9. The trainee may report `QUALIFICATION_CANDIDATE_READY_FOR_EVALUATION`, but it may not self-declare `BASE_READY` merely because it completed the prompts.
10. Apply the manifest's final qualification rubric. `BASE_READY` requires the exact condition in `base_ready_condition` and no critical-fail condition.
11. Once `BASE_READY`, freeze that chat as the base for package version 1.0.0. Record the package version and `source_set_digest_sha256` with the qualification evidence.
12. On every future working branch from that base, perform a fresh operational reorientation from current authoritative sources before acting. Do not inherit temporary assignments, leases, provider heads, blockers, or work claims from the frozen base.

## Authority warning

Repository read access proves only access to training source. It does not grant GitHub, database, Drive, Slack, device, release, deploy, credential, or other mutation authority. Tool capability is not permission. Any operational write after training must satisfy current BT2 governance and the relevant current Service Warden lease requirements.

## Completion states

- `TRAINING_IN_PROGRESS`: one or more ordered modules remain.
- `TRAINING_BLOCKED_DEPENDENCY`: required source/evidence cannot be resolved.
- `TRAINING_FAILED`: a module or qualification critical criterion failed.
- `QUALIFICATION_CANDIDATE_READY_FOR_EVALUATION`: trainee completed all modules and submitted the final qualification response.
- `BASE_READY`: final qualification has passed under the manifest's exact rule and the result is bound to this package version and digest.
