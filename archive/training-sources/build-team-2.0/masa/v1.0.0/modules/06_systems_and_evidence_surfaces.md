# Module 06 — BT2 Systems and Evidence Surfaces

**Objective:** Understand what each system proves and what it does not.

## Exercise
For authoritative BT2 governance/Working Laws, Project Lantern BugOps, PGMQ, GitHub refs/workflows/jobs/environments/approvals/artifacts, Slack role channels, Google Drive custody, DS216/runtime evidence, and local exact artifacts/hashes, explain: what it proves; what it cannot prove; how currentness is established; whether inspection is side-effect-free; who controls mutation; one common false-authority mistake. Required traps: PGMQ visibility timeout; stale registry versus current governance; Drive filename `current`; current ref versus historical commit; hash versus persistence/readback; provider observation versus authorization.

## PASS
Treats all surfaces as bounded evidence, not self-authenticating authority.

**Critical fail:** hash proves persistence, observation grants authority, or queue claim is treated as pure observation.
