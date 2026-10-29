"""Fail-closed batch input bounds without model loading or external writes."""

from pathlib import Path
import sys
from types import SimpleNamespace
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_personality_gguf_batch import inputs  # noqa: E402


class PersonaBatchBoundsTests(unittest.TestCase):
    def args(self, **changes):
        source = dict(threads=2, steps=4, max_length=2048, min_free_gib=20,
                      identities=["one", "two"])
        source.update(changes)
        return SimpleNamespace(**source)

    def test_rejects_duplicate_and_unknown_roles_before_disk_io(self):
        for names in ([], ["one", "one"], ["ten"], ["one", "heph"]):
            with self.subTest(names=names), self.assertRaises(ValueError):
                inputs(self.args(identities=names))

    def test_rejects_unbounded_training_before_disk_io(self):
        for overrides in ({"steps": 120}, {"steps": 3}, {"max_length": 4096},
                          {"threads": 0}, {"min_free_gib": 0}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                inputs(self.args(**overrides))


if __name__ == "__main__":
    unittest.main()
