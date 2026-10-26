# BT2 learning/retrieval experiment research record — 2026-10-26

Event: `bt2_lgcm_mosaic_sgm_noema_weknora_integration_20261026`
Agent: Thirteen (independent proposed-benchmark review)

## Frozen future experiment proposal (not yet executed)

Question: Can a resource-bounded, version-pinned integration improve persistent
pretrained-model learning and knowledge-grounded task performance over separately
matched full-history/retrieval and no-training baselines, without contaminating
hidden evaluation evidence or pretending retrieval is a weight update?

H-R: WeKnora hybrid retrieval increases held-out citation-correct document
finding versus independent BM25 under equal corpus, query, ACL, and indexing
epochs. Falsifier: recall/nDCG not improved or ACL/index drift changes custody.

H-N: Training a small LoRA adapter inside a frozen pretrained SmolLM2-135M
backbone produces persistent, restart-equivalent gains on unseen compositional
task families compared with the identical unmodified backbone, matched-head,
and retrieval/context baselines. Falsifier: no holdout gain; gain vanishes on
restarted model; training inputs include hidden evaluator labels; compute or
context budget explains difference.

H-M: A trained 135M-to-360M state bridge, when equipped with the same trained
decoding capacity as the full-history arm, yields incremental task/efficiency
advantage. Falsifier: equal or worse paired accuracy/cost, wrong/shuffled state
retains performance, or decoder interface remains at chance for all arms.

E-R (future confirmatory): prefreeze new corpus and independently sealed
document/query judgments, serve WeKnora only after async indexing completes;
compare hybrid, keyword-only, independent BM25, and no retrieval. Capture
Recall@5, nDCG@10, MRR, cited-answer grounding, ACL leakage and P50/P95 latency.
Pin corpus, chunker, embedder, index generation, access policy, model/checkpoint.

E-N (future confirmatory): inspect target host memory, disk, CPU, model cache
before dependency installation or download. If feasible, use model pinned to an
immutable revision; LoRA only on named attention modules with exact tokenizer,
optimizer, RNG and adapter checkpoint manifest. Frozen development, validation,
and independently sealed held-out family/source partitions; at least three
pilot seeds before a fresh, untouched confirmatory set of at least five seeds.
Test train/untrained/matched-head/full-information controls, wrong/zero/shuffled
adapter, fresh-process restore and uninterrupted continuation. Report per-case
predictions, paired confidence intervals, timing, tokens, state bytes and peak
resident memory. No single cross-domain accuracy metric is allowed.

E-M (future confirmatory): pair same target pretrained 360M model and equal
decoder-head capacity in latent-prefix, full-history, and reset arms. Reserve
new untouched task families. Original binary count toy is inappropriate for
claiming an accuracy win because lossless two-byte full-history is exact.

Stopping rules: no model installation/training until Lappy hardware/resources
verified; abort if cost/resource cap is exceeded or hidden evidence exposed;
never promote exploratory reused benchmark to confirmatory after inspection.
Results are marked HOLD when matched baselines tie or outperform treatment.

## Evidence log (exploratory review; no new neural run)

- R1: Mosaic repo `main@ab0fe474f3412f4db33bab55481eb1e8f40b7f6e`,
  `experiments/MOSAIC_PRETRAINED_BRIDGE_PILOT1_20261026.md`: trained latent,
  full raw history, and reset all score 64/128 on reused cohort; source reports
  CPU 169.332 s on VN1 and a post-hoc head 122/128 without new holdout.
  This motivates matched decoder heads; it does not confirm transfer.
- R2: Mosaic source `experiments/p1_pretrained_bridge_pilot.py` names frozen
  original SmolLM2 revisions source `12fd25f77366fa6b3b4b768ec3050bf629380bac`
  and target `a10cc1512eabd3dde888204e902eca88bddb4951`, `torch` plus
  `safetensors` and `transformers`. The source pilot declares 120 steps,
  batch size 4, and seed 20261026. No local hardware/model inference rerun.
- R3: BT2 feature branch `codex/learning-stack-prequential-20261026` based on
  `main@e686374cafd137a70cf49f284a8f289f0215110b`;
  `conformance/learning_stack/README.md` is a regression numeric RLS probe;
  WeKnora adapter in `integrations/weknora` is a fixture-tested client, not
  live ingestion/retrieval. No neural-training or service-effect claim.
- R9: SPM `main@64e41c0f1a95cb563051680d46f78287e875ede5` already
  contains an 8.75 MB Qwen2.5-1.5B LoRA memory-currentness specialist.
  Historical predecessor reports persistent 23/24, full-history 24/24, reset
  9/24 and a separate 96-case generalization comparison (adapter 96, base
  77, full history 96); a noisy-memory stress receipt reported adapter 70/72
  versus base 72/72. The hardened successor requires new behavioral/runtime
  qualification. Consider reuse and requalification of this actual learned
  adapter before initiating a duplicate SmolLM2 LoRA training project.
- R4: Lewis et al., RAG primary paper, https://arxiv.org/abs/2005.11401,
  retrieved 2026-10-26: distinguishes learned parametric generation from
  externally retrieved nonparametric evidence.
- R5: Thakur et al., BEIR primary paper and source repository,
  https://arxiv.org/abs/2104.08663 and https://github.com/beir-cellar/beir,
  retrieved 2026-10-26: heterogeneous IR evaluation with nDCG, MAP, Recall.
- R6: Hu et al., LoRA primary paper https://arxiv.org/abs/2106.09685,
  retrieved 2026-10-26: pretrained transformer frozen, trainable low-rank
  internal updates; distinguishes LoRA from separately trained classifier head.
- R7: Hugging Face official model card
  https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct,
  retrieved 2026-10-26: 135M pretrained model, Apache 2.0; model size alone
  does not establish host memory feasibility.
- R8: Hugging Face official PEFT quicktour,
  https://huggingface.co/docs/peft/main/quicktour, retrieved 2026-10-26:
  current API suggests `LoraConfig` and `get_peft_model`, `q_proj` targeting.
  No PEFT version lock was found in Mosaic repo; version-specific code remains
  unqualified until installed environment is inspected.

## Verdict and open work

Evidence review: **partial**. Existing Mosaic pilot is negative, source-bound.
E-R/E-N/E-M are planned but not run; SPM has historical separately recorded
training evidence, not a new run here. No claim of improved learned behavior or
WeKnora retrieval should be made. An independent fresh reviewer is needed to
qualify any future experiment result. Lappy current RAM/VRAM/disk, WeKnora
deployment/index version, pretrained model availability, and SGM identity are
UNKNOWN in this research lane.
