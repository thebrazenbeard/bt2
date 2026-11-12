# BT2 coding-role evaluation drafts — not blind

The 13 `cases/*.json` files each contain three source-grounded coding questions,
observable output properties, failure signals, and explicit source references.
They are **author-drafted** alongside the public identity profiles and training
data. They are **not** independently blind or sealed, not executed evaluations,
not trusted role labels, and not evidence that any GGUF behaves as its named
identity. Do not repeatedly tune against these and then call them a holdout.

Run the format, role coverage and source-link validator:

```sh
python tools/validate_identity_coding_evals.py
python -m unittest discover -s tests -p test_validate_identity_coding_evals.py
```

For actual qualification, establish a separately authored and protected blind
suite, preregister the scoring protocol and baseline/prompt-only arms, execute
the same prompts against the exact hashed candidate and donor GGUF in isolated
runtime, verify source/build/runtime identity, compare code outputs against a
trusted sandboxed oracle, and retain failures. These drafts can guide review
and task design but must never self-qualify model weights.
