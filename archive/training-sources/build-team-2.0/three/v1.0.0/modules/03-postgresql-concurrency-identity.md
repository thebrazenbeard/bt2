# THREE-TRAIN-03 — PostgreSQL Concurrency, Visibility, and Identity

## Learning objective
Reason correctly about PostgreSQL identity allocation, MVCC, isolation, and completeness.

## Scenario
At snapshot B0, committed rows visible to you have IDs 1, 2, 4. Another transaction has already allocated ID 3 but has not committed. You record MAX(id)=4. Later ID3 commits. At B1, the visible set is 1, 2, 3, 4.

Answer:
1. Why does `WHERE id > 4` fail to recover the B0 -> B1 delta?
2. What exactly did MAX(id)=4 prove at B0?
3. Distinguish sequence allocation order from commit/visibility order.
4. Give at least two mechanically valid ways to define a completeness/currentness boundary for a system that actually needs one.
5. Compare READ COMMITTED, REPEATABLE READ, and SERIALIZABLE for the relevant guarantees.
6. Explain when an advisory lock is useful and why it is not enforcement against writers that ignore the protocol.

## Pass standard
Any answer treating ID order as commit order fails.