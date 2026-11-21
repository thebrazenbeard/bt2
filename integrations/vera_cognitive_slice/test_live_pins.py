"""Offline regression tests for optional live pin freshness diagnostics."""
from __future__ import annotations

import unittest
from check_live_pins import EXPECTED, compare_heads


class LivePinFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pins = {name: "a" * 40 for name in EXPECTED}

    def test_all_current_when_exact_heads_match(self) -> None:
        rows = compare_heads(self.pins, lambda name: "a" * 40)
        self.assertEqual(set(rows), EXPECTED)
        self.assertTrue(all(row["matches"] for row in rows.values()))

    def test_single_changed_main_is_a_visible_noncurrent_result(self) -> None:
        name = sorted(EXPECTED)[0]
        rows = compare_heads(self.pins, lambda item: "b" * 40 if item == name else "a" * 40)
        self.assertFalse(rows[name]["matches"])
        self.assertEqual(sum(bool(row["matches"]) for row in rows.values()), len(EXPECTED) - 1)

    def test_missing_or_forged_repo_rejected_before_network(self) -> None:
        called = []
        def resolver(name: str) -> str:
            called.append(name)
            return "a" * 40
        malformed = dict(self.pins)
        malformed.pop(next(iter(malformed)))
        with self.assertRaises(ValueError):
            compare_heads(malformed, resolver)
        self.assertFalse(called)

    def test_invalid_pinned_or_remote_digest_is_not_silently_accepted(self) -> None:
        invalid = dict(self.pins)
        invalid[next(iter(invalid))] = "not-a-sha"
        with self.assertRaises(ValueError):
            compare_heads(invalid, lambda name: "a" * 40)
        with self.assertRaises(ValueError):
            compare_heads(self.pins, lambda name: "HEAD")


if __name__ == "__main__":
    unittest.main()
