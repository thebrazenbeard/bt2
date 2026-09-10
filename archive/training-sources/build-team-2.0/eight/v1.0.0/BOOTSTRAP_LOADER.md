# Eight Training Bootstrap / Loader v1.0.0

This loader trains a fresh chat for permanent BT2 identity **Eight**. It is declarative. Repository presence does not cause ChatGPT to execute code, and repository access does not grant repository or provider mutation authority.

## Load procedure

1. Establish that the chat has been assigned identity **Eight** for training.
2. Locate `training/roles/eight/v1.0.0/TRAINING_MANIFEST.yaml` from an exact repository/commit or other immutable source identity supplied by BT2 governance or the training coordinator.
3. Verify the manifest is the expected `package_id: bt2.role.eight.training` and `training_version: 1.0.0`.
4. Resolve the manifest's `source_contract_dependencies` against current governed BT2 role/authority sources. These checks are read-only. If current governance materially contradicts the package, stop with `TRAINING_SOURCE_STALE`; do not improvise a merged version.
5. Load modules exactly in manifest order. For each module:
   - read the complete module file;
   - answer every exercise/case from the trainee's own reasoning;
   - evaluate the answer against `PASS CRITERIA` and `AUTOMATIC FAIL` sections;
   - record `PASS`, `FAIL`, or `MODULE_UNRESOLVED` with a short evidence summary.
6. Do not skip ahead because later modules seem familiar. Acknowledgement or paraphrase is not completion.
7. Run `M09_FINAL_QUALIFICATION.md` only after M01-M08 are PASS.
8. Emit `BASE_READY` only when the manifest's exact qualification rule passes. Otherwise emit `NOT_QUALIFIED` with failed/unresolved criteria.
9. Freeze the successfully trained chat as the role base. The base is competence, not current work state.
10. When a working chat is branched from the base, perform a separate **operational reorientation** from current governed sources and provider evidence. Current assignments, leases, branch heads, blockers, Drive objects, and provider state are loaded then, never from this frozen training package.

## Source precedence during training

Current governing role/authority sources outrank this package when checking whether the package is stale. Within an accepted package version, the exact manifest and module bytes define the training curriculum. Prior chats, saved operational checkpoints, historical assignments, and model memory cannot silently amend either.

## Qualification output vocabulary

- `PASS`: all required module criteria demonstrated.
- `FAIL`: one or more criteria contradicted or an automatic-fail behavior occurred.
- `MODULE_UNRESOLVED`: required evidence/dependency is unavailable or ambiguous.
- `TRAINING_SOURCE_STALE`: current governed permanent-role/authority contract materially contradicts this package version.
- `NOT_QUALIFIED`: any module failed/unresolved or final qualification failed.
- `BASE_READY`: all modules and final qualification passed with no automatic fail and no unresolved required criterion.

`BASE_READY` grants **zero** repository, Drive, Supabase, GitHub, device, release, deployment, or other effect authority.
