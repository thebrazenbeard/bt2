"""One-shot synthetic VN2 advisory smoke; never connects to an exchange."""

import json

from advisory_gate import SyntheticOpportunity, deterministic_gate, granite_note


def main() -> None:
    opportunity = SyntheticOpportunity(
        gross_move_bps="100",
        buy_fee_bps="90",
        sell_fee_bps="90",
        spread_bps="4",
        slippage_bps="3",
    )
    result = deterministic_gate(opportunity)
    try:
        note = granite_note("http://127.0.0.1:11435", opportunity, timeout=10.0)
        model_status = "LIVE_LOCAL_INFERENCE"
    except Exception as exc:
        note = f"unavailable: {type(exc).__name__}"
        model_status = "ADVISORY_UNAVAILABLE"
    print(json.dumps({
        "scenario": "SYNTHETIC_TEST",
        "model_status": model_status,
        "untrusted_model_note": note,
        "deterministic_cost_bps": str(result.total_cost_bps),
        "deterministic_net_bps": str(result.net_bps),
        "deterministic_gate": result.status,
        "trade_authorized": result.trade_authorized,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
