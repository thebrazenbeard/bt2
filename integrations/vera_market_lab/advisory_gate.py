"""Source-only BT2/Market Lab advisory conformance, never an order executor.

This module deliberately has no exchange credentials, order endpoints, or
permission to promote a model response to an executable trading decision.
Only synthetic, test-owned scenarios are accepted by the demo runner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import json
import math
from typing import Literal
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


MAX_BPS = Decimal("100000")
MAX_MODEL_RESPONSE_BYTES = 16384
MAX_ADVISORY_TIMEOUT_SECONDS = 10.0


class _RejectRedirect(HTTPRedirectHandler):
    """Disable redirects even if the local model service is compromised."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _open_loopback(request: Request, timeout: float):
    # Explicit empty proxy map avoids inheriting HTTP_PROXY for loopback.
    return build_opener(ProxyHandler({}), _RejectRedirect()).open(request, timeout=timeout)


def _bps(value: object) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a basis-point value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid basis-point value") from exc
    if not result.is_finite() or abs(result) > MAX_BPS:
        raise ValueError("nonfinite or implausible basis-point value")
    return result


@dataclass(frozen=True)
class SyntheticOpportunity:
    gross_move_bps: str
    buy_fee_bps: str
    sell_fee_bps: str
    spread_bps: str
    slippage_bps: str
    purpose: Literal["SYNTHETIC_TEST"] = "SYNTHETIC_TEST"


@dataclass(frozen=True, slots=True)
class GateResult:
    status: Literal["COST_REJECT", "RESEARCH_ONLY"]
    net_bps: Decimal
    total_cost_bps: Decimal
    # Authorization must not be an init argument: Literal is only a type hint.
    trade_authorized: Literal[False] = field(default=False, init=False)


def deterministic_gate(opportunity: SyntheticOpportunity) -> GateResult:
    """Return an exact synthetic-cost verdict independent of any model text."""
    if opportunity.purpose != "SYNTHETIC_TEST":
        raise ValueError("only synthetic scenarios are accepted")
    gross = _bps(opportunity.gross_move_bps)
    costs = (
        _bps(opportunity.buy_fee_bps)
        + _bps(opportunity.sell_fee_bps)
        + _bps(opportunity.spread_bps)
        + _bps(opportunity.slippage_bps)
    )
    if min(
        _bps(opportunity.buy_fee_bps),
        _bps(opportunity.sell_fee_bps),
        _bps(opportunity.spread_bps),
        _bps(opportunity.slippage_bps),
    ) < 0:
        raise ValueError("costs cannot be negative")
    net = gross - costs
    return GateResult(
        status="COST_REJECT" if net <= 0 else "RESEARCH_ONLY",
        net_bps=net,
        total_cost_bps=costs,
    )


def granite_note(base_url: str, opportunity: SyntheticOpportunity, timeout: float = 8.0) -> str:
    """Obtain an untrusted VN2 llama.cpp note; never feed it into the gate.

    Only loopback is supported. Failure is a bounded advisory miss, not a gate
    error, and this deliberately has no retries or background activity.
    """
    if base_url != "http://127.0.0.1:11435":
        raise ValueError("only the explicitly observed numeric loopback model is supported")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(float(timeout))
        or not 0.5 <= float(timeout) <= MAX_ADVISORY_TIMEOUT_SECONDS
    ):
        raise ValueError("advisory timeout must be finite and between 0.5 and 10 seconds")
    deterministic_gate(opportunity)  # Validate synthetic purpose and values before model I/O.
    payload = json.dumps({
        "messages": [
            {"role": "system", "content": "Discuss a synthetic trading example in one sentence. Advisory only; no orders."},
            {"role": "user", "content": (
                f"Synthetic gross move {opportunity.gross_move_bps} bps, "
                f"buy fee {opportunity.buy_fee_bps} bps, sell fee "
                f"{opportunity.sell_fee_bps} bps, spread "
                f"{opportunity.spread_bps} bps, slippage "
                f"{opportunity.slippage_bps} bps. Is net positive?"
            )},
        ],
        "temperature": 0,
        "max_tokens": 64,
        "stream": False,
    }).encode("utf-8")
    request = Request(
        base_url + "/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _open_loopback(request, timeout=float(timeout)) as response:
        if response.status != 200:
            raise RuntimeError("model request did not succeed")
        raw = response.read(MAX_MODEL_RESPONSE_BYTES + 1)
        if len(raw) > MAX_MODEL_RESPONSE_BYTES:
            raise RuntimeError("model response exceeds isolated advisory budget")
        result = json.loads(raw)
    return str(result["choices"][0]["message"]["content"])[:500]

