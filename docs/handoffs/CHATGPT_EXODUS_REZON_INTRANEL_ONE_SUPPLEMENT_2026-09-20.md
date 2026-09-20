# ChatGPT Exodus — Rezon / Intranel / One Supplemental Retirement Checkpoint — 2026-09-20

Status: `STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT`

Restore key: `BT2_COORDINATOR::RESTORE::REZON_INTRANEL_ONE_SUPPLEMENT::20260920`

## What this retiring terminal was

This conversation was a replaceable BT2 execution terminal. It primarily instantiated One-like lead/integration/review behavior for:

- `thebrazenbeard/rezon`;
- Rezon Benchmark V1;
- exact-head hostile review of `thebrazenbeard/intranel`;
- coordination through `thebrazenbeard/chat-communication-bus`.

It did not create a new durable worker identity.

Durable logical role:
- One = BT2 lead orchestrator/integrator as defined by BT2 source.

Future persistent human interface:
- `BT2 Coordinator`.

No permanent One, Rezon, Masa, Mune, benchmark, or Intranel-reviewer chat is required.

## Repositories fresh-checked in this retirement terminal

Primary:
- `thebrazenbeard/bt2`
- `thebrazenbeard/rezon`

Secondary/material:
- `thebrazenbeard/intranel`
- `thebrazenbeard/chat-communication-bus`

Observed default-branch subjects:
- BT2 `main@30e81cadd94fae117a7f6875523c03251c7c9f6e`
- Rezon `main@e3d7a41eccb49a9f403ef66f511faef677ceec1b`
- Intranel `main@42e7d7f4358833b9f00e83cfe194b76abdf93e8a`
- Bus `main@aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`

These are observed source cuts only. Fresh-check before any effect.

## Classification

### ALREADY_DURABLE

The following work from this chat is already represented in Rezon source/PR history and must not be reconstructed from conversation memory:

- Kernel V0 hostile-hardening evolution that began around R2/R3/R4/R5/R6;
- exact RED/GREEN hostile regressions from Masa/Mune/One review cycles;
- source/build/test/review claim separation;
- non-promotional `ResultReceipt` / PLAN-only effect semantics;
- provenance/currentness/independence/admission hardening;
- Benchmark V1 deterministic replay architecture and its later fairness/ambiguity/currentness hardening;
- donor-repository research conclusions and the learned-signal firewall;
- requirement that HCAE/HyPER/hyperbolic learned/advisory mechanisms not become evidence, truth, authority, or identity oracles;
- no reasoning-superiority claim from deterministic replay alone.

The old chat-local R6 frontier is superseded as current state by later Rezon R51 work.

### HISTORICAL_EVIDENCE

This chat independently discovered and froze the Intranel fractional-timestamp precision defect.

Reviewed failed Intranel subject:
- PR #3 predecessor head: `581fd9e1719e76586607718875d73dc0a211c593`

Independent execution at that subject:
- CPython 3.12.10
- editable install PASS
- compileall PASS
- unittest discovery `112/112` PASS
- `git diff --check` PASS

Hostile defect:
- the accepted timestamp grammar allowed fractional seconds beyond Python `datetime` microsecond precision;
- distinct instants such as `.0000001Z` and `.0000002Z` collapsed during `expires_at > observed_at` evaluation;
- a semantically later expiry was rejected as equal.

Frozen One RED artifact:
- branch `one/intranel-r3-hostile-time-precision`
- test-only commit `16652db3099c938c04255c8a62fc6f542e9e11de`
- targeted result: 1 test / 1 error at the intended ordering boundary.

Durable Bus disposition:
- `bus/one-v2@6fd28e70c6a34977cab3b3b0479c55dfabb309df`
- disposition: `CHANGES_REQUESTED / HOSTILE_REREVIEW_FAIL`
- GitHub PR #3 review comment also mirrors the exact finding.

This is historical failure provenance, not a current Intranel defect claim.

### SUPERSEDES_EXISTING

Intranel PR #3 has since repaired the fractional timestamp defect.

Current observed PR #3 subject:
- branch `rezon/intranel-v1-r3-main-reconcile`
- head `27c4676d79621de6d17dd14ed4064ea5e742c107`
- tree `b94a4ab2cc73a4a34dd98306f3347deff95d495a`
- OPEN / DRAFT / UNMERGED / mergeable

Recorded repair:
- fractional seconds normatively capped to 1–6 digits;
- 7+ digits fail parser and schema;
- six-digit ordering is tested;
- docs describe an RFC3339-derived offset-aware ISO-8601 profile;
- leap seconds are explicitly not accepted.

