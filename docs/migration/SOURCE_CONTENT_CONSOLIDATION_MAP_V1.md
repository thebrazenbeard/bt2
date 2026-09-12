# BT2 Source Content Consolidation Map V1

Status: **MIGRATION CLASSIFICATION / NO CUTOVER**

Date: 2026-09-10

Owner: One

Purpose: classify the frozen migration source cuts by semantic destination before copying bytes into the canonical BT2 platform. This prevents source-repository boundaries from being reproduced accidentally inside `bt2` and prevents historical material from becoming active policy merely because it was imported.

## Classification vocabulary

- `CANONICALIZE` — semantics belong in active BT2 and should be represented in the new canonical platform.
- `COMPATIBILITY_UNTIL_QUALIFIED` — preserve source interface/artifact until canonical replacement demonstrates equivalent behavior and recovery.
- `HISTORICAL_ONLY` — preserve as evidence/provenance; do not make active policy/runtime state.
- `SOURCE_REFERENCE` — preserve exact source binding; source implementation informs the new design but should not be copied as the active provider-specific implementation.
- `PENDING_EVIDENCE` — insufficient evidence to assign a stronger disposition yet.

A classification is about semantic destination, not whether a file is valuable. `HISTORICAL_ONLY` can be essential evidence.

## 1. build-team-2.0

Frozen cut:
- `main@ec2987e45f64a588ac92f6cae9964cb3725b9485`
- tree `8db9f54b59e908f0ad35fbf6bf2f2ff8b48e639f`

### CANONICALIZE

- permanent numbered-agent role definitions after reconciliation with Patrick's new One-led topology;
- shared evidence/currentness/authority discipline;
- generic continuity semantics that survive migration;
- valid versioned role-training packages and package integrity machinery;
- worker-specific responsibilities that remain part of the current workforce.

### HISTORICAL_ONLY

- the older active model of ten coequal facets, because Patrick has explicitly replaced it with One as primary/orchestrator and Nine numbered subagents;
- superseded Working Laws/protocol revisions;
- obsolete Slack-era coordination assumptions;
- stale assignments, target SHAs, leases, and project-specific work state.

### DISTRIBUTED SOURCE RECOVERY

The old `main` training/continuity registry omitted Two, Three, Seven, and Eight. Exact versioned training packages were recovered separately from historical branches/Project Achilles. The main-branch omission is therefore historical integration debt, not evidence of package absence.

## 2. BugOps

Frozen cut:
- `main@39eb19bcf7669466c22703fbae7cc226bd44f714`
- tree `16209d56150f7341f39492f66dfa52263437575c`

Observed source content includes:
- `.github/ISSUE_TEMPLATE/behavioral-error-report.md`
- `REPORTING_STANDARD.md`
- `reports/BUG-0001...BUG-0004`

### CANONICALIZE

- defect intake identity and response-loss-safe convergence;
- BugOps severity semantics, including preservation of `SEV-0..SEV-3` meaning;
- evidence/correction/regression/review/readback requirements;
- closure qualification separate from a mutable status label;
- reopen history and non-erasure of prior closure evidence;
- incident reporting structure useful to future BT2 bugs.

### HISTORICAL_ONLY

- individual BUG-0001 through BUG-0004 reports as case evidence unless a fresh migration review establishes an unresolved current defect;
- old repository-specific issue/branch/PR locators as historical provenance.

### COMPATIBILITY_UNTIL_QUALIFIED

- source report format and lifecycle interpretation until canonical BugOps round-trip tests prove no semantic loss.

## 3. WIP

Frozen cut:
- `main@12a7c23dbe0482fd7bfe63659e54526778efef1e`
- tree `e2527117c7d25f92d2e6aa7365ae8b3d3b9a3c08`

Observed source families include protocols, JSON schemas/templates, recovery demo, tests, and integration instructions.

### CANONICALIZE

- workspace identity and checkpoint generation/CAS;
- append-only checkpoint lineage;
- handoff/resume semantics;
- external-effect journal with `PREPARED`, `ATTEMPTED`, `VERIFIED`, `FAILED`, `AMBIGUOUS`, and `RECONCILED` history;
- inspect-before-retry for ambiguous effects;
- recovery after replaceable runtime/session loss;
- distinction between work-state recovery and external-effect ambiguity.

