# BT2 Chat Exodus Architecture Audit — 2026-09-19

Status: `SOURCE_AUDIT / DECHATIFICATION_IN_PROGRESS`

This audit records only durable engineering/coordination state. It intentionally excludes
Patrick's personal, health, family, relational, sexual, credential, secret, and other
private conversational material.

## Scope

This audit covers the Build Team Two portfolio and the workers materially represented
by the retiring BT2 portfolio-runner conversation.

Primary durable systems:

- `thebrazenbeard/bt2`
- `thebrazenbeard/chat-communication-bus`
- source repositories named by active portfolio PRs
- WoWSQL project `bt2-479e4ad9` only when live access is available

## Classification

### ALREADY_DURABLE

- BT2 fresh-session recovery order:
  `native/project/BT2_RECOVERY_AND_STATE_V1.md`.
- Versioned worker training/role source for One, Two, Three, Four, Five, Six, Eight,
  Nine, Thirteen, Hephaestus, Masa, Mune, and historical Seven material.
- Bus protocol, recovery namespace, assignment/envelope/protocol contracts.
- Radar source/operator recovery material in `thebrazenbeard/chat-communication-bus`.
- Project-specific source, PRs, reviews, tests, and qualification artifacts.
- Non-PR coordination convention through the Chat Communication Bus.

### NEW_DURABLE_VALUE

Added by the Exodus branch:

- `native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json`
- `native/project/BT2_COORDINATOR_RECONSTRUCTION_V1.md`

These make the post-Exodus interface/worker distinction explicit and source-controlled.

### SUPERSEDES_EXISTING

The following operational assumption is superseded:

> A durable worker requires its own permanent ChatGPT conversation.

Post-Exodus, worker identity and operational state must be reconstructible from Git,
Bus, current provider evidence, and exact checkpoints. Temporary execution contexts are
terminals only.

Legacy restore prose that says to open a particular worker chat is historical
provenance, not current routing authority.

### HISTORICAL_EVIDENCE

The Bus file `docs/checkpoints/RADAR_RESTORE_2026-09-05.md` contains a historical
"fresh Radar chat" restore pattern. It remains preserved because it documents the
September 5 audit state and failed/live-provider context.

Its chat-routing instructions are not current operational requirements.

### CHAT_DEPENDENCY

One concrete legacy dependency was found:

- the historical Radar restore checkpoint describes a named persistent Radar chat as
  the recovery surface.

Closure:

- preserve the old checkpoint unchanged;
- current Bus operator recovery is being updated to runtime-neutral language;
- the BT2 Coordinator reconstruction contract defines Radar/Parallax/other workers as
  ephemeral execution contexts reconstructed from durable state.

Repository-wide GitHub code search found no current `chatgpt.com` dependency in
`thebrazenbeard/bt2` or `thebrazenbeard/chat-communication-bus` source.

### WORKER_RECONSTRUCTION_GAP

Before this branch, there was no single current BT2 source contract that bound:

- the exact three persistent human interfaces;
- One/Two as durable roles rather than chats;
- Bus checkpoint recovery;
- no-chat reconstruction and authority rules.

That gap is closed at source level by this branch.

Mutable current assignment still belongs in Bus/checkpoint state and must not be frozen
into permanent role training.

### CONFLICT

No source conflict was found between the new Exodus topology and the existing BT2
recovery doctrine. Existing training already separates frozen role competence,
operational state, provider currentness, and conversational continuity.

## Architecture findings from the shutdown exercise

1. Chat-local portfolio continuity was too convenient: the operational state was
   durable in many individual PRs/messages, but the coordinating cut was easier to
   recover from the conversation than from one checkpoint.
2. The Bus already had the correct checkpoint namespace, but the portfolio runner had
   historically persisted many checkpoints under `messages/`. Those files remain
   historical; new Exodus recovery state should use `checkpoints/<identity>/`.
3. Independent worker identity must remain distinct after chat retirement. In
   particular, Two's Systems Architect review must not collapse into One/BT2
   Coordinator merely because both can be instantiated by the same interface.
4. A source role plus tool access is not current authority. Fresh provider/branch
   currentness and protected-effect authorization remain separate.
5. Provider outage must remain visible as UNKNOWN rather than reconstructed from old
   chats. Current WoWSQL/Lantern access is an example.

## Functional reconstruction target

After this conversation is inaccessible, `BT2 Coordinator` must be able to:

1. read the current BT2 source contract;
2. read the current Bus recovery checkpoint for the portfolio;
3. fresh-read the named source PRs/heads/reviews/workflows;
4. instantiate One, Two, Radar, Parallax, or a project worker ephemerally;
5. continue safe work without finding an old ChatGPT URL;
6. stop at the same protected-effect gates Patrick would have seen here.

The Exodus is not complete until the current portfolio cut is persisted in the Bus
checkpoint namespace and the Bus operator recovery docs are runtime-neutral.
