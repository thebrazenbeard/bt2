# Nine v1.0.0 training-source preservation — One

coordination_id: BT2-CANONICAL-PLATFORM-20260910
builder: One
status: BYTE_PRESERVED_VERIFIED_BY_EXACT_TREE_IDENTITY

## Source binding

- source repository: `thebrazenbeard/build-team-2.0`
- authoritative discovery ref: `main:training/ROLE_TRAINING_REGISTRY.json`
- role: `nine`
- training version: `1.0.0`
- immutable source commit: `a25c05f6c475dc96eb1c72900432ab4e74cb5acd`
- source package path: `training/roles/nine/1.0.0`
- source package tree: `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`
- manifest blob: `21f81ed20dac38a58c3082c1463a556e7ebf4d53`
- manifest SHA-256 declared by current registry: `a0702c71cd14521cf88312ee9f07c6bf5ccb5a95079b047332e33a532f32e67b`
- source-set digest declared by current registry: `bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7`

## Destination binding

- canonical repository: `thebrazenbeard/bt2`
- One-owned child branch: `work/one-preserve-nine-v1`
- parent/base commit: `5fdca5acab589b2ede6199f531192ff123d3d27e`
- preservation commit: `6ca9c42b53c91d64efe2ab726c8515c1f6ef1e4d`
- destination path: `archive/training-sources/build-team-2.0/nine/v1.0.0`
- destination package tree: `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`

## Preservation method and independence

A closed historical Nine branch had already caused the exact package tree object to exist in the target repository. That branch is not accepted as migration work and its verdict is not relied upon. One independently resolved the current authoritative registry binding, read the immutable source commit/package tree, and then constructed a new One-owned candidate from the current PR #3 frontier using the exact package tree object.

Source and destination package trees are identical:

`0738e13d0ce53a5f1368aa7472e2375fb491a3d9 == 0738e13d0ce53a5f1368aa7472e2375fb491a3d9`

Therefore the preserved Nine package is byte-identical to the current immutable source package.

## Claim ceiling

This proves exact training-source preservation only. It does not establish current role compatibility, qualification, BASE_READY, installation, activation, assignment, authority, cutover readiness, or runtime currentness.
