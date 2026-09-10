# BT2 Canonical Database Hardening Qualification — Two V1

Status: **PARTIAL QUALIFICATION / CORE INTEGRITY SLICES PASS / CUTOVER NOT YET QUALIFIED**

Date: 2026-09-10
Reviewer/implementer: Two
Coordination: `BT2-CANONICAL-PLATFORM-20260910`
Target: WoWSQL `bt2-479e4ad9`
Source branch: `work/two-canonical-platform-integrity-v1`

## Evidence discipline

This record distinguishes source, runtime application, behavioral qualification, and remaining unknowns. A successful migration statement is not by itself behavioral qualification. Rollback-contained probes were used where possible so qualification evidence did not leave synthetic runtime records.

## Source/runtime binding

The canonical database definition is now represented in GitHub by:

- `database/schema/0001_bt2_runtime_baseline.sql`
- `database/schema/0002_bt2_runtime_indexes_views_functions.sql`
- ordered hardening migrations `0003` through `0011`

The source chain captures the pre-hardening WoWSQL runtime and then applies reviewed changes. The live WoWSQL target has been advanced through the same logical hardening sequence. No old repository/schema retirement or canonical cutover is implied.

## Identity, topology, training and recovery

Disposition: **PASS FOR TESTED INVARIANTS**.

Behaviorally verified with rollback-contained hostile probes:

- invalid orchestration shape is rejected;
- cross-agent qualification/package binding is rejected;
- cross-agent operational-checkpoint predecessor is rejected;
- workspace checkpoint generation must advance the locked workspace HEAD exactly once;
- stale/noncontiguous workspace generation is rejected;
- operational and workspace checkpoint histories reject mutation;
- external-effect operation history preserves a linear append-only event chain;
- `PREPARED -> ATTEMPTED -> VERIFIED` succeeds with required receipt data;
- illegal direct `PREPARED -> VERIFIED` transition is rejected.

Runtime/session provenance is represented separately from durable agent identity. No runtime locator is promoted into logical-agent identity by equality.

## Dispatch queue V2

Disposition: **PASS FOR TESTED RESPONSE-LOSS / LEASE SEMANTICS**.

A live stale-lease incident occurred while Two was consuming One's architecture assignment: the original lease expired before ACK; ACK failed `STALE_OR_INVALID_LEASE`; readback showed the item had not been reclaimed; Two reclaimed it under a new generation/token and ACKed exactly once.

Queue V2 then received source-first hardening and rollback-contained qualification covering:

- enqueue response-loss replay converges by caller-supplied enqueue identity and request digest;
- same enqueue identity with a different request digest is rejected;
- claim request replay returns the original claim receipt and does not renew lease authority;
- claim generation increases on reclaim;
- stale/expired lease tokens cannot ACK or release current work;
- ACK response-loss replay is idempotent;
- release/dead replay is idempotent for the exact action digest;
- terminal queue projection clears lease token/owner/expiry;
- queue transitions are retained in append-only `work_queue_events`;
- historical pre-V2 queue state is represented by `MIGRATED_SNAPSHOT`, not fabricated event history.

Qualification rollback readback showed zero synthetic test queue rows, claim requests, or queue events remained.

## BugOps convergence

Disposition: **PASS FOR TESTED CANONICAL LIFECYCLE**.

The source BugOps system was independently inspected before normalization. The canonical model preserves independent defect `state_version`, `routing_revision`, and `dispatch_revision` rather than collapsing them into one generation. Severity is canonically stored as `SEV-0..SEV-3`; legacy `CRITICAL/HIGH/MEDIUM/LOW` inputs are accepted through an explicit mapping.

Source-first runtime qualification discovered and corrected three implementation defects before PASS:

1. nested Queue V2 output names collided with `report_bug_v2` output variables;
2. the same collision existed in route/reopen paths;
3. non-CLOSED status transitions referenced an unassigned closure-evidence record.

Corrective migrations are `0008`, `0009`, and `0010`.

