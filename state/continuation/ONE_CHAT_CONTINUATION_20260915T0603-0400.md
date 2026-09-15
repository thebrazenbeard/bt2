# ONE CHAT CONTINUATION — 2026-09-15 06:03 ET

Restore token: `ONE::BT2::RESTORE::ONE_CHAT_CONTINUATION_20260915T0603-0400`

## Identity / authority

- Role: One, BT2 lead orchestrator/integrator.
- Canonical BT2 source: `thebrazenbeard/bt2`.
- Current canonical source observed at save: `main@30e81cadd94fae117a7f6875523c03251c7c9f6e`.
- Current WoWSQL runtime target remains `bt2-479e4ad9`; Supabase is superseded and is not a fallback.
- Patrick's current instruction is to fix what is needed from the hostile audits. Treat this as authority for bounded remediation work (branches/PRs/tests/Bus coordination), not as blanket merge/deploy/provider/protected-effect authority.
- Preserve exact-head review binding. Do not silently promote draft/remediation work to canonical source.

## BT2 / WoWSQL migration status

Migration is closed and operational.

- Native Project Instructions V3 are active.
- Unsuffixed V3 Lantern Project files are installed; V1/V2/transport-suffixed copies are historical/inactive.
- WoWSQL free-shared read/currentness path is operational and previously reverified stable through projection preflight -> B0 -> payload -> B1.
- Producer mode remains `FROZEN_ZERO_PRODUCER` / hosted writes NOT QUALIFIED. This is a supported read-frozen state, not a migration failure.
- Canonical BT2 source fixed the V3 acceptance semantics at `30e81cadd94fae117a7f6875523c03251c7c9f6e`: free-shared read acceptance is separate from hosted producer qualification.
- Do not reopen the Supabase migration or weaken the producer verifier just to get green.

## Hostile audits delivered

Four in-depth hostile audits were completed and durably delivered to project owners on the Chat Bus:

- Noema: `project/noema-v1`, `projects/noema/messages/20260914T-hostile-audit-from-one.md`, audit commit `b6247f244830edf5f29ea0872cb7ec422745aff7`.
- ABIL: original audit sent from `bus/one-v2`, `messages/20260914T-one-to-abil-owner-hostile-audit.md`, commit `14a1ba8ad8a89b16f1ae872dda6bd087db80bf15` because no dedicated ABIL hub existed at audit time.
- HC Brain: `project/hc-brain-v1`, `projects/hc-brain/messages/20260914T-hostile-audit-from-one.md`, audit commit `a0311eca4f8aacca866974d4af8bb217c708c4ee`.
- Vera Works: `project/vera-works-v1`, `projects/vera-works/messages/20260914T-hostile-audit-from-one.md`, audit commit `ddadfb2cf3245b9bb65e0a9b7920ae7e889e425e`.

Cross-project hostile finding: architecture/governance quality generally exceeds mechanical currentness/promotion enforcement. Classic `main` protection was disabled across the audited repositories, and private-repo rulesets were not available on the observed plan.

## ABIL remediation

A dedicated ABIL Bus project hub was created after the audit:

- Bus branch: `project/abil-v1`.
- `projects/abil/README.md` defines routing.
- `projects/abil/CURRENTNESS.json` records the last observed main and active PR subjects.
- PR mirror records were added for ABIL PRs #2-#5.
- Latest observed hub content includes source main `0812d9780ce1648820269fa142a43e17030ef793`, PR #2 `712d5b30b45ba9299dcfce0599878cb81db70e8f`, PR #3 `c31d760a711dfd36c00ef9f40a7036b2b1701f45`, PR #4 `10339bfd32d65b984361fa45380ba4b06b0cb338`, PR #5 `90b46fd81544cc1c4f8cb9a8bce6284c1a0bd62e`.

Remediation PR:

- `thebrazenbeard/abil` PR #6: **Add fail-closed write-capability admission boundary**.
- Base: PR #2 branch `work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f`.
- Head: `one/write-admission-remediation-20260914@9d41aa2c9eefca7db67d0301419102392a7ca45d`.
- Current save readback: OPEN, DRAFT, MERGEABLE, 2 commits, 2 changed files.
- Adds machine-readable `ABIL_WRITE_CAPABILITY_ADMISSION_V1` schema plus companion contract requiring exact implementation subject, target, monotonic authority epoch, independent authority grant, safety classification, commissioning envelope, control coverage, active artifact, exactly-one-writer fence, allowed effects, and authorizers.
- Missing/stale/mismatched/revoked/expired/incomplete admission is explicitly not write authority.
- Design/governance only; no machine connection, control code, commissioning, deployment, or merge authority.

Next ABIL work: fresh-review PR #6 exact head; mirror PR #6 into `project/abil-v1`; route remediation receipt to owner; do not merge without explicit authority.

## Noema remediation

Remediation PR:

- `thebrazenbeard/noema` PR #35: **Add research currentness and contract-integrity gate**.
- Base: canonical research PR #32 exact head `be8eeb9a5f71e992180f3b3272ca5a0b80d8fc33` on `work/noema-representation-drift-scope-20260906`.
- Head: `one/research-governance-remediation-20260914@ab4491c0e5f250dde963b0a5243d6c9e8eb90556`.
- Current save readback: OPEN, DRAFT, MERGEABLE, 2 commits, 2 changed files.
- Adds machine-readable research-currentness record and CI research-contract-integrity gate.
- Gate is intended to parse working-design JSON, verify active V2 preregistration/handoff surface exists, and enforce fail-closed research authority ceiling.
- Does not alter research contracts or authorize I0/I1/E0/P0, learning, experiments, publication, deployment, or merge.

