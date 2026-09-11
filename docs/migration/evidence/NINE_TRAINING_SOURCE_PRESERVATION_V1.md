# Nine v1.0.0 Training-Source Preservation Evidence V1

Status: CANDIDATE_BYTE_PRESERVATION / INDEPENDENT_VERIFICATION_REQUIRED / QUALIFICATION_UNPROVEN / INSTALLATION_UNPROVEN

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

## Selected source

- source repository: `thebrazenbeard/build-team-2.0`
- source ref: `training/nine-v1.0.0`
- immutable source commit: `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`
- source commit tree: `faf7501b8f93aeca2346b3848131d7386f6c86a5`
- source package path: `training/roles/nine/1.0.0`
- source package tree: `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`
- source manifest path: `training/roles/nine/1.0.0/training_manifest.json`
- source manifest Git blob: `21f81ed20dac38a58c3082c1463a556e7ebf4d53`
- source manifest SHA-256 recorded by the later authoritative registry: `a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b`
- source-set digest SHA-256: `bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7`

## Fresh source selection / supersession check

The current `build-team-2.0` branch inventory was refreshed before selection. Plausible Nine surfaces included `main`, the operational `nine` branch, `training/nine-v1.0.0`, and `training/nine-checkpoint-bootstrap-v1`.

`training/nine-checkpoint-bootstrap-v1@aee251f9e42e951e886fac3643456ab68e598382` is later checkpoint/startup/registry support, not a new training-package version. Its `training/roles/nine/1.0.0` subtree is exactly the same Git tree `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`. Its role registry explicitly keeps Nine at `current_training_version: 1.0.0`, binds the immutable training source to `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`, and separately identifies fresh-chat/checkpoint protocol paths. The operational `nine` branch does not expose a newer `training/roles/nine` package.

Therefore the checkpoint/bootstrap material is intentionally **not** copied into the immutable Nine v1.0.0 package. It remains separate continuity/support provenance.

## Candidate destination

- target repository: `thebrazenbeard/bt2`
- base subject: `work/source-preservation-v1@692b72e423077ad47fc2f8c3f104742ce7216c5f`
- builder branch: `work/preserve-nine-v1`
- destination package path: `archive/training-sources/build-team-2.0/nine/v1.0.0`

Every package file was recreated as a target-repository Git blob from the exact source bytes. Each recreated Git blob SHA matched its source Git blob SHA before the candidate tree was assembled. The post-commit verifier must still independently read the candidate subtree and prove that its exact tree is `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`; this builder record is not independent acceptance.

## Claim ceiling

This work preserves an exact reusable training-source candidate. It does not establish historical or current Nine qualification, BASE_READY status, compatibility with current governance, runtime/session installation, activation, current assignment, current authority, or any production/deployment effect. No qualification/install/activation record is created by this branch.
