# Module 05 — Operator Runbook Without Assuming SSH
**Objective:** Obtain decisive evidence through a small human procedure without destroying failure state.

## Required research
Retrieve current official Synology documentation for remote DSM/QuickConnect or applicable remote access. Access is only an access route unless authoritative evidence proves more.

## Exercise
Design the smallest no-SSH-assumption runbook that records target/time; immutable pre-action Package Center evidence; exact action+authority/operation ID; visible terminal result or absence; GUI evidence gaps; smallest separately authorized read-only/local route to close them; failed state before further mutation; no retry-to-green; distinct remote-access, DSM-session, Package Center, readiness, manager, process/responder, and product-semantic failure classes.

### Adversarial case
Remote DSM drops immediately after the operator presses Start. Outcome unknown. Give the next action. Do not press Start again until effect state is reconciled.

## PASS
Remote access not service-state authority; ambiguous Start -> readback/reconciliation; runbook is small but provenance-preserving; gaps named; missing evidence route escalated.

## FAIL
Starts with reboot/Repair/retry or treats connection loss as proof mutation did not happen.
