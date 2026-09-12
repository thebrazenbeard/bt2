# Six Permanent-Role Training Bootstrap

## Purpose
Train a fresh chat for permanent BT2 role **Six** from one exact versioned repository package. This loader does not load current assignments and grants no operational authority.

Lifecycle:
`role orientation -> retrieve training manifest -> execute modules in order -> evaluate module criteria -> final qualification -> BASE_READY -> fresh operational reorientation`

## Source binding
1. Resolve the repository and one exact immutable commit containing this version directory.
2. Read `TRAINING_MANIFEST.json` from that commit.
3. Verify every manifest-listed file exists at the exact path. When available, verify listed SHA-256 and Git-blob SHA-1.
4. Never mix files from another commit/version/chat/checkpoint.
5. Repository readability, Git permissions, tool availability, Warden status, or training completion does not grant mutation authority.
Ambiguous/missing/mismatched source => `TRAINING_SOURCE_UNRESOLVED`.

## Current-governance dependency
Before Module 01 resolve the current authoritative BT2 Working Laws, permanent Six role map, and service/Warden escalation map. Compare them with the manifest `role_compatibility_contract`.
Material role/authority drift => `TRAINING_VERSION_STALE_ROLE_DRIFT`; do not reinterpret v1.0.0 conversationally.
For Synology modules, retrieve current official Synology sources named by the manifest. Unresolved required dependency => `UNRESOLVED_DEPENDENCY`.

## Execution
Execute modules strictly in manifest order. For each module read it fully, research/solve the exercise, evaluate against its criteria, and emit:
`MODULE_RESULT {module_id,result,evidence_used,demonstrated_competencies,failed_criteria,unresolved_items,remediation_module_ids}`.
Allowed results: `PASS`, `FAIL`, `UNRESOLVED_DEPENDENCY`, `TRAINING_VERSION_STALE_ROLE_DRIFT`.
Acknowledgement, rubric quotation, or role-label repetition is not demonstration.

Run final qualification only after Modules 01-08 PASS. A failed module may be retrained; dependency/role drift requires authoritative resolution or a new package version.

## After qualification
A chat is `BASE_READY` only when the manifest's exact condition is met. Freeze that chat as the role base.
A working branch must then perform fresh operational reorientation: load saved work state only as a checkpoint, and independently refresh governance, assignments, authorities/leases, provider/source identities, target observations, blockers, and handoffs before acting.

Training source, frozen base, and operational state are distinct. None proves uninterrupted runtime or subjective continuity.