The final unchanged lifecycle probe reached `BUGOPS_V2_ROLLBACK_PASS` after verifying:

- report succeeds and normalizes `HIGH -> SEV-1`;
- replay of the same operation returns the established result;
- the same intake/digest under a different operation adopts one canonical bug;
- initial bug dispatch validates while current;
- route increments state, routing, and dispatch revisions;
- route operation replay is idempotent;
- stale dispatch revision is rejected;
- a previously claimed dispatch becomes invalid after reroute;
- the current routed dispatch validates;
- ordinary status transition preserves dispatch revision;
- CLOSED without current complete closure evidence is rejected;
- closure evidence bound to the exact current bug state permits close;
- close increments dispatch revision and invalidates outstanding dispatch;
- reopen creates a new state and fresh coordinator dispatch;
- reopened dispatch validates;
- closure evidence from the old state cannot close the reopened bug;
- the append-only bug event count matches the tested lifecycle.

Rollback readback confirmed zero probe bugs, bug queue rows, BugOps operations, or probe closure-evidence rows remained.

## Governed material / Lantern

Disposition: **CURRENT READ CUT PASS / ADMISSION NEGATIVE GATES PASS / POSITIVE CONCURRENT ADMISSION NOT EXECUTED**.

Lantern was rebound to exact Supabase target `agvhmutlrolbaijzlbqk` using the governed B0 -> payload -> B1 sequence. B0 and B1 were identical. The current source cut remained exactly two materials under:

- profile `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- policy `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`

WoWSQL `bt2.material_cut_v1('PROJECT_LANTERN')` returned the same two member UUIDs and canonical/semantic/source digest tuples after the admission-function change. Active producer-permit count remained zero.

The prior canonical admission implementation compared material `exact_members` around a SHARE lock on the profile table. That was timing-sensitive rather than useful serialization: unrelated material membership could change while the actual serialized subject was profile lineage. `0011_lantern_admission_lineage_equivalence_v1.sql` restores the source Lantern rule by comparing the complete accepted-profile lineage before and after profile-table serialization.

Non-authorizing rollback qualification reached `LANTERN_NEGATIVE_ROLLBACK_PASS` and verified:

- duplicate JSON keys are rejected before canonicalization;
- a valid material request with no current producer permit is rejected without partial material creation;
- duplicate semantic identity is rejected by the canonical uniqueness invariant;
- no active producer permit is created or reactivated by qualification.

A positive simultaneous-distinct-admission test is intentionally **not claimed**. There is no current producer authorization, and this workstream does not authorize manufacturing one for testing. Source-equivalent lineage serialization is now installed; positive concurrent admission remains a future qualification case when an authorized isolated qualification subject exists.

## GitHub Projects / GraphQL-capable route check

At Patrick's direction, Two explicitly checked the connected GitHub surface beyond ordinary REST wrappers before declaring any GitHub capability absent. GraphQL-backed PR review and review-thread routes are available and were used to inspect BT2 PRs #1, #2, and #3. No submitted reviews or inline review threads were present at that check. No Projects-v2/board-specific wrapper was exposed by connector discovery under `project`, `board`, or the available GraphQL-capable function set. This is a connector-surface observation, not a claim that GitHub itself lacks Projects GraphQL APIs.

## Remaining cutover blockers / unknowns

This qualification does **not** establish full canonical-platform cutover readiness. Remaining work includes:

- positive authorized concurrent material-admission qualification;
- complete legacy/history import and digest/count verification;
- canonical training-package and qualification population from One's recovered source universe after relational hardening integration;
- access-control/service-boundary qualification for WoWSQL;
- blank-database rebuild from the canonical source chain and execution of the full migration acceptance suite;
- final compatibility/retirement proof for old repositories/APIs/schemas;
- explicit Patrick-authorized cutover/retirement decision.

No merge, source retirement/deletion, qualification manufacture, Vera-Supabase mutation, or canonical cutover is asserted by this record.
