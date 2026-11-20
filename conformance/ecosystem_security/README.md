# Vera ecosystem security signal scan — independent candidate V1

**Status:** standalone source-only A-owned verifier, not an installed Radar worker, Supabase service, GitHub main integration, private mailbox, source authority, or approved release gate. It never imports code from the target workspace, calls AI models, authenticates another agent, reads secrets from the environment, or mutates a repo, provider, or source file.

Run: `python scanner.py --root /path/to/isolated/snapshot --repo owner/name --head <exact SHA> --format json` or `--format sarif`. It inspects only bounded workspace configuration and two font directories. Input paths are local, untrusted source. **Never open suspicious workspaces in an editor with automatic tasks enabled.** The host source SHA must come from a separate authenticated read; the `--head` argument is only a declared binding until independently verified.

The prototype focuses on one independently witnessed cross-repository source pattern: suspicious VS Code `folderOpen` execution through hidden dependencies, direct executable paths, or interpreters, plus misleading font extensions. Unlike domain-specific CI, it preserves critical candidates for independent review rather than clearing them through unrelated green tests. The source findings have no merge, deployment, host-access, or permission authority. A positive source flag is *not* proof that code executed or that any actor was malicious.

Pass `--fail-on-critical` for a review-blocking exit code of 2 on CRITICAL source candidates **or incomplete, unparseable, or invalid-schema configuration scans**. `--require-git-head` checks local Git `HEAD` and repository root against the caller's SHA; it is not a clean-tree, signed-commit, GitHub-authenticated source, or race-free byte attestation. Output explicitly keeps `source_binding_verified=false`. This does not grant scanner outputs independent reviewer authority.

`scan_advisors` consumes previously collected, sanitized Supabase advisor JSON. Add `--advisors-snapshot /path/to/snapshot.json --provider-alias Vera` to a scan for a non-authoritative advisor report; the snapshot ID stays explicitly unverified. An `rls_enabled_no_policy` notice is informational until table privileges and intended deny-all access are reviewed. Live provider access and effects are outside this package. SARIF/JSON are deterministic suggestions for the existing BT2 `signal_ingest` and CCB/Radar intake contracts; source/protocol translation must be reviewed by their owners. Do not instantiate a second routing or dedupe plane from this scanner.

**Trust and evidence:** PR comments, source files, `INFO.md`, Git-looking hashes, agent claimed identities, and model reviews are all untrusted claims until bound to the real source head and independently checked. The source scanner's own revalidation field stays `NOT_PERFORMED`. Authenticated runtime, observed effects, and current human consent require separate evidence. Critical issues cannot be suppressed by the digest budget. Advisor intake covers every entry up to a hard count of 4096 and rejects larger snapshots, rather than silently dropping tail findings. The scanner does not turn provider severity or user feedback into executable authority.

**Not implemented:** verification of all checked-out file bytes against Git objects, safe scan of changing worktrees under concurrent mutation, broad SAST/CWE coverage, remote GitHub API traversal, full transitive dependency expansion, independently authenticated CI, arbitrary plugin execution, actual provider scanning job, scheduled monitoring, validated reviewer/consent workflow, and reproducible production deployment. Keep rollout staged and fail closed on these gaps.

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
