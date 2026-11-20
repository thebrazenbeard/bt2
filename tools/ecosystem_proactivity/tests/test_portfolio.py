import sys
import unittest
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).parents[1]))
from test_engine import sig,ctx
from governor.engine import Action, evaluate
from governor.portfolio import DependencyEdge, blocked_consumers, diverse_briefing, explicit_feedback


class PortfolioTests(unittest.TestCase):
    def test_owner_scoped_provisional_dependencies(self):
        edges=[DependencyEdge('memory','reviewer-auth','doc-missing','repo/docs/contract@sha'),
               DependencyEdge('memory','live-currentness','need-binding','repo/docs/runtime@sha'),
               DependencyEdge('gui','human-consent','need-human','vnc/host@sha')]
        b=blocked_consumers(edges,frozenset({'reviewer-auth'}))
        self.assertEqual(b,{'gui':('human-consent',),'memory':('live-currentness',)})

    def test_diverse_briefing_avoids_one_lane_monopoly(self):
        signals=[]
        for i in range(5):
            signals.append(sig(signal_id=f's{i}',fingerprint=f'network-{i}', subject=f'host#{i}'))
        signals.append(sig(signal_id='s6',fingerprint='creative-1',subject='design#1',domain='creative'))
        signals.append(sig(signal_id='s7',fingerprint='memory-1',subject='memory#1',domain='memory'))
        c=ctx(verified_signal_ids=frozenset(s.signal_id for s in signals),daily_notification_limit=1)
        b=evaluate(signals,c)
        briefing=diverse_briefing(b,limit=4,max_per_domain=2)
        self.assertEqual(len(briefing),4)
        self.assertEqual(len([x for x in briefing if x.domain=='security']),2)
        self.assertEqual(set(x.domain for x in briefing),{'security','creative','memory'})

    def test_feedback_requires_explicit_label_and_is_reversible(self):
        c=ctx()
        head=sig().exact_head
        after=explicit_feedback(c,'risk-1','test-repo#1',head,'NOISY')
        self.assertEqual(evaluate([sig()],after).decisions[0].action,Action.DRAFT)
        restored=explicit_feedback(after,'risk-1','test-repo#1',head,'ACCEPTED')
        self.assertEqual(evaluate([sig()],restored).decisions[0].action,Action.NOTIFY)
        self.assertEqual(c.feedback,())
        with self.assertRaises(ValueError):
            explicit_feedback(c,'risk-1','test-repo#1',head,'AUTO_DETECTED')
        with self.assertRaises(TypeError):
            explicit_feedback(c,'risk-1','NOISY')

    def test_explicit_feedback_does_not_cross_subject_or_head(self):
        head=sig().exact_head
        c=ctx(verified_head_bindings=frozenset({('test-repo#1',head),('different-repo#2',head)}))
        after=explicit_feedback(c,'risk-1','test-repo#1',head,'NOISY')
        other=sig(subject='different-repo#2')
        self.assertEqual(evaluate([other],after).decisions[0].action,Action.NOTIFY)
        self.assertEqual(evaluate([sig()],after).decisions[0].action,Action.DRAFT)
        revised=explicit_feedback(after,'risk-1','test-repo#1',head,'ACCEPTED')
        self.assertEqual(evaluate([sig()],revised).decisions[0].action,Action.NOTIFY)
        self.assertEqual(evaluate([other],revised).decisions[0].action,Action.NOTIFY)

    def test_briefing_is_just_data_not_queued_work(self):
        b=evaluate([sig()],ctx())
        t=diverse_briefing(b)
        self.assertFalse(b.monitor_is_active)
        self.assertFalse(b.external_effects)
        self.assertFalse(t[0].effect_authority)
        self.assertFalse(t[0].emitted)


if __name__=='__main__':unittest.main()
