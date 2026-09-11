#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

_SHA40 = re.compile(r'^[0-9a-f]{40}$')
_SHA64 = re.compile(r'^[0-9a-f]{64}$')
_IMAGE = re.compile(r'^postgres(?::[A-Za-z0-9._-]+)?@sha256:[0-9a-f]{64}$')
_MANIFEST_VERSION = 'BT2_DATABASE_BUILD_MANIFEST_V1'


class QualificationError(RuntimeError):
    pass


def fail(code: str) -> None:
    raise QualificationError(code)


def git_blob_sha1(data: bytes) -> str:
    header = f'blob {len(data)}\0'.encode('ascii')
    return hashlib.sha1(header + data).hexdigest()


def validate_postgres_image(value: str) -> str:
    if not isinstance(value, str) or _IMAGE.fullmatch(value) is None:
        fail('POSTGRES_IMAGE_NOT_IMMUTABLE')
    return value


def _safe_path(repo_root: Path, rel: Any) -> Path:
    if not isinstance(rel, str) or not rel or rel.startswith('/'):
        fail('MANIFEST_PATH_INVALID')
    root = repo_root.resolve()
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        fail(f'MANIFEST_PATH_ESCAPES_REPOSITORY:{rel}')
    if not path.is_file():
        fail(f'MANIFEST_PATH_MISSING:{rel}')
    return path


def _manifest_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    qualification = manifest.get('qualification')
    if not isinstance(qualification, dict):
        fail('MANIFEST_QUALIFICATION_INVALID')
    groups = [
        manifest.get('ordered_apply'),
        manifest.get('post_preservation_data_loads', []),
        qualification.get('smoke_tests'),
    ]
    out: list[dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, list):
            fail('MANIFEST_ENTRY_GROUP_INVALID')
        for entry in group:
            if not isinstance(entry, dict):
                fail('MANIFEST_ENTRY_INVALID')
            out.append(entry)
    return out


