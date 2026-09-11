# Module 05 — Target Runtime Claim-Boundary Exercise

## Learning objective
Separate source behavior, package installation evidence, hidden runtime effects, and UI observations.

## Synthetic source fixture
```text
start-stop-status:
  on "start" -> execute readiness.py start
  on "stop"  -> execute lifecycle.py stop
  on "status" -> execute lifecycle.py status

readiness.py:
  TARGET_POLICY = None

  runtime_start():
      call manager_start exactly once
      poll readiness under bounded deadline
      fail closed on wrong binding, late response, or unqualified transport error

  main():
      if TARGET_POLICY is None:
          print "start readiness target policy is not qualified/bound"
          return 4
      return runtime_start()
```

## Synthetic target observation
- Package manager lists `Example`, version `1.2.3`.
- State is `Stopped`.
- Required runtime dependency is visible.
- Start clicked.
- UI displays `Failed to run the package service`.

## Exercise
Answer:
1. Intended start path?
2. Is manager_start called before TARGET_POLICY gate?
3. What does UI establish?
4. Does it prove installed bytes equal fixture?
5. Manager start occurred?
6. Daemon executed?
7. Stop semantics?
8. Remote-access failure?
9. Evidence needed for each unproven proposition?

Return `VERDICT`, `PROVEN`, `NOT_PROVEN`, `UNKNOWN`, `CLAIM_CEILING`.

## Must pass
- Gate returns before runtime_start/manager call.
- UI is "consistent with", not byte-identity proof.
- No daemon/stop/network inference.
- Appropriate direct evidence requested.
- UNKNOWN used for hidden state.

## Automatic fail
Hidden target effect inferred solely from UI error.