Recorded executable evidence on exact PR #3 head:
- `115/115` tests PASS
- compileall PASS
- clean diff/readback
- additional parser/schema, state-machine, Python↔Node canonical probes recorded in PR body.

The original `581fd9e1...` hostile disposition must not be carried to `27c4676d...`.

### CURRENT INTRANEL SUCCESSOR FRONTIER

Draft PR #5:
- title: `R4: harden direct governance-array constructor boundary`
- branch `rezon/intranel-v1-r4-constructor-array-hardening`
- base `27c4676d79621de6d17dd14ed4064ea5e742c107`
- head `0338f053fa90cca66981c066180bdf706f0e8ca2`
- OPEN / DRAFT / UNMERGED / mergeable

Corrected defect:
- wire/parser `[null]` governance-array input was already fail-closed;
- the real defect was direct construction / `dataclasses.replace()` with tuples containing `None`;
- affected arrays: constraints, prohibited_effects, capabilities, provenance.

Current review evidence:
- multiple exact-head independent comments accept the bounded two-file source repair;
- recorded local full suite: `117/117` PASS;
- hosted CI is `NO-RUN / UNKNOWN` because jobs did not start;
- source-review acceptance is not hosted qualification, merge, install, deployment, or provider effect.

### CURRENT REZON FRONTIER

Observed current Rezon kernel candidate:
- Draft PR #79
- title `P0 R51: bind receipt failure summary to trace`
- branch `radar/r51-failure-summary-binding-20260919`
- head `8289914ec500a1392b10fe1a3774dee166e73b40`
- base failed R50 `91253aaad94cc3a656321186935a89791f8a08ce`
- OPEN / DRAFT / UNMERGED / mergeable

R51 control:
- failures carried by exact trace records must be represented in top-level `ResultReceipt.failures`;
- additional receipt-only scheduler/authority/unavailable failures may remain valid.

Recorded PR evidence:
- evidence-export tests `10/10` PASS;
- full repo `275/275` PASS;
- compile/diff PASS;
- accepted Benchmark R4 no-commit composition `334/334` PASS.

Recorded exact-head review:
- Project Runner review comment on `8289914e...` = `PASS_WITH_CLAIM_CEILING` for the three-file structural delta;
- it does not prove object origin, currentness, authority, distributed fencing/completion, merge, deployment, provider/model effect, or general reasoning superiority.

### CURRENT BENCHMARK FRONTIER

Accepted Benchmark R4 source used in later Rezon compositions:
- branch `rezon/benchmark-v1-r4-unknown-currentness`
- exact head `d7373867d3813d32032cb30463e54a6ddf573025`
- tree `efbfa03efa824b65379a6cb65cb7c6353733061c`

The earlier benchmark branch/tasks from this chat are historical ancestors. Future work must start from current R4/R5 design state, not from this chat's old Task-5/Task-6 frontier.

### CONFLICT

Rezon PR #79 body states that Issue #5 “remains CLOSED”.

Fresh GitHub issue readback in this retirement terminal shows:
- Rezon Issue #5 `P0: Rezon Kernel V0 executable qualification`
- state: `OPEN`

Disposition:
- preserve the discrepancy;
- do not newest-wins from prose;
- do not infer the learned-routing gate from PR body text;
- fresh-check Issue #5 directly before any learned-routing/gate/effect decision.

A durable correction comment was added to PR #79 during this Exodus.

### CHAT_DEPENDENCY / WORKER RECONSTRUCTION

No unique One identity, authority, Rezon architecture, benchmark design, Intranel finding, review obligation, or current frontier now requires this conversation.

Current BT2 Exodus consolidation candidate:
- BT2 Draft PR #35
- branch `exodus/bt2-role-interface-reconciliation-v1-20260920`
- observed head `0ea6b0167d4ea9bfd5a976737fa77471a59759a6`
- OPEN / DRAFT / UNMERGED

It reconciles:
- the 13-role durable BT2 worker map;
- exactly three persistent interfaces:
  - Vera
  - Vera Control Plane Coordinator
  - BT2 Coordinator
- source reconstruction separately from qualification/install/assignment/authority.

Older BT2 PR #26 and Bus PR #134 are now CLOSED/UNMERGED historical source candidates. Do not treat their former “preferred” labels as current.

