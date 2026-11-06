# BT2 → Vera Market Lab synthetic advisory conformance

This is an isolated source test, **not** an installed BT2 role coordinator,
Rezon-authenticated delegate, trading strategy, exchange quote, or order path.

`advisory_gate.py` accepts only synthetic test-owned numbers, calculates exact
round-trip fee/spread/slippage costs, and refuses to authorize *any* trade.
Granite on VN2 may optionally supply an explicitly untrusted advisory note;
model text cannot affect the deterministic result.

Run: `python3 -m unittest discover -s integrations/vera_market_lab -p 'test_*.py'`

Example: 100 bp synthetic gross movement − 90 bp buy − 90 bp sell − 4 bp
spread − 3 bp slippage = −87 bp, `COST_REJECT`, `trade_authorized=False`.

BT2 source/runtime evidence: `thebrazenbeard/bt2@09a224105e26336df09e8787c1c99e9ea6298ffc`.
`BT2_COORDINATOR_RECONSTRUCTION_V2.md` says the V5 Project package is source
candidate and is not installed. The local Granite model is not a qualified
BT2 worker merely because it responds to a BT2-inspired instruction.
