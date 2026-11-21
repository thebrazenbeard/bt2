"""Security policy and workflow paths cannot be untracked yet appear clean."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCANNER = Path(__file__).resolve().parents[1] / 'scanner.py'

class UntrackedSecuritySource(unittest.TestCase):
    def exercise(self, relpath):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / '.vscode').mkdir()
            (root / '.vscode/tasks.json').write_text('{"version":"2.0.0","tasks":[]}', encoding='utf-8')
            def git(*args):
                result = subprocess.run(['git','-C',d,*args], capture_output=True, text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                return result.stdout.strip()
            git('init','-q')
            git('add','.vscode')
            git('-c','user.name=Test','-c','user.email=t@example.invalid','commit','-qm','fixture')
            head = git('rev-parse','HEAD')
            suspicious = root / relpath
            suspicious.parent.mkdir(parents=True,exist_ok=True)
            suspicious.write_text('name: verification-candidate\n', encoding='utf-8')
            self.assertIn(str(relpath).replace('\\','/'), git('status','--porcelain','--untracked-files=all'))
            result = subprocess.run([sys.executable,str(SCANNER),'--root',d,'--repo','fixture/repo',
                       '--head',head,'--fail-on-high','--require-git-head','--require-clean-source'],
                       capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0,'untracked security source falsely marked clean')
            self.assertIn('SOURCE_TREE_DIRTY',result.stderr)

    def test_new_workflow_not_ignored_by_provenance(self):
        self.exercise(Path('.github/workflows/untracked.yml'))

    def test_new_scanner_policy_file_not_ignored_by_provenance(self):
        self.exercise(Path('conformance/ecosystem_security/new_policy.py'))

if __name__ == '__main__':
    unittest.main()
