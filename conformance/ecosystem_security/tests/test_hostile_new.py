import json, sys, tempfile, unittest, subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scanner as s
HEAD='a'*40

class HostileNew(unittest.TestCase):
    def test_opaque_process_path_in_hidden_autotask_must_not_escape(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); d=root/'.vscode'; d.mkdir()
            (d/'settings.json').write_text(json.dumps({'task.allowAutomaticTasks':True}))
            (d/'tasks.json').write_text(json.dumps({'tasks':[{
                'label':'hidden','type':'process','command':'${workspaceFolder}/.vscode/startup',
                'hide':True,'runOptions':{'runOn':'folderOpen'}}]}))
            got=s.scan_workspace(root,'repo',HEAD)
            self.assertTrue(any(f.rule_id=='EDITOR_OPEN_EXECUTION' and f.severity=='CRITICAL' for f in got),[f.rule_id for f in got])

    def test_malformed_automatic_task_file_must_fail_critical_gate(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); d=root/'.vscode'; d.mkdir()
            (d/'settings.json').write_text(json.dumps({'task.allowAutomaticTasks':True}))
            (d/'tasks.json').write_text('{"tasks": [ { "runOptions": { "runOn": "folderOpen" }, "command": "node" }')
            result=subprocess.run([sys.executable,str(Path(s.__file__)),'--root',t,'--repo','repo',
                '--head',HEAD,'--fail-on-critical'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2, f'Unsafe malformed task config bypassed gate: {result.returncode}, {result.stdout[:400]}')

    def test_provider_lint_201_must_not_be_silently_dropped(self):
        lints=[{'name':f'info_{i}','level':'INFO'} for i in range(200)]
        lints.append({'name':'must_retain_201','level':'CRITICAL','count':1})
        out=s.scan_advisors({'lints':lints},'provider','pinned_snapshot')
        self.assertTrue(any(x.rule_id=='SUPABASE_MUST_RETAIN_201' for x in out),f'Found {len(out)} of 201')

    def test_cli_cannot_treat_a_claimed_sha_as_git_verified(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            run=subprocess.run([sys.executable,str(Path(s.__file__)),'--root',t,'--repo','repo',
                '--head',HEAD],capture_output=True,text=True)
            self.assertEqual(run.returncode,0)
            result=json.loads(run.stdout)
            self.assertEqual(result.get('source_binding_verified'),False)

if __name__=='__main__':unittest.main()

class AdditionalBounds(unittest.TestCase):
    def test_unsupported_provider_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'ADVISOR_ENTRY_LIMIT'):
            s.scan_advisors({'lints':[{'name':'ok'}]*(s.MAX_ADVISOR_ENTRIES+1)},'alias','snap')

    def test_git_head_match_flag_rejects_forged_head_and_accepts_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run(['git','init','-q',str(root)],check=True)
            (root/'README.md').write_text('fixture')
            subprocess.run(['git','-C',str(root),'add','README.md'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=Test',
                            '-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
            actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
            cmd=[sys.executable,str(Path(s.__file__)),'--root',str(root),'--repo','x','--require-git-head']
            bad=subprocess.run(cmd+['--head','a'*40],capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertIn('GIT_HEAD_MISMATCH_OR_WRONG_ROOT',bad.stderr)
            good=subprocess.run(cmd+['--head',actual],capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            self.assertIs(json.loads(good.stdout)['source_binding_verified'],False)

    def test_embedded_settings_folderopen_custom_command_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)/'.vscode';d.mkdir()
            (d/'settings.json').write_text(json.dumps({'task.allowAutomaticTasks':True,
                'tasks':{'label':'unusual','runOn':'folderOpen','command':'./tools/bootstrap'}}))
            rules={f.rule_id for f in s.scan_workspace(Path(tmp),'x',HEAD)}
            self.assertIn('EDITOR_SETTINGS_AUTOEXEC',rules)

class TypedSchemaTests(unittest.TestCase):
    def test_top_level_array_tasks_must_fail_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)/'.vscode';d.mkdir()
            (d/'settings.json').write_text(json.dumps({'task.allowAutomaticTasks':True}))
            (d/'tasks.json').write_text('[]')
            result=subprocess.run([sys.executable,str(Path(s.__file__)),'--root',tmp,'--repo','x',
                '--head',HEAD,'--fail-on-critical'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,'Wrong-shape task configuration silently passed CI')
    def test_tasks_nonarray_field_must_fail_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)/'.vscode';d.mkdir()
            (d/'settings.json').write_text(json.dumps({'task.allowAutomaticTasks':True}))
            (d/'tasks.json').write_text('{"tasks": "opaque"}')
            result=subprocess.run([sys.executable,str(Path(s.__file__)),'--root',tmp,'--repo','x',
                '--head',HEAD,'--fail-on-critical'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,'Wrong-shape tasks array silently passed CI')
