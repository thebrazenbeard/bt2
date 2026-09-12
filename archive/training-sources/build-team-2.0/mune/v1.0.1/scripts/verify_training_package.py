#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
EXPECTED_SCHEMA='BT2_ROLE_TRAINING_MANIFEST_V1'
EXPECTED_PACKAGE='BT2_MUNE_DEBUGGER_VERIFICATION_TRAINING'
EXPECTED_VERSION='1.0.1'
EXPECTED_MODULE_COUNT=9

def git_blob_sha(data: bytes) -> str:
    h=hashlib.sha1(); h.update(f'blob {len(data)}\0'.encode('ascii')); h.update(data); return h.hexdigest()

def load_json(path: Path): return json.loads(path.read_text(encoding='utf-8'))

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--json',action='store_true'); args=ap.parse_args(); root=Path(args.root); errors=[]
    mp=root/'training-manifest.json'
    if not mp.is_file(): manifest={}; errors.append('missing training-manifest.json')
    else:
        try: manifest=load_json(mp)
        except Exception as exc: manifest={}; errors.append(f'manifest parse failed: {exc}')
    if manifest.get('schema')!=EXPECTED_SCHEMA: errors.append('wrong manifest schema')
    if manifest.get('package_id')!=EXPECTED_PACKAGE: errors.append('wrong package id')
    if manifest.get('training_version')!=EXPECTED_VERSION: errors.append('wrong training version')
    modules=manifest.get('modules')
    if not isinstance(modules,list) or len(modules)!=EXPECTED_MODULE_COUNT: errors.append('module count/order structure invalid'); modules=[]
    if [m.get('order') for m in modules if isinstance(m,dict)]!=list(range(1,EXPECTED_MODULE_COUNT+1)): errors.append('module order must be exactly 1..9')
    required=[]
    if isinstance(manifest.get('bootstrap'),dict): required.append(manifest['bootstrap'])
    cp=manifest.get('checkpoint_support',{})
    if isinstance(cp,dict):
        for key in ('protocol','template','package_verifier','checkpoint_verifier'):
            if isinstance(cp.get(key),dict): required.append(cp[key])
    required.extend(m for m in modules if isinstance(m,dict))
    seen=set()
    for item in required:
        rel=item.get('path'); expected=item.get('git_blob_sha1')
        if not isinstance(rel,str) or not rel: errors.append('required item missing path'); continue
        if rel in seen: errors.append(f'duplicate required path: {rel}')
        seen.add(rel); p=root/rel
        if p.is_symlink(): errors.append(f'symlink forbidden: {rel}'); continue
        if not p.is_file(): errors.append(f'missing file: {rel}'); continue
        got=git_blob_sha(p.read_bytes())
        if expected and got!=expected: errors.append(f'git blob mismatch: {rel}: {got} != {expected}')
    result={'schema':'BT2_MUNE_TRAINING_PACKAGE_VERIFICATION_V1','package_id':EXPECTED_PACKAGE,'training_version':EXPECTED_VERSION,'status':'PASS' if not errors else 'FAIL','errors':errors,'checked_required_paths':len(seen)}
    print(json.dumps(result,sort_keys=True) if args.json else json.dumps(result,indent=2,sort_keys=True))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
