"""Entire suite offline: no actual host, GitHub, database or notification effects."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from signal_ingest.v1 import normalize, SignalError, INPUT_SCHEMA, OUTPUT_SCHEMA

HERE = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((HERE / 'fixtures' / 'synthetic_v1.json').read_text())
HEAD_A = 'a' * 40
HEAD_B = 'b' * 40


class SignalNormalizationTest(unittest.TestCase):
    def load(self):
        return deepcopy(FIXTURE)

    def test_01_duplicate_reports_one_underlying_failure(self):
        out = normalize(self.load())
        incident = [o for o in out['observations']
                    if o['repository'] == 'example/app' and o['incident_key'] == 'rfb-input-frame']
        self.assertEqual(len(incident), 1, 'same failure with two different reporters/URLs must group')
        self.assertEqual(len(incident[0]['reports']), 2)
        self.assertEqual(incident[0]['categories'], ['CI_RESULT', 'COORDINATION'])
        self.assertEqual(len(incident[0]['source_refs']), 2)
        self.assertTrue(incident[0]['candidate_observation'])
        self.assertFalse(incident[0]['independently_authenticated'])

    def test_02_head_change_invalidates_prior_evidence(self):
        out = normalize(self.load())
        stale = next(o for o in out['observations'] if o['incident_key'] == 'previous-ci-failure')
        current = next(o for o in out['observations'] if o['incident_key'] == 'head-moved')
        self.assertEqual(stale['head_currentness'], 'STALE_HEAD')
        self.assertFalse(stale['candidate_observation'])
        self.assertEqual(current['head_currentness'], 'EXACT_HEAD')
        self.assertTrue(current['candidate_observation'])

    def test_03_green_ci_does_not_release(self):
        out = normalize(self.load())
        green = next(o for o in out['observations'] if o['incident_key'] == 'passing-workflow')
        self.assertEqual(green['statuses'], ['PASSED'])
        self.assertFalse(green['candidate_observation'])
        self.assertFalse(green['release_permission'])
        self.assertFalse(out['release_permission'])
        self.assertEqual(out['policy_decision'], 'NOT_MADE')

    def test_04_lantern_unknown_not_availability(self):
        out = normalize(self.load())
        lantern = next(x for x in out['runtime'] if x['subject'] == 'lantern')
        self.assertEqual(lantern['currentness'], 'UNKNOWN')
        self.assertEqual(lantern['availability'], 'UNKNOWN')
        self.assertFalse(lantern['independently_authenticated'])
        claimed = next(x for x in out['observations'] if x['incident_key'] == 'lantern-claim')
        self.assertFalse(claimed['candidate_observation'])
        self.assertFalse(claimed['independently_authenticated'])

    def test_05_spoofed_owner_reviewer_and_authentication(self):
        out = normalize(self.load())
        claimed = next(x for x in out['observations'] if x['incident_key'] == 'spoofed-review')
        report = claimed['reports'][0]
        self.assertEqual(report['claimed_owner'], 'trusted-owner')
        self.assertEqual(report['claimed_reviewer'], 'reviewer-A')
        self.assertFalse(report['owner_verified'])
        self.assertFalse(report['reviewer_verified'])
        self.assertEqual(report['authentication'], 'UNVERIFIED')
        self.assertIn('SELF_ASSERTED_AUTHENTICATION_IGNORED', claimed['confidence_limitations'])

    def test_06_no_external_actions_from_source_alert(self):
        out = normalize(self.load())
        self.assertEqual(out['external_effects'], [])
        self.assertEqual(out['host_task_proposals'], [])
        self.assertFalse(out['side_effects_performed'])
        self.assertEqual(out['policy_decision'], 'NOT_MADE')

    def test_07_expired_host_cutoff_prevents_new_host_tasks(self):
        out = normalize(self.load())
        self.assertEqual(out['host_task_start_permitted'], 'NO_EXPIRED_CUTOFF')
        self.assertEqual(out['host_task_proposals'], [])
        alternate = self.load()
        alternate['snapshot']['observed_at'] = '2026-11-20T17:55:00Z'
        for obs in alternate['observations']:
            obs['observed_at'] = '2026-11-20T17:50:00Z'
        pre = normalize(alternate)
        self.assertEqual(pre['host_task_start_permitted'], 'UNKNOWN_UNVERIFIED_AUTHORITY')
        self.assertEqual(pre['host_task_proposals'], [])

    def test_08_deterministic_permutations_and_json_bytes(self):
        a, b = self.load(), self.load()
        b['observations'].reverse()
        b['snapshot']['subjects'].reverse()
        self.assertEqual(normalize(a), normalize(b))
        self.assertEqual(json.dumps(normalize(a), sort_keys=True),
                         json.dumps(normalize(b), sort_keys=True))
        self.assertEqual(normalize(a)['schema'], OUTPUT_SCHEMA)

    def test_09_one_key_two_different_heads_not_conflated(self):
        doc = self.load()
        current = next(x for x in doc['observations'] if x['incident_key']=='rfb-input-frame')
        old = deepcopy(current)
        old['id'] = 'old-head-second-witness'
        old['head'] = HEAD_A
        old['source_ref'] = 'https://github.com/example/app/issues/45'
        doc['observations'].append(old)
        groups = [x for x in normalize(doc)['observations'] if x['incident_key']=='rfb-input-frame']
        self.assertEqual(len(groups), 2)
        self.assertEqual(sum(x['candidate_observation'] for x in groups), 1)

    def test_10_reporter_replay_does_not_increase_count(self):
        doc = self.load()
        doc['observations'].append(deepcopy(doc['observations'][0]))
        out = normalize(doc)
        record = next(x for x in out['observations'] if x['incident_key']=='rfb-input-frame')
        self.assertEqual(len(record['reports']), 2)

    def test_11_conflicting_reused_report_id_fails_closed(self):
        doc = self.load()
        duplicate = deepcopy(doc['observations'][0])
        duplicate['status'] = 'PASSED'
        doc['observations'].append(duplicate)
        with self.assertRaisesRegex(SignalError, 'CONFLICTING_OBSERVATION_ID'):
            normalize(doc)

    def test_12_untrusted_source_cannot_confess_its_way_to_auth(self):
        doc = self.load()
        for ob in doc['observations']:
            ob['claims_authenticated'] = True
        out = normalize(doc)
        self.assertTrue(all(not x['independently_authenticated'] for x in out['observations']))
        self.assertTrue(all(x['authentication']=='UNVERIFIED'
                            for o in out['observations'] for x in o['reports']))

    def test_13_bools_and_unexpected_fields_rejected(self):
        for field, value, error in [('runtime_required', 1, 'INVALID_RUNTIME_FLAG'),
                                    ('runtime_required', None, 'INVALID_RUNTIME_FLAG')]:
            doc = self.load()
            doc['snapshot']['subjects'][0][field] = value
            with self.subTest(value=value), self.assertRaisesRegex(SignalError, error):
                normalize(doc)
        doc = self.load()
        doc['observations'][0]['run_shell'] = 'touch /tmp/should-not-run'
        with self.assertRaisesRegex(SignalError,'INVALID_OBSERVATION'):
            normalize(doc)

    def test_14_head_status_contradiction_fails_closed(self):
        doc = self.load()
        o = next(o for o in doc['observations'] if o['kind']=='PR_HEAD_CHANGE')
        o['previous_head'] = o['head']
        with self.assertRaisesRegex(SignalError,'HEAD_CHANGE_CONTRADICTION'):
            normalize(doc)

    def test_15_future_report_rejected(self):
        doc = self.load()
        doc['observations'][0]['observed_at'] = '2026-11-21T12:00:00Z'
        with self.assertRaisesRegex(SignalError, 'OBSERVATION_FROM_FUTURE'):
            normalize(doc)

    def test_16_prohibited_source_credentials_and_query_rejected(self):
        for ref in ('https://user:secret@github.com/example/app/issues/1',
                    'https://github.com/example/app/issues/1?token=foo',
                    'file:///tmp/probe', 'https://evil.example/owner/repo'):
            doc = self.load()
            doc['observations'][0]['source_ref'] = ref
            with self.subTest(ref=ref), self.assertRaisesRegex(SignalError,'INVALID_SOURCE_REF'):
                normalize(doc)

    def test_17_different_fingerprint_do_not_merge(self):
        doc = self.load()
        o = deepcopy(doc['observations'][0])
        o['id'] = 'separate-error'
        o['incident_key'] = 'different-cause'
        doc['observations'].append(o)
        out = normalize(doc)
        self.assertEqual(len([x for x in out['observations'] if x['incident_key'] in {'rfb-input-frame', 'different-cause'} and x['candidate_observation']]), 2)

    def test_19_missing_runtime_is_signal_without_fabricated_head(self):
        out = normalize(self.load())
        missing = next(x for x in out['observations'] if x['incident_key'] == 'missing-lantern')
        self.assertTrue(missing['candidate_observation'])
        self.assertEqual(missing['head_currentness'], 'UNKNOWN_HEAD')
        self.assertFalse(missing['independently_authenticated'])
        self.assertEqual(next(x for x in out['runtime'] if x['subject'] == 'lantern')['availability'], 'UNKNOWN')

    def test_20_invalid_port_source_ref_fails_closed(self):
        doc=self.load()
        doc['observations'][0]['source_ref']='https://github.com:badport/example/app'
        with self.assertRaisesRegex(SignalError,'INVALID_SOURCE_REF'):
            normalize(doc)

    def test_21_comment_anchor_preserved_but_arbitrary_fragment_rejected(self):
        d=self.load()
        d['observations'][0]['source_ref']='https://github.com/example/app/issues/1#issuecomment-123'
        result=normalize(d)
        self.assertTrue(any('issuecomment-123' in ref for x in result['observations']
                            for ref in x['source_refs']))
        d['observations'][0]['source_ref']='https://github.com/example/app/issues/1#token=secret'
        with self.assertRaisesRegex(SignalError, 'INVALID_SOURCE_REF'):
            normalize(d)

    def test_18_no_runtime_claim_makes_it_qualified(self):
        doc = self.load()
        item=next(x for x in doc['snapshot']['subjects'] if x['subject']=='lantern')
        item['reported_runtime_status']='REPORTED_QUALIFIED'
        out = normalize(doc)
        self.assertEqual(next(x for x in out['runtime'] if x['subject']=='lantern')['currentness'],'UNKNOWN')

if __name__ == '__main__':
    unittest.main()
