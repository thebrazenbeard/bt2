# BT2 Training / Continuity Source Recovery V1

Status: SOURCE RECOVERY / QUALIFICATION IMPORT NOT YET AUTHORIZED BY EVIDENCE

Date: 2026-09-10

Owner: One

Coordination: `BT2-CANONICAL-PLATFORM-20260910`

## Purpose

The old `build-team-2.0` main-tree training registry is incomplete as a universe of BT2 training source. It registers only a subset of the workforce even though additional versioned packages survive on historical/role branches and in specialist repositories.

This recovery record preserves those sources before consolidation and prevents two opposite errors:

1. treating absence from old `main` as proof that a role was never trained; and
2. treating package existence as proof that a particular runtime/session was qualified, installed, active, or currently authorized.

The canonical migration therefore keeps four states separate:

`PACKAGE_SOURCE` -> `QUALIFICATION_EVIDENCE` -> `RUNTIME/BASE INSTALLATION` -> `CURRENT OPERATIONAL AUTHORITY`

None implies the next without evidence.

## Active workforce topology this recovery serves

- One = primary/orchestrator.
- Two, Three, Four, Five, Six, Seven, Eight, Nine, Thirteen = One-orchestrated BT2 subagents.
- Masa + Mune = separate paired debugger/reliability unit.
- Hephaestus = independent specialist.

Historical training language that reflects older role/governance topology is source provenance. Compatibility with the new topology must be evaluated; frozen package bytes are not silently rewritten.

## A. Centrally registered package sources on the frozen `build-team-2.0` main cut

Source registry:
- repo: `thebrazenbeard/build-team-2.0`
- frozen migration cut: `main@ec2987e45f64a588ac92f6cae9964cb3725b9485`
- registry: `training/ROLE_TRAINING_REGISTRY.json`

The registry explicitly binds package source for these six numbered roles:

| Agent | Version | Package path | Historical immutable source commit | Historical source-set digest | Migration disposition |
|---|---|---|---|---|---|
| One | 1.0.0 | `training/roles/one/v1.0.0` | `ed1f2c5515425deab4c77c2f4fd291a1086191d4` | `ee7d764b48f0114bc2274a4d384390983637f9c39dbba6b9f161d0881c38e0e6` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |
| Four | 1.0.1 | `training/roles/four/1.0.1` | `bf045dd627aef5650b9ed85c036b9a6340afe68f` | `1070866d342043c21d06d9bc384fbf7cf78d231850ef2edef514b3e95229c332` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |
| Five | 1.0.0 | `training/roles/five/v1.0.0` | `da419ea83323c54908380c6ad57d65ea2c580f14` | `80d2aab944ee8c8e13b83ae99aacc4ba530bc42cda69ed6c9ab21958a64e55f8` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |
| Six | 1.0.0 | `training/roles/six/v1.0.0` | `fcb358b0e7ca7b1b57cf868e34aac28d5c0e55c4` | `ef44176582819750193c7d591e9ee449ea8c3d6743a8bff3eb5228baf4fad1cc` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |
| Nine | 1.0.0 | `training/roles/nine/1.0.0` | `a25c05f6c475dc96eb1c72900432ab4e74cb5acd` | `bcbee02e5e7f59b763ba1a441a66c4e3b83210befcb85ab7f66a5d0ccf7769e7` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |
| Thirteen | 1.0.0 | `training/roles/thirteen/corrections/v1.0.0` | `4de273b3d56ec642c7f9ba83e4767029cf054559` | `89f3da76b9033c9302e2ddb85c68b6bf0b7856383d7bce65f671170d4a8a7bc1` | PACKAGE_SOURCE_BOUND / QUALIFICATION_IMPORT_PENDING |

The old registry points qualification/checkpoint storage at Supabase project `klmbpaigzeguvnpccqzz`. That project is not one of the user-authorized migration source systems in this consolidation. The pointer is preserved as historical dependency evidence; this migration does not access, mutate, or silently import that database.

## B. Recovered package source absent from old main-tree registry

### Two — package recovered from role branch

- repo: `thebrazenbeard/build-team-2.0`
- ref: `two`
- head: `47f26e2c5c9b37e6fc61134844278d524f095b51`
- tree: `f1599a046c7dd6882a4cfdc8054c21c255441a6a`
- package tree: `e42eeb5c3c269b8e42aa955b1e85846d63eafe98`
- package path: `training/roles/two/v1.0.0`
- manifest blob: `257eaeef34c568e1c8812f6e3451a276162b1fac`
- manifest status: `PROPOSED_PENDING_REPOSITORY_PUBLICATION_AND_APPROVAL`
- package includes checksum file, qualification rubric, BASE_READY receipt template, modules 01-09, loader/index, and checkpoint support.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

