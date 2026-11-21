"""Advisory-only, dependency-free source and Supabase posture scanner.

Never executes scanned source, changes a database, fetches secrets, or grants actions.
Evidence classes and authorization are immutable source-bound output attributes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

MAX_CONFIG = 256_000
MAX_FONT = 2_000_000
MAX_ADVISORS = 1_000_000
MAX_ADVISOR_ENTRIES = 4096
MAX_SCAN_FILES = 4096
MAX_SCAN_ENTRIES = 8192
MAX_SCAN_DEPTH = 8
SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", ".sources", "node_modules", ".venv", "venv",
    "__pycache__", "dist", "build", "coverage", ".next", ".cache"
})
LIFECYCLE = frozenset({
    "preinstall", "install", "postinstall", "prepare", "prepublish",
    "prepublishOnly", "prepack", "postpack"
})
DANGEROUS_HOOK = re.compile(
    r"(?is)(?:\b(?:node|python|deno|bun|powershell|pwsh)\s+[^\r\n;&|]{0,240}\.(?:ttf|woff2?|otf|eot)\b"
    r"|\b(?:curl|wget)\b[^\r\n;]{0,220}\|\s*(?:ba)?sh\b)"
)
MAGIC = {
    '.ttf': (b'\x00\x01\x00\x00', b'true', b'ttcf', b'OTTO'),
    '.otf': (b'OTTO', b'ttcf'),
    '.woff': (b'wOFF',),
    '.woff2': (b'wOF2',),
}
EXE = re.compile(r'(?i)(?:^|[/\\\s])(?:node(?:\.exe)?|python(?:\d(?:\.\d)?)?(?:\.exe)?|powershell(?:\.exe)?|pwsh(?:\.exe)?|bash|sh|cmd(?:\.exe)?|wscript(?:\.exe)?|cscript(?:\.exe)?|npm(?:\.cmd)?|npx(?:\.cmd)?)(?:\s|$|[/\\])')


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    message: str
    source_digest: str
    evidence: tuple[str, ...]
    incident_id: str
    disposition: str = 'REVIEW_REQUIRED'
    evidence_class: str = 'SOURCE_INSPECTION'
    authority: str = 'NONE'
    independent_revalidation: str = 'NOT_PERFORMED'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _jsonc(blob: bytes) -> Any:
    if len(blob) > MAX_CONFIG:
        raise ValueError('CONFIG_SIZE_LIMIT')
    # Read-only JSONC lexical parser: preserve strings while removing comments.
    text = blob.decode('utf-8-sig')
    result = []
    i, inside, escaped = 0, False, False
    while i < len(text):
        ch = text[i]
        nxt = text[i+1] if i+1 < len(text) else ''
        if inside:
            result.append(ch)
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == '"': inside = False
            i += 1; continue
        if ch == '"': inside = True; result.append(ch); i += 1; continue
        if ch == '/' and nxt == '/':
            i += 2
            while i < len(text) and text[i] != '\n': i += 1
            continue
        if ch == '/' and nxt == '*':
            i += 2
            while i + 1 < len(text) and text[i:i+2] != '*/': i += 1
            if i + 1 >= len(text): raise ValueError('UNTERMINATED_COMMENT')
            i += 2; continue
        result.append(ch); i += 1
    # Remove trailing commas only outside JSON string literals.
    clean=''.join(result)
    result=[]; inside=False; escaped=False
    for pos,ch in enumerate(clean):
        if inside:
            result.append(ch)
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':inside=False
            continue
        if ch=='"':inside=True;result.append(ch);continue
        if ch==',' and re.match(r'\s*[}\]]',clean[pos+1:]):continue
        result.append(ch)
    return json.loads(''.join(result))


def _read(root: Path, name: str, max_size=MAX_CONFIG) -> bytes | None:
    path = root / name
    relative=Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'PATH_OUTSIDE_ROOT:{name}')
    cursor=root
    for part in relative.parts:
        cursor=cursor/part
        if cursor.is_symlink(): raise ValueError(f'SYMLINK_REFUSED:{name}')
    if not path.is_file(): return None
    if path.stat().st_size > max_size: raise ValueError(f'SIZE_LIMIT:{name}')
    return path.read_bytes()


def _make(repo: str, head: str, path: str, rule: str, severity: str,
          message: str, raw: bytes, evidence: tuple[str, ...]) -> Finding:
    # Incident IDs are computed from exact source subject. Never trust a caller ID.
    binding = '\0'.join([repo,head,path,rule,digest(raw)]).encode()
    return Finding(rule, severity, path, message, digest(raw), evidence,
                   hashlib.sha256(binding).hexdigest()[:24])


def _scan_root_workspace(root: Path, repo: str, head: str) -> list[Finding]:
    out: list[Finding] = []
    paths = ['.vscode/tasks.json', '.vscode/settings.json']
    loaded: dict[str, tuple[Any, bytes]] = {}
    for path in paths:
        try:
            raw = _read(root,path)
            if raw is None: continue
            loaded[path] = (_jsonc(raw),raw)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            # Never reread a failed/untrusted path: ancestor symlink may escape root.
            raw = b''
            out.append(_make(repo,head,path,'CONFIG_UNREADABLE','HIGH',
                'Workspace execution configuration is unparseable or unsafe to read',raw,(type(exc).__name__,)))
    tasks, raw_tasks = loaded.get('.vscode/tasks.json', ({},b''))
    settings, raw_settings = loaded.get('.vscode/settings.json', ({},b''))
    # Valid JSON with the wrong schema is not a qualified clean scan.
    if not isinstance(tasks,dict):
        if raw_tasks:
            out.append(_make(repo,head,'.vscode/tasks.json','CONFIG_SCHEMA_INVALID','HIGH',
                'Workspace tasks configuration has an unsupported top-level shape',
                raw_tasks,('expected=object',)))
        tasks = {}
    if not isinstance(settings,dict):
        if raw_settings:
            out.append(_make(repo,head,'.vscode/settings.json','CONFIG_SCHEMA_INVALID','HIGH',
                'Workspace settings configuration has an unsupported top-level shape',
                raw_settings,('expected=object',)))
        settings = {}
    tlist = tasks.get('tasks',[])
    if not isinstance(tlist,list):
        out.append(_make(repo,head,'.vscode/tasks.json','CONFIG_SCHEMA_INVALID','HIGH',
            'Workspace tasks array has an unsupported shape',raw_tasks,
            ('expected=tasks:list',)))
        tlist=[]
    elif any(not isinstance(t,dict) for t in tlist):
        out.append(_make(repo,head,'.vscode/tasks.json','CONFIG_SCHEMA_INVALID','HIGH',
            'Workspace tasks array contains non-object entries',raw_tasks,
            ('expected=each-task:object',)))
    labels=[t['label'] for t in tlist if isinstance(t,dict) and isinstance(t.get('label'),str)]
    if len(labels)!=len(set(labels)):
        out.append(_make(repo,head,'.vscode/tasks.json','CONFIG_SCHEMA_INVALID','HIGH',
            'Task labels are ambiguous; dependency binding cannot be trusted',
            raw_tasks,('duplicate_task_label',)))
    by_label = {t['label']:t for t in tlist if isinstance(t,dict) and isinstance(t.get('label'),str)}
    settings_auto = settings.get('task.allowAutomaticTasks') is True
    if settings_auto:
        out.append(_make(repo,head,'.vscode/settings.json','AUTOMATIC_TASKS_ENABLED','INFO',
            'Editor workspace allows automatic tasks; not a vulnerability alone',raw_settings,
            ('task.allowAutomaticTasks=true',)))
    # Some workspaces put an editor task directly in settings rather than tasks.json.
    nested=settings.get('tasks',{})
    if isinstance(nested,dict) and nested.get('runOn')=='folderOpen':
        # A direct executable path is as relevant as a familiar interpreter.
        command=nested.get('command','')
        if isinstance(command,str) and command.strip():
            out.append(_make(repo,head,'.vscode/settings.json',
                'EDITOR_SETTINGS_AUTOEXEC','HIGH',
                'Editor settings contain an executable folderOpen task',raw_settings,
                ('task_label='+str(nested.get('label','[unlabeled]')),)))
    for t in tlist:
        if not isinstance(t,dict) or t.get('runOptions',{}).__class__ is not dict:continue
        if t.get('runOptions',{}).get('runOn')!='folderOpen':continue
        visited:set[str]=set()
        todo=[t]
        chain=[]
        concealed=False
        executable=False
        while todo and len(visited)<64:
            item=todo.pop()
            label=str(item.get('label','[unlabeled]'))
            if label in visited:continue
            visited.add(label);chain.append(label)
            presentation=item.get('presentation') or {}
            concealed |= item.get('hide') is True or (isinstance(presentation,dict) and presentation.get('reveal')=='never')
            parts=[]
            for cfg in (item,item.get('windows'),item.get('linux'),item.get('osx')):
                if not isinstance(cfg,dict):continue
                parts.extend(str(cfg.get(k,'')) for k in ('command','args','type'))
            # VS Code can execute *any* command here, not merely a known interpreter.
            # The previous interpreter-only regex missed executable scripts, binaries,
            # and workspace-variable paths. We report execution candidates; a custom
            # command is not evidence of malicious intent.
            executable |= any(
                isinstance(cfg,dict) and isinstance(cfg.get('command'),str)
                and bool(cfg['command'].strip())
                for cfg in (item,item.get('windows'),item.get('linux'),item.get('osx'))
            )
            dep=item.get('dependsOn',[])
            if isinstance(dep,str):dep=[dep]
            if isinstance(dep,list):todo.extend(by_label[x] for x in dep if isinstance(x,str) and x in by_label)
        if todo:
            out.append(_make(repo,head,'.vscode/tasks.json','DEPENDENCY_CHAIN_LIMIT','HIGH',
                'Automatic-task dependency graph exceeds bounded traversal',raw_tasks,(f'chain_count={len(visited)}',)))
        if executable:
            sev='CRITICAL' if concealed and settings_auto else 'HIGH'
            out.append(_make(repo,head,'.vscode/tasks.json','EDITOR_OPEN_EXECUTION',sev,
                'Opening this workspace can run an executable command via task dependencies',raw_tasks,
                ('auto-task: '+str(t.get('label','[unlabeled]')), 'chain: '+' -> '.join(chain[:16]),
                 f'concealed={concealed}',f'automatic_setting={settings_auto}')))
    # MIME mismatch is a source candidate, not proof of malicious execution.
    for base in (root/'public'/'fonts',root/'.vscode'):
        if any(node.is_symlink() for node in (root/'public',root/'public'/'fonts') if node==base or node in base.parents):
            continue
        if not base.is_dir() or base.is_symlink():continue
        for path in base.iterdir():
            if not path.is_file() or path.is_symlink():continue
            ext=path.suffix.lower()
            if ext not in MAGIC:continue
            try:raw=_read(root,str(path.relative_to(root)),MAX_FONT)
            except (OSError,ValueError):continue
            if raw and not any(raw.startswith(x) for x in MAGIC[ext]):
                name=path.relative_to(root).as_posix()
                out.append(_make(repo,head,name,'FONT_MAGIC_MISMATCH','HIGH',
                    'File extension declares a font but its magic is not recognized',raw,
                    ('file_extension='+ext, 'file_signature=unrecognized')))
    return sorted(out,key=lambda x:(x.path,x.rule_id,x.incident_id))


def _enumerate_security_paths(root: Path, repo: str, head: str) -> list[Finding]:
    """Bounded non-following traversal of relevant workspace and package surfaces.

    The traversal enumerates evidence; it does not import or run repository code.
    Unreadable and symlinked source that could conceal relevant content is a
    hold rather than a clean scan.
    """
    out: list[Finding] = []
    seen = 0
    visited = 0
    def on_walk_error(error: OSError) -> None:
        # The OS may omit unreadable subtrees without raising to the caller.
        out.append(_make(repo,head,'[unreadable-subtree]','CONFIG_UNREADABLE','HIGH',
            'Operating system denied security source traversal',b'',
            (type(error).__name__,)))
    for current_str, dirnames, filenames in os.walk(root, topdown=True,
                                                    followlinks=False,onerror=on_walk_error):
        visited += 1 + len(dirnames) + len(filenames)
        if visited > MAX_SCAN_ENTRIES:
            out.append(_make(repo,head,'[traversal-limit]','SCAN_LIMIT_EXCEEDED','HIGH',
                'Security source traversal exceeded bounded total entries',b'',
                ('entry_limit',)))
            return out
        current = Path(current_str)
        rel = current.relative_to(root)
        depth = len(rel.parts)
        if depth > MAX_SCAN_DEPTH:
            out.append(_make(repo,head,str(rel),'SCAN_LIMIT_EXCEEDED','HIGH',
                'Security scan exceeded the bounded directory depth',b'',('depth_limit',)))
            dirnames.clear()
            continue
        for name in sorted(dirnames[:]):
            if name in SKIP_DIRS:
                dirnames.remove(name)
            elif (current/name).is_symlink():
                dirnames.remove(name)
                sub=(current/name).relative_to(root).as_posix()
                out.append(_make(repo,head,sub,'CONFIG_UNREADABLE','HIGH',
                    'Untrusted directory symlink cannot be treated as clean source',b'',('symlink_directory',)))
        dirnames.sort()
        # The root .vscode is handled by the original editor scanner.
        if rel.parts and '.vscode' in dirnames:
            sub=current/'.vscode'
            for finding in _scan_root_workspace(current,repo,head):
                relative=(rel/finding.path).as_posix()
                data=b''
                try:
                    data=_read(root,relative,MAX_FONT) or b''
                except (OSError,ValueError):
                    pass
                out.append(_make(repo,head,relative,finding.rule_id,finding.severity,
                    finding.message,data,finding.evidence))
        if '.vscode' in dirnames:
            dirnames.remove('.vscode')
        for name in sorted(filenames):
            path=current/name
            if (current.name=='fonts' and current.parent.name=='public' and
                    path.suffix.lower() in MAGIC):
                if current == root/'public'/'fonts':
                    continue  # already scanned by the root editor scanner
                relative=path.relative_to(root).as_posix()
                try:
                    raw=_read(root,relative,MAX_FONT)
                    if raw and not any(raw.startswith(magic) for magic in MAGIC[path.suffix.lower()]):
                        out.append(_make(repo,head,relative,'FONT_MAGIC_MISMATCH','HIGH',
                            'Nested font extension does not match source signature',raw,
                            ('file_extension='+path.suffix.lower(),)))
                except (OSError,ValueError) as error:
                    out.append(_make(repo,head,relative,'CONFIG_UNREADABLE','HIGH',
                        'Nested font candidate is unreadable or unsafe to traverse',b'',
                        (type(error).__name__,)))
                continue
            if name not in ('package.json',) and not name.endswith('.code-workspace'):
                continue
            relative=path.relative_to(root).as_posix()
            seen+=1
            if seen > MAX_SCAN_FILES:
                out.append(_make(repo,head,relative,'SCAN_LIMIT_EXCEEDED','HIGH',
                    'Maximum security manifest count exceeded',b'',('file_limit',)))
                return out
            try:
                raw=_read(root,relative)
                if raw is None:
                    raise ValueError('FILE_VANISHED')
                doc=_jsonc(raw) if name.endswith('.code-workspace') else json.loads(raw)
                if not isinstance(doc,dict):
                    raise ValueError('INVALID_SCHEMA')
            except (OSError,ValueError,UnicodeError,TypeError,json.JSONDecodeError) as exc:
                out.append(_make(repo,head,relative,'CONFIG_UNREADABLE','HIGH',
                    'Security-relevant manifest is unreadable or malformed',b'',
                    (type(exc).__name__,)))
                continue
            if name=='package.json':
                scripts=doc.get('scripts',{})
                if not isinstance(scripts,dict):
                    out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                        'Package scripts are not a mapping',raw,('scripts_not_object',)))
                    continue
                for key,command in sorted(scripts.items()):
                    if key not in LIFECYCLE:
                        continue
                    if not isinstance(command,str):
                        out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                            'Package lifecycle command is not a string',raw,(str(key),)))
                    elif DANGEROUS_HOOK.search(command):
                        out.append(_make(repo,head,relative,'PACKAGE_LIFECYCLE_EXECUTION','HIGH',
                            'Package lifecycle hook executes a disguised asset or fetched shell script',
                            raw,('hook='+key,'suspicious_signature_matched')))
                    else:
                        out.append(_make(repo,head,relative,'PACKAGE_LIFECYCLE_HOOK','INFO',
                            'Package lifecycle hook executes code during dependency operations',
                            raw,('hook='+key,)))
                continue
            settings=doc.get('settings',{})
            tasks=doc.get('tasks',{})
            if not isinstance(settings,dict) or not isinstance(tasks,dict):
                out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                    'Workspace settings/tasks have an unsupported schema',raw,('expected_object',)))
                continue
            auto=settings.get('task.allowAutomaticTasks') is True
            tasklist=tasks.get('tasks',[])
            if not isinstance(tasklist,list):
                out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                    'Workspace task list has an unsupported schema',raw,('expected_list',)))
                continue
            for task in tasklist:
                if not isinstance(task,dict):
                    out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                        'Workspace task entry has an unsupported schema',raw,('expected_object',)))
                    continue
                options=task.get('runOptions',{})
                if not isinstance(options,dict):
                    out.append(_make(repo,head,relative,'CONFIG_SCHEMA_INVALID','HIGH',
                        'Workspace task options have an unsupported schema',raw,('expected_object',)))
                    continue
                if options.get('runOn')!='folderOpen':
                    continue
                has_command=any(isinstance(cfg,dict) and isinstance(cfg.get('command'),str)
                    and bool(cfg['command'].strip()) for cfg in
                    (task,task.get('windows'),task.get('linux'),task.get('osx')))
                if has_command or task.get('dependsOn'):
                    presentation=task.get('presentation') or {}
                    concealed=task.get('hide') is True or (isinstance(presentation,dict)
                        and presentation.get('reveal')=='never')
                    out.append(_make(repo,head,relative,'WORKSPACE_FILE_AUTOEXEC',
                        'CRITICAL' if concealed and auto else 'HIGH',
                        'Code workspace can execute an automatic task on folder open',raw,
                        (f'concealed={concealed}',f'automatic_setting={auto}')))
    return out


def scan_workspace(root: Path, repo: str, head: str) -> list[Finding]:
    """Inspect root and bounded nested source surfaces without executing them."""
    out = _scan_root_workspace(root,repo,head)
    out.extend(_enumerate_security_paths(root,repo,head))
    return sorted(out,key=lambda x:(x.path,x.rule_id,x.incident_id))


def scan_advisors(advisors: dict[str,Any], project_alias: str, snapshot_id: str) -> list[Finding]:
    """Model Supabase advisor notices without promoting them into privilege grants."""
    blob=json.dumps(advisors,sort_keys=True,ensure_ascii=True).encode()
    if len(blob)>MAX_ADVISORS:raise ValueError('ADVISOR_SIZE_LIMIT')
    entries=advisors.get('lints',[])
    if not isinstance(entries,list):raise ValueError('ADVISOR_SCHEMA_INVALID')
    result=[]
    # Never silently discard tail security notices. Fail closed if a snapshot
    # exceeds the bounded all-entry processing budget.
    if len(entries)>MAX_ADVISOR_ENTRIES:raise ValueError('ADVISOR_ENTRY_LIMIT')
    for lint in entries:
        if not isinstance(lint,dict):continue
        name=lint.get('name')
        if not isinstance(name,str):continue
        if name=='rls_enabled_no_policy':
            severity='INFO';reason='No-policy tables may intentionally deny access; inspect grants before any fix'
        elif lint.get('level') in ('ERROR','CRITICAL'):
            severity='HIGH';reason='Advisor indicates a security issue requiring independent review'
        else:
            severity='INFO';reason='Advisor notice requires workload and permission context'
        result.append(_make(project_alias,snapshot_id,'supabase/advisors',
            'SUPABASE_'+re.sub(r'[^A-Z0-9_]','_',name.upper()),severity,
            reason,blob,(f'advisor={name}',f'reported_count={lint.get("count","unknown")}')))
    return result


def advisory_gate(findings: list[Finding], budget: int=8) -> dict[str,Any]:
    if budget<0:raise ValueError('INVALID_BUDGET')
    # Important: owner conflict, a budget, and optimistic model scores cannot erase criticals.
    high=[f for f in findings if f.severity in ('CRITICAL','HIGH')]
    low=[f for f in findings if f.severity not in ('CRITICAL','HIGH')]
    return {'evidence':'SOURCE_ONLY', 'source_binding_verified':False,
            'installed':False, 'actions_allowed':[],
            'critical_review_queue':[asdict(x) for x in high],
            'digest':[asdict(x) for x in low[:budget]],
            'digest_suppressed_count':max(0,len(low)-budget),
            'decisions':'PROPOSALS_ONLY', 'human_approval':'NOT_INFERRED'}


def sarif(findings:list[Finding]) -> dict[str,Any]:
    return {'version':'2.1.0','$schema':'https://json.schemastore.org/sarif-2.1.0.json',
        'runs':[{'tool':{'driver':{'name':'VeraEcosystemSecuritySourceOnly',
        'rules':[{'id':rid,'shortDescription':{'text':rid}} for rid in sorted({f.rule_id for f in findings})]}},
        'results':[{'ruleId':f.rule_id,'level':'error' if f.severity in ('HIGH','CRITICAL') else 'note',
        'message':{'text':f.message},'locations':[{'physicalLocation':{'artifactLocation':{'uri':f.path}}}],
        'properties':{'incident_id':f.incident_id,'severity':f.severity,'independent_revalidation':f.independent_revalidation,
        'authority':f.authority,'source_digest':f.source_digest,
        'source_binding_verified':False}} for f in findings]}]}



def _verify_tracked_security_bytes(root: Path) -> None:
    """Cross-check tracked security-source bytes against HEAD, ignoring Git index hints.

    This is a local snapshot consistency check, not remote source authentication,
    proof of an atomic read, or evidence that execution was safe.
    """
    result=subprocess.run(['git','-C',str(root),'ls-tree','-rz','--full-tree','HEAD'],
        capture_output=True,timeout=15,check=True)
    if len(result.stdout)>8_000_000:
        raise ValueError('GIT_TREE_LIST_LIMIT')
    inspected=0
    for entry in result.stdout.split(b'\0'):
        if not entry:
            continue
        try:
            metadata, name=entry.split(b'\t',1)
            mode, kind, oid=metadata.split(b' ')
            rel=os.fsdecode(name)
            parts=Path(rel).parts
        except (ValueError,UnicodeError):
            raise ValueError('GIT_TREE_ENTRY_INVALID') from None
        if not parts or Path(rel).is_absolute() or '..' in parts:
            raise ValueError('GIT_TREE_PATH_INVALID')
        lower=[part.casefold() for part in parts]
        if any(part in SKIP_DIRS for part in lower):
            continue
        filename=lower[-1]
        relevant=(
            '.vscode' in lower or filename=='package.json' or
            filename.endswith('.code-workspace') or
            (len(lower)>2 and lower[-3:-1]==['public','fonts']) or
            (len(lower)>2 and lower[:2]==['.github','workflows']) or
            lower==['.gitattributes'] or lower[:2]==['conformance','ecosystem_security']
        )
        if not relevant:
            continue
        inspected+=1
        if inspected>MAX_SCAN_FILES:
            raise ValueError('GIT_SECURITY_FILE_LIMIT')
        path=root.joinpath(*parts)
        # Reject any symlink, missing source, nonregular entry or unreadable file.
        cursor=root
        for part in parts:
            cursor=cursor/part
            if cursor.is_symlink():
                raise ValueError('GIT_SECURITY_SOURCE_SYMLINK')
        if kind!=b'blob' or mode not in (b'100644',b'100755') or not path.is_file():
            raise ValueError('GIT_SECURITY_SOURCE_NOT_REGULAR')
        if path.stat().st_size>2_000_000:
            raise ValueError('GIT_SECURITY_FILE_OVERSIZE')
        raw=path.read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if blob.encode()!=oid:
            raise ValueError('SOURCE_TREE_TRACKED_BYTES_MISMATCH')

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--repo',required=True)
    ap.add_argument('--head',required=True)
    ap.add_argument('--format',choices=['json','sarif'],default='json')
    ap.add_argument('--budget',type=int,default=8)
    ap.add_argument('--fail-on-critical',action='store_true',
                    help='fail CI on critical source candidates or incomplete scans; never auto-fix')
    ap.add_argument('--fail-on-high',action='store_true',
                    help='fail CI on high/critical candidates or incomplete scans; never auto-fix')
    ap.add_argument('--require-clean-source',action='store_true',
                    help='reject dirty scanned source paths (local Git check only)')
    ap.add_argument('--require-git-head',action='store_true',
                    help='require on-disk Git checkout HEAD equals --head (not a full-byte attestation)')
    ap.add_argument('--advisors-snapshot',type=Path,help='sanitized advisor JSON, optional')
    ap.add_argument('--provider-alias',help='nonsecret display alias; required with snapshot')
    a=ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',a.head):ap.error('--head must be exact 40-char lowercase SHA')
    root=a.root.resolve(strict=True)
    if a.require_git_head:
        # This is an additional local identity check, not a GitHub identity,
        # signed commit, pristine worktree, runtime admission, or TOCTOU proof.
        try:
            completed=subprocess.run(
                ['git','-C',str(root),'rev-parse','--show-toplevel','HEAD'],
                capture_output=True,text=True,timeout=10,check=True)
            lines=completed.stdout.strip().splitlines()
            if len(lines)!=2 or Path(lines[0]).resolve()!=root or lines[1]!=a.head:
                ap.error('GIT_HEAD_MISMATCH_OR_WRONG_ROOT')
        except (subprocess.SubprocessError,OSError) as exc:
            ap.error('GIT_HEAD_UNAVAILABLE: '+type(exc).__name__)
    if a.require_clean_source:
        try:
            changed=subprocess.run(['git','-C',str(root),'status','--porcelain',
                '--untracked-files=all','--', '.vscode','public/fonts','packages',
                '.github', 'conformance/ecosystem_security', '.gitattributes', '.gitignore',
                '.gitmodules', ':(glob)**/.vscode/**','**/*.code-workspace','**/package.json'],
                capture_output=True,text=True,timeout=15,check=True)
            if changed.stdout.strip():
                ap.error('SOURCE_TREE_DIRTY')
            _verify_tracked_security_bytes(root)
        except (subprocess.SubprocessError,OSError,ValueError) as exc:
            ap.error('SOURCE_TREE_UNVERIFIED: '+str(exc)[:100])
    findings=scan_workspace(root,a.repo,a.head)
    if a.advisors_snapshot:
        if not a.provider_alias or len(a.provider_alias)>64:
            ap.error('--provider-alias is required and must be short')
        data=a.advisors_snapshot.read_bytes()
        if len(data)>MAX_ADVISORS:ap.error('oversized advisor snapshot')
        try: notices=json.loads(data)
        except (ValueError,UnicodeError):ap.error('invalid advisor JSON')
        findings += scan_advisors(notices,a.provider_alias,'UNVERIFIED_PROVIDER_SNAPSHOT')
    result=sarif(findings) if a.format=='sarif' else advisory_gate(findings,a.budget)
    print(json.dumps(result,indent=2,sort_keys=True))
    # CI may gate promotion on unresolved critical source candidates.
    # Unparseable, oversized and incomplete scans must not silently green-light
    # CI even if their candidate severity is HIGH rather than CRITICAL.
    unqualified={'CONFIG_UNREADABLE','CONFIG_SCHEMA_INVALID','DEPENDENCY_CHAIN_LIMIT','SCAN_LIMIT_EXCEEDED'}
    return 2 if any(
        (a.fail_on_high and f.severity in ('HIGH','CRITICAL')) or
        (a.fail_on_critical and f.severity == 'CRITICAL') or
        ((a.fail_on_high or a.fail_on_critical) and f.rule_id in unqualified)
        for f in findings
    ) else 0

if __name__=='__main__':sys.exit(main())
