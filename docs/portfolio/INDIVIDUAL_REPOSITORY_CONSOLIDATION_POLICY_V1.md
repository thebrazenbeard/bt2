# Individual Repository Consolidation Policy V1

Status: ACTIVE WORKING CONTRACT
Date: 2026-09-21
Scope: all repositories owned by `thebrazenbeard` observed in the live estate census.

## Intent

Consolidate each repository internally. Do not create a monorepo, silently move source between repositories, or treat one repository's currentness as another repository's currentness.

For each repository, establish one explicit current integration frontier while preserving necessary provenance and independently meaningful research/history.

## Allowed consolidation states

- `MAIN_CURRENT_NO_OPEN_PR`: default branch is the current source frontier and no open PR requires integration.
- `MAIN_CURRENT_WITH_HISTORY`: default branch is current, but non-PR historical/work branches require later provenance classification rather than deletion.
- `ACTIVE_PR_SINGLE`: one open PR is the only active integration frontier.
- `EXISTING_CONSOLIDATION_FRONTIER`: an existing reconciliation/integration PR is the preferred place to compose predecessor work.
- `MULTI_LANE_RECONCILIATION_REQUIRED`: the repo contains materially independent active lanes and must not be flattened into a fake linear stack.
- `POST_MERGE_VERIFY`: a consolidation effect occurred externally; exact main/readback must be verified before predecessor disposition.
- `ARCHIVED_HOLD`: preserve archived state unless separately authorized.
- `RECOVERY_OR_IDENTITY_HOLD`: source identity or recovery semantics are unresolved; do not canonicalize by convenience.

## Rules

1. Fresh-read exact default-branch head and active PR heads before any write.
2. Prefer an existing successor/reconciliation PR over creating another meta-PR.
3. When a repo has parallel scientific/research lanes, preserve those lanes and create a source-level integration frontier only where composition is semantically valid.
4. A predecessor PR may be marked superseded only after the successor demonstrably contains or intentionally replaces its relevant source/evidence.
5. Do not delete branches or close historical PRs solely to make the repository look clean.
6. Do not merge to a canonical/default branch, force-push, deploy, change credentials/providers/rulesets/visibility, or perform destructive cleanup without separate live authority.
7. After any externally performed merge/ref move, read back the exact default-branch head before changing status.
8. Cross-repository references must be provenance pointers, not silent source substitution.
9. Archived repositories stay archived unless the user separately authorizes reopening them.
10. Repo-local consolidation is complete only when a fresh session can identify: canonical head, active frontier, preserved predecessor/history, unresolved blockers, and next executable action.

## Portfolio execution order

Run repositories independently in descending currentness risk:
1. repositories with contaminated/ambiguous main or active canonicalization candidates;
2. repositories with large PR/branch sprawl;
3. repositories with smaller active stacks;
4. repositories with orphan/history-only branches and no open PRs;
5. clean single-frontier repositories, which need only verification.

This policy records consolidation method only. It does not itself authorize any protected effect.
