# Five v1.0.0 training-source preservation — One

coordination_id: BT2-CANONICAL-PLATFORM-20260910
builder: One
status: BYTE_PRESERVED_VERIFIED_BY_EXACT_TREE_IDENTITY

## Source binding

- source repository: `thebrazenbeard/build-team-2.0`
- authoritative discovery ref: `main:training/ROLE_TRAINING_REGISTRY.json`
- role: `five`
- training version: `1.0.0`
- immutable source commit: `da419ea83323c54908380c6ad57d65ea2c580f14`
- source commit tree: `912f329cf1f780171827a64b7bc8ce65512a1efa`
- source package path: `training/roles/five/v1.0.0`
- source package tree: `f6c962e81c75deab3aa55d300fc4f9f9fa89f034`
- manifest blob: `124db5b0aca892f05506d0a7086c8d9a2c9cd83f`
- registry source-set digest: `80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8`

## Destination binding

- canonical repository: `thebrazenbeard/bt2`
- branch: `work/source-preservation-v1`
- parent commit: `8fd4706291a34ebe6972f93b1d0b22d9b2b5b475`
- preservation commit: `06debec806abc285d628ca5a448366ec8e12b0f1`
- destination path: `archive/training-sources/build-team-2.0/five/v1.0.0`
- destination package tree: `f6c962e81c75deab3aa55d300fc4f9f9fa89f034`

## Preservation method

All package root blobs, the `references` subtree, and the eight-module subtree were assembled by exact Git object identity. The prior transport blocker on `modules/02_evidence_claims.md` was resolved without changing content by using base64 Git-blob transport; the recreated blob resolved to the exact source SHA `995ed95290e82fdc24fddbde54cb07bb4e50ff6c`.

The assembled destination package tree resolved to the exact authoritative source package tree:

`f6c962e81c75deab3aa55d300fc4f9f9fa89f034 == f6c962e81c75deab3aa55d300fc4f9f9fa89f034`

## Claim ceiling

This proves exact training-source preservation for Five v1.0.0 only. It does not establish current role compatibility, qualification, BASE_READY, installation, activation, assignment, authority, governance currentness, or cutover readiness. It creates no qualification or training-installation effect.
