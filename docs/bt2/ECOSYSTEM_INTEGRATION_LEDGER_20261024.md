# BT2 ecosystem integration ledger — 2026-10-24

Status: **active, partial source repairs; no global operational qualification**.
Owner/coordinator: BT2 One. Canonical ledger branch proposed against
`thebrazenbeard/bt2@ba830cc2914813c3b4e76751f77b1cf3a132a5c4`.
This document is public-safe. Restricted repository identity and private
review details are intentionally excluded and must stay in permitted
private records.

## Evidence vocabulary

- **SOURCE** — exact Git branch/commit, not merged or installed.
- **BUILD/TEST** — exact-head automated/local tests, not real effects.
- **INSTALL** — a specific installed tree and version read back.
- **RUNTIME** — a service/process observed on a particular host.
- **E2E** — a real workflow with both endpoints and effects read back.
- **UNKNOWN** — insufficient permitted evidence. Internal/model review
  never upgrades one of the above classes.

## Public owner inventory and dependency boundaries

Owner-scoped public discovery identified 78 public repositories. The [public repository role inventory](PUBLIC_REPOSITORY_ROLE_INVENTORY_20261024.md) names all 78 and classifies them from current README/metadata only; its repository-specific installation and runtime states are UNKNOWN. An
exact Git-blob scan found a concealed VS Code `folderOpen` task and
disguised Node executable in **45 of those 78** public repositories,
across two observed asset variants. The affected checkout is a
**conditional startup exposure**, not evidence that the command ever
executed on a workstation. Additional access-restricted inventory
exists; neither counts nor identities are published here.

| Component | Responsibility | Actual connection or boundary | State |
| --- | --- | --- | --- |
| `vera-mono` | Canonical assembled Vera code: 12 Python package roots, persistent governance/recovery | Models, devices, databases and transports remain separately admitted external services | SOURCE and BUILD verified; restricted install/runtime readback is mismatched and not qualified |
| `rezon` | Multi-model reasoning and worker hearings | External repo is a donor/worker infrastructure; absorbed `packages/rezon` is internal to Mono | Test harness exists; production credential enrollment incomplete |
| `ccb-core` | Public reusable Bus/Radar production source and protocol tests | Deployment and private writer-lane overlays are external to reusable source | README source authority verified; deployed provider/version and delivery receipts unqualified |
| Restricted Bus transport | Non-PR agent messaging and private lane state | Shared coordination route is distinct from PR activity, Blotter events, and model reasoning | Whole-path current delivery qualification not established here |
| `blotter` | Agent event and effect/claim journaling | Authenticated restricted operator event endpoint; events must not be mistaken for independently verified effects | Restricted authenticated event recording verified |
| `executor`, `portal`, local devices | Authenticated execution and host/service interfaces | Devices require per-host connection, explicit capability and authority; no assumed implicit tunnel | Restricted execution path observed; cross-machine aggregate E2E UNKNOWN |
| `hc-brain` and AGI research documents | Hyperconnectome cognitive-organ design and evaluation contracts | Conceptual design/qualification evidence, not proof of a running organ or AGI | DOCUMENTED, not INSTALLED |
| Product/research repos | Other independent research or business domains | Use Bus/Blotter when coordination is justified; do not invent runtime dependency on Vera | Deliberately isolated unless tested interface warrants integration |

### Integration edges — observed versus absent

```mermaid
flowchart TD
  Agents["BT2 and project agents"] -->|"Authenticated event write: verified"| Blotter["Blotter activity ledger"]
  Agents -.->|"Message delivery: unqualified"| Bus["CCB core plus restricted transport"]
  Agents -->|"Host endpoint health: observed"| Executor["Executor device interfaces"]
  Mono["Vera Mono source candidate"] -->|"Embedded code: source tested"| Cascade["Rezon cascade"]
  Mono -.->|"Adapter not installed"| Models["Local model inference services"]
  Cascade -.->|"Production hearing: enrollment gate"| Workers["Cross-host workers"]
```

Solid arrows mean only the named limited evidence was observed; dashed arrows are proposed/missing runtime contracts. No edge alone proves effect authorization or whole-system installation. Independent product/research repositories stay isolated until a justified, executed interface is demonstrated.

The 45/78 finding is an exact-blob **SOURCE** scan, not a host
probe. Its [immutable public source manifest](PUBLIC_VSCODE_TASK_EXPOSURE_MANIFEST_20261024.md)
binds all 78 public repositories to their individual `main` HEAD
commits and task-blob identities at this snapshot: 41 match one concealed
Node loader variant, 4 match a second, 26 have nonmatching task files,
and 7 lack that path. The suspicious asset was present at each affected
pinned source head. No asset was executed, and current main/host status
may differ from the pinned snapshot.

