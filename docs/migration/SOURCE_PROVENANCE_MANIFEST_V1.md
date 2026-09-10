# BT2 Canonical Source Provenance Manifest V1

Status: ACTIVE MIGRATION EVIDENCE / NOT A CUTOVER RECEIPT
Date: 2026-09-10
Coordinator: One
Target repository: `thebrazenbeard/bt2`
Target canonical branch: `work/canonical-platform-consolidation-v1`
Target backend: WoWSQL PostgreSQL project `bt2-479e4ad9`

## Purpose

This manifest preserves the exact source cuts currently being used to assemble the canonical Build Team Two platform. It is a provenance and migration-control artifact, not proof that every source object has been imported, not proof that a source repository is obsolete, and not authority to retire or delete any legacy surface.

Migration rule:

`preserve exact source -> normalize semantics -> prove equivalence/recovery -> explicitly authorize retirement`

Historical material remains evidence/history unless separately promoted under current authority.

## Frozen source cuts

| Source | Ref | Commit | Tree | Canonical role in migration | Current migration posture |
|---|---|---|---|---|---|
| `thebrazenbeard/build-team-2.0` | `main` | `ec2987e45f64a588ac92f6cae9964cb3725b9485` | `8db9f54b59e908f0ad35fbf6bf2f2ff8b48e639f` | role/topology/training/continuity source family | PRESERVE / NORMALIZE |
| `thebrazenbeard/wip` | `main` | `12a7c23dbe0482fd7bfe63659e54526778efef1e` | `e2527117c7d25f92d2e6aa7365ae8b3d3b9a3c08` | workspace/checkpoint/handoff/decision/external-effect recovery source | PRESERVE / NORMALIZE |
| `thebrazenbeard/bugops` | `main` | `39eb19bcf7669466c22703fbae7cc226bd44f714` | `16209d56150f7341f39492f66dfa52263437575c` | defect lifecycle/intake/evidence/verification source | PRESERVE / NORMALIZE |
| `thebrazenbeard/project-achilles` | `main` | `dbf9ceb2391567463d864198405c9b5d1e77db09` | `1cd715bef0d2a33478d3a635bcc05155c95ab4f9` | Seven-specific training/qualification history source | PRESERVE / RECOVER DISTRIBUTED TRAINING |
| `thebrazenbeard/masamune` | `collab` | `af20ff29a8419c20bd51ac4e731b670d505a452b` | `a76e3aac899a24f26af77454109e4a06978f8c30` | Masa/Mune paired-unit source | PRESERVE / NORMALIZE AS SEPARATE UNIT |
| `thebrazenbeard/hephaestus` | `main` | `78f6f22a0e5d14617855006a8383765589ac8c67` | `80eb19e26ff9b82f8c2eb4126c5b4e87a2318ce6` | Hephaestus implementation/repair-unit source | PRESERVE / NORMALIZE AS INDEPENDENT UNIT |
| `thebrazenbeard/project-lantern` | `feature/lantern-material-universe-v1` | `d0e05365883d8f670030fb1a1ff5fcd847937a77` | `3b155a88967f2f7a0f4ad6fa7b32ce3cbac73da0` | governed material/provenance backend source binding | PRESERVE / GENERALIZE WITHOUT WEAKENING GOVERNANCE |

These are frozen migration subjects. They do not assert that mutable source branches have not advanced since the cut. Any later claim about a repository's current branch state must be freshly observed and recorded separately.

## Runtime-source evidence kept distinct

Project Lantern runtime evidence is a separate source class from its GitHub package source. The relevant Supabase runtime target is `agvhmutlrolbaijzlbqk`.

At the established stable read cut, the governed `PROJECT_LANTERN` material set contained exactly two visible members under:

