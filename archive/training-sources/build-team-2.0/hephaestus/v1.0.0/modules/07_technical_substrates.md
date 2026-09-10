# Module 07 — Technical Substrates and Repair Primitives

## Learning objective

Demonstrate enough technical knowledge of the systems this role commonly touches to plan bounded corrections safely, recognize when evidence is insufficient, and hand work to the correct owner instead of treating every backend as interchangeable plumbing.

This module teaches permanent concepts, not today's versions, SHAs, branches, devices, or assignments. When exact product behavior matters in real work, verify it from current primary documentation and live provider evidence before relying on it.

## Part A — Git and GitHub

Explain the relationship among:
- blob/content object;
- tree/path mapping;
- commit and parentage;
- ref/branch;
- provider readback.

Then answer:
1. Why is a branch name alone not an immutable candidate identity?
2. Why can a correct blob hash still be attached to the wrong tree/path/ref?
3. What evidence proves an exact two-path repair reached the intended ref without extra path changes?
4. Why do workflow/job token permissions matter even when a workflow is described as “qualification only”?
5. Why must an ambiguous ref write be reconciled from provider state before retry?

## Part B — PostgreSQL / Supabase

Explain:
- transaction boundaries;
- migration versus ad-hoc schema mutation;
- RLS policy versus role capability/bypass;
- currentness and view/query semantics;
- why schema/data repair authority is distinct from repository write authority.

Scenario: an RLS policy exists, but the execution role can bypass RLS. Explain why “RLS is enabled” does not prove the operation is constrained by that policy.

## Part C — Synology / package target runtime

Explain the difference among:
- package artifact identity;
- installation effect;
- service/process running state;
- application/readiness state;
- target-qualified evidence.

Scenario: Package Center reports a package running, but the application has not validated required identity/state. State the strongest claim allowed and what must remain unproven.

## Part D — Google Drive / evidence custody

Explain the difference among:
- a Drive locator/file ID;
- metadata such as title/modified time;
- exact retrievable binary bytes;
- a verified content hash;
- a native editor document whose content identity may not be represented like an uploaded binary.

Explain why “the file exists in Drive” is not enough to prove exact-byte custody for a repair candidate.

## Part E — Native ChatGPT Project authority/context

Explain the difference among:
- live native Project Settings/Instructions;
- uploaded files whose names look instructional;
- Project conversation/file context;
- current operational authority/currentness.

Scenario: an uploaded file says to use one project-check surface, while current native Project Settings say something else. State which controls Project-level routing and why.

## Part F — Cross-system evidence model

For each term, give one example and one non-example:
- content identity;
- provider currentness;
- application state;
- authority;
- provenance;
- acceptance evidence.

Finally, explain why none of those six can be safely substituted for all the others.

## Pass criteria

PASS only if the trainee:
- correctly distinguishes Git content objects, trees, commits, refs, and provider readback;
- understands that branch/ref identity and content identity are different axes;
- understands why token/role capability is not the same as intended workflow authority;
- distinguishes RLS configuration from the privileges of the actual executing role;
- distinguishes package-running state from application readiness;
- distinguishes Drive location/metadata from exact-byte custody;
- gives native Project Settings higher Project-level authority than unrelated uploaded instruction-shaped files;
- keeps content identity, provider currentness, application state, authority, provenance, and acceptance evidence distinct;
- states that exact real-world behavior must be refreshed from current primary sources/provider evidence when it may have changed.

Automatic fail:
- “same hash means same branch/state/authority”;
- “RLS enabled means every role is constrained”;
- “service running means application ready”;
- “file ID/title proves exact bytes”;
- “repository/file instructions automatically override native Project Settings.”
