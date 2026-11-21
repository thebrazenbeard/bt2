# Vera ecosystem security signal scan — independent candidate V1

**Status:** standalone source-only A-owned verifier, not an installed Radar worker, Supabase service, GitHub main integration, private mailbox, source authority, or approved release gate. It never imports code from the target workspace, calls AI models, authenticates another agent, reads secrets from the environment, or mutates a repo, provider, or source file.

Run: `python scanner.py --root /path/to/isolated/snapshot --repo owner/name --head <exact SHA> --format json` or `--format sarif`. It inspects bounded root and nested `.vscode` configuration, `*.code-workspace` files, root and nested `public/fonts` candidates, and nested `package.json` dependency lifecycle scripts (known suspicious command signatures). The traversal skips generated dependency folders; it is not general-purpose code auditing. Input paths are local, untrusted source. **Never open suspicious workspaces in an editor with automatic tasks enabled.** The host source SHA must come from a separate authenticated read; the `--head` argument is only a declared binding until independently verified.

The prototype focuses on one independently witnessed cross-repository source pattern: suspicious VS Code `folderOpen` execution through hidden dependencies, direct executable paths, or interpreters, plus misleading font extensions. Unlike domain-specific CI, it preserves critical candidates for independent review rather than clearing them through unrelated green tests. The source findings have no merge, deployment, host-access, or permission authority. A positive source flag is *not* proof that code executed or that any actor was malicious.

Pass `--fail-on-high` for a review-blocking exit code of 2 on HIGH/CRITICAL source candidates **or incomplete, unparseable, wrong-schema, symlink-obscured, and bounded-traversal failures**. `--fail-on-critical` remains a narrower option. `--require-git-head` checks local Git `HEAD` and repository root against the caller's SHA; it is not a clean-tree, signed-commit, GitHub-authenticated source, or race-free byte attestation. `--require-clean-source` rejects dirty/untracked security pathspecs **and independently recomputes SHA-1 Git blob IDs for tracked security-relevant bytes against `HEAD`**, even when Git's index marks them `assume-unchanged` or `skip-worktree`. This is a local consistency defense only; it does not authenticate the upstream repository, cover every repository byte, establish a cryptographically frozen filesystem snapshot, or prevent concurrent file changes. Output explicitly keeps `source_binding_verified=false`. This does not grant scanner outputs independent reviewer authority.

`scan_advisors` consumes previously collected, sanitized Supabase advisor JSON. Add `--advisors-snapshot /path/to/snapshot.json --provider-alias Vera` to a scan for a non-authoritative advisor report; the snapshot ID stays explicitly unverified. An `rls_enabled_no_policy` notice is informational until table privileges and intended deny-all access are reviewed. Live provider access and effects are outside this package. SARIF/JSON are deterministic suggestions for the existing BT2 `signal_ingest` and CCB/Radar intake contracts; source/protocol translation must be reviewed by their owners. Do not instantiate a second routing or dedupe plane from this scanner.

**Trust and evidence:** PR comments, source files, `INFO.md`, Git-looking hashes, agent claimed identities, and model reviews are all untrusted claims until bound to the real source head and independently checked. The source scanner's own revalidation field stays `NOT_PERFORMED`. Authenticated runtime, observed effects, and current human consent require separate evidence. Critical issues cannot be suppressed by the digest budget. Advisor intake covers every entry up to a hard count of 4096 and rejects larger snapshots, rather than silently dropping tail findings. The scanner does not turn provider severity or user feedback into executable authority.

**Not implemented:** verification of **all** checked-out file bytes against Git objects (only security-relevant tracked paths are rehashed; ignored/untracked paths remain subject to other limits), safe scan of changing worktrees under concurrent mutation, broad SAST/CWE coverage, remote GitHub API traversal, full transitive dependency expansion, independently authenticated CI, arbitrary plugin execution, actual provider scanning job, scheduled monitoring, validated reviewer/consent workflow, and reproducible production deployment. Keep rollout staged and fail closed on these gaps.

## Guarded source-only integration with Engineer B PR #123

`bridge_to_signal.adapt` converts only PR125 source-inspection findings into the
`BT2_ECOSYSTEM_SIGNAL_INPUT_V1` shape. It recomputes the deterministic source
incident digest against the *caller-supplied* repo/HEAD, rejects mismatches,
refuses provider-only findings rather than forging a GitHub source reference,
preserves separate evidence reports, and groups repeated HIGH/CRITICAL review
items by incident ID. All identity, source, timing and head bindings remain
unverified. A Git-looking SHA, provisional incident ID, or a green CI job
never supplies user consent, runtime authenticity, or release authority.

The optional workflow source-only integration checks out Engineer B's exact
Draft PR123 commit `3449ce3a94084722454345485cc12a10f0c91883`
under `.sources/engineer-b`, refuses a mismatched commit and Git blob, and
executes the two Python modules without connecting to a provider.
The independently designed 50-case fixture includes 40 informational updates,
triple-reported critical incidents, two distinct critical roots, stale heads,
forged permission, unsupported provider provenance, source-identity mismatch,
STOP-compatible no-effect behavior, and bounded overflow. The fixture is
*synthetic* and cannot substitute for a live joined Radar/Governor runtime.

