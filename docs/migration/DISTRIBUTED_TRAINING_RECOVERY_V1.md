# BT2 Distributed Training Recovery V1

Status: **SOURCE PACKAGES RECOVERED / QUALIFICATION NOT YET PROVEN**

Date: 2026-09-10

Coordinator: One

Purpose: recover versioned BT2 role-training source that existed outside the old `main` training registry, without fabricating qualification or current activation.

## Evidence rule

The old `build-team-2.0/main` registry omitted Two, Three, Seven, and Eight. That omission is not evidence that their training packages never existed.

This recovery distinguishes four separate states:

1. **SOURCE_PACKAGE_FOUND** — an exact repository/ref/commit/tree/package path exists.
2. **PACKAGE_INTEGRITY_VERIFIED** — manifest/checksum/file bytes have been mechanically verified where the package defines such integrity evidence.
3. **QUALIFICATION_EVIDENCE_FOUND** — evidence exists that a specific frozen base actually completed the exact package and passed its required evaluator/rubric.
4. **CANONICAL_ACTIVE** — current BT2 governance has admitted that exact package/qualification into the canonical registry for operational use.

No later state may be inferred from an earlier one.

## Recovered packages

### Two v1.0.0

- agent: `two`
- source repository: `thebrazenbeard/build-team-2.0`
- source ref: `two`
- exact source commit: `47f26e2c5c9b37e6fc61134844278d524f095b51`
- exact commit tree: `f1599a046c7dd6882a4cfdc8054c21c255441a6a`
- package root: `training/roles/two/v1.0.0`
- package tree: `e42eeb5c3c269b8e42aa955b1e85846d63eafe98`
- manifest: `TRAINING_MANIFEST.yaml`
- manifest blob: `257eaeef34c568e1c8812f6e3451a276162b1fac`
- manifest-declared version: `1.0.0`
- manifest source status: `PROPOSED_PENDING_REPOSITORY_PUBLICATION_AND_APPROVAL`
- source contains manifest, checksums, qualification rubric, BASE_READY receipt template, and nine ordered training modules.
- current recovery state: `SOURCE_PACKAGE_FOUND`
- integrity verification: `PENDING`
- qualification evidence: `NOT YET ESTABLISHED`
- canonical activation: `NOT YET ESTABLISHED`

The manifest explicitly requires exact-package verification, ordered module execution, independent evaluation, preserved evidence, and a BASE_READY receipt. Package presence does not satisfy those conditions.

### Three v1.0.0

- agent: `three`
- source repository: `thebrazenbeard/build-team-2.0`
- source ref: `training/three-role-v1.0.0`
- exact source commit: `f5f43e61c85ed96df040c2a2d8e1df523706a215`
- exact commit tree: `594d2000ee0cb0f5dcbdc1edf6586430140049c2`
- package root: `training/roles/three/v1.0.0`
- package tree: `696484549f1e729bb04b546e50973efc1fa4439c`
- manifest: `TRAINING_MANIFEST.json`
- manifest blob: `315777e08bffc4808ebf68e715c8d58c2d00f2ee`
- manifest-declared package ID: `bt2-role-three-training`
- manifest-declared version: `1.0.0`
- source contains bootstrap/checkpoint material, manifest, nine ordered modules, test tooling, and package validation tooling.
- current recovery state: `SOURCE_PACKAGE_FOUND`
- integrity verification: `PENDING`
- qualification evidence: `NOT YET ESTABLISHED`
- canonical activation: `NOT YET ESTABLISHED`

The manifest explicitly states that reaching the final module is not self-awarding qualification and that unresolved evidence is not PASS.

### Seven v1.0.0

- agent: `seven`
- source repository: `thebrazenbeard/project-achilles`
- source ref: `main`
- exact source commit: `dbf9ceb2391567463d864198405c9b5d1e77db09`
- exact commit tree: `1cd715bef0d2a33478d3a635bcc05155c95ab4f9`
- package root: `training/roles/seven/v1.0.0`
- package tree: `86b38a66d7bb5d6b71e1bf9754dee3248e2e9792`
- manifest: `TRAINING_MANIFEST.json`
- manifest blob: `00e89de1dd4d37e54feb6a75341335c80e878595`
- manifest-declared version: `1.0.0`
- source contains bootstrap, source baseline, checksum file, eight ordered modules, final qualification, rubric, and checkpoint tooling.
- current recovery state: `SOURCE_PACKAGE_FOUND`
- integrity verification: `PENDING`
- qualification evidence: `NOT YET ESTABLISHED`
- canonical activation: `NOT YET ESTABLISHED`

The manifest defines BASE_READY only after exact hash verification, modules 01-08 PASS, Module 09 completion before rubric load, evaluator QUALIFICATION_PASS, zero Critical Fails, preserved exact source identity, and no mutable operational state loaded into the frozen base.

### Eight v1.0.0

- agent: `eight`
- source repository: `thebrazenbeard/build-team-2.0`
- source ref: `feature/eight-training-v1.0.0`
- exact source commit: `7fb3f506a66324b5a54d7cda3103899d520c3f04`
- exact commit tree: `62fec5e73f39ba6583becc601a352f0892aa60bc`
- package root: `training/roles/eight/v1.0.0`
- package tree: `5217e383cefad53b9ef97f6e35544b0e10f8da58`
- manifest: `TRAINING_MANIFEST.yaml`
- manifest blob: `afb8042a344c01290bfd43685cc05ee489d12462`
- manifest-declared package ID: `bt2.role.eight.training`
- manifest-declared version: `1.0.0`
- source contains bootstrap loader, manifest, and nine ordered modules; branch also contains Eight checkpoint tooling outside the version root.
- current recovery state: `SOURCE_PACKAGE_FOUND`
- integrity verification: `PENDING`
- qualification evidence: `NOT YET ESTABLISHED`
- canonical activation: `NOT YET ESTABLISHED`

The manifest separates permanent competence from current assignments/leases/provider state and says unresolved criteria are not PASS.

## Canonical migration consequence

The new BT2 platform must not model these four agents as having no training source merely because the old main-branch registry omitted them. Their package source identities are now preserved in `bt2.source_snapshots` as `GITHUB_TRAINING_PACKAGE` evidence rows.

However, the new platform must also not create training qualification rows merely because package source was recovered.

Current canonical posture for all four:

`PACKAGE_FOUND / INTEGRITY_VERIFICATION_PENDING / QUALIFICATION_UNPROVEN / ACTIVATION_UNPROVEN`

## Next recovery steps

1. Verify each package's declared integrity mechanism against exact source bytes where such a mechanism exists.
2. Search source branches, continuity records, qualification receipts, and governed historical evidence for actual qualification runs/results.
3. Preserve contradictory or incomplete evidence as `UNRESOLVED`, never as inferred PASS.
4. After Two hardens agent/package/qualification relational cross-binding, register recovered exact package identities in the canonical training registry.
5. Only admit PASS/BASE_READY when exact qualification evidence satisfies that package's own rules and current compatibility/governance permits use.
6. Preserve the old main-registry omission as historical integration debt; do not rewrite history to make it appear the packages were always centrally registered.

## Relationship to continuity repair

The earlier continuity scaffolds for Two, Three, Seven, and Eight solved discoverability/shape only. This recovery supplies actual historical training-source bindings. Neither artifact alone proves current BASE_READY.

## Non-effects

This recovery does not:

- self-qualify any chat;
- declare any role currently BASE_READY;
- authorize external service mutation;
- merge source branches;
- retire old training repositories/branches;
- convert historical package rules into current governance without compatibility review;
- prove uninterrupted session/runtime identity.
