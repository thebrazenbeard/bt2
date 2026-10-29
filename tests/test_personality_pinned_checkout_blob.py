"""Source content checks must defeat Git's hidden dirty-index flags."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from train_personality_lora import checked_checkout  # noqa: E402


class PinnedCheckoutBlobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.repo / "labyrinth").mkdir()
        (self.repo / "cases").mkdir()
        (self.repo / "labyrinth/curriculum.py").write_text("PASS = True\n", encoding="utf-8")
        (self.repo / "cases/one.json").write_text('{"label":"safe"}\n', encoding="utf-8")
        self.git("add", "labyrinth/curriculum.py", "cases/one.json")
        self.git("commit", "-qm", "fixture")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              text=True, capture_output=True, check=True)

    def test_clean_exact_head_accepts_all_tracked_bytes(self):
        self.assertEqual(checked_checkout(self.repo, self.head, "labyrinth/curriculum.py"),
                         self.repo)

    def test_assume_unchanged_executable_bypass_fails_closed(self):
        self.git("update-index", "--assume-unchanged", "labyrinth/curriculum.py")
        (self.repo / "labyrinth/curriculum.py").write_text("PASS = False\n", encoding="utf-8")
        self.assertFalse(self.git("status", "--porcelain").stdout.strip())
        with self.assertRaisesRegex(ValueError, "working bytes differ from HEAD"):
            checked_checkout(self.repo, self.head, "labyrinth/curriculum.py")

    def test_skip_worktree_training_label_bypass_fails_closed(self):
        self.git("update-index", "--skip-worktree", "cases/one.json")
        (self.repo / "cases/one.json").write_text('{"label":"tampered"}\n', encoding="utf-8")
        self.assertFalse(self.git("status", "--porcelain").stdout.strip())
        with self.assertRaisesRegex(ValueError, "working bytes differ from HEAD"):
            checked_checkout(self.repo, self.head, "labyrinth/curriculum.py")


if __name__ == "__main__":
    unittest.main()