### Public main source-head bindings at this checkpoint

| Repository | Main commit |
| --- | --- |
| `bt2` | `ba830cc2914813c3b4e76751f77b1cf3a132a5c4` |
| `vera-mono` | `64c4a756a8c4d6fc791787de80303f7ee0f64869` |
| `rezon` | `d27da3cab31ae96aff3c65385fc31354dc8aeb8c` |
| `blotter` | `2493b354488cefe4a3f0d2b80372b93c6b1cfeb4` |
| `portal` | `6b601b8b291bd59cd79bcc1a96befab50ec2ebda` |
| `vera-mesh` | `3242f72a0c4b9cb53679563c78f66528841296f5` |
| `vera-control-plane` | `0654b4a646f2168b672f4f78cef71e33bc79d643` |

All implementation PRs cited below are **draft and unmerged**;
none is an installation receipt. Source/change ownership is BT2 One
or the named independent specialist; merge/legal attestations remain
with Patrick and any repository-specific protected workflow.

## Verified source repairs and exact subjects
| Subject | Defect and minimum repair | Source head / tests | Install/runtime/effect |
| --- | --- | --- | --- |
| `vera-mono` [PR #88](https://github.com/thebrazenbeard/vera-mono/pull/88) | Remove hidden editor-startup task and disguised asset; correct ineffective workspace consent claim; add source test | `ba8fab6a4f24e4f0992f98c32970ba18dd07cfcb`; GitHub monorepo CI `40103160683` PASS | Draft; not merged, installed, or host-verified |
| `vera-mono` [PR #96](https://github.com/thebrazenbeard/vera-mono/pull/96) | `pip --target` generated console entrypoint omitted target from Python import path; package a self-locating launcher inside the wheel | `590639f3c745a3bbba3ba6de2f18df594a048154`; local 641 tests + 35 subtests PASS, wheel staged and launcher executed; Windows/Ubuntu CI `40105742775` and dependency review `40105742815` PASS | Draft; portable candidate built/tested, not installed into the governed target runtime |
| `vera-mono` [PR #97](https://github.com/thebrazenbeard/vera-mono/pull/97) | Local Ollama to Rezon **unverified candidate observation** via bounded loopback transport; malformed HTTP fails closed; synthetic reviewer remains unqualified | `93d65ce87609e05e354acb0f0068db96a4977670`; local 658 tests + 35 subtests PASS; Windows/Ubuntu CI `40108548034` and dependency review `40108548021` PASS; internal independent source review PASS | Draft; no live adapter host installation or real integrated model/effect qualification. Protected staging request denied. |
| `vera-mono` [PR #98](https://github.com/thebrazenbeard/vera-mono/pull/98) | Embedded Rezon cascade incorrectly marked below-threshold answers resolved when layers/iteration budget exhausted; fail-closed gate and no-dispatch tests | `4ea394a1b24e2a7bcb382d89eb3b77b88ec74214`; original red reproductions, local 642 tests + 35 subtests PASS; GitHub monorepo and dependency review CI PASS; independent exact-head source review PASS | Draft; unmerged; no deployed effect; does not establish separately hosted Rezon defect |
| `vera-mono` [PR #99](https://github.com/thebrazenbeard/vera-mono/pull/99) | Consolidate PR #88/#96/#97/#98 plus bounded semantic preflight; reconcile PR #97's obsolete assertion about unresolved candidate persistence and correct combined module documentation | `835cabe3b93a74360c5d0d672e7d3463dd797c45` / exact Git tree `f77ee738ed7d07d49d6d38abc44a9e9653bb0d5b`; full integrated local 667 tests + 35 subtests PASS, one existing collection warning; independent source review PASS and 9 remote blobs match locally tested tree; Dependency Review PASS and Windows/Ubuntu monorepo CI `40132646910` PASS (including wheel build/installed-launcher checks) | Draft; unmerged/uninstalled; no actual adapter-on-host or independently observed model-to-action E2E |
| `rezon` [PR #119](https://github.com/thebrazenbeard/rezon/pull/119) | Linux Secret Service fallback test could use an unlocked real keyring; isolate service path with a mocked fail-closed regression | `33cba8c8b9112953f6279639755605d95499d2ae`; GitHub kernel/benchmark tests PASS | Draft; no credential enrollment or production hearing |
| `vera-control-plane` [PR #156](https://github.com/thebrazenbeard/vera-control-plane/pull/156) | Remove concealed `folderOpen` executable, misleading editor settings, add unconditional path/blob guard | `3021e3ddd8cdb8882517ba914a3403004caacb84`; source guard CI `40107264453` PASS, independent internal source review PASS | Draft; not installed; general VCP integrity CI `40107264376` FAILS 6 historical Git-object tests (260 passed, 9 subtests) |
| `tattler` [PR #17](https://github.com/thebrazenbeard/tattler/pull/17) | Remove concealed VS Code folder-open Node loader and disguised asset; add source guard; fix inherited CI failure by explicitly fetching the SAME immutable historical SPK verifier commit before checkout | `2d6a14a695a772fd9d4916f33c9675179af54aff`; local 20 Python tests PASS; independent source review PASS; exact-head GitHub build `40134250159` SUCCESS including Go, Python, SPK package/DSM verification, Windows; exact-head CodeQL `40134247326` PASS, earlier security-head Dependency Review PASS | Draft; unmerged; source/build only, no installed host effect; historical external commit remains a durability dependency |
| `discovery` [PR #54](https://github.com/thebrazenbeard/discovery/pull/54) | Remove concealed workspace folder-open Node loader and disguised asset while retaining legitimate font/debugger files; add unconditional absence regression | `6dd26c5adc935b56cf2dde51a40621ea8ff12361`; local 164 unittests plus two validators and compilation PASS; exact-head GitHub Discovery validation `40134379391` and composed lifecycle `40134379394` SUCCESS; independent exact-head source/CI review PASS | Draft; unmerged, not installed, no host compromise attestation |
| `mediaphile-server` [PR #11](https://github.com/thebrazenbeard/mediaphile-server/pull/11) | Remove concealed editor-startup task, disguised asset and misleading consent; add source guard workflow; leave all Go source/dependencies untouched | `1c093c7361ce1269f22dd2314cd9105aaeeea6d2`; local source guard 3/3 PASS; independent exact-tree review PASS; GitHub guard runs `40134742661`, `40134725120` SUCCESS; Go test/vet/build workflow `40134742715` SUCCESS | Draft; no NAS deployment, install, media mutation or host execution conclusion |
| `cricket` [PR #5](https://github.com/thebrazenbeard/cricket/pull/5) | Remove concealed editor-startup task and disguised asset, correct misleading workspace settings and add auto-discovered source guards | `629644a71a6b94814d756f9fee82aa23e324ade6` / tree `8e916dda72b4ba72addeac70ad03318812d846e1`; original tests RED, source guards 3/3 and full 81/81 local pytest PASS, wheel build PASS; exact-head GitHub test run `40134970475` SUCCESS | Draft; not merged or installed; no workstation execution inference |
| `mediaphile-client` [PR #9](https://github.com/thebrazenbeard/mediaphile-client/pull/9) | Remove two distinct source-triggered Node loaders: editor `folderOpen` disguised asset and obfuscated `api.js` called by dev/build scripts; source-only static decoding of `api.js` shows remote code retrieval and detached Node execution; retain safe app tooling and add pre-dependency guard | `f753d82b3faa0dd76231663caaaa9e63ab96ab70` / exact tree `bb496239c7711ce1268fa5be3b1cd6040fdeff6e`; local sanitized source guards 3/3, typecheck, Vitest 12/12 and Vite build PASS; exact-head GitHub CI `40135216165` SUCCESS incl pre-dependency guard, npm install, typecheck, simulated browser flows and sanitized build | Draft; three historical GitHub Build steps invoked original `node api.js` (runs `39805382366`, `39805424160`, `39805476162`); downloaded-stage effects and physical-host execution UNKNOWN; no NAS deploy/install; original loader never executed during this review |
| `vera` [PR #222](https://github.com/thebrazenbeard/vera/pull/222) | Remove concealed VS Code startup task and disguised executable, correct invalid workspace auto-task claims, add dedicated source-only regression workflow | `d88730ec186a407e43235740264bf05cf0e5ca19` / exact tree `4fb7545ac8c1f0115a97ac086c9a2ecf443f2bfa`; local RED→3/3 source guard PASS, bytecode compile PASS; GitHub source guard `40135811887`, dependency review `40135811765` and release package `40135811718` SUCCESS; Temporal pilot `40135811844` and enforcement kernel `40135811759` SUCCESS; independent exact-head source/CI review PASS | Draft; no merge, host installation or historical execution conclusion |
| `mediaphile-client` [PR #10](https://github.com/thebrazenbeard/mediaphile-client/pull/10) | Reconstruct original PR #7/#8 legitimate subtitle review/search UI on top of sanitized PR #9, excluding all old executable startup paths; pin client API snapshot to exact server Git blob | `0a4c724bbd49468c5cdcc83e6879141d25fe1a1e` / tree `e6389f234b136185f161903d491134b9dd36b26d`; independent exact local diff review PASS; guard 3/3, TypeScript, Vitest 19/19 and sanitized build local PASS; exact-head GitHub CI `40135854899` SUCCESS incl source guard/typecheck/build/Chromium simulated-API flows | Draft; stacked on security PR #9 branch, not main; no NAS effect, published provider setup or runtime qualification |
| `vera-R9A0` [PR #25](https://github.com/thebrazenbeard/vera-R9A0/pull/25) | Remove concealed editor startup task/disguised asset; preserve checksum-bound original workflow; add independent unconditional guard workflow | `8760c09f89cf03265344247056df5de44d5e25a5` / tree `6a020ea40530cc528cd8d610a457fda15532fe8b`; source guard 3/3 and native suites 70/70 + 32/32 local PASS, exact-head GitHub guard `40136226999` and native `40136226997` SUCCESS, independent review PASS; one unrelated broad local discovery failure reproduced on pristine main | Draft, unmerged/uninstalled, no host execution conclusion |
| `ccb-core` [PR #22](https://github.com/thebrazenbeard/ccb-core/pull/22) | Bound provider HTTP503 diagnosis to five allowlisted codes, suppress arbitrary body and chained tracebacks; adds regression; provider actual fault NOT fixed | `c8bd7e4f67add7407407a606172c50a1248c86bd` / tree `1d0e36958fa8459ae8114e4ddc9fbac4f3560d6b`; local focused12 and full255 PASS; exact-head GitHub CI `40136287454` and dependency review `40136287509` both SUCCESS | Draft/unmerged, 171 historical scheduled Radar failures and authenticated 503 persist; no live Bus message delivery receipts |
| `mediaphile-server` [PR #12](https://github.com/thebrazenbeard/mediaphile-server/pull/12) | Reapply only 34 legitimate subtitle review/queue/provider staging backend paths on sanitized Server PR #11; API snapshot matches clean client PR #10 exact Git blob; preserve explicit staging before separate manual install | `d9778664f8aa88309f4179025302aa4a6bedfb09` / tree `0a6afa8ce438dd1a4861861dd8ff68c36e5cba26`; source guard 3/3, diff check local PASS; independent static code/security review conditional PASS; Go 1.26 unavailable locally; exact-head GitHub Go CI `40136594166` (test/vet/build) and source guard `40136594727` both SUCCESS | Draft stacked on Server PR #11; no live NAS, API credentials, subtitle install or production effect; staged published subtitles need manual review/promotion |
| `unbound-sol` [PR #44](https://github.com/thebrazenbeard/unbound-sol/pull/44) | Remove concealed editor loader and disguised asset; wire existing public scanner and 11 regressions into continuity CI | `3e26275ac53f7f9109b740a16f884f8b80124849` / tree `5da3f938075709199219df24e17306148c09481d`; baseline scanner 6 findings, after NO_MATCH, 11/11 tests and public validator local PASS; exact-head GitHub continuity `40136752135` SUCCESS | Draft/unmerged; no runtime, editor host or independent host compromise conclusion |


**Historical CI source execution (Mediaphile Client):** Verified GitHub-hosted Actions Build logs for unsafe main runs [39805382366](https://github.com/thebrazenbeard/mediaphile-client/actions/runs/39805382366) (job `119917119873`) and [39805424160](https://github.com/thebrazenbeard/mediaphile-client/actions/runs/39805424160) (job `119917258162`), plus unsafe feature PR #7 run [39805476162](https://github.com/thebrazenbeard/mediaphile-client/actions/runs/39805476162) (job `119917430548`). Each successful Build step printed `> node api.js && tsc --noEmit && vite build`. This is **real execution of the original obfuscated first-stage command on ephemeral GitHub runners**, not proof that its network stage succeeded, it downloaded or launched additional code, accessed secrets, or affected personal computers or storage systems. PR #8's observed build script was sanitized and is not included in those three invocation claims.

**Integration lesson:** independently green PRs #97 and the semantic-admission patch initially failed when combined because an old test expected caller-provided semantics to persist after unresolved reasoning. The PR #99 aggregate was exercised as one exact tree; no source-only PASS should be promoted into runtime or AGI qualification. A rejected dispatch after resolved reasoning may still leave a schema-valid caller-supplied semantic row, which is not automatically truth.

**Mediaphile Client stale PR hold:** PR #7 still has the obfuscated build loader and editor auto-task on its open feature branch. PR #8 targets #7 (not main) and retains the suspicious asset blobs even though its package scripts stopped invoking api.js. Neither feature should be integrated as-is; replay the legitimate changes on the source-sanitized #9 tree and requalify the final exact branch before any merge.

**Known reintroduction hazards:** old draft PRs may re-add the
concealed `folderOpen` commands after a security fix. In particular,
VCP PR #155 contains a stale editor task diff. Tattler PR #13 likewise reintroduces the concealed startup task and asset and must be sanitized or held. Any merge train must
diff against a sanitized head and rerun source guards.

Security tests inspect paths and Git blobs; they never execute the
disguised assets. No source review proves whether a host was previously
affected. Windows VS Code automatic-task behavior depends on effective
user/application settings and consent; a workspace setting is not a
reliable mitigation.


## Source merge and installation dependency gates

| Scope | Safe candidate order | Required qualification before effect |
| --- | --- | --- |
| Mediaphile Client | Security PR #9 precedes rebuilt subtitle feature PR #10 (currently stacked on #9), never merge stale #7/#8 heads as-is | Rebase final combined head, source guard + browser CI, owner merge, installed client version and live API E2E |
| Mediaphile Server | Security PR #11 precedes rebuilt subtitle backend PR #12 (stacked on #11), never merge stale feature-chain heads as-is | Final Go tests/vet/build, isolated private staging root, owner merge, NAS deployment readback and explicit staged-to-reviewed-install workflow |
| Vera Mono | Consolidated PR #99 is integration candidate; independent #88/#96/#97/#98 are overlapping donors, not four separate production installs | Reviewed exact aggregate, owner merge, wheel install/version, bound model adapter, model-to-effect adversarial E2E |
| Rezon external workers | PR #119's test-isolation/credential backend fix stays in external worker project, not absorbed Mono reasoning kernel | Owner merge/installation and confidential local enrollment before four-real-worker persisted production hearing |
| Public editor-source containment | Security guards precede older feature PRs that may reintroduce known startup blobs | Inspect every final Git tree, source CI, and relevant application build; no host-clean claim from Git changes |
| Public Bus diagnostic source | ccb-core PR #22 is diagnostics, not a provider repair; active projector source remains separately pinned and qualified | Owner-authorized source activation and provider cause correction, successful authenticated cursor/journal receipt and canary message |

No single PR is a deployment receipt. Protected trust anchors and private runtime paths are deliberately excluded from this public report.

## Restricted runtime evidence (not public telemetry)

Authorized private operator readback confirmed bounded **real** local-model
inference and authenticated durable agent-event read/write. A model-generated
answer also contained a concrete factual misreading, so model output remains
an unverified candidate. The Vera runtime's installed provider binding and
cross-machine production hearing remain unqualified.

Exact machine names, endpoint addresses, installed model identifiers,
host/application versions, local service states, execution timings,
event-sequence numbers and sensitive runtime configuration are retained
only in restricted operator/Blotter records. This public ledger does not
republish them or imply that observed source/CI fixes reached production.

## Important blocked or unverified work

1. **Owner merge gates.** Repository CLAs and explicit no-merge rules
   must be satisfied by the owner. Do not make legal attestations on
   the owner's behalf, merge drafts under HOLD, or erase Git history.
2. **Production Rezon workers.** Secure credentials must be enrolled
   through owner-authorized private-local mechanisms; no credential
   printing, transport substitution, or synthetic production hearing.
3. **Mono deployment.** First sanitize and review source; then rebuild
   exact wheel, install with rollback point, bind real providers, and
   verify status/effects after service start. Green CI alone is
   insufficient.
4. **True model reasoning chain.** A bounded local model call is proven,
   but Mono/Rezon/provider/result persistence and independent epistemic
   review are not yet verified as one executed workflow.
5. **Cross-host delivery.** Authorized machines and the Bus require a fresh
   simultaneous endpoint-and-receipt test, including retry/recovery.
6. **Wider security inventory.** Remaining affected public repositories
   and stale draft PRs require individual authority checks and
   reconstructible regression fixes; do not bulk merge without review.
7. **AGI qualification.** Hyperconnectome architecture is conceptual;
   hardcoded closed-loop probes are not held-out real-model
   generalization. Separate evidence, runtime, and reviewer roles.

## Resume from this ledger

Fresh-check canonical main plus every draft head and new CI run. Recover
restricted PR details only through authorized private evidence.
Review exact-source defects, reconcile stale PRs, respect owner gates,
then install and exercise one real cross-boundary workflow at a time.
Carry the exact source, build, installation, runtime, effect, rollback
and receipt IDs into subsequent ledger revisions. No scheduled or
background continuation is asserted by this document.
