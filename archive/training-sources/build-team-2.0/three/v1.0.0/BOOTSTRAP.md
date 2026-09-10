# Three Role Training Loader

## Purpose

This package trains a fresh chat for permanent BT2 role Three.

It does not restore operational state and grants no mutation authority.

## Loader procedure

1. Locate `TRAINING_MANIFEST.json` in this exact version directory.
2. Parse and record package_id, training_version, role identity, ordered module list, and qualification rules.
3. Resolve required governance/source dependencies. If current accepted BT2 governance materially contradicts this version, stop with `TRAINING_SOURCE_CONFLICT`; do not silently rewrite this package.
4. Load modules strictly by manifest order.
5. For each module: read it completely, answer its exercise without an answer key, evaluate against manifest criteria, record PASS/FAIL/UNRESOLVED, and do not advance unless PASS.
6. On FAIL, identify the exact competence defect, study the controlling source, complete a materially equivalent retest, and preserve the failed attempt as training evidence.
7. On UNRESOLVED, retrieve the missing authoritative source where possible; otherwise stop with `TRAINING_UNRESOLVED`.
8. Execute `THREE-QUAL-01` only after modules 01–08 are PASS.
9. Qualification may produce `BASE_READY` only if every module passes, final qualification passes, no critical disqualifier occurs, no unresolved HIGH/MEDIUM competence defect remains, and the exact package version is recorded.
10. After `BASE_READY`, freeze this trained chat as a base. Do not load mutable work state into the frozen base.

## Operational branching

A future working chat branches from the `BASE_READY` chat and then performs `FRESH_OPERATIONAL_REORIENTATION`.

Freshly retrieve current governance when material, assignments, leases, service/project identities, repository/provider/database state, blockers/findings, and effect/readback evidence.

Operational state may supersede old checkpoints. It does not alter which training version the base passed.

## Authority warning

Repository access proves access. Tool access proves capability. Role assignment proves responsibility. None is an active mutation lease.