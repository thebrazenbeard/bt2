# Module 04 — Operator Evidence and Claim Ceilings
**Objective:** Build current reproducible target evidence without claim inflation.

## Exercise A
Design `SIX_TARGET_EVIDENCE_PACKET_V1` covering immutable source/artifact; device/DSM/package/runtime; observation time/currentness bracket; action; authority/lease+operation ID; Package Center; raw lifecycle bytes+digest; parsed incarnation/generation/state/provenance/transition/process; status result; manager-effect evidence; responder/control-path evidence; independent positive cessation where applicable; failure/UNKNOWN; post-effect readback; observed external effects; limitations/nonclaims; claim ceiling.
Label which fields are evidence, authority, conclusions.

## Exercise B
Classify as `SOURCE_FACT`, `CURRENT_VERIFIED_OBSERVATION`, `HISTORICAL_OBSERVATION`, `INFERENCE`, or `UNKNOWN`:
Package Center displays Stopped; control path absent; source calls manager start exactly once; branch currently points to X; service definitely stopped; remote DSM access works; expected responder live; stale screenshot says running; post-effect manager receipt names exact op; product feature ready.

## Exercise C
Minimum evidence for stable STOPPED, stable RUNNING, manager Start effect, authorized manager Stop effect, independent cessation, product readiness. Explain why control-path absence alone is not universal authorized-Stop proof.

## PASS
Evidence/authority/conclusion distinct; currentness explicit; raw evidence preserved; stale history cannot satisfy current; manager effect and cessation separate; bounded claim ceiling + UNKNOWNs.

## FAIL
UI/screenshot/control-path/source code treated as interchangeable effect receipts.
