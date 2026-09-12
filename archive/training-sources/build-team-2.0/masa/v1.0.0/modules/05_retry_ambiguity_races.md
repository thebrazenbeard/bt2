# Module 05 — Retry, Ambiguity, Idempotency, and Races

**Objective:** Handle transient reads, deterministic failures, non-idempotent ambiguity, and TOCTOU.

## Exercise
For each case state retry behavior and required evidence: GET timeout; 401; provider-documented rate-limit 403; Git ref update timeout after submission; ambiguous DB insert; queue `read` changing visibility; base ref moves between preflight and publication; crash after effect before durable receipt. Design one hostile regression each for Git ambiguity, ref movement, and crash-after-effect.

## PASS
Safe-read retry = same route then materially independent route; deterministic auth/authz/schema/hash/integrity classified directly; write ambiguity reconciled before retry; operation/idempotency identity used; TOCTOU handled; `OUTCOME_UNKNOWN` used when necessary; queue visibility trap recognized.

**Critical fail:** blind non-idempotent retry.
