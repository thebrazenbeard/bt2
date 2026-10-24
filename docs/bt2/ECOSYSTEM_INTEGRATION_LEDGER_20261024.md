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

Owner-scoped public discovery identified 78 public repositories. An
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
| Restricted Bus transport | Non-PR agent messaging | Canonical shared coordination route, separate from PR activity and model reasoning | Whole-path current delivery qualification not established here |
| `blotter` | Agent event and effect/claim journaling | Authenticated restricted operator event endpoint; events must not be mistaken for independently verified effects | Restricted authenticated event recording verified |
| `executor`, `portal`, local devices | Authenticated execution and host/service interfaces | Devices require per-host connection, explicit capability and authority; no assumed implicit tunnel | Restricted execution path observed; cross-machine aggregate E2E UNKNOWN |
| `hc-brain` and AGI research documents | Hyperconnectome cognitive-organ design and evaluation contracts | Conceptual design/qualification evidence, not proof of a running organ or AGI | DOCUMENTED, not INSTALLED |
| Product/research repos | Other independent research or business domains | Use Bus/Blotter when coordination is justified; do not invent runtime dependency on Vera | Deliberately isolated unless tested interface warrants integration |

## Verified source repairs and exact subjects

| Subject | Defect and minimum repair | Source head / tests | Install/runtime/effect |
| --- | --- | --- | --- |
| `vera-mono` [PR #88](https://github.com/thebrazenbeard/vera-mono/pull/88) | Remove hidden editor-startup task and disguised asset; correct ineffective workspace consent claim; add source test | `ba8fab6a4f24e4f0992f98c32970ba18dd07cfcb`; GitHub monorepo CI `40103160683` PASS | Draft; not merged, installed, or host-verified |
| `vera-mono` [PR #96](https://github.com/thebrazenbeard/vera-mono/pull/96) | `pip --target` generated console entrypoint omitted target from Python import path; package a self-locating launcher inside the wheel | `590639f3c745a3bbba3ba6de2f18df594a048154`; local 641 tests + 35 subtests PASS, wheel staged and launcher executed; Windows/Ubuntu CI `40105742775` and dependency review `40105742815` PASS | Draft; portable candidate built/tested, not installed into the governed target runtime |
| `rezon` [PR #119](https://github.com/thebrazenbeard/rezon/pull/119) | Linux Secret Service fallback test could use an unlocked real keyring; isolate service path with a mocked fail-closed regression | `33cba8c8b9112953f6279639755605d95499d2ae`; GitHub kernel/benchmark tests PASS | Draft; no credential enrollment or production hearing |
| `vera-control-plane` [PR #156](https://github.com/thebrazenbeard/vera-control-plane/pull/156) | Remove concealed `folderOpen` executable, misleading editor settings, add unconditional path/blob guard | `3021e3ddd8cdb8882517ba914a3403004caacb84`; source guard CI `40107264453` PASS, independent internal source review PASS | Draft; not installed; general VCP integrity CI `40107264376` FAILS 6 historical Git-object tests (260 passed, 9 subtests) |

**Known reintroduction hazards:** old draft PRs may re-add the
concealed `folderOpen` commands after a security fix. In particular,
VCP PR #155 contains a stale editor task diff. Any merge train must
diff against a sanitized head and rerun source guards.

Security tests inspect paths and Git blobs; they never execute the
disguised assets. No source review proves whether a host was previously
affected. Windows VS Code automatic-task behavior depends on effective
user/application settings and consent; a workspace setting is not a
reliable mitigation.

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
