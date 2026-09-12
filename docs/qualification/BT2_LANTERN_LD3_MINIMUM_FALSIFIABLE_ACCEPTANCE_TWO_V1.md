# BT2 Project Lantern L-D3 Minimum Falsifiable Acceptance — Two V1

Status: SOURCE-READY ACCEPTANCE CONTRACT / L-D3 OPEN
Date: 2026-09-11
Systems Architect: Two
Coordinator / execution owner: One
Execution boundary: One + Two only

## Purpose

Define the smallest evidence set that can establish removal of the current Supabase runtime dependency without weakening Project Lantern currentness semantics.

This is intentionally narrower than global BT2 cutover and narrower than final destructive retirement. L-D3 concerns the consumer/runtime route. L-D4 still owns the final frozen-source check and destructive-retirement receipt.

Source readiness is not installation. Data parity is not routing. Historical references are not current dependencies.

## Current exact evidence

The currently effective Build Team Two Project instruction still requires exact Supabase project `agvhmutlrolbaijzlbqk` for Lantern-dependent currentness. Therefore L-D3 is presently OPEN.

Successor source exists on PR #2:
- `docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md`
- `docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V1.md`
- `docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V1.md`
- exact WoWSQL target `bt2-479e4ad9`

Fresh 2026-09-11 dual-provider readback established:
- Supabase B0 -> payload -> B1 stable;
- WoWSQL B0 -> payload -> B1 stable;
- profile digest equal: `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`;
- predecessor equal: `NULL`;
- policy digest equal: `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`;
- material count equal: 2;
- exact members equal;
- payload rows equal in material IDs, schema versions, semantic keys, canonical/source digests, canonical payloads, receipt IDs, profile/policy bindings, and created timestamps.

This proves present target read equivalence. It does NOT prove installation, routing cutover, failure-path behavior, or dependency-zero.

L-D1 is separately `VERIFIED_V2`; V1 failed-attempt rows remain append-only historical evidence and V2 alone has the VERIFIED acceptance receipt.

## Minimum falsifiable propositions

L-D3 may PASS only if all six propositions below pass against the same installed successor subject.

### P1 — Installed provider binding

**Claim:** The effective ChatGPT Project runtime contract names exact WoWSQL project `bt2-479e4ad9` as the Lantern currentness provider, and no effective currentness instruction still requires Supabase `agvhmutlrolbaijzlbqk`.

**Required evidence:** direct readback of installed Project instructions/files or equivalent authoritative Project configuration evidence, bound to the reviewed successor contract.

**Smallest hostile falsifier:** start a fresh Project runtime and inspect the effective Lantern instructions. If the runtime is still required to use Supabase, or if provider identity is ambiguous, P1 FAILS.

**Current status:** FAIL/OPEN — the current Project instruction still names Supabase.

### P2 — Cold-start currentness route

**Claim:** A fresh runtime, without being told which provider to use, resolves a Lantern-currentness request through exact WoWSQL `bt2-479e4ad9`, executes B0 -> payload -> B1, cross-binds membership/profile/policy exactly, and uses that result as current material evidence.

**Required evidence:** fresh-chat execution transcript/readback bound to the installed successor contract.

**Smallest hostile falsifier:** ask the canonical cold-start prompt. If the runtime consults Supabase, answers from prose/memory/Git, skips the stable-cut sequence, or cannot bind payload membership exactly, P2 FAILS.

**Current status:** NOT ESTABLISHED — source queries work, but the successor contract is not installed.

### P3 — Same-frontier semantic equivalence

**Claim:** Immediately before provider retirement, a frozen Supabase governed cut and a WoWSQL governed cut represent the same current material universe.

**Required evidence:** same-window Supabase B0 -> payload -> B1 and WoWSQL B0 -> payload -> B1 with exact equality of profile, predecessor, policy, member IDs, canonical digests, semantic keys, source digests, receipt IDs, canonical payloads, and relevant timestamps; normalized durable rowset digests must also match the final preserved source frontier.

**Smallest hostile falsifier:** any field, membership, lineage, payload, receipt, timestamp, or normalized-rowset mismatch FAILS P3. No majority/semantic-equivalence waiver is allowed.

**Current status:** PRELIMINARY PASS on the current two-member cut; MUST REPLAY at the final frozen frontier before retirement.

### P4 — Fail-closed successor behavior / no fallback

**Claim:** If WoWSQL currentness access is unavailable after cutover, the runtime returns `UNKNOWN`/clear limitation and does not fall back to Supabase, model memory, Git source, Project prose, or historical archive material as current Lantern state.

**Required evidence:** bounded failure-path acceptance in a fresh runtime with WoWSQL access unavailable or explicitly disabled.

**Smallest hostile falsifier:** any successful currentness answer derived from Supabase or lower-grade evidence after WoWSQL failure FAILS P4.

**Current status:** NOT ESTABLISHED.

### P5 — Authority non-amplification

**Claim:** Changing the currentness provider does not create producer authorization, material-admission authority, write authority, installation authority, runtime identity continuity, or any other protected effect.

**Required evidence:** post-cutover readback showing no new active producer permit/current authority unless separately and explicitly governed; fresh-runtime answer must preserve the read-only evidence ceiling.

**Smallest hostile falsifier:** the cutover itself creates or infers a producer grant, permits material admission merely because reads work, or treats historical permits/receipts as current authority. Any such effect FAILS P5.

**Current status:** TARGET PRECONDITION PASS (current producer authority is zero); post-install runtime behavior still requires acceptance.

### P6 — Operational dependency zero

**Claim:** After installation, every remaining occurrence of `agvhmutlrolbaijzlbqk` is historical/provenance/migration-only. No current executable path, Project instruction, operator contract, scheduled workflow, or currentness procedure requires the Supabase project.

**Required evidence:** authoritative Project configuration readback plus repository/runtime dependency classification. Historical/archive references may remain if their enclosing artifact has no route/currentness/authority effect.

**Smallest hostile falsifier:** identify one current executable or effective instruction path whose successful Lantern currentness behavior requires Supabase availability. One such path FAILS P6.

**Current status:** FAIL/OPEN — the currently effective Project instruction is itself such a path.

## Closure rule

`L-D3_RUNTIME_DEPENDENCY_CUTOVER = VERIFIED` only when P1-P6 all PASS against one exact installed successor subject.

Evidence from the pre-installation source-ready state cannot satisfy P1, P2, P4, or P6. Preliminary P3 evidence must be replayed on the final frozen frontier. P5 must be checked after installation even though current target authority is zero.

No proposition may be waived merely because the Supabase and WoWSQL rows currently match.

## Execution sequence

1. Freeze the reviewed successor source subject.
2. Deliberately update Project instructions/files from the Supabase contract to the WoWSQL successor contract.
3. Read back the installed configuration and evaluate P1.
4. Run fresh-chat normal cold-start acceptance and evaluate P2.
5. Run fresh-chat WoWSQL-unavailable failure-path acceptance and evaluate P4.
6. Re-read authority/permit state and evaluate P5.
7. Classify remaining Supabase references and prove no current route depends on them; evaluate P6.
8. At final pre-retirement freeze, rerun both providers and durable-rowset equivalence; evaluate P3.
9. Only then advance to L-D4 final freeze/retirement receipt and Patrick's separate destructive-retirement decision.

## Current disposition

`L-D3 = OPEN`

The database read semantics are presently equivalent. The decisive missing evidence is installed consumer routing plus failure-path behavior. Deleting Supabase before those are proven would convert an intentional fail-closed dependency into an outage, not a successful migration.
