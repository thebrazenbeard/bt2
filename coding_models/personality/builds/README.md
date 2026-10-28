# BT2 personality-conditioned GGUF build evidence (experimental)

The separate draft release `bt2-coder-persona-labyrinth-experimental-20261028` holds 13 Q8_0 GGUF assets. Its asset names, byte lengths and GitHub SHA-256 digests were compared to local build receipts; all 13 matched. The machine-readable manifest is `personality_gguf_manifest_20261028.json`.

Each role passed four bounded synthetic-response training updates with the Labyrinth deterministic ungraded scheduler, PEFT adapter reload, safe merge, conversion and a simple Python-function inference smoke. One received the three-arm candidate / zero-learning-rate / corrupted-label control experiment; that control study was **not** repeated for all identities.

This is **not** evidence of personality fidelity, robust coding improvement, independent generalization, identity continuity, or runtime activation. The observed GGUF tensor difference between One and Two involved 56 attention Q/V tensors, proving weight difference rather than behavioral specialization.

Before admission: create private, newly authored blinded tasks with favorable and unfavorable examples; compare donor, old coding GGUF, persona GGUF under neutral and role prompting, and frozen prompt-only configurations; evaluate security/authority boundaries and coding regressions. Keep blind evaluation material out of the training corpus. Revisit reviewer-noted missing positive pass cases for Five and broader ChatGPT Project engineering cases for Hephaestus in a future, separately versioned training revision.

No model is installed; the release remains draft. The source PR is not merged.
