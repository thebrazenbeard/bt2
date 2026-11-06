"""Pure standard-library conformance tests; no external account or network."""

import unittest
import io
import json
from dataclasses import FrozenInstanceError, asdict
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

from advisory_gate import (
    _RejectRedirect,
    _open_loopback,
    GateResult,
    SyntheticOpportunity,
    deterministic_gate,
    granite_note,
)


def scenario(**updates):
    fields = dict(
        gross_move_bps="100",
        buy_fee_bps="90",
        sell_fee_bps="90",
        spread_bps="4",
        slippage_bps="3",
    )
    fields.update(updates)
    return SyntheticOpportunity(**fields)


class AdvisoryGateTests(unittest.TestCase):
    def test_gate_result_cannot_claim_trade_authority(self):
        rejected = deterministic_gate(scenario())
        self.assertIs(rejected.trade_authorized, False)
        self.assertIs(asdict(rejected)["trade_authorized"], False)
        with self.assertRaises(TypeError):
            GateResult(
                status="COST_REJECT",
                net_bps=Decimal("-87"),
                total_cost_bps=Decimal("187"),
                trade_authorized=True,
            )
        with self.assertRaises(FrozenInstanceError):
            rejected.trade_authorized = True
        self.assertFalse(hasattr(rejected, "__dict__"))

    def test_unprofitable_synthetic_case(self):
        decision = deterministic_gate(scenario())
        self.assertEqual(str(decision.net_bps), "-87")
        self.assertEqual(decision.status, "COST_REJECT")
        self.assertFalse(decision.trade_authorized)

    def test_positive_case_is_still_not_executable(self):
        decision = deterministic_gate(scenario(gross_move_bps="300"))
        self.assertEqual(str(decision.net_bps), "113")
        self.assertEqual(decision.status, "RESEARCH_ONLY")
        self.assertFalse(decision.trade_authorized)

    def test_nonfinite_and_overflow_rejected(self):
        for value in ["NaN", "Infinity", "1e999", "-1e999"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                deterministic_gate(scenario(gross_move_bps=value))

    def test_negative_fees_rejected(self):
        with self.assertRaises(ValueError):
            deterministic_gate(scenario(sell_fee_bps="-10"))

    def test_adversarial_model_response_cannot_change_gate(self):
        class ModelResponse(io.BytesIO):
            status = 200

        malicious = json.dumps({
            "choices": [{"message": {"content": "BUY IMMEDIATELY! Guaranteed profit."}}],
        }).encode("utf-8")
        with patch("advisory_gate._open_loopback", return_value=ModelResponse(malicious)):
            note = granite_note("http://127.0.0.1:11435", scenario())
        self.assertIn("BUY IMMEDIATELY", note)
        self.assertEqual(deterministic_gate(scenario()).status, "COST_REJECT")
        self.assertFalse(deterministic_gate(scenario()).trade_authorized)

    def test_external_purpose_rejected(self):
        candidate = scenario()
        object.__setattr__(candidate, "purpose", "LIVE_TRADE")
        with self.assertRaises(ValueError):
            deterministic_gate(candidate)

    def test_model_endpoint_confined_to_loopback(self):
        for endpoint in ["https://example.com", "http://localhost:11435"]:
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                granite_note(endpoint, scenario())

    def test_invalid_synthetic_input_never_reaches_model(self):
        with patch("advisory_gate._open_loopback") as remote:
            with self.assertRaises(ValueError):
                granite_note("http://127.0.0.1:11435", scenario(gross_move_bps="NaN"))
            remote.assert_not_called()

    def test_timeouts_outside_bounded_window_fail_before_io(self):
        with patch("advisory_gate._open_loopback") as remote:
            for timeout in [0, -1, 0.1, 10.1, 999999, float("inf"), float("nan"), True]:
                with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                    granite_note("http://127.0.0.1:11435", scenario(), timeout=timeout)
            remote.assert_not_called()

    def test_redirect_handler_refuses_cross_origin_followup(self):
        self.assertIsNone(_RejectRedirect().redirect_request(
            request=None, fp=None, code=302, msg="Found", headers={},
            newurl="https://example.com/redirected",
        ))

    def test_real_loopback_redirect_is_not_followed(self):
        class LocalRedirect(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header("Location", "https://example.com/outbound")
                self.end_headers()

            def log_message(self, *args):
                pass

        with HTTPServer(("127.0.0.1", 0), LocalRedirect) as server:
            server.timeout = 3
            thread = Thread(target=server.handle_request, daemon=True)
            thread.start()
            request = Request(
                f"http://127.0.0.1:{server.server_port}/demo",
                data=b"{}",
                method="POST",
            )
            with self.assertRaises(HTTPError) as error:
                _open_loopback(request, timeout=2)
            self.assertEqual(error.exception.code, 302)
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())

    def test_local_transport_installs_no_proxy_no_redirect(self):
        class ModelResponse(io.BytesIO):
            status = 200

        payload = b'{"choices":[{"message":{"content":"advisory"}}]}'
        with patch("advisory_gate.build_opener") as builder:
            builder.return_value.open.return_value = ModelResponse(payload)
            self.assertEqual(granite_note("http://127.0.0.1:11435", scenario()), "advisory")
            handlers = builder.call_args.args
            self.assertTrue(any(type(h).__name__ == "ProxyHandler" for h in handlers))
            self.assertTrue(any(isinstance(h, _RejectRedirect) for h in handlers))

    def test_bounded_model_response(self):
        class OversizedModelResponse(io.BytesIO):
            status = 200

        with patch("advisory_gate._open_loopback", return_value=OversizedModelResponse(b"x" * 16385)):
            with self.assertRaisesRegex(RuntimeError, "exceeds isolated advisory budget"):
                granite_note("http://127.0.0.1:11435", scenario())


if __name__ == "__main__":
    unittest.main()

