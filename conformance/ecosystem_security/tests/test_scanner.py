import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scanner as s

HEAD='a'*40

class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def files(self,tasks=None,settings=None):
        d=self.root/'.vscode';d.mkdir(exist_ok=True)
        if tasks is not None:(d/'tasks.json').write_text(tasks if isinstance(tasks,str) else json.dumps({'tasks':tasks}),encoding='utf-8')
        if settings is not None:(d/'settings.json').write_text(json.dumps(settings),encoding='utf-8')
    def scan(self):return s.scan_workspace(self.root,'thebrazenbeard/synthetic',HEAD)
    def codes(self):return {f.rule_id:f for f in self.scan()}
    def hidden_task(self):
        return [
          {'label':'start','runOptions':{'runOn':'folderOpen'},'dependsOn':['hidden-loader'],'hide':True},
          {'label':'hidden-loader','type':'process','command':'node','args':['${workspaceFolder}/.vscode/ini'],'presentation':{'reveal':'never'}}]
    def test_empty_is_silent(self):self.assertEqual(self.scan(),[])
    def test_ordinary_user_invoked_task_silent(self):
        self.files([{'label':'manual','command':'node','args':['--version']}],{})
        self.assertNotIn('EDITOR_OPEN_EXECUTION',self.codes())
    def test_hidden_chain_high_without_auto_setting(self):
        self.files(self.hidden_task(),{})
        self.assertEqual(self.codes()['EDITOR_OPEN_EXECUTION'].severity,'HIGH')
    def test_hidden_chain_critical_with_auto_setting(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        self.assertEqual(self.codes()['EDITOR_OPEN_EXECUTION'].severity,'CRITICAL')
    def test_automatically_allowed_tasks_alone_not_critical(self):
        self.files([],{'task.allowAutomaticTasks':True})
        self.assertEqual(self.codes()['AUTOMATIC_TASKS_ENABLED'].severity,'INFO')
    def test_jsonc_bom_comments_trailing_commas(self):
        text='\ufeff{ // comment\n "tasks":[{"label":"t","command":"node", "runOptions":{"runOn":"folderOpen",},},],}'
        self.files(text,{})
        self.assertIn('EDITOR_OPEN_EXECUTION',self.codes())
    def test_comment_markers_inside_string_safe(self):
        val=s._jsonc(b'{"url":"https://host.invalid/a//b", "value":"/*not a comment*/"}')
        self.assertEqual(val['url'],'https://host.invalid/a//b')
        self.assertEqual(val['value'],'/*not a comment*/')
    def test_unparseable_tasks_fail_closed(self):
        self.files('{ this is not valid json',{})
        self.assertIn('CONFIG_UNREADABLE',self.codes())
    def test_oversize_tasks_fail_closed(self):
        self.files('a'*(s.MAX_CONFIG+1),{})
        self.assertIn('CONFIG_UNREADABLE',self.codes())
    def test_mismatched_font_candidate(self):
        d=self.root/'public'/'fonts';d.mkdir(parents=True)
        (d/'notfont.ttf').write_bytes(b'console.log("dummy");')
        self.assertIn('FONT_MAGIC_MISMATCH',self.codes())
    def test_recognized_font_no_candidate(self):
        d=self.root/'public'/'fonts';d.mkdir(parents=True)
        (d/'valid.ttf').write_bytes(b'\x00\x01\x00\x00'+b'0'*128)
        self.assertNotIn('FONT_MAGIC_MISMATCH',self.codes())
    def test_symlinked_config_refused(self):
        import os
        d=self.root/'.vscode';d.mkdir()
        target=self.root/'external.txt';target.write_text('{"tasks":[]}')
        try:os.symlink(target,d/'tasks.json')
        except OSError:self.skipTest('symlink unavailable')
        self.assertIn('CONFIG_UNREADABLE',self.codes())
    def test_critical_not_lost_by_zero_digest_budget(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        res=s.advisory_gate(self.scan(),0)
        self.assertTrue(any(x['severity']=='CRITICAL' for x in res['critical_review_queue']))
        self.assertEqual(res['digest'],[])
    def test_incident_id_deterministic_same_exact_head(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        a=self.scan();b=self.scan()
        self.assertEqual([x.incident_id for x in a],[x.incident_id for x in b])
    def test_source_changed_changes_incident_not_privilege(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        a=self.codes()['EDITOR_OPEN_EXECUTION']
        t=json.loads((self.root/'.vscode/tasks.json').read_text())
        t['tasks'][0]['label']='changed'
        (self.root/'.vscode/tasks.json').write_text(json.dumps(t))
        b=self.codes()['EDITOR_OPEN_EXECUTION']
        self.assertNotEqual(a.incident_id,b.incident_id)
        self.assertEqual((b.authority,b.independent_revalidation),('NONE','NOT_PERFORMED'))
    def test_new_head_never_reuses_old_incident(self):
        self.files(self.hidden_task(),{})
        a=self.scan()[0]
        b=s.scan_workspace(self.root,'thebrazenbeard/synthetic','b'*40)[0]
        self.assertNotEqual(a.incident_id,b.incident_id)
    def test_forged_claim_in_task_does_not_authorize(self):
        self.files(self.hidden_task()+[{'label':'owner','verified':True,'human_approval':True}],{'task.allowAutomaticTasks':True})
        self.assertTrue(all(x.authority=='NONE' for x in self.scan()))
    def test_sarif_has_source_and_authority_limit(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        sarif=s.sarif(self.scan())
        self.assertEqual(sarif['version'],'2.1.0')
        self.assertTrue(all(x['properties']['authority']=='NONE' for x in sarif['runs'][0]['results']))
    def test_rls_no_policy_does_not_create_access_grant(self):
        inp={'lints':[{'name':'rls_enabled_no_policy','count':4,'level':'INFO'}]}
        r=s.scan_advisors(inp,'Vera','provider-snapshot-1')[0]
        self.assertEqual((r.severity,r.authority),('INFO','NONE'))
    def test_provider_error_high_requires_review_not_auto_fix(self):
        inp={'lints':[{'name':'other_security_critical','count':1,'level':'ERROR'}]}
        r=s.scan_advisors(inp,'Vera','provider-snapshot-1')[0]
        self.assertEqual((r.severity,r.disposition,r.authority),('HIGH','REVIEW_REQUIRED','NONE'))
    def test_nonlist_advisor_fails_closed(self):
        with self.assertRaises(ValueError):s.scan_advisors({'lints':'sneaky'},'Vera','x')
    def test_budget_cannot_hide_error(self):
        f=s.scan_advisors({'lints':[{'name':'missing_rls','level':'ERROR'}]},'Vera','x')
        self.assertEqual(len(s.advisory_gate(f,0)['critical_review_queue']),1)
    def test_check_source_output_is_data_not_effect(self):
        self.files(self.hidden_task(),{'task.allowAutomaticTasks':True})
        res=s.advisory_gate(self.scan())
        self.assertEqual((res['installed'],res['actions_allowed'],res['decisions']),
                         (False,[], 'PROPOSALS_ONLY'))
    def test_semantic_dedupe_does_not_trust_actor_label(self):
        a=s._make('r','a'*40,'p','rule','HIGH','x',b'abc',('agent1',))
        b=s._make('r','a'*40,'p','rule','HIGH','x',b'abc',('forged_agent1',))
        self.assertEqual(a.incident_id,b.incident_id)
    def test_different_paths_distinct_id(self):
        a=s._make('r','a'*40,'p1','rule','HIGH','x',b'abc',())
        b=s._make('r','a'*40,'p2','rule','HIGH','x',b'abc',())
        self.assertNotEqual(a.incident_id,b.incident_id)

if __name__=='__main__':unittest.main()

class EdgeTests(unittest.TestCase):
    def test_trailing_comma_string_not_modified(self):
        self.assertEqual(s._jsonc(b'{"literal":",}","t":[1,]}')['literal'],',}')
    def test_symlinked_directory_fails_closed(self):
        import os
        with tempfile.TemporaryDirectory() as folder:
            parent=Path(folder)
            outside=parent/'external';outside.mkdir()
            (outside/'tasks.json').write_text('{"tasks":[]}')
            root=parent/'repo';root.mkdir()
            try:os.symlink(outside,root/'.vscode',target_is_directory=True)
            except OSError:self.skipTest('symlinks unavailable')
            findings=s.scan_workspace(root,'x','a'*40)
            self.assertTrue(any(f.rule_id=='CONFIG_UNREADABLE' for f in findings))
    def test_traversal_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):s._read(Path(folder),'../outside')

class ExtraAdversarialTests(unittest.TestCase):
    def test_settings_embedded_autotask_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.vscode').mkdir()
            (root/'.vscode'/'settings.json').write_text(json.dumps({
                'task.allowAutomaticTasks':True,
                'tasks':{'label':'quiet','command':'npm run lint','runOn':'folderOpen'}}))
            ids={f.rule_id for f in s.scan_workspace(root,'repo','a'*40)}
            self.assertIn('EDITOR_SETTINGS_AUTOEXEC',ids)
    def test_symlinked_directory_does_not_read_target_bytes(self):
        import os
        with tempfile.TemporaryDirectory() as folder:
            parent=Path(folder);target=parent/'private';target.mkdir()
            (target/'tasks.json').write_text('private_secret_to_test_no_readback')
            root=parent/'repo';root.mkdir()
            try:os.symlink(target,root/'.vscode',target_is_directory=True)
            except OSError:self.skipTest('symlink unavailable')
            out=s.scan_workspace(root,'x','a'*40)
            self.assertTrue(any(x.rule_id=='CONFIG_UNREADABLE' for x in out))
            self.assertNotIn('private_secret_to_test_no_readback',str(out))