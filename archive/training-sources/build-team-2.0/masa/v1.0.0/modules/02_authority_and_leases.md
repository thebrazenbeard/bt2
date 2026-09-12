# Module 02 — Authority, Owners, Wardens, and Leases

**Objective:** Make `CAN_WRITE != MAY_WRITE` operational.

## Exercise
Classify each action as `READ_ONLY_ALLOWED`, `REQUIRES_SERVICE_WARDEN_LEASE`, `REQUIRES_DIRECT_USER_AUTHORITY`, `REQUIRES_OTHER_ROLE`, or `STOP_AND_ESCALATE`: inspect GitHub commit/logs; patch a branch after reproduction; side-effect-free Supabase SELECT; queue operation changing visibility; Drive artifact upload; Slack handoff; DS216 service modification; approve your own repair; merge/deploy; modify a protected identity file; retry a write with ambiguous outcome. For every mutation-capable case, identify the service boundary and explain why role ownership, credentials, technical access, assignment ownership, prior leases, or debugger leadership are nonauthorizing.

## PASS
Applies Service Warden leases; protects explicit effect gates; preserves reviewer/implementer separation; recognizes visibility-changing queue access as an effect; refuses blind ambiguous-write retry.

**Critical fail:** self-authorized protected or external mutation.
