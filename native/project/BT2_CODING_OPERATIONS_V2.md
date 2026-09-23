# BT2_CODING_OPERATIONS_V2

## Objective
Operate BT2 as a persistent coding team that can outperform a single-session coding agent by preserving reconstructible source state, separating architecture from implementation, using independent review, verifying effects, and containing external-provider failures.

## Standard task loop
1. Orient from current `bt2/main`, the relevant target repository, and open durable work.
2. Classify whether the task actually requires a live runtime-provider fact.
3. Recover current coordination/handoff state from the Bus when relevant.
4. Define the smallest deliverable that satisfies the user's request.
5. Create/use an isolated feature branch or worktree for substantial code changes.
6. Reproduce the defect or establish the baseline before editing when feasible.
7. Implement the coherent change; do not scatter speculative rewrites.
8. Run focused tests first, then broader regression checks proportionate to risk.
9. On failure, inspect evidence, correct the method, and retry; use a materially different valid method if the first correction fails.
10. Two challenges architecture/system effects for cross-cutting changes; specialist review may be added when useful.
11. Read back external/runtime effects after writes to those systems.
12. Merge/integrate when authorized and acceptance for the exact subject is sufficient.
13. Persist continuation state in Git and/or the Bus when work remains; WoWSQL persistence is optional unless the state itself is a WoWSQL-domain fact.

## Runtime-provider decision rule
Do not query WoWSQL by ritual.

Query it when at least one of these is true:
- the user asks about current WoWSQL state;
- the acceptance criterion requires a live database fact;
- a write/readback targets WoWSQL;
- Lantern currentness is materially required.

If none applies, source work should proceed without a database health gate.

If WoWSQL fails internally or is unreachable:
- mark dependent facts `UNKNOWN`/`UNAVAILABLE`;
- keep independent work running;
- do not substitute Supabase or stale source as runtime truth;
- do not repeat equivalent failing calls in a loop;
- record the limitation in any continuation checkpoint that depends on it.

## Tool policy
Use the strongest direct tool available: GitHub for repository state/actions, WoWSQL for BT2 PostgreSQL state when needed, RDC for authorized local filesystem/terminal workflows, the Chat Communication Bus for non-PR coordination, and native Project tools/files for Project context. Do not claim access a tool did not provide.

Tool availability is not authority. Tool failure is not evidence that a different source has become authoritative.

## Shared-host RDC discipline
The user's laptop may be used by other chats. Namespace BT2/One temporary directories, ports, branches, virtual environments, containers, and processes. Do not kill or reconfigure shared processes unless ownership is proven or the user explicitly directs it. Clean up only resources BT2 created and can identify.

## Review discipline
Review should attack correctness, source/runtime divergence, provider-failure containment, concurrency/retry behavior, security boundaries, rollback/recovery, and unintended effects.

Reject designs that make an unreliable optional provider a single point of failure for source recovery or unrelated coding work.

Do not add gates merely to make the process look rigorous. Once code is canonical and installed, subsequent failures are bugs to fix against that installed system.

## Delivery discipline
Prefer working code and verified effects over long plans. Keep the user informed during long operations. Do not stop at a status report when an executable next action is available and authorized.

A provider outage may narrow the final claim, but it should not erase completed independent work.
