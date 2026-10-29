# Third-party model attribution for experimental BT2 coding and personality derivatives

The experimental BT2 coding models from the 2026-10-28 pilot, and any later
personality derivatives that explicitly carry this verified provenance, derive
from **Qwen/Qwen2.5-Coder-1.5B-Instruct** at Hugging Face revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`.

- Original model: https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct
- Original license: Apache License, Version 2.0, as published at
  https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/blob/2e1fd397ee46e1388853d2af2c993145b0f1098a/LICENSE
- Original pinned safetensors SHA-256:
  `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`
- Exact pinned upstream LICENSE SHA-256:
  `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e`
- Verbatim license companion in this source tree:
  `coding_models/training/upstream/Qwen2.5-Coder-1.5B-Instruct_LICENSE`

**Changes:** The 2026-10-28 pilot used BT2 role-conditioned responses for
bounded CPU PEFT LoRA training, merged its candidate adapters into isolated
Hugging Face checkpoints, and converted them to Q8_0 GGUFs using llama.cpp.
Later personality derivatives may use a different pinned curriculum and must
carry their own exact training and conversion receipts. These are modified,
experimental derivatives. They are not official Qwen releases,
are not endorsed by the upstream model creators, and do not establish any BT2
identity fidelity, coding improvement, or production fitness.

The BT2 repository's own source-available/proprietary terms apply to BT2-owned
source and role material; they **do not replace or revoke** the Apache-2.0
permissions and obligations applicable to the upstream Qwen model component.

Any distribution of the GGUF files must retain this change notice and include
the full applicable upstream Apache-2.0 license text and any upstream notices
required by that license. The repository source, build receipts, release
artifacts, installations, and runtime effectiveness remain distinct claims.
