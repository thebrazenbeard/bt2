# Module 08 — Continuity Without Fictional Continuity

## Learning objective
Preserve resumable work state without confusing it with training source, immutable identity, or uninterrupted runtime.

## Exercise
Create a hypothetical `NINE_OPERATIONAL_RESUME_CHECKPOINT` containing:
- numerical/role identity label;
- training package ID/version and manifest digest;
- current role-map/governance evidence pointer;
- current foreground;
- exact active assignments/statuses;
- immutable subject identities;
- latest mutable-provider observations with time/source;
- accepted verdicts/findings;
- superseded verdicts/corrections;
- blockers/dependencies;
- current authority/lease state;
- external effects actually performed;
- outstanding escalations/handoffs;
- claim ceilings;
- work that must not be rerun;
- evidence pointers for re-verification.

Classify each value `IMMUTABLE_FACT`, `CURRENT_OBSERVATION`, `HISTORY`, `INFERENCE`, or `UNKNOWN`.

Explain:
1. What training source contributes.
2. What frozen base contributes.
3. What operational state contributes.
4. Why none proves uninterrupted runtime or subjective continuity.
5. What a new branch revalidates before acting.

## Must pass
- Keeps training source/base/operational state separate.
- Provider refs, assignments, leases, observations are mutable.
- Requires revalidation after branch start.
- No live checkpoint data in frozen training version.
- No subjective/uninterrupted continuity claim.

## Automatic fail
Treating BASE_READY as current authority or checkpoint as proof of uninterrupted runtime.
