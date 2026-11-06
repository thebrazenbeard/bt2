"""Bounded, one-shot BT2 -> Market Lab *synthetic-only* advisory wire.

This is not a trading protocol.  Neither this process nor its output carries
account credentials, signatures, market entitlements, order intents or authority.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from advisory_gate import SyntheticOpportunity, deterministic_gate


SCHEMA = "BT2_MARKET_LAB_ADVISORY_WIRE_V1"
MAX_REQUEST_BYTES = 4096
OPPORTUNITY_FIELDS = frozenset({
    "gross_move_bps", "buy_fee_bps", "sell_fee_bps", "spread_bps", "slippage_bps",
})
_DECIMAL = re.compile(r"[+-]?[0-9]{1,8}(?:\.[0-9]{1,8})?\Z")


class _InputRejected(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _InputRejected("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise _InputRejected("nonfinite JSON constant")


def _decode(raw: bytes) -> SyntheticOpportunity:
    if not isinstance(raw, bytes) or len(raw) > MAX_REQUEST_BYTES:
        raise _InputRejected("input boundary")
    try:
        envelope = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
        raise _InputRejected("invalid JSON") from exc
    if type(envelope) is not dict or set(envelope) != {"schema", "purpose", "opportunity"}:
        raise _InputRejected("invalid envelope fields")
    if envelope["schema"] != SCHEMA or envelope["purpose"] != "SYNTHETIC_TEST":
        raise _InputRejected("unsupported purpose or schema")
    fields = envelope["opportunity"]
    if type(fields) is not dict or set(fields) != OPPORTUNITY_FIELDS:
        raise _InputRejected("invalid opportunity fields")
    if any(type(v) is not str or not _DECIMAL.fullmatch(v) for v in fields.values()):
        raise _InputRejected("invalid bounded decimal")
    return SyntheticOpportunity(**fields)


def process_request(raw: bytes) -> dict[str, Any]:
    """Never echo input or let untrusted content supply trade authorization."""
    try:
        opportunity = _decode(raw)
        gate = deterministic_gate(opportunity)
    except (ValueError, TypeError, ArithmeticError):
        return {
            "schema": SCHEMA,
            "classification": "SYNTHETIC_INPUT_REJECTED",
            "status": "INPUT_REJECTED",
            "trade_authorized": False,
            "execution_capability": "NONE",
        }
    return {
        "schema": SCHEMA,
        "classification": "SYNTHETIC_RESEARCH_ONLY",
        "status": gate.status,
        "net_bps": str(gate.net_bps),
        "total_cost_bps": str(gate.total_cost_bps),
        "trade_authorized": False,
        "execution_capability": "NONE",
    }


def main() -> int:
    """Read at most 4097 stdin bytes; emit exactly one bounded JSON line."""
    response = process_request(sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1))
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
    return 0 if response["status"] != "INPUT_REJECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
