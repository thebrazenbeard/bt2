"""Regression: Git index hint bits do not establish pristine source bytes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[1] / 'scanner.py'
HEAD_SHA = 'HEAD'

class TrackedByteBinding(unittest.TestCase):
    def exercise(self, hint):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vscode = root / '.vscode'
            vscode.mkdir()
            tasks = vscode / 'tasks.json'
            settings = vscode / 'settings.json'
            tasks.write_text(json.dumps({'version':'2.0.0', 'tasks':[
                {'label':'hidden','type':'shell','command':'node hidden.js',
                 'hide':True,'runOptions':{'runOn':'folderOpen'}}]}))
            settings.write_text(json.dumps({'task.allowAutomaticTasks':True}))
            def git(*args):
                return subprocess.run(['git','-C',tmp,*args],
                    check=True,capture_output=True,text=True).stdout.strip()
            git('init','-q')
            git('add','.vscode')
            git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
                'commit','-qm','inert-source-fixture')
            head = git('rev-parse', HEAD_SHA)
            base = [sys.executable, str(SCANNER), '--root', tmp,
                    '--repo','example/security','--head',head,
                    '--require-git-head','--require-clean-source','--fail-on-high']
            dirty_original = subprocess.run(base, capture_output=True, text=True)
            self.assertEqual(dirty_original.returncode, 2, 'fixture must contain detectable finding')
            for path in ('.vscode/tasks.json','.vscode/settings.json'):
                git('update-index', hint, path)
            tasks.write_text('{"version":"2.0.0", "tasks":[]}')
            settings.write_text('{}')
            self.assertEqual(git('status','--porcelain'), '',
                             'fixture did not hide changes from Git status')
            checked = subprocess.run(base, capture_output=True, text=True)
            self.assertNotEqual(checked.returncode, 0,
                'tracked security source substituted under Git index hint; provenance gate passed')
            self.assertIn('SOURCE_TREE', checked.stderr,
                'rejection should be a source-verification error, not an unrelated test failure')

    def test_assume_unchanged_cannot_fake_clean_security_tree(self):
        self.exercise('--assume-unchanged')

    def test_skip_worktree_cannot_fake_clean_security_tree(self):
        self.exercise('--skip-worktree')

if __name__ == '__main__':
    unittest.main()
