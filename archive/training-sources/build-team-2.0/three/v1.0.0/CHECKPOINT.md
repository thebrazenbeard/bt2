# Training Checkpoint Support

The training package is immutable training source. Training-progress checkpoints are external records bound to one exact manifest digest; they are **not stored inside the frozen training-version directory during normal use**.

`tools/training_checkpoint.py` provides a deterministic helper for:

- initializing a progress checkpoint from the exact manifest;
- recording evaluator-assigned PASS / FAIL / UNRESOLVED results and evidence locators;
- recording critical disqualifiers;
- checking exact package/version/manifest/module-sequence binding;
- producing a declarative qualification receipt after the evaluator has judged the modules.

The script **does not judge trainee answers**. It cannot make an unqualified chat competent by changing JSON fields. Evaluator evidence and the module criteria remain authoritative for competence evaluation.

Typical use:

```bash
python tools/validate_package.py .
python tools/training_checkpoint.py init . /safe/external/path/three-training-progress.json
python tools/training_checkpoint.py record . /safe/external/path/three-training-progress.json THREE-TRAIN-01 PASS --evidence evaluator:attempt-01
python tools/training_checkpoint.py verify . /safe/external/path/three-training-progress.json
python tools/training_checkpoint.py qualify . /safe/external/path/three-training-progress.json
```

`BASE_READY` is only valid when the exact manifest binding is intact, every module including the final qualification module has evaluator-recorded PASS, no critical disqualifier is present, and no material unresolved training dependency remains.

A BASE_READY receipt is competence evidence only. It grants no assignment, database, GitHub, provider, deployment, or production authority and is not proof of uninterrupted runtime or subjective continuity.
