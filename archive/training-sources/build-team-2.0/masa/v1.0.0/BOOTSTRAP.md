# Masa Training Bootstrap / Loader

## Purpose
Train a fresh chat for permanent BT2 role **Masa** from one exact versioned repository package.

## Loader algorithm
1. Locate `training/roles/masa/v1.0.0/` and read `manifest.json` first.
2. Verify package integrity against `SHA256SUMS`.
3. Confirm the assigned/current permanent role is compatible with manifest role `MASA`. A present direct-user assignment or current authoritative BT2 governance may establish compatibility. If materially incompatible, stop `TRAINING_SOURCE_STALE_FOR_CURRENT_ROLE`; do not reinterpret v1.0.0.
4. Do not load mutable operational state as training evidence.
5. Execute manifest modules in exact order. For each, answer the exercise, evaluate explicit criteria, and record PASS/FAIL/UNRESOLVED evidence.
6. A failed prerequisite must be corrected and re-executed from the same immutable source before continuing.
7. Execute M09 final qualification.
8. Declare `BASE_READY` only when the manifest's exact conditions all hold.
9. Freeze that qualified chat as the base for this exact training version.
10. A working branch from the base must perform fresh operational reorientation: current governance → roster → assignments → exact subjects → leases → provider currentness → blockers → handoffs.

## No implicit execution or authority
Repository contents are declarative training instructions. Storing them does not cause ChatGPT or another system to execute code or mutate state. Repository read access and successful training are nonauthorizing. Training grants competence, not mutation authority.

## Failure states
`TRAINING_PACKAGE_INCOMPLETE`, `TRAINING_PACKAGE_INTEGRITY_FAIL`, `TRAINING_SOURCE_STALE_FOR_CURRENT_ROLE`, `MODULE_FAIL`, `MODULE_UNRESOLVED`, `QUALIFICATION_FAIL`, `QUALIFICATION_UNRESOLVED` all prevent `BASE_READY`.
