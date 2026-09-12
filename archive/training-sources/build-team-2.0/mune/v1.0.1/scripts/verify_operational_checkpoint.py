#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
EXPECTED_SCHEMA='BT2_MUNE_OPERATIONAL_CHECKPOINT_V1'
ALLOWED={'RESUME_READY','RESUME_READY_WITH_SUPERSESSION','BLOCKED_CURRENTNESS','BLOCKED_AUTHORITY','BLOCKED_EVIDENCE'}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('checkpoint'); args=ap.parse_args(); errors=[]
    try: data=json.loads(Path(args.checkpoint).read_text(encoding='utf-8'))
    except Exception as exc: print(json.dumps({'status':'FAIL','errors':[f'parse failed: {exc}']},sort_keys=True)); return 1
    if data.get('schema')!=EXPECTED_SCHEMA: errors.append('wrong checkpoint schema')
    if data.get('role')!='Mune — Debugger Verification / Regression Specialist': errors.append('wrong role')
    if data.get('frozen_base',{}).get('base_state')!='BASE_READY': errors.append('checkpoint is not bound to BASE_READY base')
    cur=data.get('operational_currentness_at_checkpoint')
    if not isinstance(cur,dict) or not isinstance(cur.get('exact_subject'),dict): errors.append('missing operational exact_subject')
    if not isinstance(data.get('verification_progress'),dict): errors.append('missing verification_progress')
    nf=data.get('next_frontier')
    if not isinstance(nf,dict): errors.append('missing next_frontier')
    elif nf.get('state') is not None and nf.get('state') not in ALLOWED: errors.append(f"invalid next_frontier.state: {nf.get('state')}")
    rule=data.get('resume_rule','')
    if 'Refresh' not in rule or 'self-authorize' not in rule: errors.append('resume rule does not preserve currentness/authority boundary')
    print(json.dumps({'schema':'BT2_MUNE_OPERATIONAL_CHECKPOINT_VERIFICATION_V1','status':'PASS' if not errors else 'FAIL','errors':errors},sort_keys=True)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