### COMPATIBILITY_UNTIL_QUALIFIED

- WIP JSON schemas/templates and recovery-demo fixtures until canonical database/API recovery demonstrates equivalent behavior;
- WIP protocol documents as a comparison oracle during migration.

### HISTORICAL_ONLY

- old workspace registry rows and example/demo state as runtime state; preserve them only as fixtures/evidence.

## 4. Project Lantern Git source

Frozen source binding:
- `feature/lantern-material-universe-v1@d0e05365883d8f670030fb1a1ff5fcd847937a77`
- tree `3b155a88967f2f7a0f4ad6fa7b32ce3cbac73da0`

Observed source includes material-universe SQL, benchmark artifacts, canonicalization/contracts/IDs, store/projection/trace/portability code, CLI/runtime helpers, and tests.

### CANONICALIZE

- governed material identity and provenance semantics;
- canonical/semantic/source digest separation;
- accepted-profile lineage and policy binding;
- admission receipts and producer authorization history;
- runtime-visible governed material cut;
- duplicate-key/canonicalization discipline;
- source/runtime evidence separation;
- stable-cut read protocol and relevant benchmark/qualification concepts.

### SOURCE_REFERENCE

- Supabase-specific SQL schema and provider-specific store implementation. These define source behavior and must remain preserved, but the active BT2 backend is WoWSQL/PostgreSQL and is being rebuilt provider-neutrally under Two's source-controlled database package.

### COMPATIBILITY_UNTIL_QUALIFIED

- Lantern read/admission facade and benchmark fixtures until canonical BT2 material read + admission/concurrency behavior is qualified.

### HISTORICAL_ONLY

- source-specific obsolete provider wiring after equivalent canonical behavior is proven and retirement is explicitly accepted.

## 5. Project Achilles

Frozen cut:
- `main@dbf9ceb2391567463d864198405c9b5d1e77db09`
- tree `1cd715bef0d2a33478d3a635bcc05155c95ab4f9`

Observed source is concentrated in `PROTOCOL_V2_CURRENT.md` and the complete `training/roles/seven/v1.0.0` package plus checkpoint tooling.

### CANONICALIZE

- Seven's security/adversarial role competence and exact versioned training source;
- threat-modeling, secure-review, authority/escalation, retry ambiguity, finding-quality, and continuity disciplines that remain compatible with current BT2 governance;
- package integrity/checksum rules.

### PENDING_EVIDENCE

- actual Seven BASE_READY/qualification state. Package presence and qualification exercises/rubric do not prove an evaluator PASS occurred.

### HISTORICAL_ONLY

- obsolete repository-level role boundaries if superseded by the new canonical topology; retain exact source package semantics as training-version provenance.

## 6. Masamune

Frozen cut:
- `collab@af20ff29a8419c20bd51ac4e731b670d505a452b`
- tree `a76e3aac899a24f26af77454109e4a06978f8c30`

Source contains only `README.md` and `PROTOCOL_V2_CURRENT.md`.

### CANONICALIZE

Preserve the paired Masa/Mune execution doctrine:
- evidence/root-cause/independent-review/regression rigor remains intact;
- a specific current assignment authorizes bounded reversible work and necessary reversible setup;
- Class 0 read/inspect/reproduce proceeds;
- Class 1 assigned isolated workspace/branch/test setup proceeds;
- Class 2 shared mutable state resolves one writer;
- Class 3 consequential protected effects require exact authority unless already expressly granted;
- Masa may reproduce/isolate before final remediation authority is needed;
- Mune's exact-subject verification does not turn ordinary setup into recursive permission blocking;
- repository-local stewardship remains respected.

This becomes the execution protocol of the Masa+Mune paired unit, not another top-level governance system.

## 7. Hephaestus

Frozen cut:
- `main@78f6f22a0e5d14617855006a8383765589ac8c67`
- tree `80eb19e26ff9b82f8c2eb4126c5b4e87a2318ce6`