Observed GitHub Actions result on this remediation: run `34877165774` failed with **zero executed steps**. Treat as infrastructure/runner failure, not source FAIL and not PASS.

Next Noema work: locally verify PR #35 exact head independent of GitHub runner availability; route exact-head remediation receipt to `project/noema-v1`; request owner/independent review; do not merge without authority.

## HC Brain remediation

Remediation/review subject:

- `thebrazenbeard/hc-brain` PR #18: **Qualify reference-kernel authority hardening**.
- Base: `main@cf92a32122c436beb5cc516bd7480af00f0ba29f`.
- Head: `noah/reference-kernel-authority-hardening-v1@c5d8851dfb14f73ce1a300135481d39030cf662f`.
- Current save readback: OPEN, DRAFT, MERGEABLE, 24 commits, 8 changed files.
- Purpose is to turn the existing branch-only hardened reference-kernel line into an explicit PR/CI/review subject. It already contains kernel/durable-kernel work and Four adversarial suites.

Observed GitHub Actions result: Reference Kernel run `34877037690` / run #47 failed with job `104086684790`, **zero executed steps**. Treat as infrastructure/runner failure, not source FAIL and not PASS.

Next HC work: locally run exact PR #18 head tests; route review/remediation receipt to `project/hc-brain-v1` / Noah; consider stale PR #1 disposition separately (do not close without owner authority); do not merge PR #18 without explicit authority/review.

## Vera Works remediation

Remediation PR:

- `thebrazenbeard/vera-works` PR #11: **Qualify revenue-experiment artifacts in Ops Spine**.
- Base: PR #10 exact head `ops/revenue-experiments-20260913@846aec2e6c1f438937785975e12dfe20de646c28`.
- Head: `one/ops-spine-qualification-remediation-20260914@94f07d62f84b01d715fe0812448c9a8ba3d0dfb1`.
- Current save readback: OPEN, DRAFT, MERGEABLE, 1 commit, 1 changed file.
- Change expands Ops Spine triggers to `work/revenue-experiments/**`, pins Node setup by immutable commit SHA, and adds execution of the three existing deterministic artifact suites.

Exact-head local verification was run on Lappy after cloning PR #11 head and PASSED:

- `HEAD=94f07d62f84b01d715fe0812448c9a8ba3d0dfb1`
- Root Python unit suite: **46 tests PASS**.
- Event-store validation: **62 events, errors=[]**, queues empty, resolved_holds=2.
- Agent behavior qualification proof: BEFORE `0/12` release `STOP`; AFTER `12/12` release `PASS`; `PROOF_PASS`.
- Agent release gate: **11 deterministic cases passed**.
- CSV Preflight v0.2: **PASS**.

GitHub Actions run #97 (`34877421530`) was observed QUEUED immediately after PR creation; fresh-read it in the next chat before assigning any CI status.

Next Vera Works work: fresh-read run #97; if runner infrastructure again yields zero-step failure, preserve local exact-head PASS separately from CI UNKNOWN/INFRASTRUCTURE_FAIL; route remediation receipt to `project/vera-works-v1`; do not merge without authority.

## Infrastructure / producer-gateway idea from Patrick's links

Patrick supplied references including Cloudflare Workers, Kong, APISIX, PostgREST, Supabase pg-gateway/jit-db-gatekeeper/proxy patterns, Envoy, supabase-js, and supabase-py.

Useful architectural conclusion:

- These patterns can help build a future **BT2 Authority/Producer Gateway**, but a proxy cannot manufacture upstream database privileges that WoWSQL free-shared does not grant.
- Do NOT resurrect Supabase as Lantern's currentness backend.
- If governed writes are desired later, a plausible design is ChatGPT/BT2 -> Cloudflare Worker (auth, request signature, idempotency, authority/policy checks) -> one narrow append endpoint -> PostgREST/RPC or direct PostgreSQL -> `bt2.append_material_v1(...)` -> immutable receipt.
- Read currentness can stay on qualified WoWSQL `bt2_project_read`.
- Write gateway should mechanically bind exact subject SHA, request identity, idempotency key, authority ceiling, allowed operation/effect, policy digest, and receipt.
- This is an architectural frontier only. Nothing has been deployed, no provider changed, and no protected credential has been created.

## Immediate continuation order

1. Fresh-read PR #11 Actions run #97 and preserve CI vs local-verification distinction.
2. Locally verify Noema PR #35 exact head and HC Brain PR #18 exact head because GitHub Actions produced zero-step failures.
3. Mirror/receipt the new remediation PRs to their project Bus hubs, including ABIL PR #6 now that `project/abil-v1` exists.
4. Obtain/route independent owner review on exact heads; repair real defects if found.
5. Do not merge/deploy/activate protected effects absent explicit authority.
6. Keep the Authority/Producer Gateway as a separate future design task unless Patrick asks to advance it.

## Restore behavior

On a new chat, first fresh-read canonical `bt2/main`, all four remediation PR heads/statuses, and the relevant project Bus hubs. Do not carry PASS/FAIL forward if a head moved. Treat this checkpoint as durable continuation evidence, not proof that external state is unchanged.