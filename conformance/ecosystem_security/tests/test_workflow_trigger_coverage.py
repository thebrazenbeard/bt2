"""Source-only PR workflow trigger contract; not evidence of a trusted required check."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[3] / '.github/workflows/ecosystem-security-source.yml'


def event_blocks(text: str):
    """Return direct event blocks for the deliberately simple on: mapping."""
    lines = text.splitlines()
    assert 'on:' in lines, 'missing explicit event map'
    first = lines.index('on:') + 1
    result = {}
    current = None
    for line in lines[first:]:
        if line and not line.startswith(' ') and not line.startswith('#'):
            break
        if line.startswith('  ') and not line.startswith('    ') and line.strip().endswith(':'):
            current = line.strip()[:-1]
            result[current] = []
        elif current is not None:
            result[current].append(line)
    return result


class TriggerCoverage(unittest.TestCase):
    def test_review_check_not_path_filtered(self):
        blocks = event_blocks(WORKFLOW.read_text(encoding='utf-8'))
        self.assertIn('pull_request', blocks)
        # Security checks must run for source changes outside known signatures,
        # e.g. a new untrusted workflow or hidden provider bootstrap script.
        for event in ('pull_request', 'push'):
            self.assertIn(event, blocks)
            for line in blocks[event]:
                self.assertNotIn(line.strip().split(':')[0], ('paths','paths-ignore'),
                    f'{event} security gate silently skips unrelated changed paths')
        self.assertTrue(any('branches: [main]' in line for line in blocks['push']))

if __name__ == '__main__':
    unittest.main()
