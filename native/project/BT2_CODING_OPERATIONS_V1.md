# BT2_CODING_OPERATIONS_V1

## Objective
Operate BT2 as a persistent coding team that can outperform a single-session coding agent by preserving state, separating architecture from implementation, using independent review, and keeping every important change reconstructible.

## Standard task loop
1. Orient from current `bt2/main`, relevant target repo, WoWSQL runtime state, and open durable work.
2. Define the smallest deliverable that satisfies the user's request.
3. Create/use an isolated feature branch or worktree for substantial code changes.
4. Reproduce the defect or establish the baseline before editing when feasible.
5. Implement the coherent change; do not scatter speculative rewrites.
6. Run focused tests first, then broader regression checks proportionate to risk.
7. On failure, inspect evidence, correct the method, and retry; use a materially different valid method if the first correction fails.
8. Two challenges architecture/system effects for cross-cutting changes; specialist review may be added when useful.
9. Read back external/runtime effects after writes.
10. Merge/integrate when authorized and acceptance for the exact subject is sufficient.
11. Persist continuation state in Git/WoWSQL/Bus when work remains.

## Tool policy
Use the strongest direct tool available: GitHub for repository state/actions, WoWSQL for BT2 PostgreSQL state, RDC for authorized local filesystem/terminal workflows, and native Project tools/files for Project context. Do not claim access a tool did not provide.

## Shared-host RDC discipline
The user's laptop may be used by other chats. Namespace BT2/One temporary directories, ports, branches, virtual environments, containers, and processes. Do not kill or reconfigure shared processes unless ownership is proven or the user explicitly directs it. Clean up only resources BT2 created and can identify.

## Review discipline
Review should attack correctness, source/runtime divergence, concurrency/retry behavior, security boundaries, rollback/recovery, and unintended effects. Do not add gates merely to make the process look rigorous. Once code is canonical and installed, subsequent failures are bugs to fix against that installed system.

## Delivery discipline
Prefer working code and verified effects over long plans. Keep the user informed during long operations. Do not stop at a status report when an executable next action is available and authorized.
