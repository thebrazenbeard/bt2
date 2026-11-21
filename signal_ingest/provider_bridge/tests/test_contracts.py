import json
import subprocess
import sys
import unittest
from pathlib import Path

from signal_ingest.provider_bridge.v1 import bridge
from signal_ingest.provider_bridge.semantic_exchange import exchange

ROOT=Path(__file__).resolve().parents[1]

class ContractAndCli(unittest.TestCase):
    def test_github_contract_fixture(self):
        contract=json.loads((ROOT/"CONTRACT_V1.json").read_text())
        data=json.loads((ROOT/"fixtures"/"synthetic_github_observation.json").read_text())
        result=bridge(data)
        self.assertEqual(result["schema"],contract["output_schema"])
        self.assertFalse(result["signal"]["release_permission"])

    def test_semantic_contract_fixture(self):
        contract=json.loads((ROOT/"SEMANTIC_CONTRACT_V1.json").read_text())
        data=json.loads((ROOT/"fixtures"/"synthetic_semantic_exchange.json").read_text())
        result=exchange(data)
        self.assertEqual(result["schema"],contract["output_schema"])
        self.assertEqual(result["truth"],"NOT_DETERMINED")
        self.assertEqual(result["consent"],"NOT_GRANTED")
        self.assertEqual(result["autobiographical_admission"],"NONE")

    def test_cli_repeatability_zero_effects(self):
        file=ROOT/"fixtures"/"synthetic_github_observation.json"
        argv=[sys.executable,"-m","signal_ingest.provider_bridge.v1",str(file)]
        r1=subprocess.run(argv,cwd=ROOT.parents[1],text=True,capture_output=True,check=True)
        r2=subprocess.run(argv,cwd=ROOT.parents[1],text=True,capture_output=True,check=True)
        self.assertEqual(r1.stdout,r2.stdout)
        output=json.loads(r1.stdout)
        self.assertEqual(output["side_effects"],[])
        self.assertEqual(output["source_authentication"],"UNVERIFIED_NO_SIGNED_RECEIPT")

    def test_replay_cache_not_independent(self):
        contract=json.loads((ROOT/"CONTRACT_V1.json").read_text())
        self.assertEqual(contract["output"]["replay_scope"],
                         "CALLER_PROVIDED_CACHE_NOT_INDEPENDENT")
        self.assertFalse(contract["output"]["release_permission"])
        self.assertEqual(contract["output"]["side_effects"],[])

    def test_three_versioned_semantic_heads(self):
        data=json.loads((ROOT/"fixtures"/"synthetic_semantic_exchange.json").read_text())
        s=data["source"]
        for key in ("head","vsns_head","empathy_head"):
            self.assertEqual(len(s[key]),40)
        self.assertIn("/blob/"+s["head"]+"/",s["source_ref"])
        self.assertIn("/blob/"+s["vsns_head"]+"/",s["vsns_ref"])
        self.assertIn("/blob/"+s["empathy_head"]+"/",s["empathy_ref"])

    def test_private_text_is_forbidden(self):
        contract=json.loads((ROOT/"SEMANTIC_CONTRACT_V1.json").read_text())
        self.assertEqual(contract["inputs"]["raw_utterances"],"FORBIDDEN")
        self.assertEqual(contract["inputs"]["private_person_ids"],"FORBIDDEN")
        self.assertEqual(contract["fixed_output_effects"]["memory_admission"],"NONE")

if __name__=="__main__":
    unittest.main()