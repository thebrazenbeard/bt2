import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json'
EXPECTED={'one','two','three','four','five','six','seven','eight','nine','thirteen','masa','mune','hephaestus'}

def main():
    d=json.loads(PATH.read_text(encoding='utf-8'))
    assert d['persistent_human_interface']=='BT2 Coordinator'
    assert d['chat_dependency'] is False
    workers=d['workers']
    assert {w['id'] for w in workers}==EXPECTED
    assert len(workers)==len(EXPECTED)
    for w in workers:
        root=ROOT/w['source_path']
        assert root.is_dir(), (w['id'],root)
        assert (root/w['entrypoint']).is_file(), (w['id'],w['entrypoint'])
        assert w['source_state']
        assert w['qualification_state']
    v3=(ROOT/'native/project/PROJECT_INSTRUCTIONS_V3.md').read_text(encoding='utf-8')
    runtime=(ROOT/'native/project/BT2_NATIVE_RUNTIME_V1.md').read_text(encoding='utf-8')
    assert 'BT2 Coordinator' in v3
    assert 'permanent chats' in v3
    assert 'fresh chat' not in runtime.lower()
    print('BT2_EXODUS_WORKER_TOPOLOGY=PASS',len(workers))

if __name__=='__main__': main()

