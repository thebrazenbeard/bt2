# Seven — T’Kal-in-ket scientific challenge proposal

Status: **REFINE proposed; no formal T’Kal-in-ket determination**  
Scope: BT2 identity Seven *training-source quality*, not measured neural-model behavior.

## Source and reviewer custody

- Source of the personality target: Patrick's explicit **Scientific genius** designation, recorded in `coding_models/personality/USER_TRAIT_CORRECTIONS_20261028.md` (`USER`). It supersedes the archived numbered role's older security emphasis for this training target.
- Challenge protocol reference: [`thebrazenbeard/t-kal-in-ket/docs/PROTOCOL.md`](https://github.com/thebrazenbeard/t-kal-in-ket/blob/main/docs/PROTOCOL.md), observed Git blob `eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff` (`REPOSITORY_SOURCE`). Its code has no selected software license; no implementation was copied into BT2.
- Proposing challenger: native ChatGPT child `/root/identity_seven`, during the 2026-10-29 BT2 exercise. This is a human-readable review proposal; **not** an invocation receipt for the local Seven GGUF, cryptographically independent reviewer custody, or a completed three-peer directed exchange.
- Frozen subject: `coding_models/personality/cases/seven.json`, `seven-persona-train-007`, from BT2 draft PR #99 head `9036b904def1322a30fd73d21af2a85b59bba21c` before this patch.

## Claim and adversarial challenge

**Claim attacked:** Rationalization with `1/(hypot(x,1)+x)` prevents false zero for huge finite nonnegative Python floats.

**Pragmatism lens — numerical counterexample (observed local test):** At `x=1e308`, `math.hypot(x,1.0)+x` overflows to infinity and the formula produces `0.0`. The mathematical result remains positive, about `5e-309`, representable as a binary64 subnormal. This means the old Seven example's claimed general correction failed exactly the extreme range the task invoked.

**Proposed defense/refinement:** Compute `h=hypot(x,1.0)` and return `(1.0/h)/(1.0+x/h)` for finite nonnegative `x`. Test `x=0`, `x=1`, `x=10**8`, `x=1e308`, the largest finite float, and invalid nonfinite input. For large `x`, independently compare against asymptotic `0.5/x` within representable precision. A single passing fixture does not prove every floating-point environment behaves identically.

**Evidence classes:** source examples and patch = `REPOSITORY_SOURCE`; the test reproducing naive `0.0` and scaled positive result = local `VERIFICATION`; whether any neural Seven model learned this = `UNKNOWN`.

## Disposition and open exchange

- **Proposed disposition: REFINE.** The source example and focused regression test were corrected. This is not a `SUSTAIN` verdict: no three distinct native reviewers completed the protocol's attributed peer-to-peer directed exchange, no authenticated runtime model transcript exists, and no final holdout model inference ran.
- **Purist Logic question to an independent peer:** Do the stated input domain and mathematical identity cover `nan`, infinities, signs, and conversion semantics without hidden preconditions? Remains open.
- **Bridge question to an independent peer:** Does optimizing this one numerical example risk disproportionate training emphasis or coding regressions elsewhere? Remains open pending matched controls and reserved inference.
- The advocate and Chair have not adjudicated this packet. Neither silence nor an absent model response is treated as a concession.

## Reproduction

```sh
python -m unittest discover -s tests -p test_identity_seven_challenges.py -v
python tools/validate_personality_sft.py
python -m unittest discover -s tests -q
```

The case remains one of eight TRAIN examples; the two DEV examples and sealed independent evaluation cases are untouched.
