import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]

class HighOnlyGateTest(unittest.TestCase):
    def test_disguised_font_high_finding_requires_review_not_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            target=root/'public'/'fonts'
            target.mkdir(parents=True)
            (target/'apparently-safe.ttf').write_bytes(b'const not_a_font = 1;')
            command=[sys.executable,str(HERE/'scanner.py'),'--root',str(root),'--repo','example/repo','--head','a'*40,'--fail-on-high']
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertIn('FONT_MAGIC_MISMATCH', result.stdout, 'candidate silently unreported or option unsupported')
            self.assertEqual(result.returncode, 2, 'HIGH-only finding wrongly allows promotion')

if __name__=='__main__':unittest.main()