Observed source includes operating/governance/continuity docs, Project-engineering knowledge, state/checkpoints, qualification packet, training ledger, two holdout evaluations, templates, and work state.

### CANONICALIZE

- Hephaestus as an independent agent unit rather than a numbered subagent;
- native ChatGPT Project-engineering competence and operating doctrine;
- qualification evidence with exact scope limits;
- continuity/checkpoint semantics that remain valid under the generic BT2 continuity layer;
- useful working-chat bootstrap/state templates after normalization.

### QUALIFICATION EVIDENCE — SUPPORTED

Unlike Two/Three/Seven/Eight package discovery, the frozen Hephaestus source contains multiple mutually consistent qualification artifacts:
- `state/checkpoints/CHECKPOINT_0004_QUALIFIED.md` => `qualification_state: QUALIFIED`;
- `training/QUALIFICATION_PACKET.md` => custom external evaluator `QUALIFIED`;
- `training/HOLDOUT_2_EVALUATION.md` => fresh-branch holdout `PASS`, final training-program `QUALIFIED`;
- `training/TRAINING_LEDGER.md` => curriculum/capstones/holdouts and final `QUALIFIED`.

This supports migration of a qualification-evidence subject after the canonical training schema is hardened. It does NOT prove live deployment, installation, or surface qualification; the source explicitly reports zero verified runtime project installations for the fictional capstone.

### HISTORICAL_ONLY / REORIENT BEFORE ACTIVE

- `work/ACTIVE_WORK.md`, `work/BACKLOG.md`, `state/CURRENT.md`, and mutable working-state checkpoints must not be frozen into the new platform as current simply because they were current at the source cut. Import as history first; fresh reorientation determines later current state.

## 8. Supabase Project Lantern runtime database

Source target:
- `agvhmutlrolbaijzlbqk`

Stable governed material cut at migration capture:
- profile digest `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- policy digest `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`
- exact visible members: 2

Other BT2-owned source schemas observed include `bug_ops`, `governance`, `r9a0_coordination`, and `r9a0_governance`.

### CANONICALIZE

- accepted governed material rows + receipts/lineage under a verified migration;
- active semantics from source schemas only when separately mapped and accepted into the new canonical model.

### HISTORICAL_ONLY

- obsolete R9A0/Slack-era coordination/governance rows unless independently reauthorized;
- expired/revoked producer authority as authority history, never current authority merely because restored.

### SOURCE_REFERENCE

- Supabase service-specific RLS/extensions/provider assumptions. The target access/security model must be qualified for WoWSQL rather than copied mechanically.

## 9. Canonical repository destination map

Target shape is semantic rather than source-repository-shaped:

```text
bt2/
  agents/
    numbered/              # One + numbered specialists, with One-led topology
    masa-mune/             # paired debugger/reliability unit
    hephaestus/            # independent Project-engineering unit
  training/                # consolidated package/qualification registry and versioned packages
  continuity/              # generic continuity protocol + agent bindings
  recovery/                # WIP-derived workspace/effect recovery contracts
  bugops/                  # defect-specific reporting/lifecycle layer
  materials/               # Lantern-derived governed-material contracts/facade
  governance/              # current topology/authority/assignment semantics
  database/                # source-controlled WoWSQL/PostgreSQL schema+migrations+tests
  docs/migration/          # source cuts, mappings, receipts, retirement gates
  archive/                 # preserved historical artifacts where file-level preservation is useful
```

Exact directory names remain implementation choices until merged, but the subsystem boundaries above are the intended semantic separation.

## 10. Retirement rule

No legacy repository/schema/API becomes logically superseded until:

1. exact source cut and provenance are preserved;
2. all required active semantics map to canonical subjects;
3. required historical objects/rows have membership/count/digest evidence;
4. compatibility/replay/acceptance tests pass;
5. no active workflow writes only to the legacy surface;
6. new-system rollback/recovery has been demonstrated;
7. explicit authorized cutover/retirement acceptance exists.

Logical supersession never requires deleting the historical source repository.
