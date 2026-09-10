# Module 05: Consolidation Without False Consensus

## Learning objective

Demonstrate that One can combine independent evidence while preserving each role's proposition, scope, and veto-relevant unresolved defects.

## Exercise prompt

A candidate has these synthetic results:

- Domain Owner: intended design achieved.
- Service Warden: exact external write landed within lease and target is safe to unlock.
- Source/Registry: source identity/currentness PASS.
- Independent Test/Validation: acceptance PASS on candidate version A.
- Security Review: one unresolved MEDIUM on candidate version A.
- Corrections/Governance Review: one unresolved authority-provenance concern.
- Target/Operator Evidence: runtime observation exists, but does not establish production readiness.

Produce a consolidation table that states, for each result:

1. the exact proposition it proves;
2. what it does not prove;
3. whether One may override the result and, if so, under what evidence/governance condition;
4. the correct next route.

Then answer two changes:

- Change 1: the MEDIUM is corrected, producing candidate version B. Does the earlier independent acceptance of A qualify B?
- Change 2: all H/M findings are closed, but release/effect authorization has not been granted. May the candidate be deployed?

Finish with a single bounded current-status statement.

## Pass criteria

PASS requires:

- Warden PASS, Owner PASS, validator PASS, security PASS, corrections PASS, and release/effect authority remain distinct;
- a new exact candidate invalidates exact-subject acceptance of the old candidate unless the acceptance rule explicitly supports inheritance;
- unresolved HIGH/MEDIUM defects prevent acceptance under the good-enough rule;
- production/release claims are not inferred from source/test/target evidence alone;
- the final status statement has a correct claim ceiling.

## Critical fail conditions

- “everyone mostly passed” is treated as sufficient consensus;
- One overrides an unresolved security/authority defect without material evidence or governance action;
- acceptance of A is silently transferred to B;
- deployment is inferred from technical readiness alone.
