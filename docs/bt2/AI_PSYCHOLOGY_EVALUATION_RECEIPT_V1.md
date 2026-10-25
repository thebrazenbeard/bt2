# AI psychology evaluation receipt V1 (research-only)

Event: `bt2_coordination_ai_psychology`. This contract is a **bounded format bridge**, not an installed Vera runtime adapter.

`tools/ai_psychology/validate_receipt.py` accepts one strict JSON receipt and returns **FORMAT_VALID_EVIDENCE_UNVERIFIED**. It uses the Python standard library only; it never imports, invokes, downloads, or authorizes `meta`, `humility`, `driftguard`, or `vera-mono`.

The input must pin exact 40-character lowercase Git source hashes for those four research components, identify a method proposer distinct from an evaluator, bind disjoint training/heldout/shift dataset digests, supply distinct event and source-dependence-group IDs, and provide nonempty method-execution *claim* references. It requires PREQUENTIAL observation ordering and separate baseline/candidate Brier, coverage, abstention, and case counts on heldout and shift sets. Different counts for a pair fail validation.

All unknown JSON fields fail closed. Boolean/nonnumeric/nonfinite/out-of-range metrics, duplicate JSON object keys, duplicate evidence IDs, reused split digests, conflicting roles, non-`NONE` effect claims, or an assertion of independently verified label custody are rejected. Raw prompts, labels, personal/relational records, and free-form text have no schema field. The CLI refuses symlinked input and files exceeding 128 KiB.

```powershell
python -m unittest discover -s tests -p test_ai_psychology_receipt.py -v
python -m tools.ai_psychology.validate_receipt path\to\untrusted-receipt.json
```

The output contains a candidate-minus-baseline Brier difference and a separate shift Brier difference. Negative delta is a lower Brier score; positive is a higher one. **Neither sign proves improvement or causal learning.** The script does not accept or emit a deployment, policy, identity, training, or behavioral promotion decision.

### Missing qualification and next owner tasks

1. Independently witnessed model/method execution, host/source identity, and non-colluding evaluator custody.
2. Outcome release commitments and a genuinely hidden/locked heldout split; the supplied digests are unverified claims.
3. Recomputed Brier and abstention from signed per-event predictions/outcomes, not merely caller-supplied aggregate numbers.
4. Prequential and shift comparisons against frozen, randomized, reflection-only, and unchanged-method baselines, with negative-transfer results retained.
5. An *external* DriftGuard report conversion/admission step that independently checks evaluator provenance and thresholds; this validator does **not** generate `PASS`.
6. External protection for private history: `deepmemorystorage` and `conations` do not become generic evaluation/training material.

Do not interpret a successful format check as evidence of calibrated epistemic humility, an autonomous new learning rule, personhood, or an operational integration link. `vera-mono` remains self-contained, and sibling repositories are research/provenance candidates rather than implicit runtime dependencies.
