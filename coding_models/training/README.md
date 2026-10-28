# BT2 identity LoRA data: unqualified candidates

`cases/*.json` contains 13 sets of **synthetic, source-grounded candidate** coding conversations. Each identity has four training examples and two separate development examples. They are not authenticated expert labels, a blind exam, trained adapters, or proof of role competence. The development split is visible in Git; it must not be represented as an independent holdout after tuning against it.

The files can be validated and exported as chat-format JSONL:

```sh
python tools/identity_sft_candidates.py validate
python tools/identity_sft_candidates.py export --identity one --split train
python tools/identity_sft_candidates.py export --identity one --split dev
python -m unittest discover -s tests -p test_identity_sft_candidates.py
```

Export writes to standard output only. Redirect the output to a *new*, separately managed training-artifact directory if a reviewed training run is authorized. The output is intended for a later Hugging Face/PEFT SFT pipeline, not for direct use as Labyrinth's current `train-hf` arithmetic-answer dataset.

## Actual weights and GGUF sequence

The identified Lappy inference donor is `qwen2.5-coder:1.5b-instruct-q8_0` (~1.6 GB) under Ollama. The source Qwen/Qwen2.5-Coder-1.5B-Instruct HF checkpoint is about 3.09 GB in safetensors; it is **not interchangeable** with a Q8_0 GGUF for gradient training. Neither the presence of an Ollama blob nor these JSON files establishes a compatible local HF checkpoint or any trained LoRA.

1. Record the exact HF donor revision, safetensors/tokenizer digests, software versions, base GGUF digest and license. Use an isolated workspace; never overwrite Ollama's shared base blobs.
2. Have the proposed instruction/answer cases reviewed. Add significantly more independent role-specific code tasks and a truly reserved evaluator authored and scored separately. Do not train on the development/evaluation answers.
3. Run a single-role, bounded HF/PEFT LoRA pilot with before/after tensor digests, unchanged frozen-weight checks, same-exposure zero-update and corrupted-label controls, fixed seeds, and save/reload verification. Measure CPU/RAM/VRAM and elapsed time. Replicate before scaling to 13 identities.
4. Evaluate actual code outputs and role adherence against baseline and prompt-only variants, plus regressions on general coding tasks. Labyrinth can provide controlled task and lifecycle machinery, but its current `train-hf` uses a <=1 GiB safetensors ceiling and numeric maze answers; extending it to this Qwen 1.5B coding target and role data requires reviewed code changes and separate qualification.
5. Once real compatible LoRA adapters exist, merge each adapter with the **matching pinned HF base** using PEFT, convert merged HF weights with llama.cpp `convert_hf_to_gguf.py`, then quantize with `llama-quantize`, or use a qualified `convert_lora_to_gguf.py` + `llama-export-lora` path. Verify by loading each output in an isolated runtime and evaluating against its named identity's baseline. Only then call it a single, identity-adapted GGUF.
6. Preserve model digests, training/evaluation receipts, source refs and exact runtime state separately. Store large model artifacts outside ordinary Git history; decide independently whether to use Git LFS or releases. Do not label any trained artifact active or qualified solely because its file exists.

Lappy's currently probed `py` environment has CPU-only PyTorch despite a 4 GiB RTX 3050. The installed Labyrinth HF pilot has no direct >1 GiB path for this donor. A separate GPU-enabled environment or a measured CPU pipeline is a prerequisite to responsible full-scale training. No training, merge, GGUF output, install, or model-quality improvement is claimed by this package.
