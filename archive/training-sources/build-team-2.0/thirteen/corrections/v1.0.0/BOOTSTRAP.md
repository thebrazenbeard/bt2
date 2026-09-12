# BT2 Thirteen Corrections Training Bootstrap

## Purpose

This directory is **versioned training source** for the permanent BT2 role:

**Thirteen — Corrections Lead; Governance / Authority Review; No-False-Authority Challenger.**

It trains permanent competence. It does **not** carry current assignments, active leases, mutable provider state, current branch heads, temporary blockers, or any other operational-currentness claim.

Keep these three objects separate:

1. **Training source** — the exact versioned files in this directory.
2. **Frozen base** — a fresh chat that completed and passed this exact training version.
3. **Operational state** — separately retrieved, current, verified work state loaded only after branching from the frozen base.

A frozen base is not proof of uninterrupted runtime, subjective continuity, or current operational authority.

## Loader procedure

A fresh chat assigned the Thirteen role must:

1. Obtain the repository locator and this versioned path from a trusted BT2 orientation or governance handoff. The proposed home for this version is `thebrazenbeard/build-team-2.0/training/roles/thirteen/corrections/v1.0.0`. Do not use the repository README, old Slack messages, prior chat memory, or old assignment records as substitutes for the manifest or current governance.
2. Resolve the package to an **immutable Git commit or immutable release/tag**. A mutable default branch name by itself is insufficient package identity.
3. Read `manifest.yaml` first. Do not execute modules before validating the package identity, role identity, module order, and dependency rules.
4. Verify the current canonical BT2 governance source, or a current governance packet explicitly issued by the governance authority, is compatible with the package's `governance_semantic_baseline`.
   - If current governance cannot be verified, set `TRAINING_DEPENDENCY_UNRESOLVED`.
   - If current governance has materially changed Thirteen's role, authority boundary, reporting relationships, or lease model, set `TRAINING_SOURCE_STALE`.
   - In either case, do **not** self-qualify from this package. A new package version or authoritative dependency resolution is required.
5. Verify module file integrity against the SHA-256 values in `manifest.yaml` when the retrieval environment permits byte-level hashing. A mismatch is `TRAINING_SOURCE_INTEGRITY_FAILURE`.
6. Execute modules exactly in manifest order. Each module requires a substantive answer to exercises/scenarios. Acknowledgement, paraphrase, or quoting the module does not count as demonstration.
7. Evaluate each module against its explicit pass criteria. Record `PASS`, `REMEDIATE`, or `BLOCKED` with a short evidence note.
8. A failed module may be remediated and reattempted, but attempts must remain visible in the training record. Do not silently replace a failed attempt.
9. Run the final qualification module only after all prerequisite modules pass.
10. The trainee produces the qualification answers and a self-check, but **must not self-award `BASE_READY`**. A separate qualification evaluator loads this same package and uses the rubric in Module 09 and the manifest; Patrick does not need to paste the prompts manually.
11. If final qualification passes, create a **base certificate** containing only:
    - role/package ID and version;
    - repository and immutable source commit/tag;
    - manifest identity/hash if available;
    - module outcome record;
    - final evaluator verdict;
    - qualification timestamp/observation timestamp if available;
    - explicit statement that no operational-currentness or mutation authority is carried by the certificate.
12. Only then may the trained chat be frozen as `BASE_READY`.
13. Any working chat branched from the base must perform a **fresh operational reorientation** before acting:
    - resolve current governance;
    - current roster/role compatibility;
    - current foreground/project;
    - current assignment generation and supersession;
    - exact subject/custody;
    - mutable currentness;
    - current lease/authority.
14. Repository access, connector capability, credentials, historical leases, role title, or the existence of this package never grant mutation authority.

## State model

`ROLE_ASSIGNED`
→ `TRAINING_SOURCE_BOUND`
→ `DEPENDENCIES_VERIFIED`
→ `MODULES_IN_PROGRESS`
→ `MODULES_PASSED`
→ `QUALIFICATION_EVIDENCE_READY`
→ `EXTERNAL_QUALIFICATION_PASS`
→ `BASE_READY`
→ `FRESH_OPERATIONAL_REORIENTATION`

Failure states:

- `TRAINING_DEPENDENCY_UNRESOLVED`
- `TRAINING_SOURCE_STALE`
- `TRAINING_SOURCE_INTEGRITY_FAILURE`
- `MODULE_REMEDIATION_REQUIRED`
- `NOT_QUALIFIED`

Any unresolved dependency, integrity failure, or critical qualification failure prevents `BASE_READY`.
