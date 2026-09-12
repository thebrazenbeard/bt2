---
module_id: TWO-TRN-03
role_id: BT2-TWO
training_version: 1.0.0
title: Systems architecture under hostile assumptions
objective: Define invariants, trust roots, state/currentness semantics, concurrency, UNKNOWN behavior, and cross-role handoffs before choosing mechanisms.
---

## Learning exercise

Design a stateful feature spanning repository code and PostgreSQL. Do **not** begin with tables, endpoints, or code.

First define:

- system invariant;
- authoritative/trusted evidence sources and what is explicitly nonauthoritative;
- stable identities versus mutable observations;
- state machine and allowed transitions;
- currentness cuts and generation/incarnation binding;
- concurrency/serialization model;
- idempotency and replay rules;
- failure and `UNKNOWN` behavior;
- claim ceiling;
- cross-service lease boundaries;
- independent review boundaries.

Then propose the smallest mechanism that implements those requirements.

Attack your own design with these cases:

- stale base;
- duplicate exact request;
- conflicting semantic duplicate;
- crash after durable DB effect but before receipt;
- two concurrent writers;
- ABA generation reuse;
- cloned/restored state presenting a familiar identifier;
- inaccessible required evidence;
- model-generated receipt claiming success;
- mutable provider state moves between opening and closing observations.

For every hostile, state `PASS`, `FAIL_CLOSED`, `UNKNOWN`, or `REQUIRES_ESCALATION`, and explain why.

Finally assign responsibilities for architecture, schema/state stewardship, service mutation, security hostile review, independent acceptance, custody, and governance/integration.

## Pass criteria

PASS only if invariants/trust/currentness are defined before mechanism; stale/replay/ABA cases are not waved away by identifier equality; UNKNOWN is used when evidence cannot justify a state transition; and producer work remains separate from independent validation and service authority.

Critical fail: lets caller-supplied/model-generated fields self-authorize a state transition or treats a same-looking identifier after an intervening generation as sufficient currentness proof.
