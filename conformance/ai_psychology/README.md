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

## Source-only MESO -> Volition -> Pre-Active correlation envelope

`lineage_envelope.py` is a separate, narrower **advisory-only** contract and
does not run the outcome oracle's test-controlled verifier. Its `ForwardTrace`
records *claimed* MESO source event -> signal -> goal/choice/target identity,
`CurrentGoalBinding` records a *claimed* current goal receipt, and
`CandidateTrace` reflects the current Pre-Active V1 outcome candidate fields.
When the goal instance, choice, signal, target, candidate goal, candidate state
and observation window are structurally consistent, the only result is
`CORRELATED_UNVERIFIED`, with `authorization_effect=NONE`,
`may_complete_goal=False` and `may_update_need=False`. The SHA-256 correlation
digest proves deterministic serialization of **caller inputs only**, never
the existence, custody, authenticity, or causal relationship of an observation.

The V1 candidate itself has **no choice ID, MESO event ID or signal ID**. The
candidate `need_id` and `action_request_id` remain claimant supplied, with
neither an upstream MESO need observation nor any independently verified tool
effect. The complete Pre-Active V1 claim fields affecting identity are included
in the correlation digest, notably `claimed_need_change`, `source_actor_id`,
`source_revision`, `schema_version` and evidence timing. No independent
**absolute need observation** is admitted from this self-reported delta. A
same-target stale-goal/choice (ABA) mismatch, future/expired or
rejected candidate and model-generated self-report are held. Even a
structurally correlated `SUCCESS` cannot claim satisfaction or need reduction.
This correlation seam is not a substitute for independent witness custody.

`InertLineageIndex` reserves event identities and rejects conflicting replays
**within one process** (including initial HOLD receipts), but it is purposely
volatile. Recreating the index after a crash forgets all event IDs; cross-
restart idempotence, durable rejection records, and atomic rollback are still
unimplemented **runtime blockers**, not green-test achievements. Separately,
the MESO, Volition and Pre-Active repositories must integrate their own
persisted receipts under independent custody before this can advance beyond
source-level conformance. LGCM (prediction/evaluation), F.U.C.K.U.P. (durable
reconciliation) and Physica (simulation) are adjacent evaluation candidates,
**not** qualified outcome observers or a source of admitted effect evidence.

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

## Optional Lou-Pole adversarial review handoff

`lou_pole_advisory.py` consumes a local FreeRowCochkar/Lou-Pole
`--json --provenance` report plus the **exact UTF-8 input bytes** used for that
report. It checks the source-text SHA-256, validates bounded source evidence
and shapes, and emits `BT2_LOU_POLE_ADVISORY_V1` on stdout. It performs **no
network access, engine execution, model inference, or protected state update**.

For a separately installed, reviewed Lou-Pole checkout:

```bash
freerowcochkar rules.txt --profile instructions --json --provenance > report.json
python conformance/ai_psychology/lou_pole_advisory.py \
  rules.txt report.json --engine-revision 245186d6baad672460dec112b916470d8b13633e
```

The example commit is Lou-Pole's inspected `main` source revision from
2026-10-25; update it to the exact **actual** engine revision before use. The
adapter accepts only a well-shaped SHA but **cannot verify that revision or
prove the report really came from the engine**. A caller-declared `source_url`
is preserved as unverified metadata, never fetched or authenticated. The
input is limited to 64 KiB, incoming JSON to 128 KiB and output to 64 KiB.
The CLI checks for symlinked paths (best-effort on Windows and against path
races) and rejects non-ordinary inputs. Source text produced with
different newline normalization fails the digest check closed.

Candidate findings are advisory only. Even zero findings and apparently full
coverage produce `NO_DETECTED_FINDINGS_NOT_CLEARED`, never `PASS` or a grant.
This wrapper cannot attest independent outcome evidence, reduce a MESO need,
mark Volition satisfied, approve Pre-Active, or authorize VeraMono effects.
The local conformance suite exercises the wrapper and its negative boundaries;
this is **not** an installed cross-repository runtime integration.
