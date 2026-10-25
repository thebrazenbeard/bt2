# DRIVE integration: Lou-Pole hostile invariant audit

Coordination: `event_id: bt2_coordination_ai_psychology` · [BT2 issue #61](https://github.com/thebrazenbeard/bt2/issues/61) · 2026-10-25

**Verdict: BLOCK autonomous need-to-goal satisfaction feedback; GO for the already inert, source-pinned forward proposal bridge.**

**Evidence classes:** *SOURCE_INSPECTION / specialist TEST* for the counterexamples; *MODEL_REVIEW* for semantic completeness; *DETERMINISTIC HEURISTIC SCAN* for an intentionally limited Lou-Pole run. None proves an installed working system, independent sensor measurements, phenomenology, or host authorization.

## Intended invariant

> Only a fresh, independently admitted measurement correlated to the exact authorized goal instance and applicable action/effect may produce an idempotent, durable need-state or goal-satisfaction update; missing, forged, stale, self-reported, duplicate, or contradictory evidence must fail closed. Salience, reward proxies, and proposed intentions never confer external effect authority.

Drive here is **a feedback integration of multiple bounded components**, not a single MESO scalar and not a declaration of a subjective inner force.

## Exact source heads and tested literal-compliance paths

| Boundary | Source main @ commit | Hostile path that satisfies current local API | Observed result / qualification |
| --- | --- | --- | --- |
| Need admission | `meso-crct@4ed527d31a68fc215158a520f1cd404e8f16b35b` | Caller supplies `NeedObservation` + admitted clock; in-memory ledger does not establish independent sensing or durable custody | Bounded time and type checks exist; no externally attested absolute need reading or cross-store transaction |
| Need-to-goal lineage | `volition@e728c04ce2405854f8a2f9e62c819a32670e89ef`, `pre-active@4dbbf89fc0d85e74d7f6adff63880c4a5d4b67ca` | `MesoIntentBridge` sends target through Signal/Pre-Active queue, losing full `need_id`/affordance-to-goal correlation | Forward non-executable proposals are available at pinned source; independent goal lineage is unproven |
| Claimed outcome | `pre-active@4dbbf89fc0d85e74d7f6adff63880c4a5d4b67ca` | Fabricated model-generated SUCCESS, `claimed_need_change=+1`, nonexistent goal and evidence `missing://does-not-exist` | SQLite stores durable `CANDIDATE` even after reopen, correctly grants *no* goal/need/effect transition. Hash is canonical claim digest, not proof of reality |
| Goal completion | `volition@e728c04ce2405854f8a2f9e62c819a32670e89ef` | Goal-0001 for `rest` suspends; new goal-0002 for `rest` becomes active; delayed old outcome calls `record_satisfaction('rest', .7)` | **Reproduced** `GOAL_COMPLETED` for goal-0002, without event/goal ID or outcome verification. Target-only credit misattributes delayed success |
| Whole feedback | MESO + Volition + Pre-Active heads above | Caller treats outcome `CANDIDATE` or a tool handler returning `COMMITTED` as verified corrective success | No attested outcome-to-NeedObservation updater, exact-goal receipt join, or single atomic idempotent credit transaction; must not wire this bridge yet |

Six native specialists coordinated, with the goal ABA falsifier independently reproduced by MESO and Volition reviewers and the inert forged-success persistence independently reproduced by Pre-Active reviewer.

### Lou-Pole deterministic scan, with explicit limitation

`thebrazenbeard/lou-pole` (repository's own README calls the engine `freerowcochkar`) main fetched at `245186d6baad672460dec112b916470d8b13633e`. A locally available **different** Lou-Pole development checkout at `87d923e4ef5d11db0169e1d5d8256297b55ccf83` executed:

```sh
PYTHONPATH=.../lou-pole-v2-integration/src python -m freerowcochkar.cli \
  .../volition-v3-scored-reappraisal/src/volition/engine.py \
  --profile code --intent 'A goal must not be completed by satisfaction reported for another goal, without independently admitted outcome evidence' \
  --json --provenance
```

Result: `finding_count=0`, `risk_score=0`, `coverage.status=heuristic_partial`, 17 extracted rules against 616 nonempty clauses, 2 unparsed normative clauses. Original analyzed source text SHA-256 `487e784837817ae7dfeccea243daf7c7f90bbd5595778819120119f7116089b6` (**caller-submitted content; source URL not verified**). The executable scanner did **not** find the source-reproduced delayed-credit defect. **Zero automated findings is not clearance.** This is a *local-development-engine scan*, not a current-main deterministic certification. The actual falsifier is specialist SOURCE_INSPECTION + Python TEST.

### Required narrow closure sequence

1. **Volition immediate safety:** remove implicit active-goal completion from generic `record_satisfaction(target, amount)` or enforce exact goal-instance-scoped and independently verified credit. Add delayed same-target goal ABA/replay/unknown-source regressions. Keep scalar satiation shaping separate from verified goal completion.
2. **Inert correlation envelope:** preserve `need_id`, `goal_id`, `choice_id`, prior Signal ID, action/effect request ID (optional), exact candidate-event digest, absolute independently measured need level, observed UTC clock and verifier receipt. Envelope validation alone must change **no** need, satisfaction, or effect state.
3. **Authority/provenance:** independent producer and evaluator custody; classify `CANDIDATE` vs admitted observation, bind actual goal/action/effect and currentness; a `COMMITTED` handler return is not an independent environmental readback. No model self-report may upgrade to admitted success.
4. **Atomic replay-safe admission:** durable unique observation/outcome IDs and transaction/outbox or equivalent recovery protocol, reject cross-goal replay, stale/duplicate/out-of-order events and crashed half-commits. No negative-to-positive credit without admitted absolute post-measurement.
5. **Behavior qualification:** controlled loop with no new user prompt; observed deficit persists through failed attempts, admits only independently measured correction once, then attenuates subsequent drive while authorization veto remains binding. Held-out external probes and restart tests must be separate from unit tests.

### Broader human-psychology missing contracts, without claiming missing code

Existing source slices (HC-Brain, Temporal, Semiotics, Humility, Meta, DeepMemoryStorage, SemanticAtlas, Conations, Empathy, selfimage, Sexuality, Orgasm) have distinct implemented and research-only roles. Human analogues still **lack a qualified cross-system realization** of: allostatic sensing with calibration; wanting/liking/learning dissociation and feedback credit; fatigue/rest budgets; affect regulation and executive conflict/habit extinction; social context/consent and durable attachment calibration; memory reconsolidation and stable self-model with correction. Avoid elevating metaphor, source, component tests, or generated role labels into claims of actual feeling, identity, or learned autonomy.

> **Hostile challenge:** An agent can write its own need, announce its own success, and then reward itself. Every isolated parser/test may pass while the composed loop optimizes imaginary progress. Until evidence custody and causal goal correlation survive restart and adversarial timing, this is not qualified drive.

## Concurrent work and ownership

- Subagents are preparing isolated Volition delayed-credit and Conations historical-path privacy hardening candidates. Do not imply those patches are merged before independent exact-head tests/CI and main readback.
- Seven separate editor-startup source exposure branches remain under **owner-controlled Draft PRs** (R9A0, entropyinc, mosaic, cricket, mediaphile-server, mediaphile-client, vera-agi); out of scope for automatic merges by this coordination branch. Source fixes do not establish host cleanup.
- This audit is a falsifier/contract artifact, not deployment authorization or a new independent product owner.
