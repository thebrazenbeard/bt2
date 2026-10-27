"""SQLite-owned issuance for MESO immutable event identities."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = os.environ.get("BT2_VERA_COGNITIVE_REPOS")

class DurableMesoTests(unittest.TestCase):
    def test_concurrent_issuer_and_restart_do_not_repeat_id(self):
        self.assertTrue(ROOT, "BT2_VERA_COGNITIVE_REPOS must be set")
        sys.dont_write_bytecode = True
        sys.path.insert(0,str(Path(ROOT)/"meso-crct"/"src"))
        from durable_meso import DurableEventIssuer
        with TemporaryDirectory(prefix="bt2-meso-issuer-") as temp:
            ledger = Path(temp)/"meso.db"
            issuer=DurableEventIssuer(ledger)
            with ThreadPoolExecutor(max_workers=8) as pool:
                events=list(pool.map(lambda _:issuer.issue("fixture-stream"),range(20)))
            self.assertEqual({event.sequence for event in events},set(range(1,21)))
            self.assertEqual(len({event.event_id for event in events}),20)
            restarted=DurableEventIssuer(ledger)
            later=restarted.issue("fixture-stream")
            self.assertEqual(later.sequence,21)
            self.assertNotIn(later.event_id,{item.event_id for item in events})
            with self.assertRaises(ValueError):
                restarted.issue("")
            self.assertEqual(restarted.issue("fixture-stream").sequence,22)

if __name__ == "__main__":
    unittest.main()
