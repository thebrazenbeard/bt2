# Six v1.0.0 training-source preservation — One

coordination_id: BT2-CANONICAL-PLATFORM-20260910
builder: One
status: BYTE_PRESERVED_VERIFIED_BY_EXACT_TREE_IDENTITY

## Source binding

- source repository: `thebrazenbeard/build-team-2.0`
- authoritative discovery ref: `main:training/ROLE_TRAINING_REGISTRY.json`
- role: `six`
- training version: `1.0.0`
- immutable source commit: `fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4`
- source package path: `training/roles/six/v1.0.0`
- source package tree: `ba3ffa8adc18f635e516356a92e7d0450fa7a789`
- manifest blob: `bc6906f8dd5c41712fea3691c167b14a39ffd7b9`
- package/source-set digest: `ef44176582819750193c7d591e9ee449ea8c3d6743a8bff3eb5228baf4fad1cc`

## Destination binding

- canonical repository: `thebrazenbeard/bt2`
- One-owned child branch: `work/one-preserve-six-v1`
- parent/base commit: `185569a23d54778ed8319ca1bc3427b52370cc9c`
- preservation commit: `6f751ef53d4909c7c4f71ed2ad74608f202505a0`
- destination path: `archive/training-sources/build-team-2.0/six/v1.0.0`
- destination package tree: `ba3ffa8adc18f635e516356a92e7d0450fa7a789`

## Preservation method

Every source file was read from the immutable source package and recreated in the canonical repository. Each recreated Git blob SHA matched its source Git blob SHA. The assembled destination subtree then resolved to the exact source package tree:

`ba3ffa8adc18f635e516356a92e7d0450fa7a789 == ba3ffa8adc18f635e516356a92e7d0450fa7a789`

This proves byte-identical package preservation for the exact registered Six v1.0.0 source subject.

## Claim ceiling

This receipt proves exact training-source preservation only. It does not establish current role compatibility, qualification, BASE_READY, installation, activation, assignment, authority, target-runtime state, or cutover readiness. It creates no qualification or training-installation effect.
