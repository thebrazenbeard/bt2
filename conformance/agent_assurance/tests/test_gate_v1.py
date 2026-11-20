"""Hostile, offline tests for a non-executing agent-assurance policy adapter."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gate_v1 import decide, parse_evidence


def case(operation='inspect', **overrides):
    d = {
        'schema': 'BT2_AGENT_ASSURANCE_INPUT_V1',
        'operation': operation,
        'proposed_action_id': 'codex.inspect_metadata',
        'model_label': 'ALLOW',
        'world_model': {'status': 'AGREEMENT_UNQUALIFIED', 'grants_effect': False},
        'recovery': {'status': 'PARTIAL_FAILED_TURN', 'complete_conversations': 0, 'source_rows_verified': True},
        'skillopt': {'status': 'REJECT_CRITICAL_BLOCK_MISS', 'critical_block_miss_count': 2},
        'authority': {'owner_approval_verified': False, 'runtime_bound': False},
    }
    d.update(overrides)
    return d


class AssuranceTests(unittest.TestCase):
    def test_inspect_only_candidate_without_authority(self):
        v = decide(case())
        self.assertEqual(v['decision'], 'READ_ONLY_CANDIDATE')
        self.assertFalse(v['action_authorized'])
        self.assertFalse(v['cleanup_authorized'])
        self.assertFalse(v['qualification_granted'])

    def test_all_mutating_operations_hold_even_if_owner_claim_true(self):
        for op in ('archive', 'repair', 'delete', 'publish', 'install', 'promote', 'restart', 'change_permissions'):
            with self.subTest(op=op):
                d = case(operation=op, authority={'owner_approval_verified': True, 'runtime_bound': True})
                v = decide(d)
                self.assertFalse(v['action_authorized'])
                self.assertNotEqual(v['decision'], 'READ_ONLY_CANDIDATE')

    def test_critical_action_denied_even_if_model_allows(self):
        for action_id in ('credentials.publish', 'history.fabricate', 'codex.delete_live_wal', 'security.disable'):
            with self.subTest(action_id=action_id):
                v = decide(case(operation='inspect', proposed_action_id=action_id))
                self.assertEqual(v['decision'], 'BLOCK_HAZARDOUS_ACTION')

    def test_other_action_ids_do_not_get_read_only_candidate(self):
        for action_id in ('codex.archive', 'codex.inspect_metadata;delete', 'codex.inspect_metadata/../delete', ''):
            with self.subTest(action_id=action_id):
                self.assertNotEqual(decide(case(proposed_action_id=action_id))['decision'], 'READ_ONLY_CANDIDATE')

    def test_conflicted_observation_holds_even_read_only(self):
        v=decide(case(world_model={'status': 'CONFLICT_HOLD', 'grants_effect': False}))
        self.assertEqual(v['decision'], 'HOLD_SOURCE_CONFLICT')

    def test_world_model_attempt_to_grant_effect_fails_closed(self):
        with self.assertRaises(ValueError):
            decide(case(world_model={'status':'AGREEMENT_UNQUALIFIED','grants_effect':True}))

    def test_reported_complete_recovery_not_clean_up_approval(self):
        v=decide(case(operation='archive', recovery={'status':'COMPLETE_VERIFIED','complete_conversations':2,'source_rows_verified':True}))
        self.assertFalse(v['cleanup_authorized'])

    def test_model_claim_cannot_qualify_skill(self):
        for value in ('ALLOW', 'ASK', 'BLOCK'):
            with self.subTest(value=value):
                v=decide(case(operation='promote', model_label=value, skillopt={'status':'SOURCE_CANDIDATE_ONLY','critical_block_miss_count':0}))
                self.assertFalse(v['qualification_granted'])
                self.assertEqual(v['decision'], 'HOLD_PROTECTED_ACTION')

    def test_missing_or_unknown_schemas_rejected(self):
        for patch in ({'schema':'BAD'},{'operation':'sudo'},{'model_label':'YES'},{'extraneous':'AUTHORIZE'}):
            d=case();d.update(patch)
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                decide(d)

    def test_invalid_claim_types_rejected(self):
        variants=[
            {'recovery':{'status':'PARTIAL_FAILED_TURN','complete_conversations':True,'source_rows_verified':True}},
            {'skillopt':{'status':'REJECT_CRITICAL_BLOCK_MISS','critical_block_miss_count':-1}},
            {'authority':{'owner_approval_verified':'true','runtime_bound':False}},
            {'world_model':{'status':'AGREEMENT_UNQUALIFIED','grants_effect':0}},
            {'recovery':{'status':'PARTIAL_FAILED_TURN','complete_conversations':0,'source_rows_verified':False,'recovered':True}},
        ]
        for patch in variants:
            d=case();d.update(patch)
            with self.subTest(patch=patch),self.assertRaises(ValueError):decide(d)

    def test_incomplete_recovery_never_becomes_verified(self):
        d=case(operation='repair')
        v=decide(d)
        self.assertEqual(v['decision'],'HOLD_PARTIAL_RECOVERY')
        self.assertEqual(v['recovery_class'],'PARTIAL_FAILED_TURN')

    def test_skill_critical_miss_blocks_promotion(self):
        d=case(operation='promote')
        self.assertEqual(decide(d)['decision'],'BLOCK_CRITICAL_SKILLOPT_MISS')

    def test_json_duplicate_keys_rejected(self):
        payload=json.dumps(case()).replace('"operation": "inspect",','"operation": "inspect", "operation": "archive",')
        with self.assertRaises(ValueError):parse_evidence(payload.encode())

    def test_json_nonfinite_rejected(self):
        payload=json.dumps(case()).replace('"complete_conversations": 0','"complete_conversations": NaN')
        with self.assertRaises(ValueError):parse_evidence(payload.encode())

    def test_budget_and_non_object_rejected(self):
        for bad in (b'[]',b'\xff',b'\x00',b'{}',b' '*100001):
            with self.subTest(bad=bad[:10]),self.assertRaises(ValueError):parse_evidence(bad)

    def test_fixture_and_cli_output_protects_private_fields(self):
        p=ROOT/'fixtures'/'synthetic_partial_hold_v1.json'
        loaded=parse_evidence(p.read_bytes())
        self.assertEqual(decide(loaded)['decision'],'HOLD_PARTIAL_RECOVERY')
        run=subprocess.run([sys.executable,str(ROOT/'gate_v1.py'),str(p)],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        out=json.loads(run.stdout)
        self.assertNotIn('private_message',out)
        self.assertFalse(out['action_authorized'])

    def test_readonly_cannot_bypass_with_unknown_status(self):
        for state in ('IMAGINED','VERIFIED','NONE'):
            d=case(world_model={'status':state,'grants_effect':False})
            with self.subTest(state=state),self.assertRaises(ValueError):decide(d)

    def test_privacy_redaction_does_not_create_authority(self):
        d=case();self.assertFalse(decide(d)['action_authorized'])
        d['authority']['owner_approval_verified']=True
        self.assertFalse(decide(d)['action_authorized'])


if __name__=='__main__':unittest.main()

# Additional malformed-shape probes: parsers must reject rather than TypeError-crash.
class MalformedEvidenceTests(unittest.TestCase):
    def test_nested_list_and_mapping_unhashable_values(self):
        for path,value in [('operation',[]),('model_label',[]),('world_model.status',[]),
                           ('recovery.status',{}),('skillopt.status',{})]:
            d=case()
            if '.' in path:
                group,name=path.split('.')
                d[group][name]=value
            else:d[path]=value
            with self.subTest(path=path),self.assertRaises(ValueError):decide(d)

    def test_never_execute_even_for_syntactically_valid_unknown_action(self):
        d=case(proposed_action_id='some_new_action')
        self.assertEqual(decide(d)['decision'],'HOLD_UNKNOWN_ACTION')
        self.assertFalse(decide(d)['action_authorized'])
