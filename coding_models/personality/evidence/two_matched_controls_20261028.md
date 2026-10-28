# Two personality LoRA: matched mechanism controls and donor diagnostic (2026-10-28)

**Status:** experimental, unqualified, not installed. This document records a fresh Lappy observation against the historical V1 training source; it is **not** a V2 training receipt and does not qualify any model.

## Exact inputs and isolation

- Historical clean BT2 source: `a9a6ffd27e896b530d78babd914cb6b107d81f55`.
- Clean Labyrinth scheduler source: `d9df0210761089549daeaed0cacd24181b8db962`.
- HF donor: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, local `model.safetensors` SHA-256 `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- All three Two arms: four training cases, deterministic Labyrinth schedule `001,004,002,003`, seed `74413`, `--steps 4 --max-length 2048 --threads 2`, CPU-only PEFT LoRA rank 4 on `q_proj,v_proj`. Candidate/sham use the same targets; corrupted arm rotates targets within Two's four cases. Candidate and corrupt learning rate `0.0002`; sham rate `0`.
- Existing candidate: `C:\Temp\bt2-persona-gguf-batch-20261028\two\run`. Newly isolated controls: `D:\BT2IdentityModels\bt2-two-controls-20261028-one\sham` and `...\corrupt`. These are on-host artifact paths, not Git-tracked binaries.
- Source commands: `tools/train_personality_lora.py train --identity two --arm sham|corrupt --steps 4 --max-length 2048 --threads 2 --seed 74413` with the exact source, Labyrinth, donor and new run-directory arguments above; `verify-reload --run-dir RUN_DIR --threads 2` was executed separately for each saved control.
- The source tool validates clean exact-head checkouts, verifies frozen model parameters/buffers, and refuses preexisting output directories. The historical V1 script does **not** provide the training-time config/tokenizer metadata pin added in draft PR #92; do not retrofit a V2 claim to these V1 receipts.

## Actual observations

| Arm | LoRA tensor SHA-256 after training | Four step losses | Adapter safetensors SHA-256 |
| --- | --- | --- | --- |
| Candidate, earlier | `329ca7c7341788f6d1a84ef78316a15e79c328d0c0a83017e914a21844554fbe` | 4.587366, 4.323823, 4.650092, 4.273845 | `69b9fb1024da436747694b300eea3ed6efe2c10523965765606dc2bf5357da99` (prior receipt) |
| Sham, new | `02837e24bf60e866fa965c88571860065835b3b31e4884e52a14d81da1009e17` | 4.587366, 4.326900, 4.660017, 4.290902 | `1a41f43982716b19df8eed7bf079d6244f5d09b266d3553074d470b40b8a91d7` |
| Corrupt, new | `6293d868f427401c4f813c5d3f1e97a3ed891e488a613b63109ecdd2f5e66ae4` | 4.636872, 4.653223, 4.925046, 4.939337 | `7f8d4db918960a0cafd438eb524d9cc92964cfabc4173d0801a21c54bc05b64a` |

All start with LoRA tensor digest `02837e24bf60e866fa965c88571860065835b3b31e4884e52a14d81da1009e17`. Sham ends at exactly that digest; candidate and corrupt change. Both new control adapters are 2,193,720 bytes. Each new control reports frozen parameters and persistent buffers unchanged, and separate `verify-reload` processes returned `EXACT_ADAPTER_TENSORS_RELOADED` and exit code 0. Fresh file reads independently matched both reported adapter SHA-256 digests. New training processes finished with exit code 0 (sham 95.61 s, corrupt 95.79 s). Those are **mechanism observations only**.

The within-role rotated-label arm is not an adequate identity-specific negative control: responses remain plausibly relevant to Two. Its loss is not directly comparable as a like-for-like target likelihood because the supervised answer bytes differ. A cross-role/counterfactual control and an independent behavioral holdout are still needed.

## One-case baseline diagnostic (not a score)

Using the same neutral ChatML prompt for a reserved meta-evaluation case B02, `llama-cli` Q8_0 CPU generation with `--temp 0 --seed 42 -n 160 -c 1024 -t 2 -ngl 0` loaded:

- Fresh converted unadapted donor GGUF: `D:\BT2IdentityModels\bt2-donor-q8-eval-20261028-one\qwen25coder-donor-q8_0.gguf`, 1,646,572,736 bytes, SHA-256 `c579ea9379d512c22928734b227a8f34a6120cd6784ccd3823caab34377cd1d8`.
- Earlier Two coding GGUF: SHA-256 `8e9d02b6b0ad8d4892f7ac45825263f94e267af59b0465afacc5b3285c6be51b`.
- Existing Two personality GGUF: SHA-256 `28a605b12a570280db7712539a553774c04c73e994df8fcc8f83af1635507d5b`.

All three inference processes exited 0 and gave broadly generic, partly questionable training-loss/generalization discussion. No clear hostile-systems-architect behavioral distinction was observed. Outputs were not a fully preserved, blinded or rubric-scored study; the 160-token cap truncates answers. Do not consume this as a passing held-out personality test. Coding retention, role fidelity, prompt-only superiority, and generalization all remain **UNKNOWN**.

## Host/readback and governance

On completion, Lappy had approximately 13.7 GiB physical RAM available, 42,581,245,952 bytes free on D:, two Ollama processes and one `llama-server` present, and zero remaining Two training Python processes. No shared service restart, model tag/install, protected branch merge, or release publication occurred. The unadapted donor came from an Apache-2.0-labeled upstream model card; preserve the upstream license/notices before distribution.

**Outcome:** SURVIVES for bounded real-weight-update and frozen-weight mechanism; UNKNOWN for personality training effectiveness and coding retention. Next qualify on new, independent role-contrast and coding cases with donor, older coding model, prompt-only persona control, exact-V2 train/reload/merge receipts and stronger corrupt-label arms. Labyrinth's current role here is a deterministic ungraded scheduler, not a demonstrated reasoning grader.
