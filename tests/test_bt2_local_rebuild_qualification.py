import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'scripts' / 'bt2_local_rebuild_qualification.py'


def load_module():
    spec = importlib.util.spec_from_file_location('bt2q', MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sample_manifest():
    return {
        'manifest_version': 'BT2_DATABASE_BUILD_MANIFEST_V1',
        'target': {'qualified_major_version': 16, 'required_extensions': ['pgcrypto']},
        'package_identity': {
            'digest_input': 'schema:a|migrations:b|tests:c|admin:d|data:e|postgres-major:16|required-extension:pgcrypto',
            'package_digest_sha256': None,
        },
        'ordered_apply': [
            {'path': 'database/schema/0001.sql', 'git_blob': None},
            {'path': 'database/migrations/0002.sql', 'git_blob': None},
        ],
        'post_preservation_data_loads': [
            {'path': 'database/data/0001.sql', 'git_blob': None},
        ],
        'qualification': {
            'smoke_tests': [
                {'path': 'database/tests/0001.sql', 'git_blob': None},
                {'path': 'database/tests/0002.sql', 'git_blob': None},
            ],
        },
        'authority': {'merge': False, 'cutover': False},
    }


def write_package(tmp_path):
    manifest = sample_manifest()
    for rel in [x['path'] for x in manifest['ordered_apply'] + manifest['post_preservation_data_loads'] + manifest['qualification']['smoke_tests']]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'-- {rel}\nselect 1;\n')
    mod = load_module()
    for entry in manifest['ordered_apply'] + manifest['post_preservation_data_loads'] + manifest['qualification']['smoke_tests']:
        entry['git_blob'] = mod.git_blob_sha1((tmp_path / entry['path']).read_bytes())
    import hashlib
    manifest['package_identity']['package_digest_sha256'] = hashlib.sha256(
        manifest['package_identity']['digest_input'].encode('utf-8')
    ).hexdigest()
    mpath = tmp_path / 'database/BUILD_MANIFEST_V1.json'
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest))
    return mpath, manifest


def test_requires_digest_pinned_postgres_image():
    mod = load_module()
    with pytest.raises(mod.QualificationError, match='POSTGRES_IMAGE_NOT_IMMUTABLE'):
        mod.validate_postgres_image('postgres:16')
    assert mod.validate_postgres_image('postgres:16.15@sha256:' + 'a' * 64).endswith('a' * 64)


def test_manifest_verification_checks_package_digest_and_all_git_blobs(tmp_path):
    mod = load_module()
    mpath, manifest = write_package(tmp_path)
    checked = mod.load_and_verify_manifest(tmp_path, mpath)
    assert checked['package_identity']['package_digest_sha256'] == manifest['package_identity']['package_digest_sha256']
    (tmp_path / 'database/migrations/0002.sql').write_text('select 2;\n')
    with pytest.raises(mod.QualificationError, match='GIT_BLOB_MISMATCH:database/migrations/0002.sql'):
        mod.load_and_verify_manifest(tmp_path, mpath)


def test_manifest_sequence_is_apply_then_data_then_smokes(tmp_path):
    mod = load_module()
    mpath, _ = write_package(tmp_path)
    manifest = mod.load_and_verify_manifest(tmp_path, mpath)
    assert mod.manifest_execution_paths(manifest) == [
        ('APPLY', 'database/schema/0001.sql'),
        ('APPLY', 'database/migrations/0002.sql'),
        ('TEST', 'database/tests/0001.sql'),
        ('TEST', 'database/tests/0002.sql'),
    ]
    assert mod.post_preservation_paths(manifest) == ['database/data/0001.sql']


def test_receipt_is_deterministic_for_same_evidence():
    mod = load_module()
    kwargs = dict(
        source_commit='1' * 40,
        source_tree='2' * 40,
        manifest_digest='3' * 64,
        package_digest='4' * 64,
        postgres_image='postgres:16.15@sha256:' + '5' * 64,
        postgres_version='16.15',
        docker_version='29.7.2',
        stage_results=[{'stage': 'APPLY:a', 'exit_code': 0}],
    )
    a = mod.build_receipt(**kwargs)
    b = mod.build_receipt(**kwargs)
    assert a == b
    assert a['status'] == 'PASS'
    assert a['mode'] == 'LOCAL_DOCKER_NO_PAID_SERVICES'
    assert a['protected_effects_performed'] is False
    assert a['live_wowsql_mutated'] is False
    assert a['post_preservation_data_loads_executed'] is False


