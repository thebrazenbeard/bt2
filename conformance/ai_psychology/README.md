# AI-psychology outcome-feedback conformance seed

This is an **inert cross-repository contract oracle**, not an integration or a
production driver. It can falsify unsafe proposed outcome-reducer behavior
without requiring the private Bus, Supabase, a model server, MESO, Volition or
Pre-Active to be installed. No outgoing network and no external writes occur.

Run from the repository root:

```bash
python -m unittest discover -s conformance/ai_psychology -p 'test_*.py' -v
```

The green tests exercise *only this local reference contract*:

- claims with no independently governed witness fail closed;
- event-ID replay and conflicting payloads cannot apply twice;
- duplicate attempt IDs and reused evidence references across *different*
  event IDs cannot manufacture a second update;
- stale need revision, wrong goal/need, stale/future observation and mismatched
  witness bindings fail closed;
- failures, no-ops, ambiguous effects and non-improving outcomes cannot satisfy
  a need;
- valid fixture evidence produces a single in-process, thread-serialized
  revision advance, even when competing claims arrive concurrently.

One restart test is deliberately `expectedFailure` and two unimplemented
runtime qualification tests are explicitly skipped: there is **no installed**
MESO -> Volition -> Pre-Active -> independently witnessed outcome -> MESO/Volition
reverse integration, no durable cross-restart receipt store, and no atomic
MESO+Volition update. The dedicated GitHub Actions check exercises these local
tests only. A green suite with expected failures/skips **must not**
be represented as a runtime or physiological/emotional qualification.

## Next real adapter requirements

The test double `verifier` is controlled by the test itself. A production
adapter must establish observer identity and evidence custody independently of
any model/caller payload, bind evidence to an actual effect attempt, use a
durable atomic event/revision transaction across restarts/concurrent workers,
and preserve permanent conflict/rejection receipts. This reference oracle
does **none** of those things. It has no authority to call
`VolitionEngine.record_satisfaction()`, update MESO observations, or dispatch a
tool. Promoting this to a production seam requires separate implementation,
red/green hostile tests, and exact-runtime verification.

Coordination: `bt2_coordination_ai_psychology`,
[BT2 #61](https://github.com/thebrazenbeard/bt2/issues/61).
