# Three: implementation-first source challenge, 2026-10-29

Status: **SOURCE-LEVEL REPAIR ONLY**. No Three GGUF was loaded, trained, or
evaluated. This is not a held-out inference score.

## Source and external challenge custody

- Original ten-facet source: archived `thebrazenbeard/build-team-2.0` README,
  live read 2026-10-29. Three is concrete, energetic, implementation-first.
- External inquiry: `thebrazenbeard/t-kal-in-ket/docs/PROTOCOL.md`, Git blob
  `eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff`. Its Pragmatism lens
  challenges implementation, controls, data quality, and feasibility.
- No code copied from T'Kal-in-ket; its README declares no software license.
  This is inquiry inspiration, not an independent model invocation or quorum.

## Falsifiers and repairs

1. **Duplicate save — FAILED prior source gate.** Three's original answer
   proposed React `isSaving` state but no synchronous reentry guard. State
   remains a render snapshot before re-render; a same-tick second invocation
   may observe stale state. The revised answer uses `useRef` before awaiting
   and releases in `finally`; UI guard and server idempotency are distinct.
   Official references: [React state snapshot](https://react.dev/learn/state-as-a-snapshot)
   and [useRef](https://react.dev/reference/react/useRef).
2. **Malformed parser — FAILED prior source gate.** The original answer
   described a fix but supplied no concrete Python. The revised case specifies
   a bounded comma-separated integer contract, parseable implementation,
   valid-empty and valid-data checks, and a `ValueError` negative witness.

Both preserve 8 TRAIN / 2 public DEV. Tests inspect authored training source
and parse syntax, but deliberately do not execute model-generated code.

## Verification

- Red before repair: 2/2 focused tests failed.
- Green after repair: 2/2 focused tests passed.
- `python -m unittest discover -s tests -q`: 124/124 passed.
- `python tools/validate_personality_sft.py`: 13 dossiers / 130 cases valid.
- `git diff --check`: passed.

## Evidence ceiling

The corpus more explicitly specifies competent Three behavior. Learned
personality, live React behavior, and coding retention remain **UNKNOWN**
until independent runtime tests and reserved GGUF inference.
