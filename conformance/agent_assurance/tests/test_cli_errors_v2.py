"""Hostile CLI error egress tests: no sensitive local paths or tracebacks."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class SafeCliErrors(unittest.TestCase):
    def _run(self, payload):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'privately-named-recovery-evidence.json'
            p.write_bytes(payload)
            r=subprocess.run([sys.executable, '-B', str(ROOT/'gate_v1.py'), str(p)],
                             capture_output=True,text=True,timeout=5)
            self.assertNotEqual(r.returncode,0)
            self.assertNotIn('Traceback',r.stderr)
            self.assertNotIn('privately-named-recovery-evidence',r.stderr)
            self.assertNotIn('privately-named-recovery-evidence',r.stdout)
            self.assertEqual(r.stdout,'')
            self.assertIn('Rejected evidence input',r.stderr)
    def test_oversized_file_safely_rejected(self):
        self._run(b' '*100001)
    def test_invalid_json_safely_rejected(self):
        self._run(b'{"untrusted": \xff}')

if __name__=='__main__':unittest.main()
