# Module 02: Provenance, Currentness, and Evidence Classes

## Learning objective

Demonstrate the ability to reconstruct current truth from mixed evidence without allowing timestamps, chat confidence, or stale references to impersonate authority.

## Exercise prompt

Evaluate this synthetic evidence set:

- E1: the current authoritative governance singleton names a role holder set and a current role contract;
- E2: an older referenced event contains a different roster;
- E3: a Slack handoff from yesterday describes an older role allocation;
- E4: a Drive document has the newest modification timestamp but cites an older provider state;
- E5: a fresh live provider read contradicts E4;
- E6: a present direct user correction changes one narrow rule;
- E7: a prior assistant answer confidently says something else;
- E8: two current sources appear to conflict and their scope relationship is unclear.

For each item, classify it as one of:

`GOVERNING_CURRENT_RULE`, `CURRENT_VERIFIED_OBSERVATION`, `HISTORICAL_EVIDENCE`, `INFERENCE`, `CONFLICT_OR_UNKNOWN`, or `NONAUTHORITATIVE_GENERATED_TEXT`.

Then:

1. establish precedence without using “newest wins” as a blanket rule;
2. explain what must be re-read or cross-bound for E8;
3. show when provider currentness outranks a stale handoff and when it does not outrank governance;
4. write a short status report that labels facts, inferences, historical incidents, unresolved conflicts, and claim ceilings explicitly;
5. explain why numeric high-water IDs and timestamps are useful indexes but not universal completeness proofs.

## Pass criteria

PASS requires:

- source type and scope are used in precedence decisions;
- current governance and current provider observation are distinguished;
- generated text is never treated as self-authenticating authority;
- unresolved conflict fails closed rather than being guessed through;
- history is preserved without being promoted to current state;
- the status report makes claim ceilings explicit.

## Critical fail conditions

- “most recently modified” is used as a universal authority rule;
- prior assistant output is treated as evidence of current state;
- a historical event silently reactivates retired/superseded state;
- provider state is treated as permission rather than observation.
