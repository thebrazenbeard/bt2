# Nine v1.0.0 Training-Source Preservation Evidence V1

Status: CANDIDATE_BYTE_PRESERVATION / INDEPENDENT_VERIFICATION_REQUIRED / QUALIFICATION_UNPROVEN / INSTALLATION_UNPROVEN

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

## Selected source

- source repository: `thebrazenbeard/build-team-2.0`
- authoritative discovery registry: `main:training/ROLE_TRAINING_REGISTRY.json`
- source ref: `training/nine-v1.0.0`
- immutable source commit: `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`
- source commit tree: `faf7501b8f93aeca2346b3848131d7386f6c86a5`
- source package path: `training/roles/nine/1.0.0`
- source package tree: `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`
- source manifest path: `training/roles/nine/1.0.0/training_manifest.json`
- source manifest Git blob: `21f81ed20dac38a58c3082c1463a556e7ebf4d53`
- source manifest SHA-256 recorded by the authoritative main registry: `a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b`
- source-set digest SHA-256: `bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7`

## Fresh source selection / supersession check

The current `build-team-2.0` branch inventory was refreshed before selection. Plausible Nine surfaces included `main`, the operational `nine` branch, `training/nine-v1.0.0`, and `training/nine-checkpoint-bootstrap-v1`.

`training/nine-checkpoint-bootstrap-v1@aee251f9e42e951e886fac3643456ab68e598382` is later checkpoint/startup/registry support, not a new training-package version. Its `training/roles/nine/1.0.0` subtree is exactly the same Git tree `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`. Its role registry explicitly keeps Nine at `current_training_version: 1.0.0`, binds the immutable training source to `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`, and separately identifies fresh-chat/checkpoint protocol paths. The operational `nine` branch does not expose a newer `training/roles/nine` package.

Therefore the checkpoint/bootstrap material is intentionally **not** copied into the immutable Nine v1.0.0 package. It remains separate continuity/support provenance.

## Authoritative-registry correction and process incident

After the first candidate commit, a fresh One coordination read exposed `one-0165`, which correctly states that `build-team-2.0@main:training/ROLE_TRAINING_REGISTRY.json` is the authoritative discovery registry and that branch-name inference must not outrank it. Although Nine's selected source happened to match the corrected authoritative Nine binding exactly, Nine had not read the **main** registry entry immediately before the first write. That is a process/currentness defect in the builder sequence and is preserved here rather than erased by the fact that the bytes were correct.

Nine then independently read the authoritative main registry. Its current Nine tuple is exactly:

- current version `1.0.0`
- package `training/roles/nine/1.0.0`
- manifest `training/roles/nine/1.0.0/training_manifest.json`
- immutable source commit `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`
- manifest SHA-256 `a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b`
- source-set digest `bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7`

Nine also re-read the exact manifest at the immutable commit. Its `file_inventory` contains 12 package files with explicit SHA-256 and byte-count bindings. Applying the authoritative registry rule — SHA-256 over lexicographically sorted inventory entries encoded as `path + NUL + sha256 + NUL + decimal byte_count + LF` — independently recomputes:

`bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7`

which exactly matches the current main registry source-set digest. No source-selection or byte change was required after this correction.

The same correction invalidates Nine's earlier `nine-v2-0044` claim that Four v1.1.0 should outrank the older recovery record. The current main registry explicitly binds Four to v1.0.1; that earlier Four source-selection warning is superseded and must not be used for execution.

## Candidate destination

- target repository: `thebrazenbeard/bt2`
- base subject: `work/source-preservation-v1@692b72e423077ad47fc2f8c3f104742ce7216c5f`
- builder branch: `work/preserve-nine-v1`
- destination package path: `archive/training-sources/build-team-2.0/nine/v1.0.0`

Every package file was recreated as a target-repository Git blob from the exact source bytes. Each recreated Git blob SHA matched its source Git blob SHA before the candidate tree was assembled. The complete target package subtree reads back as Git tree `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`, exactly equal to the immutable source package tree. The independent verifier must still re-fetch and verify this candidate; this builder record is not independent acceptance.

## Claim ceiling

This work preserves an exact reusable training-source candidate. It does not establish historical or current Nine qualification, BASE_READY status, compatibility with current governance, runtime/session installation, activation, current assignment, current authority, or any production/deployment effect. No qualification/install/activation record is created by this branch.
