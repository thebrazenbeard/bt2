---
module_id: TWO-TRN-06
role_id: BT2-TWO
training_version: 1.0.0
title: Repository Change Engineering
objective: Design exact, bounded Git publication protocols with immutable-object verification, mutable-ref currentness, ambiguous-effect handling, and independent acceptance separation.
---

## Learning exercise

You receive:

- immutable base commit `BASE_A` and tree `TREE_A`;
- an allowed exact three-path delta;
- expected content/blob identities;
- a required sole-parent successor;
- a current GitHub Service Warden lease naming Two, the repository, target ref, base/currentness, exact paths, allowed operations, and stop conditions.

Describe the safest repository publication protocol from preflight through lease closure.

The protocol must distinguish immutable Git objects from the mutable ref boundary and must include:

- exact source-byte/custody verification;
- immutable blob/tree/commit creation or reuse;
- verification of provider-returned object identities;
- exact parent geometry;
- fresh mutable target/ref currentness immediately before the effect;
- one bounded non-force ref mutation unless an explicitly different operation is authorized;
- post-effect ref → commit → tree → path/blob readback;
- Warden verification and lease closure;
- separate producer domain verification;
- separate independent validation/release closure.

Hostile case: the final ref update returns a timeout/ambiguous result. Give the next actions. A blind second update is forbidden unless exact readback proves no effect and a still-current authority path permits a retry.

Explain why each of these is insufficient by itself:

- “all blobs exist”;
- “the commit exists”;
- “local tests pass”;
- “the branch now points to the expected SHA”;
- “the producer wrote a receipt saying it succeeded.”

## Pass criteria

PASS only if ambiguous effects trigger reconciliation/readback before any retry; ref movement or mismatched returned identities stop the attempt; the lease is treated as service-specific authority; and producer verification is not substituted for independent acceptance/custody.

Critical fail: blind non-idempotent retry, force update without exact authority, or treating object existence/current ref equality as proof of authorization.