def test_runner_cleanup_is_attempted_even_when_stage_fails(monkeypatch, tmp_path):
    mod = load_module()
    mpath, _ = write_package(tmp_path)
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = '29.7.2\n' if cmd[:2] == ['docker', 'version'] else ('16.15\n' if 'show server_version;' in cmd else '')
            stderr = ''
        if cmd[:2] == ['docker', 'exec'] and 'psql' in cmd and '-f' in cmd:
            raise mod.QualificationError('STAGE_FAILED')
        return R()

    monkeypatch.setattr(mod.subprocess, 'run', fake_run)
    monkeypatch.setattr(mod, 'verify_source_binding', lambda *args, **kwargs: ('1' * 40, '2' * 40))
    monkeypatch.setattr(mod.time, 'sleep', lambda _: None)
    with pytest.raises(mod.QualificationError, match='STAGE_FAILED'):
        mod.run_qualification(
            repo_root=tmp_path,
            manifest_path=mpath,
            postgres_image='postgres:16.15@sha256:' + 'a' * 64,
            source_commit='1' * 40,
            source_tree='2' * 40,
            container_name='bt2-test',
        )
    assert ['docker', 'rm', '-f', 'bt2-test'] in calls


def test_source_binding_requires_exact_clean_checkout(monkeypatch, tmp_path):
    mod = load_module()
    outputs = iter(['1' * 40 + '\n', '2' * 40 + '\n', ''])

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 0
            stdout = next(outputs)
            stderr = ''
        return R()

    monkeypatch.setattr(mod, '_run', fake_run)
    assert mod.verify_source_binding(tmp_path, '1' * 40, '2' * 40) == ('1' * 40, '2' * 40)

    outputs2 = iter(['9' * 40 + '\n', '2' * 40 + '\n', ''])
    def wrong_run(cmd, **kwargs):
        class R:
            returncode = 0
            stdout = next(outputs2)
            stderr = ''
        return R()
    monkeypatch.setattr(mod, '_run', wrong_run)
    with pytest.raises(mod.QualificationError, match='SOURCE_COMMIT_MISMATCH'):
        mod.verify_source_binding(tmp_path, '1' * 40, '2' * 40)


def test_stage_execution_uses_read_only_mount_and_psql_file_paths(monkeypatch, tmp_path):
    mod = load_module()
    mpath, _ = write_package(tmp_path)
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = '29.7.2\n' if cmd[:2] == ['docker', 'version'] else ('16.15\n' if 'show server_version;' in cmd else ('1\n' if any('pg_extension' in part for part in cmd) else ''))
            stderr = ''
        return R()

    monkeypatch.setattr(mod.subprocess, 'run', fake_run)
    monkeypatch.setattr(mod, 'verify_source_binding', lambda *args, **kwargs: ('1' * 40, '2' * 40))
    monkeypatch.setattr(mod.time, 'sleep', lambda _: None)
    mod.run_qualification(
        repo_root=tmp_path,
        manifest_path=mpath,
        postgres_image='postgres:16.15@sha256:' + 'a' * 64,
        source_commit='1' * 40,
        source_tree='2' * 40,
        container_name='bt2-test',
    )
    run = next(cmd for cmd in calls if cmd[:2] == ['docker', 'run'])
    mount_index = run.index('--mount') + 1
    assert run[mount_index] == f'type=bind,src={tmp_path.resolve()},dst=/workspace,readonly'
    file_calls = [cmd for cmd in calls if cmd[:2] == ['docker', 'exec'] and 'psql' in cmd and '-f' in cmd]
    assert [cmd[cmd.index('-f') + 1] for cmd in file_calls] == [
        '/workspace/database/schema/0001.sql',
        '/workspace/database/migrations/0002.sql',
        '/workspace/database/tests/0001.sql',
        '/workspace/database/tests/0002.sql',
    ]


def test_container_sql_path_rejects_parent_escape():
    mod = load_module()
    assert mod._container_sql_path('database/tests/0003.sql') == '/workspace/database/tests/0003.sql'
    with pytest.raises(mod.QualificationError, match='MANIFEST_PATH_INVALID'):
        mod._container_sql_path('database/tests/../secret.sql')
