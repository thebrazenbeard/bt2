# LGCM prequential persistence probe

Status: **source-level numerical integration probe**, not an installed HC
runtime, neural training, learned specialist transfer, or generalized reasoning.

This probe calls the real `lgcm.ContextualWorldModel` public API. For each
bounded numeric observation it predicts **before** applying that event's
outcome; it scores a separate persistence baseline (zero predicted delta), applies the
LGCM online RLS update, serializes at event 30, reloads it, and compares every
prediction and final serialized model-state digest against an uninterrupted run. It emits all
60 prediction receipts rather than only aggregate accuracy. No retrieval
document, prompt, benchmark label, or text embedding feeds into the learner.

Run with an independently cloned, exact pinned LGCM source (Python >=3.12,
NumPy >=2):

```bash
git clone https://github.com/thebrazenbeard/lgcm.git /tmp/lgcm-for-bt2-probe
git -C /tmp/lgcm-for-bt2-probe rev-parse HEAD  # record exact revision
PYTHONPATH=/tmp/lgcm-for-bt2-probe/src python -m unittest discover \
  -s conformance/learning_stack -p 'test_*.py' -v
PYTHONPATH=/tmp/lgcm-for-bt2-probe/src:conformance/learning_stack python -c \
  'import json; from lgcm_prequential import run_probe; print(json.dumps(run_probe(), indent=2))'
```

Record the exact LGCM source SHA alongside the emitted fixture digest. The
fixture is a deliberately reused `+0.6/-0.6/+0.6` three-regime stream; its
status is `REGRESSION`, **not** an untouched scientific holdout. Readback of a
snapshot and deterministic continuation here do not establish transactionally
exactly-once learning across crashes, concurrent workers, or external state
stores; they do not qualify WeKnora ingestion or Mosaic inference. A later
experiment must use independent unseen streams, matched trained/no-training
controls, retrieval-index versions, and an evaluator inaccessible to learners.

This adapter aligns with existing BT2 `ObservationEnvelope` and
`PlasticityCandidate` families and the ancestry/evidence-isolation contracts;
it does **not** create a competing HC global state schema.

Pinned Linux regression output, including every prequential prediction:
[`results/LGCM_PREQUENTIAL_REGRESSION_20261026.json`](results/LGCM_PREQUENTIAL_REGRESSION_20261026.json).
The reference source is LGCM `6bc748f3b1687f70eea6866bdd28a471465db473`;
the BT2 workflow checks out that exact commit. This fixture's observed mean
squared error was `0.0540731` versus `0.3600000` for zero-delta persistence.
This is a reused simulator case, not an unseen holdout or a neural result.

From PowerShell on Lappy after cloning the pinned source and installing NumPy:

```powershell
$env:PYTHONPATH = 'C:\path\to\lgcm\src'
py -m unittest discover -s conformance/learning_stack -p 'test_*.py' -v
```
