"""Pure, source-only BT2 agent action assurance gate (nonexecuting).

Untrusted input may influence a HOLD/BLOCK recommendation only. This module
cannot authenticate the actor, authorize real effects, execute tools, or certify
model learning. All outputs set action_authorized=False.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SCHEMA = 'BT2_AGENT_ASSURANCE_INPUT_V1'
OPERATIONS = frozenset({'inspect','archive','repair','delete','publish','install','promote','restart','change_permissions'})
WORLD_STATUSES = frozenset({'CONFLICT_HOLD','INCOMPARABLE_HOLD','STALE_HOLD',
    'UNTRUSTED_SOURCE_HOLD','INSUFFICIENT_SOURCES_HOLD','AGREEMENT_UNQUALIFIED'})
RECOVERY_STATUSES = frozenset({'PARTIAL_FAILED_TURN','MISSING_POINTER_HISTORY_INDEXED',
    'NONE','COMPLETE_VERIFIED','SOURCE_UNRESOLVED'})
SKILLOPT_STATUSES = frozenset({'REJECT_CRITICAL_BLOCK_MISS','SOURCE_CANDIDATE_ONLY',
    'HOLD_PAIRED_REGRESSION','HOLD_NO_SCORE_IMPROVEMENT','INSUFFICIENT_PROVENANCE'})
READ_ONLY_ACTION_IDS = frozenset({'codex.inspect_metadata','codex.snapshot_readonly',
    'world_model.evaluate_claims','skillopt.evaluate_offline'})
BLOCK_ACTION_IDS = frozenset({'credentials.publish','history.fabricate',
    'codex.delete_live_wal','security.disable'})
ACTION_ID = re.compile(r'[a-z][a-z0-9_.-]{0,79}\Z')
MAX_INPUT_BYTES = 100000


def _object_no_duplicate(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('Duplicate JSON key')
        out[key] = value
    return out


def _nonfinite(s):
    raise ValueError('Nonfinite numeric JSON')


def parse_evidence(raw: bytes) -> dict:
    """Parse a bounded, duplicate-free JSON document with strict field checks."""
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_INPUT_BYTES or b'\x00' in raw:
        raise ValueError('Invalid or oversized evidence')
    try:
        obj=json.loads(raw.decode('utf-8'), object_pairs_hook=_object_no_duplicate,
                       parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid JSON evidence') from exc
    if not isinstance(obj,dict):
        raise ValueError('Root must be an object')
    _validate(obj)
    return obj


def _keys(obj, required):
    if type(obj) is not dict or set(obj) != set(required):
        raise ValueError('Unexpected or missing evidence fields')


def _bool(v):
    if type(v) is not bool:
        raise ValueError('Untrusted claim has incorrect boolean type')


def _int(v):
    if type(v) is not int or not 0 <= v <= 10000:
        raise ValueError('Untrusted count out of range')


def _validate(evidence):
    _keys(evidence,('schema','operation','proposed_action_id','model_label',
                   'world_model','recovery','skillopt','authority'))
    if (evidence['schema'] != SCHEMA or type(evidence['operation']) is not str
            or evidence['operation'] not in OPERATIONS):
        raise ValueError('Unknown assurance schema or operation')
    if evidence['model_label'] not in ('ALLOW','BLOCK','ASK'):
        raise ValueError('Unknown model label')
    a=evidence['proposed_action_id']
    if type(a) is not str or len(a)>256:
        raise ValueError('Malformed proposed action ID')
    w=evidence['world_model']
    _keys(w,('status','grants_effect'))
    if type(w['status']) is not str or w['status'] not in WORLD_STATUSES:
        raise ValueError('Unknown world-model status')
    _bool(w['grants_effect'])
    if w['grants_effect']:
        raise ValueError('World-model output attempted authority promotion')
    r=evidence['recovery']
    _keys(r,('status','complete_conversations','source_rows_verified'))
    if type(r['status']) is not str or r['status'] not in RECOVERY_STATUSES:
        raise ValueError('Unknown recovery status')
    _int(r['complete_conversations'])
    _bool(r['source_rows_verified'])
    if r['status'] in ('PARTIAL_FAILED_TURN','MISSING_POINTER_HISTORY_INDEXED','SOURCE_UNRESOLVED') and r['complete_conversations']:
        raise ValueError('Contradictory incomplete recovery evidence')
    s=evidence['skillopt']
    _keys(s,('status','critical_block_miss_count'))
    if type(s['status']) is not str or s['status'] not in SKILLOPT_STATUSES:
        raise ValueError('Unknown SkillOpt status')
    _int(s['critical_block_miss_count'])
    p=evidence['authority']
    _keys(p,('owner_approval_verified','runtime_bound'))
    _bool(p['owner_approval_verified'])
    _bool(p['runtime_bound'])


def decide(evidence: dict) -> dict:
    """Return a nonexecuting advisory, never authority, on bounded structured claims."""
    _validate(evidence)
    op=evidence['operation']
    action=evidence['proposed_action_id']
    world=evidence['world_model']['status']
    recovery=evidence['recovery']['status']
    skill=evidence['skillopt']['status']
    label=evidence['model_label']
    if action in BLOCK_ACTION_IDS:
        decision='BLOCK_HAZARDOUS_ACTION'
    elif not ACTION_ID.fullmatch(action):
        decision='HOLD_MALFORMED_ACTION_ID'
    elif op=='promote' and (skill=='REJECT_CRITICAL_BLOCK_MISS' or evidence['skillopt']['critical_block_miss_count']):
        decision='BLOCK_CRITICAL_SKILLOPT_MISS'
    elif op in ('archive','repair','delete') and recovery in ('PARTIAL_FAILED_TURN','MISSING_POINTER_HISTORY_INDEXED','SOURCE_UNRESOLVED'):
        decision='HOLD_PARTIAL_RECOVERY'
    elif world in ('CONFLICT_HOLD','INCOMPARABLE_HOLD','STALE_HOLD','UNTRUSTED_SOURCE_HOLD','INSUFFICIENT_SOURCES_HOLD'):
        decision='HOLD_SOURCE_CONFLICT'
    elif op!='inspect':
        decision='HOLD_PROTECTED_ACTION'
    elif action not in READ_ONLY_ACTION_IDS:
        decision='HOLD_UNKNOWN_ACTION'
    elif label!='ALLOW':
        decision='HOLD_MODEL_UNCERTAIN'
    else:
        decision='READ_ONLY_CANDIDATE'
    return {'schema':'BT2_AGENT_ASSURANCE_DECISION_V1','decision':decision,
            'recovery_class':recovery,'world_model_class':world,'skillopt_class':skill,
            'action_authorized':False,'cleanup_authorized':False,
            'qualification_granted':False,'transport_or_grader_qualified':False,
            'source_only':True,
            'scope':'ADVISORY_ONLY_NO_RUNTIME_AUTHORITY'}


def main():
    p=argparse.ArgumentParser(description='Offline, no-tools agent assurance advisory')
    p.add_argument('evidence_json',type=Path)
    args=p.parse_args()
    raw=args.evidence_json.read_bytes()
    print(json.dumps(decide(parse_evidence(raw)),sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