Existing One durable recovery:
- `bus/one-v2`
- observed head before this supplemental write: `c3792422173f248ecb15be4c7f5b1488b3cfcd84`
- `checkpoints/one/ONE_EXODUS_FINAL_R2_20260919T2122-0400.md`
- `checkpoints/bt2-coordinator/BT2_COORDINATOR_ONE_EXODUS_HANDOFF_R2_20260919T2123-0400.md`

Those checkpoints remain valid historical recovery layers but must be freshened against current PR #35 and current project heads.

### LANTERN CURRENTNESS

Exact required target:
- WoWSQL `bt2-479e4ad9`

This retirement terminal attempted exact-target access before V3 preflight.
The WoWSQL tool failed internally before project metadata / SQL evidence was returned.

Therefore:
- `LANTERN_CURRENTNESS = UNKNOWN_FROM_THIS_TERMINAL`
- no V3 preflight/B0/payload/B1 cut was established;
- no Supabase, Git, project prose, memory, or prior snapshot was substituted.

Retry only the exact V3 route when Lantern currentness materially matters.

### PRIVATE_OR_OUT_OF_SCOPE

No personal, health, family, relational, sexual, credential, private autobiographical, or other unrelated Patrick material was exported into these project repositories.

## Chat-specific authority and holds

This Exodus authorizes reversible evacuation work only.

No authority is created here for:
- merge;
- canonical promotion;
- deployment/install/activation;
- provider/database mutation;
- credential/permission/ruleset change;
- destructive delete/rewrite/force push;
- paid infrastructure;
- visibility/public release change;
- model training;
- Project Settings or canonical-memory mutation;
- Slack reconnection/configuration;
- learned-routing activation;
- protected machine/device effect.

Historical Patrick-only merge/protected-effect boundaries remain in force unless a later live instruction explicitly changes them.

## Reconstruction procedure

A fresh `BT2 Coordinator` can continue without this conversation:

1. Read current installed BT2 Project Instructions.
2. Fresh-check `thebrazenbeard/bt2` main and current Exodus reconciliation PRs, starting with current PR #35 or its successor.
3. Read durable One recovery on `bus/one-v2`, but treat its embedded heads as snapshots.
4. Fresh-check `thebrazenbeard/rezon` active kernel and benchmark PRs; current observed anchors are R51 PR #79 and Benchmark R4 `d7373867...`.
5. Fresh-check Rezon Issue #5 directly because current issue state conflicts with PR-body prose.
6. Fresh-check `thebrazenbeard/intranel` PR #3 and PR #5; preserve the fractional-time RED as historical regression provenance.
7. Instantiate One/Masa/Mune/other reviewers only as ephemeral workers from durable role/assignment state.
8. Use the Bus for non-PR coordination and mirror outside-repo PR work as current Bus protocol requires.
9. If Lantern currentness is required, use exact WoWSQL `bt2-479e4ad9` V3 preflight -> B0 -> payload -> B1 and fail closed if inaccessible.
10. Stop at Patrick's current authority boundary for protected effects.

## Exact next directive

Future interface:
`BT2 Coordinator`

Directive:

`BT2_COORDINATOR::EXODUS_RESUME::FRESH_CHECK_REZON_PR79_BENCHMARK_R4_INTRANEL_PR3_PR5_ISSUE5_AND_BT2_PR35::PRESERVE_EXACT_SUBJECT_REVIEW_CEILINGS::NO_PERMANENT_WORKER_CHAT::NO_MERGE_NO_PROVIDER_EFFECT`

Priority:
1. reconcile Issue #5 live state with Rezon R51/Benchmark gating;
2. continue independent exact-head R51 review as required by current source;
3. keep Benchmark R4 evidence separate from any live-model reasoning-superiority claim;
4. preserve Intranel R3 timestamp failure as closed historical regression and treat PR #5 as the current Intranel successor;
5. update current Exodus worker reconstruction only through durable BT2/Bus candidates;
6. no permanent worker chat is required.

## Reconstruction-test result

Assuming this conversation is inaccessible, a fresh BT2 Coordinator with current Project instructions, GitHub/Bus, and authorized provider access can determine:

- this terminal's role and projects;
- the current versus historical Rezon state;
- Benchmark V1's durable progression;
- the exact Intranel defect this chat found and how it was repaired;
- the current Intranel successor frontier;
- the current Issue #5 conflict;
- One's durable reconstruction route;
- the Lantern fail-closed result;
- the authority ceiling;
- the next safe actions and communication route.

Therefore this conversation is not required infrastructure after this supplement and its Bus recovery pointer are read back.
