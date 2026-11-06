# Vera cognitive vertical-slice qualification

This is a source-bound, no-model-tool, synthetic host integration test.
It is NOT a Vera Mono selected runtime, active deployment, trained neural
model, emotional competence measure, or proof of independent semantic accuracy.

## Source and Lappy reproducibility

source_pins.json specifies eight exact commits. Checkouts must be at those
heads, unmodified, or the runner fails closed before imports. Pins are a frozen
reproducibility boundary, not proof that GitHub main still matches. Before a
fresh-current qualification, run the optional read-only check:

    python integrations/vera_cognitive_slice/check_live_pins.py

A nonzero exit means at least one source main moved or the check failed; review
the upstream changes and deliberately refresh exact pins before requalifying.
A successful check is a time-of-check observation across eight separate GitHub
requests, **not an atomic cross-repository snapshot**. Source main could move
immediately afterward; the executed qualification remains bound to exact
immutable SHA pins, not to the claim that every upstream main stayed still.
Never auto-update pins as part of the qualification itself. To create an
isolated checkout set on Lappy:

    python integrations/vera_cognitive_slice/prepare_sources.py --out C:\Temp\bt2-cognitive-source-new

The source preparer explicitly disables `core.autocrlf` in each checkout,
including on Lappy. Manual Windows clones made with Git's global
`core.autocrlf=true` can pass `git status` yet FAIL the raw-worktree-byte guard:
line-ending conversion changes bytes without changing normalized Git blob IDs.
Use `prepare_sources.py`, or explicitly clone with
`git -c core.autocrlf=false clone ...` into a fresh isolated directory.
Do not disable the raw-byte guard or reinterpret its failure as a runtime pass.

Then set BT2_VERA_COGNITIVE_REPOS to that folder and execute:

    python -m unittest discover -s integrations/vera_cognitive_slice -p test_qualify.py -v

The run uses an ephemeral SQLite Store and a deterministic no-tool model
adapter. It exercises actual VolitionBridge, Store and Engine, including
persistence, restart, duplicate evidence admission, rejection of a future-revision completion receipt, host-observed completion,
and idempotent replay. This does not simulate an older receipt after a real goal
revision; that separate future behavior still requires qualification.

Semiotics, Semantic Atlas, Humility, Meta, MESO-CRCT and Personification
are called through their exact source APIs on explicitly synthetic inputs.
A Meta toy score is not validation of real-world learning or independent
label custody. An immutable MESO EventSequencer requires its owner to
persist the successor and serialize issuance; the fixture tests only
successor issuance, not distributed concurrency.

The host, not the model, edits the fixture to demonstrate **host-verified
fixture completion**. A false model claim cannot close a goal. The host
requires exact expected bytes and a change from the observed baseline before
issuing a fixture completion receipt; the test rejects the unchanged case.
This remains a host-created verifier allowlist, **not independent third-party
verification** of a real repair. No model tools or effect authority are granted.

The current source pins include the Semantic Atlas manifest-aware generation
reader and Personification's bounded source admission. The fixture materializes
Atlas objects and verifies both JSON and SQLite from one committed generation,
including a tamper-rejection negative control. It also checks module origins
against the pinned repositories and rejects preloaded substituted modules.
Python optimized mode is refused (assertions must remain active). Bytecode
writing is disabled so repeated source checks do not dirty their worktrees.

Those source checks provide path/commit consistency, not cryptographic trust
in the manifest provider, and do not immunize a mutable filesystem against
all race conditions or malicious checkout content.
The check does not write or install anything into D:\VERA.

## Optional model-agnostic evidence proposal

`cognitive_advisory.propose(repos, AdvisoryRequest(...))` is a callable,
read-only boundary that executes the **actual pinned Humility** likelihood
revision method on caller-supplied `EvidenceSignal` records. It authenticates
all eight worktree source snapshots (including tracked JSON and Markdown),
rejects repeated evidence identities and dependence groups, and returns an
immutable, serializable advisory with source pins. This API invokes Humility
only; verifying the other seven source snapshots does not mean that all eight
contributed to the resulting posterior. Meta's current parity-task method
chooser has no justified general conversational interpretation and is not
silently used as a dialogue policy.

The returned posterior is *conditional mathematics over unverified likelihoods*.
It is not an independently measured calibration, truth determination, memory
admission, model identity, tool permission, or effect authority. The API never
calls a model or writes a ledger. Callers must govern source, privacy and
external label custody separately. The qualification uses synthetic inputs;
production conversational improvement is unproven.

Production activation, real model behavior, cross-host state persistence,
source authentication, and rollout to VN1/VN2 remain separate qualification
gates. Re-run with new exact source pins when a participating main changes.

The BT2-only DurableEventIssuer uses SQLite BEGIN IMMEDIATE to serialize
local MESO event issuance across transactions and survive host restarts.
It does not replace the immutable MESO core or qualify network/SMB locking.


## Hostile review qualification boundaries

A source-bound hosted run rejects Python optimization, preloaded cognitive
modules, source HEAD drift, modified tracked Git blobs (code and data),
unexpected untracked Python files, Python bytecode, and a nonempty or directly
linked state directory.
The trusted runner/Git executable and operating-system path ancestry are part
of the host trust boundary; these checks do not authenticate a malicious
operator who replaces Git or the source while it is executing.

The synthetic model response deliberately claims that the file was repaired
even though it never wrote it. The want remains active until the fixture host
changes the file and supplies a separately admitted completion. This tests
claim-vs-state separation, NOT independently authenticated verifier custody.
The test checks a FUTURE revision mismatch, not an old revision after a real
goal revision. No real model serving, protected tool execution or production
routing is qualified.

Durable MESO SQLite issuance serializes cooperating local writers using
BEGIN IMMEDIATE. Ambiguous responses after a successful commit may consume
a sequence without giving the caller its event; this is not request-keyed
exactly-once retry or a distributed database contract.