Two's package itself requires independent evaluation and explicitly forbids trainee self-award of BASE_READY. Package existence therefore cannot be converted into a historical qualification claim.

### Three — package recovered from stranded training branch

- repo: `thebrazenbeard/build-team-2.0`
- ref: `training/three-role-v1.0.0`
- head: `f5f43e61c85ed96df040c2a2d8e1df523706a215`
- tree: `594d2000ee0cb0f5dcbdc1edf6586430140049c2`
- package tree: `696484549f1e729bb04b546e50973efc1fa4439c`
- package path: `training/roles/three/v1.0.0`
- manifest blob: `315777e08bffc4808ebf68e715c8d58c2d00f2ee`
- package includes bootstrap/checkpoint material, modules 01-09, validation tooling, and tests.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

The frozen package encodes an older governance/ownership map (including One as sole governance and Two/Three database roles). That content is historical package semantics. Compatibility with the new One-led subagent topology must be decided explicitly; the v1.0.0 package must not be silently rewritten.

### Seven — complete package recovered from Project Achilles

- repo: `thebrazenbeard/project-achilles`
- ref: `main`
- commit: `dbf9ceb2391567463d864198405c9b5d1e77db09`
- tree: `1cd715bef0d2a33478d3a635bcc05155c95ab4f9`
- package tree: `86b38a66d7bb5d6b71e1bf9754dee3248e2e9792`
- package path: `training/roles/seven/v1.0.0`
- manifest blob: `00e89de1dd4d37e54feb6a75341335c80e878595`
- package includes SHA256 inventory, source baseline, modules 01-08, final qualification, separate rubric, checkpoint schema/template, and training checkpoint tooling.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

Seven's manifest defines BASE_READY only after exact package verification, ordered module PASS, a separate final evaluator `QUALIFICATION_PASS`, zero Critical Fails, and a training record bound to the immutable source used. No such runtime qualification is inferred merely from finding the package.

### Eight — package recovered from stranded feature branch

- repo: `thebrazenbeard/build-team-2.0`
- ref: `feature/eight-training-v1.0.0`
- head: `7fb3f506a66324b5a54d7cda3103899d520c3f04`
- tree: `62fec5e73f39ba6583becc601a352f0892aa60bc`
- package tree: `5217e383cefad53b9ef97f6e35544b0e10f8da58`
- package path: `training/roles/eight/v1.0.0`
- manifest blob: `afb8042a344c01290bfd43685cc05ee489d12462`
- package includes bootstrap loader, modules M01-M09, checkpoint protocol, and tooling.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

The package requires current-governance compatibility resolution and treats unresolved required criteria as unresolved rather than PASS.

### Masa — package recovered from stranded training branch

- repo: `thebrazenbeard/build-team-2.0`
- ref: `training/masa-v1.0.0`
- head: `bdfe4e04bdba3dca1661ac7f940e0d7ed0206a8d`
- tree: `7e34b0aca5ab58b5ca5046b694989b158b5fc4ff`
- package tree: `96f8aa5f37dc8bb72d5ec270bf372e28a5b992a5`
- package path: `training/roles/masa/v1.0.0`
- manifest blob: `6d04c333fea85cbf410b36861211579e16d276a9`
- package includes manifest, SHA256SUMS, bootstrap, operational reorientation, reusability audit, modules 01-09, checkpoint/result schemas, and support tooling.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

Masa's package explicitly separates debugger leadership/root-cause competence from routine repair implementation, self-verification, final acceptance, and external-write authority. That separation is compatible in principle with the new paired Masa/Mune unit, subject to formal compatibility review.

### Mune — v1.0.1 recovered as recommended package

- repo: `thebrazenbeard/build-team-2.0`
- ref: `training/mune-debugger-verification-v1.0.1`
- head: `6c84086e217fa4f8a1214eb0d69718e48a96e12d`
- tree: `892c0ea4fd77543fdadd9d19d7c7cc7ac7d91697`
- package tree: `5e8c87021bfda9a6fc44fa121c32410ddc6aedf9`
- package path: `training/roles/mune/v1.0.1`
- manifest blob: `5d2b6cdaa603b60edc860801eaae5dd8644d3c9a`
- `training/roles/mune/CURRENT.json` points to v1.0.1 as the recommended version.
- v1.0.1 supersedes v1.0.0 as a checkpoint/verification-tooling patch without changing module semantics.

