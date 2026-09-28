# ChatGPT Exodus — Rezon / Project Runner BT2 Receipt

status: `STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT`

## Primary checkpoint

- repo: `thebrazenbeard/bt2`
- branch: `state/chatgpt-exodus-rezon-projectrunner-20260919`
- checkpoint path: `docs/handoffs/CHATGPT_EXODUS_REZON_PROJECT_RUNNER_2026-09-19.md`
- checkpoint commit: `47743adec96d14bf2b32d6d9774bbaee94d4c284`
- checkpoint Git blob: `93090c63162a9cc5a76e8be967ecd8ff349af05f`
- checkpoint SHA-256: `8d23e7cd033d4fb9bdc2df7a51a18f301c03089bbcb15bd1b2a6ab1ca65a84c3`
- Draft PR: `#25`

## Bus recovery handoff

- repo: `thebrazenbeard/chat-communication-bus`
- branch: `bus/one-v2`
- path: `messages/20260919T1924-one-chatgpt-exodus-final-recovery.md`
- commit: `5ee550d49e38f79e1cad7483f5359233570dcddc`
- Git blob: `255d962900d414a85370d94f8a5c5c6303e75b3c`
- SHA-256: `307adb28441e60a192aa95165c3c3a37b1c3b0d038ad87ae6a04e28176d9e26d`

## Exact live subjects at final readback

- Rezon R51 PR #76: `3b9a0f36e0f1d1c60c7b3f79da6915f0b213476b`, draft/open/mergeable; independent hostile rereview pending.
- Project Runner PR #10: `da05cc6e9dd171e2098ef30f1959957109d088e3`, draft/open/mergeable.
- Project Runner PR #11: `edebeecdbfba08e92cb4153162575f6549cd8f7a`, draft/open/mergeable.
- Bus Exodus PR #131: `7aae3ae165a153bb391d2ad4570a3b7d872ef99a`, draft/open/mergeable.

## Reconstruction test

PASS at source/coordination scope.

A fresh runtime using only current BT2 Project instructions, GitHub repositories, Bus state, this checkpoint/receipt, and authorized provider reads can determine:
- project/worker identity and role;
- current exact source frontiers;
- completed source/build/test evidence;
- failed predecessors and reasons;
- unresolved hostile-review gates;
- authority and protected-effect limits;
- durable communication routes;
- exact safe next directive.

No access to the retiring conversation is required.

## Runtime-currentness limitation

`LANTERN_CURRENTNESS = UNKNOWN_FROM_THIS_TERMINAL` because exact WoWSQL target `bt2-479e4ad9` could not be read due connector failure. No fallback was used.

## Next interface and directive

Interface: `BT2 Coordinator`

`BT2::EXODUS_CONTINUE::FRESH_CHECK_R51_PR76_AND_PROJECT_RUNNER_PR10_PR11_AND_BUS_PR131`

No merge/deploy/install/provider/credential/Slack/training/protected effect is authorized by this receipt.
