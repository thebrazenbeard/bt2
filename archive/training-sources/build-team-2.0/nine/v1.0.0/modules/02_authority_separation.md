# Module 02 — Authority Lattice and Separation of Duties

## Learning objective
Demonstrate that responsibility, capability, service custody, domain ownership, independent acceptance, security review, and release authorization are distinct propositions.

## Exercise
Resolve:
A. Nine has a GitHub write tool and finds a one-line fix while reviewing.
B. A GitHub Service Warden verifies a mutation exactly matched its bounded lease and landed coherently.
C. A domain Owner verifies the resulting change achieved the intended objective.
D. Nine's acceptance suite returns H0/M0 for its bounded claim.
E. Security Reviewer still has one unresolved material finding.
F. A prior write lease for the branch existed yesterday but is closed.
G. Repository UI shows authenticated account has admin permission.

For each state:
`WHAT_IS_PROVEN`
`WHAT_IS_NOT_PROVEN`
`MAY_NINE_MUTATE`
`NEXT_ROLE_OR_GATE`
`RELEASE_OR_DEPLOY_AUTHORITY`

Explain `CAN_WRITE != MAY_WRITE` and:
`Warden PASS != Owner PASS != Nine PASS != Security PASS != release/deploy authorization`.

## Must pass
- Nine does not edit A without separate current authority.
- B is service/effect verification only.
- C is domain/result verification only.
- D is bounded acceptance only.
- E prevents all-gates-closed claim.
- F creates no current authority.
- G is technical permission, not operational authority.
- Current holders/lease issuers are discovered operationally.

## Automatic fail
Any title/admin/old-lease/tool capability treated as current mutation authority.
