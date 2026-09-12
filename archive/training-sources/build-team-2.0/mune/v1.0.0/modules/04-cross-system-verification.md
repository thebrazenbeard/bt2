# Module 04 — Cross-System Verification

## Learning objective
Keep source, custody, coordination, provider application, and target behavior orthogonal.

## Scenario
One release claim spans GitHub, Supabase/Postgres, Drive, Slack, and a target runtime.

## Exercise
Produce a verification matrix for:
1. exact GitHub source/head/tree/path set;
2. exact database schema/function/role/RLS state;
3. exact Drive object/revision/custody;
4. Slack message existence/addressing;
5. provider migration/application;
6. target runtime consumption/behavior.

Give at least eight invalid implications, including examples such as:
- commit exists → deployed;
- row exists → consumed/current;
- Slack delivery → target acted;
- green local test → provider qualified;
- file title → artifact identity.

For every system, identify what current Owner/Warden interface is required if mutation becomes necessary.

## PASS
- all six evidence planes remain separate;
- at least eight false implications are rejected;
- mutation escalation is correctly routed;
- provider and target behavior require readback rather than source inference;
- coordination is not canonical memory or automatic execution.

## Fatal FAIL
Any collapse of source→provider, provider→target, coordination→consumption, or artifact presence→authority.
