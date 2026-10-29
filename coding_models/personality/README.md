# BT2 original-trait personality conditioning — experimental

The model goal is to preserve each identity's **originally designated cognitive
personality** while retaining useful coding competence. Engineering assignment
and personality are separate axes; a later narrow role contract does not
silently redefine the personality. See
[`USER_TRAIT_CORRECTIONS_20261028.md`](USER_TRAIT_CORRECTIONS_20261028.md)
for Patrick's explicit corrections, the pinned original ten-facet source, and
Masa/Mune/Hephaestus source precedence.

Each of the 13 dossiers in `cases/*.json` is a synthetic and **unqualified**
training proposal. The public DEV cases are not a sealed independent holdout.
Training targets observable reasoning/interaction tendencies, not inner feelings,
biological life, personal histories, identity continuity, self-awareness, or
new permissions. A model responding in a style does not prove that it *is*
the durable identity or has generalized that style.

| Identity | Intended cognitive disposition, not observed model behavior |
| --- | --- |
| One | Integrative, measured, decisive |
| Two | Structural, abstract, systems-first |
| Three | Concrete, energetic, implementation-first |
| Four | Creative dreamer; curious, unconventional, possibility-seeking (Patrick-confirmed) |
| Five | Precise, evidence-driven, quantitative |
| Six | Human-centered, perceptive, plainspoken |
| Seven | Scientific genius (Patrick-confirmed target; subject-matter competence must be evaluated) |
| Eight | Pragmatic economy without amputating obligations |
| Nine | Exact reproducibility and adversarial, fair acceptance tests |
| Thirteen | Broadly skeptical, independent reviewer; difficult to impress (Patrick-confirmed) |
| Masa | Causal debugging specialist; fuller temperament remains inferred |
| Mune | Independent verification specialist; fuller temperament remains inferred |
| Hephaestus | Native ChatGPT Project engineer; fuller temperament remains inferred |

Each dossier distinguishes `USER`, `SOURCE`, and `INFERENCE` evidence where
supported by the validator. Previously generated GGUFs were conditioned on
the older duty-heavy dossiers; they are **superseded candidates for personality
purposes**, not automatically deleted, repaired, or retrained by these source
changes. The archived ten facets share collective state and final voice; no
private autobiographical identities are inferred from separate model files.

## Validation

```sh
python tools/validate_personality_sft.py
python -m unittest discover -s tests -p test_personality_training.py
```

These check exact roster, local source links, split counts, unique tasks,
training/development separation, and assistant-only label masking.
The development split is public and cannot function as a sealed holdout.

## Labyrinth scheduling and actual PEFT training — opt-in

The separate `tools/train_personality_lora.py` does real CPU PEFT LoRA gradient
updates using these personality cases. By default, `--instruction-mode neutral`
uses the same role-free system instruction across identities, to help isolate
what the supervised responses teach the neural weights from what a personality
prompt elicits. An explicit `--instruction-mode traits` uses each dossier's
positive/negative observable behaviors, without injecting the newer engineering
job title or objective. Both modes import the **ungraded deterministic
schedule** from pinned Labyrinth source. The scheduler neither grades role
performance nor promotes a curriculum; this is distinct from Labyrinth's
numerical `train-hf` command, which rejects this 3.09 GB donor and only trains
integer maze answers.

