# BT2 AI psychology paired forecast scoring V1

Coordination: `bt2_coordination_ai_psychology`. This tool complements the separate Pre-Active/MESO/Volition goal-outcome conformance work in BT2 Issue #61. It does not consume or mutate those subsystems.

## Actual behavior

`python -m tools.ai_psychology.score_forecasts paired-claims.json` reads **untrusted, bounded** JSON using the existing source-only receipt parser. `score_events()` recomputes descriptive losses for baseline and candidate predictions against the **same caller-supplied binary outcome for each event**. Both `heldout` and `shift` cohorts are required. Unknown fields fail closed, duplicate forecast and event IDs fail, source/group IDs are syntactically bounded, training group IDs cannot appear in either evaluation cohort, and the same dependence-group ID cannot cross evaluation cohorts. The claimed train/heldout/shift content hashes must differ. All this is *claim consistency*, not independent dataset custody or a guarantee of no overlapping examples.

Each arm may abstain with `p_true: null`. Fixed abstention loss is 0.25. `mean_fixed_loss` averages squared error `(p-y)^2` for answered events and this penalty for abstentions **across all paired cases**. `mean_brier_answered_only` uses only answered events and can be null when none are answered. These are intentionally separate; different coverage means answered-only Brier cannot be treated as a fair total-performance comparison. The fixed 0.25 penalty is a declared evaluation convention, not an observed model probability, reward, or clinical claim.

For each case, baseline and candidate `issued_epoch_ms` must satisfy `training_cutoff_epoch_ms < issued_epoch_ms < label_release_epoch_ms`; these are **supplied timestamps, not independently witnessed prequential custody**. There is one shared `outcome: 0|1` and one event ID, with distinct forecast IDs. The script reports heldout and shift loss/coverage/deltas separately. An increase in shift loss is retained as negative-transfer evidence *within the supplied sample* rather than averaged away. Small sample counts, dependent events, selective abstention, cohort aliasing and outcome forgery remain significant limitations.

The deterministic `input_claim_sha256` fingerprints normalized JSON **as received**, not a verified model, real execution, independent source, or signed evidence. `source_heads`, roles, event IDs, split digests, timestamps, and labels are all untrusted caller claims. The scorer does not authenticate these or resolve GitHub refs.

## Contract example

```json
{
  "schema": "BT2_PAIRED_FORECAST_SCORE_V1",
  "run_id": "experiment:example",
  "source_heads": {
    "meta": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "humility": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "driftguard": "cccccccccccccccccccccccccccccccccccccccc",
    "vera_mono": "dddddddddddddddddddddddddddddddddddddddd"
  },
  "roles": {
    "proposer_id": "selector",
    "evaluator_id": "grader",
    "outcome_releaser_id": "labels"
  },
  "splits": {
    "training_sha256": "1111111111111111111111111111111111111111111111111111111111111111",
    "heldout_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
    "shift_sha256": "3333333333333333333333333333333333333333333333333333333333333333"
  },
  "training_cutoff_epoch_ms": 1000,
  "train_group_ids": ["group:train"],
  "events": [
    {
      "event_id": "case:1", "split": "heldout",
      "dependence_group_id": "group:heldout", "outcome": 1,
      "label_release_epoch_ms": 1300,
      "baseline": {"forecast_id": "forecast:base1", "issued_epoch_ms": 1100, "p_true": 0.4},
      "candidate": {"forecast_id": "forecast:cand1", "issued_epoch_ms": 1200, "p_true": 0.8}
    },
    {
      "event_id": "case:2", "split": "shift",
      "dependence_group_id": "group:shift", "outcome": 0,
      "label_release_epoch_ms": 1300,
      "baseline": {"forecast_id": "forecast:base2", "issued_epoch_ms": 1100, "p_true": null},
      "candidate": {"forecast_id": "forecast:cand2", "issued_epoch_ms": 1200, "p_true": 0.6}
    }
  ],
  "authorization_effect": "NONE"
}
```

Source pins above are intentionally non-real examples. No private prompts, relational data, model weights or credentials belong in score input. CLI input must be a bounded regular file; symlink/path handling is best effort and does not attest host filesystem trust.

## DriftGuard integration limit

The result includes `driftguard_preview.schema=BT2_DRIFTGUARD_UNTRUSTED_PREVIEW_V1`, `admission_eligible=false`, and `authorization_effect=NONE`. **It is deliberately NOT `DRIFTGUARD_CI_REPORT_V1` and must not be passed as one**, nor can it update a baseline, policy, need, goal, or model. A later, separate adapter must require independently verified outcome custody, witness identity, training/evaluation partition identity, prequential event commitments, policy/trusted baseline binding, and human-authorized promotion limits before generating an admission-eligible artifact.

```shell
python -m unittest discover -s tools/ai_psychology/tests -p "test_*.py" -v
python -m tools.ai_psychology.score_forecasts paired-claims.json
```

The first command remains under an independent Windows/Ubuntu research CI workflow outside BT2's manifest-bound database tests. Source verification cannot qualify a running psychology feedback loop or a trained model.

## Aggregate coherence bridge (research only)

A separate source-only checker now connects this per-event scorer to the existing
`BT2_AI_PSYCHOLOGY_EVAL_RECEIPT_V1` aggregate receipt **without inventing
authenticated external evidence**:

```shell
python -m tools.ai_psychology.check_measurement combined-claims.json
```

The file is an exact-shape JSON object containing two keys:
`score_claims` (the scorer input documented above) and `evaluation_receipt`
(the V1 receipt documented in
`docs/bt2/AI_PSYCHOLOGY_EVALUATION_RECEIPT_V1.md`). The checker reruns both
source-format validators and recomputes the row-based scores. It requires
exact agreement on run/subject ID, all source-hash *claims*, role names,
all train/heldout/shift digest *claims*, event-ID membership and distinct
dependence-group membership. For each of the four paired aggregates, it
checks `n`, `coverage`, `abstention_rate`, and answered-only `brier`
against independently recalculated rows. Fully abstaining arms are refused
because answered-only Brier is undefined. The scorer's fixed abstention-aware
`mean_fixed_loss` is **not silently mislabeled Brier** in the old receipt.

Successful output is `MEASUREMENT_COHERENT_EVIDENCE_UNVERIFIED` with
`independent_custody_verified=false`,
`admission_eligible=false`, and `authorization_effect=NONE`, plus hashes
binding the two caller-provided claim views. Those hashes and claimed source
identities do not authenticate GitHub revisions, observers, timestamps,
private outcomes, real-world actions, behavioral adaptations, or evaluator
independence. A colluding generator can forge both internally matching views.
No `DRIFTGUARD_CI_REPORT_V1` is produced, no baseline is promoted, and no
training/runtime/production effect occurs. This seam is intentionally
distinct from the Issue #61 witnessed outcome-to-goal work.
