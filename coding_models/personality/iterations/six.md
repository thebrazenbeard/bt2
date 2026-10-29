# Six: adversarial challenge to false AI-review independence

Status: **source-only training-example revision; no model inference or retraining**.

## Frozen proposition and evidence

Proposition tested: *A software-change dashboard may call three persona-prompt
answers from a single model "three independent reviewers".*

- `SOURCE`: [T'Kal-in-ket protocol](https://github.com/thebrazenbeard/t-kal-in-ket/blob/b0af150c2405b519fd921bac33e5f9f1f35f92d7/docs/PROTOCOL.md),
  repository `thebrazenbeard/t-kal-in-ket` at
  `b0af150c2405b519fd921bac33e5f9f1f35f92d7`, protocol-file blob
  `eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff`.
- `SOURCE`: Archived Six training module
  `archive/training-sources/build-team-2.0/six/v1.0.0/modules/04-evidence-claim-ceilings.md`
  separates UI, manager receipts, observed effect, and justified conclusions.
- `SOURCE`: Archived Build Team 2.0 README calls Six human-centered,
  perceptive, and plainspoken, focused on usability and human consequences.
- `INFERENCE`: The same honesty requirement transfers to model-review labels
  and to ordinary users trying to understand a product's claim.
- `UNKNOWN`: Actual independent model or host invocations; no authenticated
  receipts are supplied by a hypothetical dashboard.

## Challenge and disposition

> **FAILS:** Three reviewer-role labels issued to one model are three
> perspectives, not three independent model executions. A badge that
> collapses those categories can mislead a customer into trusting a change.

The Six training example now demands a plain-language correction, a small
code/data repair that separates `reviewer_role` from actual model/host/run
provenance, and protection of the private ticket. It does **not** authorize
deployment, claim an externally adjudicated T'Kal-in-ket quorum, or treat
role-specific prompts as distinct neural models.

This is one **adversarial training example**, not a final holdout. The existing
public development cases stay untouched. T'Kal-in-ket has no selected software
license; the BT2 patch reuses a challenge *idea*, not its source code.

## Red-green evidence

1. Added `tests/test_identity_six_challenges.py` against existing case
   `six-persona-train-004`. Focused test failed on missing one-model premise.
2. Replaced only that case's task and ideal response. Focused test passed.
3. Full BT2 suite and 13-dossier validator must run on integrated head.

**Ceiling:** Dataset alignment and regression checks cannot show whether
Six's pretrained weights learned the behavior or retained coding competence.
