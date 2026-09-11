# Module 03 — DS216 / DSM Execution Model
**Objective:** Reason from operator action through DSM lifecycle to process/product semantics without skipping evidence boundaries.

## Required research
Retrieve current official Synology package lifecycle/start-stop-status documentation. Record locator and observation. Material contradiction with the teaching model => `TRAINING_VERSION_STALE_ROLE_DRIFT`.

## Training fixture — NOT operational state
Fictional versioned package pipeline:
`Package Center -> DSM prestart/start dispatcher -> readiness gate -> manager_start -> package-user service -> process -> control responder -> durable lifecycle state -> Package Center status`.
Fixture:
- status contract `RUNNING=0`, `STOPPED=3`, `UNKNOWN/transitional=4`;
- Start enters readiness;
- readiness policy is `UNBOUND`;
- UNBOUND returns rc4 **before manager_start**;
- operator sees “Failed to run the package service”;
- product semantic state separately says `BLOCKED_FEATURE_NOT_IMPLEMENTED`.

## Exercise
For every boundary state: invoker; evidence proving it occurred; evidence not proving it; UNKNOWN propagation.
Then state fixture proven/disproven/UNKNOWN facts, why “service crashed” overclaims, and why process RUNNING still cannot establish product feature readiness.
Specify fresh target evidence needed to prove manager effect, expected responder, current durable RUNNING, and product readiness.

## PASS
UI != manager effect; source/fixture flow != target execution; runtime RUNNING != product readiness; rc4-before-manager is not daemon crash; UNKNOWN survives unobserved boundaries.

## FAIL
Infers unseen manager/process activity from UI or promotes package health into product readiness.
