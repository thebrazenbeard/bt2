# Two — conditional structural invariants (2026-10-29)

**Status:** Source-level REFINE proposal, not a model behavior result or a live
T’Kal-in-ket quorum. BT2 source basis: archived
`build-team-2.0@950112a697550b689049da807f2d8176a507c38f` identifies Two as
**structural, abstract, systems-first**. The current dossier's 8 TRAIN / 2 DEV
case split and evidence provenance are preserved.

**Challenge source:** `thebrazenbeard/t-kal-in-ket`, `docs/PROTOCOL.md` blob
`eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff`. Its Purist Logic,
Pragmatism, and Bridge lenses inspired the following *analytical questions*.
This is independent source inspection, **not** evidence that three peers or
models were invoked; no software from that unlicensed repo was copied.

## Claim and falsifiers

Claim under review: "Two can reject unnecessary distributed coordination by
identifying the smallest sufficient invariant."

> **Purist Logic:** Does the rule still hold when the effect transitions from
> repeatable computation to non-repeatable billing or notification? A blanket
> "never coordinate" answer fails; a blanket "always elect a leader" also fails.

> **Pragmatism:** Can two workers race or retry after a crash and produce two
> charges despite content-addressed output? If yes, where is the smallest
> enforced idempotency boundary?

> **Bridge:** Does minimizing current computation cost silently discard future
> customer-facing consistency, or demand a needless cluster today?

**Disposition: REFINE.** Revised `two-persona-train-008` explicitly asks about
today's harmless duplicate work and tomorrow's billing/notification effects.
Its target reply distinguishes atomic content publication from idempotent
external effects, names crash/retry tests, and defers infrastructure choice
until the invariant genuinely requires it. This corrects the hidden risk of
training a reflexive *anti-complexity* slogan rather than structural judgment.

## Verification ceiling

`tests/test_identity_two_challenges.py` failed before the case change and
passes afterward. It guards the conditional scenario's coverage but cannot
grade generated reasoning, demonstrate LoRA learning, or authenticate a quorum.
Reserved independent inference remains necessary.
