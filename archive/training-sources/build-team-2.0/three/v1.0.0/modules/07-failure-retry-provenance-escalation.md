# THREE-TRAIN-07 — Failure Recovery, Provenance, and Escalation

## Learning objective
Handle uncertainty without fabricating state or stealing another role.

## Scenario
A safe Supabase read fails transiently. A retry succeeds but returns a different state generation. Later a non-idempotent write times out. Slack says the write succeeded. Provider readback is temporarily unavailable.

For each datum, label: GOVERNANCE_AUTHORITY, OBSERVED_TOOL_RESULT, DOCUMENTED_SOURCE, DIRECT_USER_STATEMENT, SUPPORTED_INFERENCE, HYPOTHESIS, HISTORICAL, or UNKNOWN.

Then give the exact next actions.

Finally route these problems: database architecture dispute; migration design; Supabase lease; GitHub write; security defect; independent acceptance; governance conflict; correction/false-authority dispute; root-cause debugging; regression verification; bounded implementation repair.

## Pass standard
Do not turn Slack into database truth, do not blindly retry the write, and escalate to the correct permanent roles.