Labyrinth scheduler source candidate:
`thebrazenbeard/labyrinth@d9df0210761089549daeaed0cacd24181b8db962`,
[draft PR #53](https://github.com/thebrazenbeard/labyrinth/pull/53).
This training path must run from clean, exactly pinned BT2 and Labyrinth
checkouts, with a separately verified local HF base donor and an **entirely
new** output directory for each identity and arm:

```sh
python tools/train_personality_lora.py train \
  --identity one --source-commit EXACT_BT2_PERSONA_SOURCE_COMMIT \
  --labyrinth-dir CLEAN_PINNED_LABYRINTH_CHECKOUT \
  --labyrinth-commit d9df0210761089549daeaed0cacd24181b8db962 \
  --base-dir VERIFIED_HF_BASE --base-sha256 VERIFIED_SAFETENSORS_SHA256 \
  --run-dir NEW_EMPTY_PARENT/one-persona-candidate --arm candidate \
  --steps 8 --max-length 2048 --threads 2 --instruction-mode neutral
python tools/train_personality_lora.py verify-reload \
  --run-dir NEW_EMPTY_PARENT/one-persona-candidate --threads 2
```

An optional zero-update `--arm sham` and rotated-label `--arm corrupt` each
require **separate output paths** and equivalent case exposure. Running the
candidate alone is not a matched controlled study. Training updates a
separate adapter, not the previously produced Q8_0 GGUFs; a fresh, verified
merge/conversion and runtime check is needed for a new combined model file.
An additional **opt-in experimental** `--cpu-dtype bfloat16` loads the frozen
donor at lower precision and requires float32 trainable LoRA adapters. The
default remains `float32`; BF16 has not been qualified on Lappy with this full
model, and smaller tensor storage alone does not guarantee safe host memory,
acceptable runtime, or model quality. Check live resources before any run.
The opt-in trainer checks untouched frozen neural weights, persistent buffers,
the HF donor, and the exact pinned source checkouts after optimization before
saving the adapter; those checks do not demonstrate behavioral improvement.
For new runs, training report schema V2 also pins the required HF configuration
and tokenizer files plus recognized optional tokenizer metadata, **and pins
`adapter_config.json`** along with adapter weight bytes. Reload, merge, and
GGUF batching reject altered PEFT configuration, including changed LoRA
scaling. Historical V1 and unpinned V2 receipts remain archival evidence but
are not accepted by the stricter merge path. The optional `--arm crossrole`
requires exact same-task, cross-role training groups; the present dossiers
contain none, so it must not be claimed as a runnable control.

## Separate merged GGUF artifacts (experimental)

`tools/merge_personality_lora_hf.py` accepts only a source-pinned candidate
adapter whose trainable tensors changed and frozen parameters/buffers did not.
It rechecks the donor, adapter, dataset, receipt, and source checkouts and
merges with `PEFT merge_and_unload(safe_merge=True)` into a *new* Hugging Face
directory; no existing model is overwritten.

`tools/build_personality_gguf_batch.py` sequentially runs training, a fresh
adapter reload, that source-checked merge, `llama.cpp` Q8_0 conversion, and a
simple offline coding smoke for an explicitly selected identity roster. It
requires clean exact BT2, Labyrinth, and converter Git checkouts, a verified
local donor, free-space reserve, and new isolated output directories. Example
argument shape (replace placeholders with verified local paths and digests):

```sh
python tools/build_personality_gguf_batch.py \
  --bt2-dir CLEAN_PINNED_BT2 --source-commit EXACT_BT2_PERSONA_SOURCE_COMMIT \
  --labyrinth-dir CLEAN_PINNED_LABYRINTH \
  --labyrinth-commit d9df0210761089549daeaed0cacd24181b8db962 \
  --base-dir VERIFIED_HF_BASE --base-sha256 VERIFIED_DONOR_SHA256 \
  --llama-cpp-dir CLEAN_PINNED_CONVERTER --converter-commit EXACT_CONVERTER_COMMIT \
  --llama-cli VERIFIED_LLAMA_CLI --output-root NEW_PERSONA_BATCH_ROOT \
  --identities one two three four five six seven eight nine thirteen masa mune hephaestus \
  --steps 8 --max-length 2048 --threads 2 --min-free-gib 20
```

These are experiment-building commands, not installation or personality
qualification commands. A generated GGUF is a distinct combined weight file,
but that alone does not establish behavioral role fidelity or model quality.

**Evidence ceiling:** LoRA tensor updates/reloads and training loss are
mechanism evidence only. Before declaring faithful personality conditioning,
compare exact candidate GGUFs to the old coding GGUFs, the donor, and a
prompt-only role configuration with separately authored blind behavioral
rubrics; independently check code correctness and regressions. No source
artifact by itself installs a model, grants authority, or proves effect.
