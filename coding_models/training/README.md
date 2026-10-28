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

## Experimental CPU LoRA mechanism pilot

`tools/train_identity_lora_pilot.py` implements an intentionally bounded CPU-only PEFT LoRA mechanism test against a **separately obtained, locally verified** HF safetensors donor. It refuses missing/mismatched base weights, existing run directories, missing role profiles, and unbounded steps. Only assistant-response tokens receive supervised labels; instruction tokens are masked. The main `train` command saves a separate safetensors adapter and a source/evidence report. Run the `verify-reload` command in a **fresh Python process** to compare numerical LoRA tensor values.

```sh
python tools/train_identity_lora_pilot.py train \
  --identity one --base-dir LOCAL_PINNED_HF_BASE \
  --base-sha256 VERIFIED_64_HEX_SHA256 \
  --source-commit EXACT_BT2_GIT_SHA \
  --run-dir NEW_EMPTY_PARENT/one-candidate --arm candidate --steps 2 --threads 2
python tools/train_identity_lora_pilot.py verify-reload \
  --run-dir NEW_EMPTY_PARENT/one-candidate --threads 2
```

Separate `--arm sham` (same-exposure zero learning rate) and `--arm corrupt` (rotated target responses) runs are available for later matched controls. These are **not** completed by the candidate run. Even if the saved/reloaded LoRA tensors match, there is no code-correctness or role-behavior improvement claim without independent evaluation. `train` does not create GGUF, install an Ollama tag, merge weights, mutate the base donor, or train all identities. The current small synthetic cases exist only to establish bounded plumbing before any source-reviewed larger curriculum.

## Actual weights and GGUF sequence

The identified Lappy inference donor is `qwen2.5-coder:1.5b-instruct-q8_0` (~1.6 GB) under Ollama. The source Qwen/Qwen2.5-Coder-1.5B-Instruct HF checkpoint is about 3.09 GB in safetensors; it is **not interchangeable** with a Q8_0 GGUF for gradient training. Neither the presence of an Ollama blob nor these JSON files establishes a compatible local HF checkpoint or any trained LoRA.

1. Record the exact HF donor revision, safetensors/tokenizer digests, software versions, base GGUF digest and license. Use an isolated workspace; never overwrite Ollama's shared base blobs.
2. Have the proposed instruction/answer cases reviewed. Add significantly more independent role-specific code tasks and a truly reserved evaluator authored and scored separately. Do not train on the development/evaluation answers.
3. Run a single-role, bounded HF/PEFT LoRA pilot with before/after tensor digests, unchanged frozen-weight checks, same-exposure zero-update and corrupted-label controls, fixed seeds, and save/reload verification. Measure CPU/RAM/VRAM and elapsed time. Replicate before scaling to 13 identities.
4. Evaluate actual code outputs and role adherence against baseline and prompt-only variants, plus regressions on general coding tasks. Labyrinth can provide controlled task and lifecycle machinery, but its current `train-hf` uses a <=1 GiB safetensors ceiling and numeric maze answers; extending it to this Qwen 1.5B coding target and role data requires reviewed code changes and separate qualification.
5. Once real compatible LoRA adapters exist, merge each adapter with the **matching pinned HF base** using PEFT, convert merged HF weights with llama.cpp `convert_hf_to_gguf.py`, then quantize with `llama-quantize`, or use a qualified `convert_lora_to_gguf.py` + `llama-export-lora` path. Verify by loading each output in an isolated runtime and evaluating against its named identity's baseline. Only then call it a single, identity-adapted GGUF.
6. Preserve model digests, training/evaluation receipts, source refs and exact runtime state separately. Store large model artifacts outside ordinary Git history; decide independently whether to use Git LFS or releases. Do not label any trained artifact active or qualified solely because its file exists.

### Executed One mechanism pilot — 2026-10-28

The separate, isolated Python 3.11 environment on Lappy trained **One** against the pinned Hugging Face `Qwen/Qwen2.5-Coder-1.5B-Instruct` safetensors using CPU PEFT LoRA for **two optimizer steps**. It completed a fresh-process adapter reload check and two matched experimental arms: a zero-learning-rate sham with unchanged trainable tensor digest, and a rotated-label arm with different resulting digest. The candidate adapter was merged into a newly written HF checkpoint and converted to **one 1,646,572,704-byte Q8_0 GGUF**, SHA-256 `297f71992ff92092dd3e0e373084c455cc30f093c4e27aac1bb14cbc31c33dd6`. A local `llama-cli` CPU inference smoke produced a valid two-line Python addition function. See [`pilots/one_qwen25coder_cpu_lora_q8_0_20261028.json`](pilots/one_qwen25coder_cpu_lora_q8_0_20261028.json) for exact source and artifact digests, controlled observations, and limitations.

This establishes actual adapter update, serialization, HF merge, GGUF conversion, and local loading, **not** improved coding performance or faithful identity behavior. The model file is kept in an isolated Lappy experiment workspace, outside Git; no shared Ollama base was modified, no tag installed, and no identity activated. Labyrinth's existing numeric maze trainer was **not** used for this coder run; a suitably extended Labyrinth evaluation path and independent role holdouts are still needed before qualification.

### Remaining twelve experimental builds — 2026-10-28

The isolated batch builder [`tools/build_identity_gguf_batch.py`](../../tools/build_identity_gguf_batch.py) then trained a **separate two-step CPU LoRA**, reloaded its saved adapter in a new process, merged it with the same pinned HF donor, converted the merged checkpoint directly to Q8_0 GGUF, and loaded the GGUF using `llama-cli` for each of **Two, Three, Four, Five, Six, Seven, Eight, Nine, Thirteen, Masa, Mune, and Hephaestus**. The builder verifies source/donor/converter hashes, reserves disk headroom, requires unique output directories, and stores per-identity run reports, log files, and receipts.

All twelve receipts report `smoke_exit_code=0`, two optimizer steps, changed trainable LoRA tensor hashes, and a non-installed/non-qualified state. All twelve GGUF paths and sizes were observed on disk, and their reported SHA-256 digests are distinct. The One pilot and [twelve preserved batch receipts](builds/receipts/) are indexed in [`builds/gguf_q8_0_batch_20261028.json`](builds/gguf_q8_0_batch_20261028.json). Files are held outside ordinary Git objects in isolated Lappy experiment directories; the manifest does not imply downloadable release assets.

**This is a mechanism demonstration only.** The full batch has no completed matched sham/corrupt-label arms, no blind code or role-identity scoring, no direct comparison against the unadapted donor or prompt-only variants, and no installation. Two optimizer steps against synthetic candidate responses cannot establish that these named models actually behave like their BT2 roles. The 39 public evaluation drafts are a design aid, not a substitute for independent evaluation. Preserve exact artifacts and provenance before any future qualification or controlled Labyrinth extension.
