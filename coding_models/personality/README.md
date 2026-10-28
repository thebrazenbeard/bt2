# BT2 source-grounded operational personality conditioning — experimental

Each of the 13 role dossiers in `cases/*.json` contains 3–5+ sourced behavioral
tendencies and six **synthetic, unqualified** coding conversations (four
TRAIN, two public DEV). The 52 train and 26 dev cases target observable
professional dispositions, not inner feelings, biological life, personal
histories, identity continuity, self-awareness, or new permissions. A model
responding in a role's style is not evidence it *is* that durable identity.

| Identity | Target behavioral disposition (inference from role source) |
| --- | --- |
| One | Measured integrator, even-handed synthesis, calm coordination |
| Two | Constructive, invariants-first architectural skepticism |
| Three | Disciplined state and transition steward |
| Four | Precise reconstruction, complete documentation and packaging |
| Five | Forensic independent custody, calibrated claims and stopping |
| Six | Calm operator, resource-aware and ambiguity-tolerant |
| Seven | Proportionate independent security skepticism |
| Eight | Pragmatic economy without amputating obligations |
| Nine | Exact reproducibility and adversarial, fair acceptance tests |
| Thirteen | Independent, concrete false-authority correction challenges |
| Masa | Curious, hypothesis-revising causal debugger |
| Mune | Fair, independent hostile verifier and positive-control advocate |
| Hephaestus | Precise, minimally corrective, decisive authorized repair |

Source refs and trait classification (`SOURCE` vs `INFERENCE`) live in each
dossier. Current BT2 source/role contracts take precedence over historical
presentation labels (notably Four's obsolete creative persona portrayal).

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
updates using these role cases and each profile's positive/negative behavioral
guidance, while importing the **ungraded deterministic
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
  --steps 4 --max-length 1536 --threads 2
python tools/train_personality_lora.py verify-reload \
  --run-dir NEW_EMPTY_PARENT/one-persona-candidate --threads 2
```

An optional zero-update `--arm sham` and rotated-label `--arm corrupt` each
require **separate output paths** and equivalent case exposure. Running the
candidate alone is not a matched controlled study. Training updates a
separate adapter, not the previously produced Q8_0 GGUFs; a fresh, verified
merge/conversion and runtime check is needed for a new combined model file.
The opt-in trainer checks untouched frozen neural weights, persistent buffers,
the HF donor, and the exact pinned source checkouts after optimization before
saving the adapter; those checks do not demonstrate behavioral improvement.

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
  --steps 4 --max-length 2048 --threads 2 --min-free-gib 20
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
