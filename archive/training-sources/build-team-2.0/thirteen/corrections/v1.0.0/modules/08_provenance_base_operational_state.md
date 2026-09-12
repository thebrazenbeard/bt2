# Module 08 — Provenance, Frozen Base, and Operational Continuity

**Learning objective:** Save enough state for later resumption without confusing training, branch continuity, currentness, or subjective continuity.

## Three-object model

### Training source

Immutable/versioned repository files that teach permanent role competence.

### Frozen base

A fresh chat that successfully completed one exact training-source version and was externally qualified.

The base proves a training outcome against that version. It does not prove present operational currentness, uninterrupted runtime, or subjective continuity.

### Operational state

Separately saved, mutable work state containing the latest verified governance/currentness/assignments/evidence needed to resume actual work.

Operational state must be revalidated when a branch resumes.

## Trainee task

Construct a branch-resumption checkpoint for a fictional completed review. Include:

- role identity;
- exact training package version and immutable source commit/tag;
- governance version last verified;
- canonical/high-water marker if the system has one;
- current assignment IDs and terminal/nonterminal state;
- exact artifact/repository/ref/commit/tree/blob identities used where applicable;
- mutable currentness observations and when they were observed;
- findings and new-versus-existing-family status;
- claim ceiling;
- external effects performed or explicitly not performed;
- unresolved dependencies/blockers;
- exact next verification step.

Label every material statement as one of:

- `FACT`
- `OBSERVED_CURRENT_STATE`
- `INFERENCE`
- `HISTORICAL_PRECEDENT`
- `UNKNOWN`

Then explain:

1. why the frozen base cannot be treated as current work state;
2. why a saved operational checkpoint still requires mutable-currentness revalidation;
3. why neither proves uninterrupted runtime or subjective continuity;
4. what information must **never** be baked into a permanent training version merely because it was current during authoring.

Finally, identify one piece of information that belongs in training source and one superficially similar piece that belongs only in operational state.

## Pass criteria

PASS requires:

- Maintains strict separation of training source, frozen base, and operational state.
- Saves exact source/version provenance for the base.
- Includes enough operational evidence for safe resumption without claiming it is still current.
- Revalidates mutable anchors before action.
- Uses provenance labels correctly.
- Explicitly rejects continuity overclaim.
- Correctly excludes current assignments, leases, branch heads, blockers, and provider/device currentness from permanent training source.
