import sys
import unittest
from dataclasses import replace
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, str(Path(__file__).parents[1]))
from governor.engine import (
    Signal, Context, Action, EvidenceClass, decide_one, evaluate, measure,
    parse_time,
)

HEAD = 'daf3f1e5eacdc1a464600fea833b7e89404a7d62'
TIME = '2026-11-20T23:00:00+00:00'  # a fixed simulated clock


def sig(**kw):
    values = dict(signal_id='s1', fingerprint='risk-1', subject='test-repo#1',
                  domain='security', cause='unexpected-loader',
                  evidence_refs=('repo/path@' + HEAD,),
                  evidence_classes=(EvidenceClass.SOURCE, EvidenceClass.CI),
                  exact_head=HEAD, observed_at=TIME, freshness_hours=48,
                  severity=5, relevance=5, actionability=5, confidence=5,
                  hours_to_impact=6, concrete_next_step='Prepare review-only containment patch',
                  owner_lane='SECURITY', corroborated=True, source_verified_by_evaluator=True)
    values.update(kw)
    return Signal(**values)


def ctx(**kw):
    vals = dict(now=TIME, owner_lanes=frozenset({'SECURITY'}),
                verified_signal_ids=frozenset({'s1','s2','s3','s4'}),
                verified_head_bindings=frozenset({('test-repo#1', HEAD)}))
    vals.update(kw)
    return Context(**vals)


