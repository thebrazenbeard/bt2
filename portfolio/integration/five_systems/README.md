# Five-system research seam — LGCM / Mosaic / SPM / Noema / WeKnora

Event: `bt2_lgcm_mosaic_sgm_noema_weknora_integration_20261026`.
The original "SGM" identifier was corrected by the user to **SPM**,
Semantics & Pragmatics Model (`thebrazenbeard/spm`). Coordination:
[private Bus issue #395](https://github.com/thebrazenbeard/chat-communication-bus/issues/395).

## Exact observed source subjects (2026-10-26)

| Project | SHA | Verified scope |
| --- | --- | --- |
| LGCM | `6bc748f3b1687f70eea6866bdd28a471465db473` | Numerical prequential recurrent-context learning and snapshots |
| Mosaic | `ab0fe474f3412f4db33bab55481eb1e8f40b7f6e` | Governed Core, local neural inference, modular/model residency research |
| SPM | `64e41c0f1a95cb563051680d46f78287e875ede5` | Qwen2.5-1.5B rank-8 LoRA bounded memory/currentness gate, not full SPM |
| Noema | `8f81e4ffac444c016c05ff9a477a790da9e403e5` | I0 source/I1 deterministic, no E0 learning qualification |
| WeKnora | `26fe2a08e9f63ae34c79584957e4f375408dea4a` | External retrieval system; `knowledge-search` read-only interface |
| BT2 | `e686374cafd137a70cf49f284a8f289f0215110b` | Research adapter owner, NOT a selected live backend |

## Composable interfaces (not one fused neural network)

```
Document ingestion -> WeKnora KB [scope, chunk provenance]
  -> read-only /api/v1/knowledge-search -> Passage[KB, doc, chunk, digest]
  -> SPM *candidate* memory-view input (only with qualified base + adapter)
  -> Mosaic untrusted specialist input (Core reasons, verifier remains separate)
Numerical (observation, action, next observation) stream
  -> LGCM prequential predictor/update -> independent learned world state
Noema I0/I1 contracts -> offline hostile controls, not active E0 authority.
```

The WeKnora adapter uses exact upstream `POST /api/v1/knowledge-search`,
`knowledge_base_ids` and `match_count`. It disables ambient proxies,
redirects and non-TLS remote destinations; its caller **must** provide a KB
whitelist; responses with absent/mismatched scope, ambiguous JSON or invalid
citations fail closed. No credential, network endpoint or WeKnora server is
configured/connected by this research work. Upstream WeKnora is **MIT** with
third-party exceptions and notices; no source from WeKnora was copied.

`LocalCorpus` is an offline ingestion and lexical retrieval reference,
not WeKnora itself. Snapshot SHA-256 protects against accidental mutation but
is **not** authentication, signature, atomic replacement or currentness proof.
The SPM source adapter requires exact 4-bit NF4 base model/LoRA digests and
enables memory only with retrieved records; our standalone Qwen2.5-Coder
Ollama model is a **different model** and must never be called SPM.

## Repeatable outcomes and falsification

Run from the BT2 repository root on Python 3.12+:

```powershell
python -m unittest discover -s portfolio/integration/five_systems/tests -v
python -m portfolio.integration.five_systems.pilot `
  --output path-to-new-result.json
```

Local Lappy 2026-10-26: the predeclared six synthetic inspection-token
questions yielded **6/6 exact matches with relevant retrieval**, **0/6
with irrelevant passages**, **0/6 without passages** on the advertised
`qwen2.5-coder:1.5b-instruct-q8_0` inference endpoint, temperature zero.
A separate second run reproduced all 18 exact model responses and the same
6/0/0 arm scores; both JSON receipts are retained under `results/`.
This only shows context access improves a tiny invented-fact task. It is not
SPM LoRA behavior, cross-model latent sharing, a statistical generalization
claim, or an actual WeKnora deployment. Result stored under `results/`.

LGCM official `experiments/heldout_probe.py` at pinned source passed
alongside **68/68 tests + 4 subtests**. Its four-seed mean overall MSE for
abrupt regimes: LGCM 0.00159888, EW-RLS 0.00192425, cumulative ridge
0.00251357; for gradual regimes: LGCM 0.00148289, EW-RLS 0.00188207,
cumulative ridge 0.00247880. No large/unseen-distribution or LLM
improvement is established. The full source-produced output is in
`results/lgcm_official_heldout_20261026.json`. Separately at exact source
SHA, SPM's focused gated-memory/provenance test selection passed 23/23,
while Mosaic's full unittest selection passed 189 (one skipped). Noema's
Python-3.13 I1 suite was not rerun on this host; its published verification
receipt must not be promoted into this integration's runtime result.

Relevant independent research: [RAG (NeurIPS 2020)](https://arxiv.org/abs/2005.11401)
separates parametric and retrieval memory; [Farahani/Johansson, EMNLP
2024](https://aclanthology.org/2024.emnlp-main.943/) investigates model
reliance on retrieved vs parametric knowledge; [Wang et al., TPAMI
2024](https://pubmed.ncbi.nlm.nih.gov/38407999/) surveys continual-learning
forgetting/generalization. [CounterMem, EMNLP 2026](https://aclanthology.org/2026.findings-emnlp.1054/)
provides a stronger counterfactual context-change benchmark than our tiny
synthetic smoke test.

Hostile null hypotheses still open: relevant and nuisance-matched retrieval
may tie on novel questions; SPM's qualified adapter may not improve when
memory is stale/noisy; LGCM's numeric context experts may not transfer to
text; Mosaic's specialists may exchange only tokens rather than learned
weights; Noema source tests do not demonstrate online learning; prompt
injection and cross-KB scope leakage must be rejected. A positive synthetic
retrieval score does NOT qualify merges of model/training components.

## Next independent gates

1. Bind to an actual local, consented WeKnora instance and execute its
   scope/error/restart tests. Never store API keys in this repository.
2. Reproduce exact SPM base + adapter identity and held-out noisy-currentness
   comparison in an isolated qualified runtime, not the wrong Ollama variant.
3. Compare independent pretrained/learned specialist models under equivalent
   prompt, memory, tokens, latency and contamination budgets; inspect weights
   and state before/after reload to determine if learning truly persists.
4. Separate Noema E0 experimental authorization and source-only I0/I1 state;
   evaluate LGCM on novel dynamical regimes with frozen baselines.
5. Obtain independent architect/security hostile reviews and source-bound
   readback before considering any integration merge.

Other repositories' source trees were not modified in this wave.
