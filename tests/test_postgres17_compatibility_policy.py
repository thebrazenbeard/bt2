import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_DIR = ROOT / "tools" / "qualification"
sys.path.insert(0, str(QUALIFICATION_DIR))
MODULE_PATH = QUALIFICATION_DIR / "run_postgres17_blank_rebuild_compatibility.py"
spec = importlib.util.spec_from_file_location("bt2_pg17_compat", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class PostgreSQL17CompatibilityPolicyTests(unittest.TestCase):
    def test_skip_set_is_exact_and_closed(self):
        observed = {
            path.name for path in module.COMPATIBILITY_SKIPPED_MIGRATIONS
        }
        self.assertEqual(
            observed,
            {
                "0012_internal_schema_access_assertion_v1.sql",
                "0018_lantern_producer_boundary_v1.sql",
            },
        )

    def test_forward_replacement_is_exact(self):
        self.assertEqual(
            module.COMPATIBILITY_REPLACEMENT_MIGRATION.name,
            "0024_postgresql_v4_provider_neutral_owner_boundary_v1.sql",
        )
        self.assertTrue(module.COMPATIBILITY_REPLACEMENT_MIGRATION.is_file())

    def test_replacement_orders_after_skips(self):
        replacement = module.COMPATIBILITY_REPLACEMENT_MIGRATION.name
        for skipped in module.COMPATIBILITY_SKIPPED_MIGRATIONS:
            self.assertLess(skipped.name, replacement)


if __name__ == "__main__":
    unittest.main()
