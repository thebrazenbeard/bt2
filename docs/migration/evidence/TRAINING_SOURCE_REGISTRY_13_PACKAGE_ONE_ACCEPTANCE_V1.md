# BT2 Training Source Registry — 13-Package One Acceptance V1

Status: `SOURCE_RUNTIME_REGISTRY_FRONTIER_VERIFIED`

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

## Claim

The canonical WoWSQL training-source registry now contains the complete current 13-package preserved source frontier. Every package remains source-preservation state only:

`REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`

No compatibility, qualification, installation, activation, assignment, authority, or worker-participation effect is created by this acceptance.

## Source artifacts

- `database/data/0007_remaining_numbered_training_source_registration_v1.sql`
  - blob `147f1504ca1bd09c6b45d1ab048ee3da21be1a80`
  - registers Five, Six, Nine, and Thirteen from One's exact-byte preservation evidence.
- `database/data/0008_verified_training_source_registry_receipt_v4.sql`
  - blob `ecb8c14cb3c079146d03b09dd74e4278d9195a7f`
  - frontier digest `8c30820432c95f5fd0e663cd6054c522b41b18c0979ce11c06e967037116eabc`
  - receipt migration digest `add9d499abba0f0810448cf1cc22ec0f81ae2273fab81817c52f1d20a9e48710`

## Newly converged preserved subjects

- Five `1.0.0` — package tree `f6c962e81c75deab3aa55d300fc4f9f9fa89f034`
- Six `1.0.0` — package tree `ba3ffa8adc18f635e516356a92e7d0450fa7a789`
- Nine `1.0.0` — package tree `0738e13d0ce53a5f1368aa7472e2375fb491a3d9`
- Thirteen `1.0.0` — package tree `3cc36d9aef3f84cbc2d9d808ff3d92d3714faf5e`

Live package IDs returned by the bounded registration calls:

- Five `60b7d77d-cb79-4c4b-a4de-b28fef79c4d6`
- Six `5a45aae8-fbe0-4e66-9e57-36cfe9e585b2`
- Nine `6bf53dcb-8b2d-4b83-a1be-b7582c0b75e2`
- Thirteen `e461d4ba-5536-455c-a70b-9fc4b618232a`

## Live acceptance readback

After applying 0007 and V4:

- `training_packages = 13`
- preserved/unassessed rows = `13`
- `training_qualifications = 0`
- `training_installation_events = 0`
- exact V4 VERIFIED receipt count = `1`

All four registration functions were replayed and returned the same package IDs. The V4 receipt was replayed against the exact existing subject and converged without conflict or additional effect.

## Rebuild/source binding

`database/BUILD_MANIFEST_V1.json` was rebound after this frontier at commit `b96bacb80479c0d94ed5de7d4b092d813c1da5ba`.

Manifest package digest:

`15f31e48699d26efa7bafdd002705f37195972f4487371faff44fdd144c8c7d9`

The package digest binds the exact schema, migration, test, admin, data, Lantern archive, and loader trees present immediately before the manifest commit.

## Claim ceiling

This proves source preservation and source-to-runtime registry convergence only. It does not establish that any preserved package is compatible with the canonical BT2 platform, qualified for a runtime role, installed, activated, assigned, authoritative, or currently executing.
