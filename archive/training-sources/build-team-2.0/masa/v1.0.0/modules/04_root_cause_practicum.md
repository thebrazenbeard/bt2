# Module 04 — Root-Cause Debugging Practicum

**Objective:** Turn a symptom into the smallest defensible violated invariant.

## Exercise
A workflow fails with `permission denied`. One person proposes three retries plus a second API route; another proposes returning `UNKNOWN`. Produce: exact frozen subject; reproduction; observations; hypotheses; trigger; smallest violated invariant; root cause; severity/blast radius; dedup/failure-family decision; smallest hostile regression; correction oracle; falsifier/counterevidence; limitations; handoff target. Explicitly test deterministic auth/authz versus transient transport.

## PASS
Separates observation/hypothesis/trigger/root cause/impact; reproduces current exact subject; classifies deterministic auth/authz; deduplicates by invariant; creates oracle without implementing repair; states falsifying evidence.

**Critical fail:** retry-laundering deterministic failure or confident root-cause storytelling without evidence.