Disposition: `PACKAGE_FOUND / QUALIFICATION_UNPROVEN`.

Mune's manifest requires governance compatibility, modules 01-08 PASS, Module 09 qualification, all critical categories PASS, no unresolved critical dependency, and a completion receipt. It also states that training completion does not grant write authority.

## C. Hephaestus — standalone evidence outranks stale central copy for migration custody

Primary migration source:
- repo: `thebrazenbeard/hephaestus`
- ref: `main`
- commit: `78f6f22a0e5d14617855006a8383765589ac8c67`
- tree: `80eb19e26ff9b82f8c2eb4126c5b4e87a2318ce6`

The standalone repository contains:
- `training/QUALIFICATION_PACKET.md`
- `training/HOLDOUT_1_EVALUATION.md`
- `training/HOLDOUT_2_EVALUATION.md`
- `training/TRAINING_LEDGER.md`
- `state/checkpoints/CHECKPOINT_0001_POST_TRAINING.md` through `CHECKPOINT_0008_PROTOCOL_V2.md`
- `state/checkpoints/CHECKPOINT_0004_QUALIFIED.md`
- continuity/governance/operating material.

WoWSQL already contains a source-provenance record classifying this as `EVIDENCE_SUPPORTS_QUALIFIED`, while deliberately holding creation of a canonical qualification row pending training-schema hardening.

Disposition: `QUALIFICATION_EVIDENCE_FOUND / CANONICAL_QUALIFICATION_IMPORT_HELD`.

This does not prove any current runtime installation or current operational authority.

## D. Masamune operational/history sources remain distinct from reusable training packages

The `thebrazenbeard/masamune` repository has separate `masa`, `mune`, `continuity/masa`, and `collab` branches. These contain role-specific operational/design/review history, including a Masa continuity state and substantial Mune adversarial research/review evidence.

They should be migrated as operational/history evidence, not treated as substitutes for the recovered reusable training packages above.

## E. Canonical import rules

Before inserting a canonical `training_packages` row as REGISTERED/current candidate:

1. exact source repo/ref/commit/tree/package path must be bound;
2. manifest/package integrity must be verified under that package's own digest/checksum rule;
3. package semantics must undergo compatibility review against the new workforce topology;
4. historical package bytes remain immutable;
5. incompatible package semantics create a new canonical successor version rather than editing the old package in place.

Before inserting a canonical PASS/BASE_READY qualification:

1. exact package binding must already exist;
2. actual qualification evidence for the subject must be available;
3. evaluator identity/evidence must meet the package's own rules;
4. no unresolved critical condition may be laundered into PASS;
5. runtime/session identity, where known, remains separate from durable logical-agent identity;
6. qualification grants competence provenance only, not current assignment or external mutation authority.

## F. Current recovery status

| Agent | Package source located | Qualification evidence established for canonical import | Runtime installation established | Current authority implied |
|---|---:|---:|---:|---:|
| One | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Two | YES | NO | NO | NO |
| Three | YES | NO | NO | NO |
| Four | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Five | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Six | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Seven | YES | NO | NO | NO |
| Eight | YES | NO | NO | NO |
| Nine | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Thirteen | YES | PENDING HISTORICAL STORE/EVIDENCE REVIEW | NO | NO |
| Masa | YES | NO | NO | NO |
| Mune | YES | NO | NO | NO |
| Hephaestus | YES / standalone specialist package+ledger | YES, source evidence supports qualification; canonical row held pending schema hardening | NO | NO |

## G. Remaining work

- Verify every recovered package under its own checksum/digest canonicalization rule.
- Preserve exact package bytes in the canonical private BT2 repository without silently normalizing immutable historical versions.
- Determine compatibility with the new active topology and create successor versions only where semantically required.
- Import canonical package records only after Two's training/package/qualification relational hardening is integrated and verified.
- Import qualification records only where independent evidence supports them.
- Migrate Masamune role-branch operational/history material separately from package source.
- Preserve old qualification/checkpoint-store pointers as historical dependency evidence; do not access unlisted external databases by inference.

No package discovery in this document constitutes cutover, installation, qualification, merge authority, deployment authority, or external write authority.
