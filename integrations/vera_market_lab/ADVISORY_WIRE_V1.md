# BT2 / Market Lab synthetic wire V1

`advisory_wire.py` is a one-shot standard-library JSON-lines adapter for
**synthetic test values only**. It accepts no exchange account, quote, model
opinion, rights attestation, order, approval, or credential fields.

Run using an isolated BT2 source checkout:

```sh
printf '%s' '{"schema":"BT2_MARKET_LAB_ADVISORY_WIRE_V1","purpose":"SYNTHETIC_TEST","opportunity":{"gross_move_bps":"100","buy_fee_bps":"90","sell_fee_bps":"90","spread_bps":"4","slippage_bps":"3"}}' | python3 integrations/vera_market_lab/advisory_wire.py
```

Reads no more than 4097 bytes from stdin, accepts at most a 4096-byte UTF-8
request, rejects duplicate keys, unknown fields, non-decimal numeric values,
and non-synthetic purpose. Emits exactly one JSON line. Rejected input exits 2
and returns `INPUT_REJECTED` without echoing supplied data; a valid synthetic
case exits 0 and reports exact basis-point arithmetic. All results explicitly
contain `trade_authorized:false` and `execution_capability:"NONE"`.

This is a candidate interop fixture, not an installed connection to Market Lab,
BT2 coordinator, Rezon, Coinbase, or a model. Internal checksum/shape or
synthetic arithmetic never establishes market rights, venue depth, cost basis,
profitability or permission to execute. Treat any future consumer that promotes
this advisory into financial authorization as a contract violation.

Tests: `python3 -B -m unittest discover -s integrations/vera_market_lab -p 'test_*.py' -v`.