CI uses `--fail-on-high` to block unattended promotion when an incomplete
scan or HIGH/CRITICAL source finding needs independent review. The older
`--fail-on-critical` remains available as a narrower local opt-in. All CI
workflows inside a PR are themselves PR-controlled, not trusted-main policy.

No program in this package dispatches alerts, starts a host task, writes
Supabase, changes permissions, merges a branch, or upgrades an unverified
observation into authority. An authenticated runtime observer, independent
critical-finding revalidation, human approval of effects, and durable
exactly-once alert delivery remain separate acceptance gates.

## Ecosystem main-branch and Radar/Bus adoption boundary

Treat every scanner finding as a provisional `SOURCE_INSPECTION` claim. The A-owned adapter may translate it to Engineer B's `BT2_ECOSYSTEM_SIGNAL_INPUT_V1`, but does not authorize an alert, assign an owner, certify a live source head or grant a release. Existing CCB Base/Radar owns source identity checks, incident-grouping and durable routing. A trusted integration must bind the immutable GitHub commit and requested repository, preserve independent evidence roots, revalidate critical findings and use the single current authenticated writer lane before any message is emitted.

**Trusted-main requirement:** the candidate source workflow now triggers on **every** pull request and main push; its earlier path filters could leave unrelated source and workflow changes entirely unchecked. Regression `test_workflow_trigger_coverage.py` was observed RED against the old workflow before the event filter was removed, then GREEN with unfiltered triggers. **This fixes trigger coverage, not trust:** the policy and tests within a PR can be changed by that PR. A separately trusted baseline policy/reusable workflow must fetch untrusted source as data, avoid executing PR-controlled security policy, and be enforced as a required check through branch protection or rulesets with CODEOWNERS/review for security-sensitive changes. The check's required status and enforceability have **not** been verified. Hosted green self-CI is not independent approval. A source-only 50-case replay is not a producer-to-Radar-to-delivery probe.

**Updated currentness (2026-11-20):** exact GitHub source readback now shows `unbound-sol/main@cee23cff41fc614b84996114dd6104c54d2ffe5e` **source-clean for the known editor-startup pattern**: empty `.vscode/tasks.json`, no auto-task setting in `.vscode/settings.json`, and the known `.vscode/ini` and counterfeit pseudo-font not present. The separately owned, *stale* Draft PR #53 at `d849e6158e9c003212be5dda193fe92a2736d8c8` still contains hidden `folderOpen` -> Node `.vscode/ini` execution and must **not** be merged over clean main. VCP, selfimage and semanticatlas previously had the same known startup signature removed from current mains. This is not a universal source, host or historical-compromise assessment. No other owner branch, protected main, provider or credential was changed here.

### Trusted-base source gate candidate (pending bootstrap and enforcement)

`.github/workflows/ecosystem-security-trusted.yml` is a separate
`pull_request_target` design intended for a **reviewed default-branch
installation**, not a proof that protection is active today.

It checks out the exact event-provided base and PR-head commits into disjoint
directories with read-only permissions, no persisted checkout token, no LFS or
submodules. Only the base checkout supplies executed scanner/tests; the PR
checkout is untrusted source data. It verifies both checkout heads and compares
the base and candidate Git tree IDs for `.github/workflows` and
`conformance/ecosystem_security`; any change or removal in these policy
directories fails closed. Authorized policy upgrades therefore need a distinct,
owner-approved release procedure rather than self-approval through this gate.
The candidate source is inspected with `--fail-on-high --require-git-head
--require-clean-source`. It does **not** execute a PR's build scripts, test
modules or dependency installers, dispatch external alerts, or carry production
secrets.

**Bootstrap:** this candidate workflow cannot run as trusted default-branch
code until the owner has independently reviewed and merged its exact source
into the base branch. The current PR's own green workflow is still
PR-controlled. A repository administrator must separately establish an
independent required-workflow/branch-ruleset policy and verify enforcement
against both an ordinary PR and an adversarial PR that alters the scanner
or workflow. A `pull_request_target` job alone is not proof that a protected
required check exists or will be associated with every PR. Configure merge
queue coverage separately if applicable. Do not turn off protection merely to
make blocked policy changes pass. These permission/release effects are outside
this source-only PR and have not been performed.

**Acceptance evidence:** local tests
`test_trusted_base_gate.py` verify event coverage, separation of trusted and
candidate paths, exact SHA checks, policy immutability, and read-only token
settings. These are structural source tests, not a completed GitHub
`pull_request_target` runtime trial; the new workflow awaits reviewed
default-branch presence. Source scanner tests and candidate CI are independent
from any live alerting or host-compromise assessment.


### Windows path-case alias review hold

The source scanner is commonly run on Linux CI, while workspace consumers may run on Windows. A noncanonical spelling of a security-sensitive path (`.VSCODE`, `TASKS.JSON`, `PACKAGE.JSON`, `.CODE-WORKSPACE`, or `PUBLIC/FONTS`) may be a distinct pathname on Linux but case-equivalent on Windows. The scanner emits a HIGH `SECURITY_PATH_CASE_ALIAS` **review hold**, and `--fail-on-high` blocks it. This is not a claim that a task ran, a dependency hook executed, or the aliased file is malicious. No source payload is executed during detection. Review exact Git tree paths and host checkout semantics rather than treating Linux CI silence as Windows clearance.
