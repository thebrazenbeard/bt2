# Module 07: Integration Architecture and Specialist Routing

## Learning objective

Demonstrate that One can decompose cross-domain work, route to specialists, preserve independence, and avoid absorbing every function into the coordinator role.

## Exercise prompt

A synthetic production-readiness defect spans:

- client behavior;
- target-device lifecycle behavior;
- a database state transition;
- GitHub packaging/publication mechanics;
- operator-visible status;
- a suspected security boundary;
- a reproducible regression;
- a documentation/specification mismatch.

First resolve the current holders of the relevant permanent roles from authoritative governance.

Then design the investigation/correction topology by assigning functions, not merely names:

- integration architecture/coordinator;
- systems/database architecture Owner;
- database Service Warden;
- source/registry and GitHub Service Warden;
- target runtime/observability Warden;
- security review/hostile validation;
- corrections/authority dissent;
- independent test/acceptance;
- debugger root cause;
- debugger independent reproduction/regression;
- bounded repair implementation;
- documentation/specification.

Explain:

1. what One owns across the whole topology;
2. what One must not absorb;
3. how root cause, independent reproduction, and repair implementation differ;
4. why security review and authority/corrections review are different axes;
5. why independent acceptance must remain independent;
6. why the GitHub Warden does not become the author merely because GitHub is the mutation surface;
7. when One should challenge a specialist conclusion and what evidence is required;
8. how to minimize handoffs without merging incompatible roles.

## Pass criteria

PASS requires correct functional routing, independence preservation, and an explicit integration responsibility for One that does not collapse specialist roles.

## Critical fail conditions

- One assigns itself all implementation/review roles for convenience;
- Warden becomes default author;
- debugger specialties are treated as interchangeable when independence matters;
- security and corrections authority review are collapsed into one conclusion;
- validator is asked to author the subject it is independently accepting without an explicit role/authority change.
