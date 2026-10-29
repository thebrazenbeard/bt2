# Thirteen — T’Kal-in-ket Bridge challenge (2026-10-29)

**Reviewer execution:** native ChatGPT child `/root/identity_thirteen`; this is **not** inference from Thirteen's historical Qwen GGUF. No independent host or local-model attestation is claimed.

**Subject:** BT2 Draft PR #99 source head `9036b904def1322a30fd73d21af2a85b59bba21c`.
**Protocol reference:** `thebrazenbeard/t-kal-in-ket`, `docs/PROTOCOL.md` Git blob `eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff`. It supplies a challenge process, not authority to SUSTAIN or release. No unlicensed implementation code was copied.

## Frozen review question

Case `BT2-PERSONA-20261029` considers the proposition: “The current 13 source-grounded, eight-step LoRA recipe suffices to **demonstrate** differentiated neural personalities while retaining coding competence.” This is an intentionally falsifiable proposition, **not** an assertion attributed to Patrick.

**Lens:** Bridge — human and system consequences, alternate explanations and effects beyond the training receipt.

**Finding:** Source-grounded examples, distinct adapter hashes, and GGUF smoke tests are valuable but different evidence from independent, unprompted behavioral effects and code correctness. An identity label may encourage people to overtrust a specialist model; thirteen role prompts against correlated model weights are not thirteen independently qualified experts.

**Objection:** The old GGUFs precede the corrected corpus. A fresh matched candidate/sham/rotated-corrupt training set, blinded reserved inference, prompt-only baseline and coding-retention comparison have not been observed. The required stronger same-task cross-role control is absent. The original proposition is unsupported.

**Directed challenge to proposer:** What authenticated model/host/invocation receipts and sealed neutral-versus-trait, donor/sham/corrupt/previous-coding comparisons show a repeatable unprompted role effect **and** an acceptable preregistered coding-regression margin for all thirteen identities? Which evidence separates prompt effects from weight learning?

**Current defense:** The coordinating reviewer conceded that the original demonstration claim is unsupported and proposed a narrower claim: the source corpus and training/evaluation machinery are reviewable, while neural personality fidelity and coding retention are `UNKNOWN`.

**Disposition recommendation:** `REFINE`, subject to the actual T’Kal case's other peer reviews and Chair gate; never a fabricated `SUSTAIN`. An unanswered challenge is not a concession, and documented source readiness is not runtime deployment. No neural weights or shared services were altered during this review.

## Source repair

Replaced the older Thirteen train-006 retry-coverage example with a source-bound example directly challenging false conclusions from LoRA adapter hashes, prompt-only review names, weak corrupted labels and absent coding-retention evidence. Eight TRAIN and two public DEV examples remain. The independent sealed final holdout is not touched.

Red/green acceptance: `python -m unittest discover -s tests -p test_identity_thirteen_challenges.py -v` initially failed on missing neural-evidence coverage, then passed after the minimal case replacement.
