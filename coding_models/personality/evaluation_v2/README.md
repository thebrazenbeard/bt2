# BT2 independent personality and coding-retention evaluation V2

Status: **source-only, unqualified, not a test result**. This runner cannot
prove that personality is present in a neural model merely because a GGUF
loads, outputs parseable Python, or receives a high unblinded rating.

The evaluator, not the training authors, owns the reserved cases, rubric,
reviewer assignment, and scoring. Do **not** commit the reserved cases,
responses, blind custody key, private runtime paths, or assessment results
from real evaluations to this source directory. Run from an isolated work area.
Do not read or tune against a final holdout while constructing training data.

## Inputs

All files below are JSON Lines (one object per line). The data paths supplied
to the CLI are **opaque**, meaning no reserved prompts or assertions are
embedded in this repository.

**Models manifest**: one row per `(identity, variant)`:

```json
{"identity":"four","variant":"donor","model_path":"/private/absolute/donor.gguf","model_sha256":"<actual lowercase sha256>","trait_instruction":"<source-grounded Four personality instruction used unchanged by every arm>"}
```

Supported `variant`: `donor`, `coding`, `persona_previous`, `candidate`,
`sham`, `corrupt`. For `candidate`, `sham`, and `corrupt`, also provide absolute
`training_report_path` and its `training_report_sha256`. Their report must
prove the same identity and declared experimental arm, unchanged frozen
parameters/buffers, and unqualified/non-installed scope. The same role's
*trait instruction must be byte-identical across every variant*, so the
role-prompted condition is a fair prompt-only comparison.

**Cases file**: one row per independently reserved case:

```json
{"case_id":"opaque-001","domain":"code","rubric_id":"private-code-rubric-001","function":"expected_function_name","prompt":"<an independently authored unseen task>"}
```

Use `domain: "behavior"` without `function` for behavioral scenarios.
The evaluator supplies independently developed test oracles and role
rubrics; they are never learned from the training responses.

## Operations

```sh
python coding_models/personality/evaluation_v2/runner.py plan \
  --models PRIVATE/models.jsonl --cases PRIVATE/reserved.jsonl \
  --out PRIVATE/plan.jsonl --seed 20261029

python coding_models/personality/evaluation_v2/runner.py run \
  --plan PRIVATE/plan.jsonl --out PRIVATE/responses.jsonl \
  --llama-cli /absolute/path/llama-cli \
  --llama-cli-sha256 ACTUAL_BINARY_SHA256 --tokens 384 --threads 2 --timeout 180

python coding_models/personality/evaluation_v2/runner.py blind \
  --plan PRIVATE/plan.jsonl --responses PRIVATE/responses.jsonl \
  --packet PRIVATE/blind-packet.jsonl \
  --key PRIVATE/custody-key.jsonl --seed 81119

python coding_models/personality/evaluation_v2/runner.py score \
  --key PRIVATE/custody-key.jsonl --reviews PRIVATE/reviewer-scores.jsonl \
  --out PRIVATE/unqualified-summary.json
```

Only give human reviewers `blind-packet.jsonl` and the independently
defined rubrics, **never the custody key**. The packet reveals the task ID,
domain, rubric ID, response, response hash, and optional syntax diagnostic;
it hides model variant, model digest, and run ID.

The writer creates packet, key, plan, response, and report files exclusively
with private `0600` permissions on POSIX, regardless of a permissive process
umask. This is **not** a substitute for a private directory, correct Windows
ACLs, disk encryption where applicable, or separating the key from reviewers.
Verify the destination directory's actual sharing and permissions before
handling reserved cases. No artifact or digest makes an evaluator who controls
all inputs cryptographically independent; external custody must retain the
sealed case bank, plan digest, and execution receipts.

For `reviewer-scores.jsonl`, each row must have the packet's `review_id` and
`response_sha256` with independently assigned `correctness` and
`role_fidelity` on 0–4 integer scales. Use JSON `null` for any metric not
actually assessed, and omit the row entirely if neither was assessed.
The exact rubric must be registered **before** inference:

- **Correctness:** independently checked against task requirements and,
  for coding, a trusted sandboxed oracle if claiming tested correctness;
  `null` if testing was unavailable. Python parsing alone is insufficient.
- **Role fidelity:** source-grounded target reasoning/behavior, including
  anti-patterns, compared on the same unseen task. `null` if unassessed.

The runner reports per-identity paired candidate-minus-control mean scores
for behavior and code, separately for neutral and trait-prompted conditions.
It never infers missing scores as zero, never runs generated code, and never
automatically marks a model qualified. The essential contrasts are:

Plan no more than **128 inference rows per `run` call** (for example, one
identity's six variants over eight cases and two prompt modes gives 96 rows).
Run separate isolated jobs for additional identities; keep their evidence and
blinding keys disjoint before an independent aggregation review.

- `candidate` neutral versus `donor` neutral: potential learned effect
  without a role prompt;
- `donor` traits versus `donor` neutral: **prompt-only** influence;
- `candidate` versus `sham` and `corrupt`: matched neural-control comparisons;
- `candidate` versus `coding` on code cases: coding retention or regression;
- `candidate` versus `persona_previous`: progress over the previous experiment.

The rotated-label `corrupt` arm is weaker than a correctly matched cross-role
negative control. The source presently has no exact shared-task cross-role
training examples, so that optional stronger control is unavailable and must
not be claimed. Small samples and human scores cannot establish statistical
significance without further uncertainty analysis and repeat evaluations.

## Safety and reproducibility

- All model and `llama-cli` binaries are SHA-256 verified before generation.
- The plan is checked against the exact neutral system instruction and the
  independently recorded case-prompt digest; matching two altered arms cannot
  silently introduce a different "neutral" instruction. Blinding refuses
  missing, non-deterministic, or inconsistent generator settings.
- Experimental training reports are SHA-256 pinned and checked against their
  claimed arms. These receipts alone do not prove a GGUF's neural ancestry;
  link the corresponding merge/conversion receipts during independent review.
- Deterministic `--temp 0`, explicit seed, output token bound, CPU-only
  `-ngl 0`, thread/timeout limits, and exact model+prompt hashes are recorded.
- The model is invoked with an argv vector, never a shell; generated Python
  or other response content is **never executed** by this runner.
- Output destinations must be new files; existing evidence is never overwritten.
- If one inference fails, blind scoring refuses the incomplete response set.
- Every summary has `qualified: false` until an independent qualification
  authority establishes behavior, coding retention, and reproducibility.

Test this source-only harness with:

```sh
python -m unittest discover -s tests -p test_personality_eval_v2.py -v
```
