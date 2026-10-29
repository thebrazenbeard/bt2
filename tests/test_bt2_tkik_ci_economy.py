"""Keep the hosted T'Kal replay bounded and triggered by every T'Kal test."""

from pathlib import Path
import unittest


WORKFLOW = (Path(__file__).resolve().parents[1] /
            ".github/workflows/bt2-tkik-identity-qualification.yml")


class TkalCiEconomyTests(unittest.TestCase):
    def test_real_core_gate_stays_pinned_and_bounded(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("repository: thebrazenbeard/t-kal-in-ket", source)
        self.assertIn("ref: b0af150c2405b519fd921bac33e5f9f1f35f92d7", source)
        self.assertIn("TKIK_EXACT_REPO: ${{ github.workspace }}/external/t-kal-in-ket", source)
        self.assertIn("python -m unittest discover -s tests -q", source)
        self.assertIn("run_bt2_tkik_proceeding.py", source)
        self.assertIn("timeout-minutes: 10", source)
        self.assertEqual(source.count("fetch-depth: 1"), 2)
        self.assertNotIn("fetch-depth: 0", source)

    def test_new_tkal_provenance_tests_also_trigger_hosted_gate(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("- 'tests/test_bt2_tkik_*.py'", source)
        self.assertNotIn("- 'tests/test_bt2_tkik_proceeding.py'", source)


if __name__ == "__main__":
    unittest.main()