class GovernorTests(unittest.TestCase):
    def test_high_confidence_urgent_unknown_new_signal_proposes_notification_only(self):
        d = decide_one(sig(), ctx())
        self.assertEqual(d.action, Action.NOTIFY)
        self.assertFalse(d.emitted)
        self.assertFalse(d.effect_authority)
        self.assertFalse(d.source_authenticity_verified)

    def test_already_known_exact_head_suppressed(self):
        d = decide_one(sig(), ctx(known_observations=frozenset({('risk-1','test-repo#1',HEAD)})))
        self.assertEqual(d.action, Action.SILENT)

    def test_different_head_not_suppressed_by_old_head(self):
        old_head='a'*40
        d = decide_one(sig(), ctx(known_observations=frozenset({('risk-1','test-repo#1',old_head)})))
        self.assertEqual(d.action, Action.NOTIFY)

    def test_no_new_owner_alert_when_independently_acknowledged(self):
        d = decide_one(sig(known_to_owner=True),
                       ctx(trusted_owner_ack_keys=frozenset({('risk-1','test-repo#1',HEAD)})))
        self.assertEqual(d.action, Action.DRAFT)

    def test_source_only_claim_to_runtime_demoted(self):
        d = decide_one(sig(runtime_claim=True, evidence_classes=(EvidenceClass.SOURCE,)), ctx())
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('SOURCE_NOT_RUNTIME_EVIDENCE', d.reasons)

    def test_phenomenology_model_claim_requires_evidence_not_produced(self):
        d = decide_one(sig(model_subjectivity_claim=True, domain='agency'), ctx())
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('SUBJECTIVITY_UNVERIFIED', d.reasons)

    def test_protected_effect_never_grants_authority(self):
        d = decide_one(sig(protected_effect=True), ctx())
        self.assertEqual(d.action, Action.NOTIFY)
        self.assertFalse(d.effect_authority)

    def test_external_owner_is_not_assumed_writer(self):
        d = decide_one(sig(owner_lane='ENGINEER_B'), ctx())
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('DIFFERENT_WRITER_OWNER', d.reasons)

    def test_unassigned_owner_suppresses_notice(self):
        d = decide_one(sig(owner_lane='UNASSIGNED'), ctx())
        self.assertEqual(d.action, Action.DRAFT)

    def test_private_signal_never_includes_source_refs_in_decision(self):
        d = decide_one(sig(contains_private_data=True), ctx())
        self.assertEqual(d.action, Action.DRAFT)
        self.assertEqual(d.evidence_refs, ())
        self.assertNotIn('repo/path', str(d.public_record()))

    def test_user_muting_cannot_be_outvoted_into_notification(self):
        d = decide_one(sig(), ctx(muted_domains=frozenset({'security'})))
        self.assertEqual(d.action, Action.DRAFT)
        self.assertFalse(d.emitted)

    def test_muted_low_severity_noise_remains_silent(self):
        d = decide_one(sig(severity=1, actionability=1, confidence=1),
                       ctx(muted_domains=frozenset({'security'})))
        self.assertEqual(d.action, Action.SILENT)

    def test_explicit_noisy_feedback_does_not_interrupt(self):
        d = decide_one(sig(), ctx(feedback=(('risk-1','test-repo#1',HEAD,'NOISY'),)))
        self.assertEqual(d.action, Action.DRAFT)
        self.assertFalse(d.emitted)

    def test_trusted_evidence_not_borne_by_signal_fields_alone(self):
        d = decide_one(sig(), ctx(verified_signal_ids=frozenset()))
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('UNVERIFIED_SOURCE_ASSERTION', d.reasons)

    def test_not_revalidated_on_expired_source(self):
        s = sig(observed_at='2026-11-16T12:00:00+00:00')
        d = decide_one(s, ctx())
        self.assertEqual(d.action, Action.SILENT)
        self.assertIn('STALE_SUBJECT', d.reasons)

    def test_future_observation_rejected(self):
        d = decide_one(sig(observed_at='2026-11-21T23:00:00+00:00'), ctx())
        self.assertEqual(d.action, Action.SILENT)

    def test_repeated_alert_in_cooldown_stays_silent(self):
        c=ctx(notification_log=(('risk-1','test-repo#1', HEAD, '2026-11-20T22:00:00+00:00'),))
        self.assertEqual(decide_one(sig(),c).action,Action.SILENT)

    def test_daily_budget_blocks_second_even_across_domains(self):
        s1=sig()
        s2=sig(signal_id='s2',fingerprint='risk-2',subject='different-project', domain='runtime')
        batch=evaluate([s1,s2],ctx(daily_notification_limit=1))
        self.assertEqual(sum(d.action == Action.NOTIFY for d in batch.decisions),1)
        self.assertEqual(sum(d.action == Action.DRAFT for d in batch.decisions),1)
        self.assertFalse(batch.external_effects)

    def test_log_budget_still_enforced_without_recent_same_risk(self):
        c=ctx(notification_log=(('other','other-repo',HEAD,'2026-11-20T20:00:00+00:00'),))
        self.assertEqual(decide_one(sig(),c).action,Action.DRAFT)

    def test_dependency_currentness_does_not_inherit_source_pass(self):
        s=sig(outcome_is_release=True, needed_capabilities=('authenticated-reviewer','currentness-runtime'))
        d=decide_one(s,ctx(qualified_capabilities=frozenset({'authenticated-reviewer'})))
        self.assertEqual(d.action,Action.DRAFT)
        self.assertIn('RELEASE_DEPENDENCY_HOLD', d.reasons)

    def test_question_requires_owner_decision_and_high_value(self):
        d=decide_one(sig(needs_user_decision=True),ctx())
        self.assertEqual(d.action,Action.QUESTION)
        self.assertFalse(d.emitted)

    def test_duplicate_same_head_coalesces(self):
        a=sig()
        b=sig(signal_id='s2',evidence_refs=('different-source',))
        r=evaluate([a,b],ctx())
        self.assertEqual(len(r.decisions),1)
        self.assertEqual(r.dropped_duplicate_signal_ids,('s2',))

    def test_same_fingerprint_conflicting_head_downgraded(self):
        a=sig()
        b=sig(signal_id='s2',exact_head='b'*40)
        r=evaluate([a,b],ctx())
        self.assertEqual(r.decisions[0].action,Action.DRAFT)
        self.assertIn('UNVERIFIED_SOURCE_ASSERTION',r.decisions[0].reasons)

    def test_claimed_owner_awareness_without_independent_ack_does_not_suppress_urgent_signal(self):
        d = decide_one(sig(known_to_owner=True), ctx())
        self.assertEqual(d.action, Action.NOTIFY)

    def test_independent_owner_ack_downgrades_repeated_urgent_notice(self):
        d = decide_one(sig(known_to_owner=True), ctx(trusted_owner_ack_keys=frozenset({('risk-1','test-repo#1',HEAD)})))
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('OWNER_ALREADY_AWARE', d.reasons)

    def test_explicit_noise_feedback_does_not_erase_severe_evidence(self):
        d = decide_one(sig(), ctx(feedback=(('risk-1','test-repo#1',HEAD,'NOISY'),)))
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn('USER_FEEDBACK_SUPPRESSION', d.reasons)

    def test_same_fingerprint_different_subjects_retained_but_denied_as_collision(self):
        a = sig()
        b = sig(signal_id='s2', subject='independent-repo#2')
        batch = evaluate([a, b], ctx())
        self.assertEqual(len(batch.decisions), 2)
        self.assertTrue(all(d.action == Action.DRAFT for d in batch.decisions))
        self.assertTrue(all('FINGERPRINT_COLLISION' in d.reasons for d in batch.decisions))

    def test_background_noise_does_not_notify(self):
        d=decide_one(sig(severity=0,relevance=1,actionability=0,confidence=1,
                           hours_to_impact=720,domain='coordination'),ctx())
        self.assertEqual(d.action,Action.SILENT)

    def test_bounded_scan_refuses_unbounded_sprawl(self):
        a=[sig(signal_id=f's{i}',fingerprint=f'f{i}',subject=f'project{i}') for i in range(41)]
        with self.assertRaises(ValueError): evaluate(a,ctx())

    def test_invalid_head_or_naive_timestamp_fails(self):
        with self.assertRaises(ValueError):sig(exact_head='unknown')
        with self.assertRaises(ValueError):sig(observed_at='2026-11-20T13:00:00')

    def test_metric_does_not_mislabel_synthetic_gold_as_independent(self):
        r=evaluate([sig()],ctx())
        m=measure(r.decisions,{('risk-1','test-repo#1',HEAD):'notify'})
        self.assertEqual(m['agreement_rate'],1.0)
        self.assertFalse(m['independent_ground_truth'])


if __name__=='__main__': unittest.main()
