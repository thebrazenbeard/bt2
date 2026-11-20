"""Synthetic, deterministic and non-operational illustration; no real source reads."""
from governor.engine import Signal, Context, EvidenceClass, evaluate
from governor.portfolio import diverse_briefing

STAMP = '2026-11-20T19:00:00+00:00'
HEAD = 'a'*40

def fixture(i, domain, severity, relevance, actionability, confidence, impact):
    return Signal(signal_id=f'fixture-{i}', fingerprint=f'fictional-risk-{i}',
        subject=f'fictional-repo-{i}', domain=domain, cause=f'fictional-cause-{i}',
        evidence_refs=(f'fixture://{i}',), evidence_classes=(EvidenceClass.SOURCE,),
        exact_head=HEAD, observed_at=STAMP, freshness_hours=72,
        severity=severity, relevance=relevance, actionability=actionability,
        confidence=confidence, hours_to_impact=impact,
        concrete_next_step='Inspect a bounded synthetic fixture',
        source_verified_by_evaluator=True, corroborated=True,
        owner_lane='EXAMPLE_REVIEWER')

signals = [fixture('security','security',5,5,5,5,6),
           fixture('memory','memory',4,4,4,4,24),
           fixture('noise','coordination',1,2,1,1,240)]
ctx = Context(now=STAMP, owner_lanes=frozenset({'EXAMPLE_REVIEWER'}),
              verified_signal_ids=frozenset(s.signal_id for s in signals),
              verified_head_bindings=frozenset((s.subject, s.exact_head) for s in signals))
result = evaluate(signals, ctx)
for d in result.decisions:
    print(d.public_record())
print('DIVERSE_PROPOSALS', len(diverse_briefing(result)))
print('NO_EXTERNAL_EFFECTS', not result.external_effects)
