"""Advisory-only, dependency-free source and Supabase posture scanner.

Never executes scanned source, changes a database, fetches secrets, or grants actions.
Evidence classes and authorization are immutable source-bound output attributes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

MAX_CONFIG = 256_000
MAX_FONT = 2_000_000
MAX_ADVISORS = 1_000_000
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


def scan_workspace(root: Path, repo: str, head: str) -> list[Finding]:
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
    if not isinstance(tasks,dict): tasks = {}
    if not isinstance(settings,dict): settings = {}
    tlist = tasks.get('tasks',[])
    if not isinstance(tlist,list): tlist=[]
    by_label = {t['label']:t for t in tlist if isinstance(t,dict) and isinstance(t.get('label'),str)}
    settings_auto = settings.get('task.allowAutomaticTasks') is True
    if settings_auto:
        out.append(_make(repo,head,'.vscode/settings.json','AUTOMATIC_TASKS_ENABLED','INFO',
            'Editor workspace allows automatic tasks; not a vulnerability alone',raw_settings,
            ('task.allowAutomaticTasks=true',)))
    # Some workspaces put an editor task directly in settings rather than tasks.json.
    nested=settings.get('tasks',{})
    if isinstance(nested,dict) and nested.get('runOn')=='folderOpen':
        command=str(nested.get('command',''))
        if EXE.search(command):
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
            executable |= any(EXE.search(part) for part in parts)
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


def scan_advisors(advisors: dict[str,Any], project_alias: str, snapshot_id: str) -> list[Finding]:
    """Model Supabase advisor notices without promoting them into privilege grants."""
    blob=json.dumps(advisors,sort_keys=True,ensure_ascii=True).encode()
    if len(blob)>MAX_ADVISORS:raise ValueError('ADVISOR_SIZE_LIMIT')
    entries=advisors.get('lints',[])
    if not isinstance(entries,list):raise ValueError('ADVISOR_SCHEMA_INVALID')
    result=[]
    for lint in entries[:200]:
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
    return {'evidence':'SOURCE_ONLY', 'installed':False, 'actions_allowed':[],
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
        'authority':f.authority,'source_digest':f.source_digest}} for f in findings]}]}


def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--repo',required=True)
    ap.add_argument('--head',required=True)
    ap.add_argument('--format',choices=['json','sarif'],default='json')
    ap.add_argument('--budget',type=int,default=8)
    ap.add_argument('--fail-on-critical',action='store_true',help='fail CI on source critical candidates; never auto-fix')
    ap.add_argument('--advisors-snapshot',type=Path,help='sanitized advisor JSON, optional')
    ap.add_argument('--provider-alias',help='nonsecret display alias; required with snapshot')
    a=ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',a.head):ap.error('--head must be exact 40-char lowercase SHA')
    root=a.root.resolve(strict=True)
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
    return 2 if a.fail_on_critical and any(f.severity=='CRITICAL' for f in findings) else 0

if __name__=='__main__':sys.exit(main())
