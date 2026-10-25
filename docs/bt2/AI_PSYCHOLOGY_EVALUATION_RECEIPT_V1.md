# AI psychology evaluation receipt V1 (research-only)

Event: `bt2_coordination_ai_psychology`. This contract is a **bounded format bridge**, not an installed Vera runtime adapter.

`tools/ai_psychology/validate_receipt.py` accepts one strict JSON receipt and returns **FORMAT_VALID_EVIDENCE_UNVERIFIED**. It uses the Python standard library only; it never imports, invokes, downloads, or authorizes `meta`, `humility`, `driftguard`, or `vera-mono`.

The input must provide four exact-shaped lowercase 40-character source-commit **claims** (without resolving their repositories), differently spelled proposer/evaluator IDs (without authenticating their principals), distinct but **unverified** training/heldout/shift digest claims (without checking data overlap), unique opaque event and dependence-group IDs (without event-to-group mappings), and method-execution *claim* references (without execution attestation). It requires PREQUENTIAL observation ordering and separate baseline/candidate Brier, coverage, abstention, and case counts on heldout and shift sets. Different counts for a pair fail validation.

All unknown JSON fields fail closed. Boolean/nonnumeric/nonfinite/out-of-range metrics, duplicate JSON object keys, duplicate evidence IDs, reused split digests, conflicting roles, non-`NONE` effect claims, or an assertion of independently verified label custody are rejected. Raw prompts, labels, personal/relational records, and free-form text have no schema field. The CLI performs best-effort symlink-ancestor rejection and descriptor-based regular-file and 128 KiB read bounds; it limits JSON nesting and numeric token length. This is not a trusted filesystem boundary or a guarantee against Windows reparse-point/path races.

```powershell
python -m unittest discover -s tools/ai_psychology/tests -p test_receipt.py -v
python -m tools.ai_psychology.validate_receipt path\to\untrusted-receipt.json
```

The output contains a candidate-minus-baseline Brier difference and a separate shift Brier difference. Negative delta is a lower *caller-reported* Brier score; positive is a higher one. Different coverage/abstention can also make aggregated scores noncomparable. The code neither recomputes scores from observations nor verifies whether method choices actually occurred. **Neither sign proves improvement or causal learning.** The script does not authenticate identity or accept or emit a deployment, policy, training, or behavioral promotion decision.

### Missing qualification and next owner tasks

1. Independently witnessed model/method execution, host/source identity, and non-colluding evaluator custody.
2. Outcome release commitments and a genuinely hidden/locked heldout split; the supplied digests are unverified claims.
3. Recomputed Brier and abstention from signed per-event predictions/outcomes, not merely caller-supplied aggregate numbers.
4. Prequential and shift comparisons against frozen, randomized, reflection-only, and unchanged-method baselines, with negative-transfer results retained.
5. An *external* DriftGuard report conversion/admission step that independently checks evaluator provenance and thresholds; this validator does **not** generate `PASS`.
6. External protection for private history: `deepmemorystorage` and `conations` do not become generic evaluation/training material.

Do not interpret a successful format check as evidence of calibrated epistemic humility, an autonomous new learning rule, personhood, or an operational integration link. `vera-mono` remains self-contained, and sibling repositories are research/provenance candidates rather than implicit runtime dependencies.

**Verification scope:** The bundled tests may write disposable JSON fixtures and start a child Python CLI process. The production validator itself only reads a nominated receipt; this distinction is intentional.
