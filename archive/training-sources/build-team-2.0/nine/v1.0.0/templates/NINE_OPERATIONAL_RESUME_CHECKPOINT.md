# NINE_OPERATIONAL_RESUME_CHECKPOINT Template

This structure is for later operational state. Do not fill it with live values inside the versioned training directory.

```yaml
schema: NINE_OPERATIONAL_RESUME_CHECKPOINT_V1
training:
  package_id: null
  version: null
  manifest_sha256: null
  source_commit_or_digest: null
role_identity:
  label: Nine
  numerical_identity: 9
current_governance:
  evidence_pointer: null
  observed_at: null
  classification: CURRENT_OBSERVATION
foreground:
  value: null
  classification: CURRENT_OBSERVATION
assignments: []
immutable_subjects: []
mutable_observations: []
verdicts_current: []
verdicts_superseded: []
blockers: []
authority_and_leases: []
external_effects: []
handoffs_and_escalations: []
claim_ceilings: []
do_not_rerun: []
evidence_pointers: []
unknowns: []
```

A later branch must independently refresh mutable observations and current authority before acting.
