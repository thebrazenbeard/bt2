# Four v1.0.1 training-source preservation — One

coordination_id: BT2-CANONICAL-PLATFORM-20260910
builder: One
status: BYTE_PRESERVED_VERIFIED_BY_EXACT_TREE_IDENTITY

## Source binding

- source repository: `thebrazenbeard/build-team-2.0`
- authoritative discovery ref: `main:training/ROLE_TRAINING_REGISTRY.json`
- role: `four`
- training version: `1.0.1`
- immutable source commit: `bf045dd627aef5650b9ed85c036b9a6340afe68f`
- source package path: `training/roles/four/1.0.1`
- source package tree: `0953afaeeec7543697f97711e5a2326d954e9fa3`
- manifest blob: `25c89bc947edf1e09470e567f2f5f193cb928333`
- source-set digest declared by manifest: `1070866d342043c21d06d9bc384fbf7cf78d231850ef2edef514b3e95229c332`

The manifest explicitly identifies v1.0.1 as the clean successor to v1.0.0 because the registered v1.0.0 source failed its manifest byte-count/integrity contract. This is why v1.0.1, not the historical v1.1.0 branch package, is the preservation subject for the current canonical registry pass.

## Destination binding

- canonical repository: `thebrazenbeard/bt2`
- One-owned child branch: `work/one-preserve-four-v1`
- parent/base commit: `692b72e423077ad47fc2f8c3f104742ce7216c5f`
- preservation commit: `3a9ad076771d43653bc4ea5f9664d724c2ae02f4`
- destination path: `archive/training-sources/build-team-2.0/four/v1.0.1`
- destination package tree: `0953afaeeec7543697f97711e5a2326d954e9fa3`

## Preservation method

The package was transferred by exact Git object identity rather than reserializing file text through a content writer. Each destination path references the original source Git blob SHA. The complete destination subtree resolves to the exact same Git tree SHA as the source package:

`0953afaeeec7543697f97711e5a2326d954e9fa3 == 0953afaeeec7543697f97711e5a2326d954e9fa3`

Therefore the archived package is byte-identical to the immutable source package.

## Claim ceiling

This receipt proves exact source-package preservation only. It does **not** establish current role compatibility, qualification, BASE_READY, installation, activation, assignment, authority, cutover readiness, runtime state, or any production effect.

No qualification row or training-installation event is created by this repository receipt.
