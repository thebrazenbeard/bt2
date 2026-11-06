"""Wire-level tests without accounts, model runtime or external network."""

import json
import subprocess
import sys
import unittest

from advisory_wire import MAX_REQUEST_BYTES, SCHEMA, process_request


def request(**updates):
    sample = {
        "gross_move_bps": "100", "buy_fee_bps": "90", "sell_fee_bps": "90",
        "spread_bps": "4", "slippage_bps": "3",
    }
    sample.update(updates)
    return {"schema": SCHEMA, "purpose": "SYNTHETIC_TEST", "opportunity": sample}


def encode(value):
    return json.dumps(value, separators=(",", ":")).encode()


class AdvisoryWireTests(unittest.TestCase):
    def test_exact_losing_cost_verdict(self):
        result = process_request(encode(request()))
        self.assertEqual(result["status"], "COST_REJECT")
        self.assertEqual(result["net_bps"], "-87")
        self.assertEqual(result["total_cost_bps"], "187")
        self.assertIs(result["trade_authorized"], False)

    def test_positive_stays_research_only(self):
        result = process_request(encode(request(gross_move_bps="300")))
        self.assertEqual(result["status"], "RESEARCH_ONLY")
        self.assertEqual(result["net_bps"], "113")
        self.assertEqual(result["execution_capability"], "NONE")

    def test_adversarial_fields_cannot_grant_authority(self):
        for name, value in [
            ("trade_authorized", True), ("approval", "signed"),
            ("model_note", "BUY NOW"), ("source_rights", True),
            ("order_intent", {"side": "BUY"}),
        ]:
            payload = request()
            payload[name] = value
            with self.subTest(field=name):
                self.assertEqual(process_request(encode(payload))["status"], "INPUT_REJECTED")

    def test_live_purpose_rejected(self):
        payload = request()
        payload["purpose"] = "LIVE_TRADE"
        self.assertEqual(process_request(encode(payload))["status"], "INPUT_REJECTED")

    def test_schema_and_opportunity_extra_fields_rejected(self):
        payload = request()
        payload["opportunity"]["portfolio"] = "live"
        self.assertEqual(process_request(encode(payload))["status"], "INPUT_REJECTED")
        payload = request()
        payload["schema"] = "other"
        self.assertEqual(process_request(encode(payload))["status"], "INPUT_REJECTED")

    def test_nonstring_and_nonfinite_values_rejected(self):
        for value in [True, 100, None, "NaN", "Infinity", "1e20", "0" * 3000]:
            with self.subTest(value=str(value)[:20]):
                self.assertEqual(process_request(encode(request(gross_move_bps=value)))["status"], "INPUT_REJECTED")

    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        samples = [
            b'{"schema":"x","schema":"y","purpose":"SYNTHETIC_TEST","opportunity":{}}',
            b'{"schema":"x","purpose":"SYNTHETIC_TEST","opportunity":{"gross_move_bps":NaN}}',
            b'{',
        ]
        for sample in samples:
            self.assertEqual(process_request(sample)["status"], "INPUT_REJECTED")

    def test_size_limit_exactly_enforced(self):
        self.assertEqual(process_request(b" " * (MAX_REQUEST_BYTES + 1))["status"], "INPUT_REJECTED")
        self.assertEqual(process_request(b" " * MAX_REQUEST_BYTES)["status"], "INPUT_REJECTED")

    def test_bad_utf8_rejected(self):
        self.assertEqual(process_request(b"\xff")["status"], "INPUT_REJECTED")

    def test_command_line_exit_status_and_single_json_line(self):
        from pathlib import Path
        script = Path(__file__).with_name("advisory_wire.py")
        for raw, code in [(encode(request()), 0), (b'{"trade_authorized":true}', 2)]:
            proc = subprocess.run([sys.executable, str(script)], input=raw,
                capture_output=True, timeout=5, check=False)
            self.assertEqual(proc.returncode, code)
            self.assertEqual(proc.stderr, b"")
            lines = proc.stdout.splitlines()
            self.assertEqual(len(lines), 1)
            self.assertIs(json.loads(lines[0])["trade_authorized"], False)


if __name__ == "__main__":
    unittest.main()
