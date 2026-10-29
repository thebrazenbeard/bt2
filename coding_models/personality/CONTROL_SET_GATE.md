# Matched personality control receipt gate (experimental)

Run the donor-identical candidate, zero-learning-rate sham and weak rotated-label
control separately, with the **same identity, seed, source heads, donor SHA,
schedule, tokenizer instruction, CPU dtype, checkpointing setting, limits and
LoRA initialization**. Their output paths must be different and previously absent.

After all three runs have completed and each adapter has reloaded successfully:

```bash
python tools/verify_personality_control_set.py \
  --candidate /absolute/experiment/one-candidate \
  --sham /absolute/experiment/one-sham \
  --corrupt /absolute/experiment/one-corrupt
```

This static gate rehashes adapters and PEFT configurations, checks frozen-state
receipts, schedules and per-step losses, rejects different donor/seed/prompt
conditions, and rejects a sham reporting updated trainable tensors. It is not
an inference benchmark and **cannot prove** that the frozen donor was really
unchanged when producing an untrusted report. Runtime logs, independently
verified process provenance and model evaluation remain separate evidence.

The `corrupt` arm rotates responses among different prompts *within the same
role*. It is a weak negative-label control. The stronger `crossrole` training
arm requires explicit same-task `contrastive_group` examples; the current
13-role corpus does not supply those groups. Do not call a rotated-label result
equivalent to a matched same-task different-role corruption control.

`--gradient-checkpointing` is an **optional**, non-reentrant activation-memory
tradeoff. It is not hardware-qualified on Lappy, may slow CPU training, and
must be set identically for all arms. Default remains disabled. No GGUF is
installed, no release is published, and no model is behaviorally qualified by
this gate.

The training preflight also verifies the **working bytes of every tracked file**
in the pinned BT2 and Labyrinth checkout against that commit's Git blobs. Plain
`git status` alone can miss source changes hidden by `assume-unchanged` or
`skip-worktree`. For an exact-source run, checkout text must retain the tracked
bytes (including line endings); an automatic Windows CRLF rewrite fails closed.