- profile digest `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- policy digest `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`

The generalized WoWSQL material-cut facade independently reproduced the same member UUIDs and digest tuples during review. This establishes exact-member read equivalence for that cut only. It does not collapse GitHub source binding, Supabase runtime state, WoWSQL installed state, or behavioral qualification into one status.

## Canonical active topology to preserve

The target active workforce is not the older coequal-facet representation.

- One: primary/orchestrator.
- Two, Three, Four, Five, Six, Seven, Eight, Nine, Thirteen: Build Team Two subagents orchestrated by One.
- Masa + Mune: separate paired debugger/reliability unit.
- Hephaestus: separate independent implementation/repair unit.
- One coordinates with Masa/Mune/Hephaestus but does not gain transitive implementation/deployment authority merely from coordination.

Older topology material is preserved as historical evidence, not inserted into active topology projections by import side effect.

## Source families that require semantic preservation

### Build Team 2.0 / distributed training sources

Preserve role identity, training package provenance, continuity/checkpoint semantics, and qualification evidence. The old central registry's omission of Two, Three, Seven, and Eight is not evidence that those roles lacked historical training. Distributed source recovery must occur before qualification import is declared complete.

No canonical `PASS` may be manufactured because a historical package is missing or inconvenient to recover.

### WIP

Preserve optimistic generation/CAS semantics, checkpoint lineage, handoff/decision provenance, and append-only external-effect recovery. A mutable current-state projection is insufficient if it erases the event history needed to distinguish PREPARED, ATTEMPTED, VERIFIED, FAILED, AMBIGUOUS, and later RECONCILED states.

### BugOps

Preserve BugOps-specific intake identity, SEV semantics, closure evidence requirements, regression/review/readback evidence, reopen history, and the distinction between source merge and verified runtime correction. Generic task/issue normalization must remain reversible to the source meaning.

### Project Lantern

Preserve source/runtime separation, profile/policy lineage, producer authorization history, duplicate-key/canonicalization protections, admission receipts, runtime-visible cut semantics, and fail-closed currentness. Historical producer permits do not become active merely because their rows were imported.

The canonical platform must explicitly decide whether its material-admission concurrency rule remains stricter than source Lantern or is brought to source-equivalent behavior; either choice requires qualification.

### Masa/Mune and Hephaestus

Preserve their distinct organizational boundaries. Masa/Mune remain a paired unit rather than numbered BT2 subagents. Hephaestus remains an independent implementation/repair unit. Coordination relationships do not imply orchestration, merge authority, deployment authority, or protected-effect authority.

## Historical preservation record requirements

Before a legacy object can be called preserved, the canonical record should be able to identify:

1. source system/repository/schema;
2. exact frozen source snapshot;
3. original path/table/row or primary identity;
4. content or row digest where feasible;
5. source-native classification/status;
6. canonical classification (`HISTORICAL`, `SUPERSEDED`, `ACTIVE_CANDIDATE`, or other explicit state);
7. import/migration receipt;
8. whether the canonical representation is lossless, mapped, summarized, or intentionally excluded;
9. any compatibility dependency that still points to the old source;
10. explicit promotion evidence if historical material is later made active.

## Retirement gate

No legacy repository, schema, API, or workflow boundary is logically retired until all of the following are established for that boundary:

1. exact source cut is preserved and content-addressed;
2. required active semantics are mapped into canonical subjects;
3. historical records have membership/count/digest or equivalent preservation evidence;
4. compatibility/replay tests pass;
5. no active workflow writes only to the old surface;
6. rollback/recovery through the canonical system has been demonstrated;
7. the canonical source/runtime/effect states are distinguishable and reviewable;
8. Patrick or current authorized governance explicitly accepts retirement/cutover.

Logical retirement never implies repository deletion.

## Current known incomplete areas

The following are intentionally not claimed complete:

- complete distributed training-package recovery for every active agent;
- full `bt2_legacy` historical population;
- full migration receipt population;
- blank-database rebuild from canonical GitHub DDL;
- response-loss/crash/retry qualification of the canonical queue and operation journal;
- BugOps round-trip fidelity qualification;
- final Lantern admission-concurrency policy qualification;
- final service access-control model;
- cutover, dual-write/freeze sequencing, or legacy retirement.

Two owns the database-source/integrity-hardening slice under assignment `BT2-CANONICAL-DB-HARDENING-TWO-20260910-V1`. One owns integration, source-history preservation, compatibility/equivalence, and final consolidation review.

## Acceptance evidence link

Two's private architecture review defines 40 falsifiable migration acceptance cases in:

`docs/architecture/BT2_CANONICAL_PLATFORM_INTEGRITY_REVIEW_TWO_V1.md`

Those cases are the current minimum integrity gate for database hardening. Passing them is necessary evidence; it is not by itself authority to merge, cut over, or retire legacy systems.