def load_and_verify_manifest(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    try:
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise QualificationError('MANIFEST_READ_INVALID') from exc
    if not isinstance(manifest, dict) or manifest.get('manifest_version') != _MANIFEST_VERSION:
        fail('MANIFEST_VERSION_INVALID')

    target = manifest.get('target')
    if not isinstance(target, dict) or not isinstance(target.get('qualified_major_version'), int):
        fail('MANIFEST_TARGET_INVALID')
    extensions = target.get('required_extensions')
    if not isinstance(extensions, list) or not all(isinstance(x, str) and x for x in extensions):
        fail('MANIFEST_EXTENSIONS_INVALID')

    identity = manifest.get('package_identity')
    if not isinstance(identity, dict):
        fail('PACKAGE_IDENTITY_INVALID')
    digest_input = identity.get('digest_input')
    package_digest = identity.get('package_digest_sha256')
    if not isinstance(digest_input, str) or not isinstance(package_digest, str) or _SHA64.fullmatch(package_digest) is None:
        fail('PACKAGE_DIGEST_INVALID')
    if hashlib.sha256(digest_input.encode('utf-8')).hexdigest() != package_digest:
        fail('PACKAGE_DIGEST_MISMATCH')

    seen: set[str] = set()
    for entry in _manifest_entries(manifest):
        rel = entry.get('path')
        blob = entry.get('git_blob')
        if not isinstance(rel, str) or rel in seen:
            fail(f'MANIFEST_PATH_DUPLICATE_OR_INVALID:{rel}')
        seen.add(rel)
        if not isinstance(blob, str) or _SHA40.fullmatch(blob) is None:
            fail(f'MANIFEST_GIT_BLOB_INVALID:{rel}')
        path = _safe_path(repo_root, rel)
        actual = git_blob_sha1(path.read_bytes())
        if actual != blob:
            fail(f'GIT_BLOB_MISMATCH:{rel}')

    authority = manifest.get('authority')
    if isinstance(authority, dict) and any(value is True for value in authority.values()):
        fail('MANIFEST_PROTECTED_AUTHORITY_TRUE')
    return manifest


def manifest_execution_paths(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    qualification = manifest['qualification']
    return [
        *[('APPLY', entry['path']) for entry in manifest['ordered_apply']],
        *[('TEST', entry['path']) for entry in qualification['smoke_tests']],
    ]


def post_preservation_paths(manifest: dict[str, Any]) -> list[str]:
    return [entry['path'] for entry in manifest.get('post_preservation_data_loads', [])]


def _run(cmd: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, input=input_text, text=True, capture_output=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or '').strip().replace('\n', ' ')[:500]
        fail(f'COMMAND_FAILED:{cmd[0]}:{detail}')
    return result


def _container_sql_path(rel: str) -> str:
    if not isinstance(rel, str) or not rel or rel.startswith('/') or '..' in Path(rel).parts:
        fail(f'MANIFEST_PATH_INVALID:{rel}')
    return '/workspace/' + rel.replace('\\', '/')


def _docker_exec_psql_file(container: str, rel: str) -> subprocess.CompletedProcess[str]:
    return _run([
        'docker', 'exec', container,
        'psql', '-X', '-v', 'ON_ERROR_STOP=1', '-U', 'postgres', '-d', 'bt2_ci',
        '-f', _container_sql_path(rel),
    ])



def verify_source_binding(repo_root: Path, expected_commit: str, expected_tree: str) -> tuple[str, str]:
    if _SHA40.fullmatch(expected_commit) is None or _SHA40.fullmatch(expected_tree) is None:
        fail('SOURCE_BINDING_INVALID')
    cwd = str(repo_root.resolve())
    commit = _run(['git', '-C', cwd, 'rev-parse', 'HEAD']).stdout.strip().lower()
    tree = _run(['git', '-C', cwd, 'rev-parse', 'HEAD^{tree}']).stdout.strip().lower()
    status = _run(['git', '-C', cwd, 'status', '--porcelain', '--untracked-files=no']).stdout.strip()
    if commit != expected_commit:
        fail(f'SOURCE_COMMIT_MISMATCH:{commit}:{expected_commit}')
    if tree != expected_tree:
        fail(f'SOURCE_TREE_MISMATCH:{tree}:{expected_tree}')
    if status:
        fail('SOURCE_WORKTREE_DIRTY')
    return commit, tree

def build_receipt(
    *,
    source_commit: str,
    source_tree: str,
    manifest_digest: str,
    package_digest: str,
    postgres_image: str,
    postgres_version: str,
    docker_version: str,
    stage_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        'schema': 'BT2_LOCAL_REBUILD_QUALIFICATION_RECEIPT_V1',
        'status': 'PASS',
        'mode': 'LOCAL_DOCKER_NO_PAID_SERVICES',
        'source_commit': source_commit,
        'source_tree': source_tree,
        'manifest_sha256': manifest_digest,
        'package_digest_sha256': package_digest,
        'postgres_image': postgres_image,
        'postgres_version': postgres_version,
        'docker_version': docker_version,
        'stage_results': stage_results,
        'post_preservation_data_loads_executed': False,
        'post_preservation_data_load_policy': 'VERIFIED_AS_PACKAGE_BYTES; EXERCISED_ONLY_BY_DECLARED_TRANSACTIONAL_SMOKE_WITH_SYNTHETIC_PRECONDITIONS',
        'live_wowsql_mutated': False,
        'protected_effects_performed': False,
        'max_out_of_pocket_cost_usd': 0,
    }


def run_qualification(
    *,
    repo_root: Path,
    manifest_path: Path,
    postgres_image: str,
    source_commit: str,
    source_tree: str,
    container_name: str | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    validate_postgres_image(postgres_image)
    verify_source_binding(repo_root, source_commit, source_tree)
    manifest = load_and_verify_manifest(repo_root, manifest_path)
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    package_digest = manifest['package_identity']['package_digest_sha256']
    container = container_name or f'bt2-rebuild-{uuid.uuid4().hex[:12]}'
    stage_results: list[dict[str, Any]] = []

    docker_version = _run(['docker', 'version', '--format', '{{.Server.Version}}']).stdout.strip()
    if not docker_version:
        fail('DOCKER_VERSION_UNAVAILABLE')

    try:
        _run([
            'docker', 'run', '--detach', '--name', container,
            '-e', 'POSTGRES_PASSWORD=bt2-local-only',
            '-e', 'POSTGRES_DB=bt2_ci',
            '--mount', f'type=bind,src={repo_root},dst=/workspace,readonly',
            postgres_image,
        ])

        ready = False
        for _ in range(60):
            probe = _run(['docker', 'exec', container, 'pg_isready', '-U', 'postgres', '-d', 'bt2_ci'], check=False)
            if probe.returncode == 0:
                ready = True
                break
            time.sleep(1)
        if not ready:
            fail('POSTGRES_READINESS_TIMEOUT')

        version_result = _run([
            'docker', 'exec', container,
            'psql', '-X', '-At', '-U', 'postgres', '-d', 'bt2_ci', '-c', 'show server_version;',
        ])
        postgres_version = version_result.stdout.strip()
        try:
            observed_major = int(postgres_version.split('.', 1)[0])
        except (ValueError, IndexError) as exc:
            raise QualificationError('POSTGRES_VERSION_INVALID') from exc
        expected_major = manifest['target']['qualified_major_version']
        if observed_major != expected_major:
            fail(f'POSTGRES_MAJOR_MISMATCH:{observed_major}:{expected_major}')

        for stage_kind, rel in manifest_execution_paths(manifest):
            _docker_exec_psql_file(container, rel)
            stage_results.append({'stage': f'{stage_kind}:{rel}', 'exit_code': 0})

        for extension in manifest['target']['required_extensions']:
            result = _run([
                'docker', 'exec', container,
                'psql', '-X', '-At', '-U', 'postgres', '-d', 'bt2_ci', '-c',
                f"select count(*) from pg_extension where extname='{extension.replace(chr(39), chr(39)*2)}';",
            ])
            if result.stdout.strip() != '1':
                fail(f'REQUIRED_EXTENSION_MISSING:{extension}')

        return build_receipt(
            source_commit=source_commit,
            source_tree=source_tree,
            manifest_digest=manifest_digest,
            package_digest=package_digest,
            postgres_image=postgres_image,
            postgres_version=postgres_version,
            docker_version=docker_version,
            stage_results=stage_results,
        )
    finally:
        _run(['docker', 'rm', '-f', container], check=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Zero-cost isolated BT2 blank-database rebuild qualification.')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--manifest', default='database/BUILD_MANIFEST_V1.json')
    parser.add_argument('--postgres-image', required=True, help='Immutable postgres image, e.g. postgres:16.15@sha256:<digest>')
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--source-tree', required=True)
    parser.add_argument('--receipt', default='')
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    manifest = (repo_root / args.manifest).resolve()
    try:
        receipt = run_qualification(
            repo_root=repo_root,
            manifest_path=manifest,
            postgres_image=args.postgres_image,
            source_commit=args.source_commit.lower(),
            source_tree=args.source_tree.lower(),
        )
    except QualificationError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(receipt, sort_keys=True, indent=2) + '\n'
    if args.receipt:
        Path(args.receipt).write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
