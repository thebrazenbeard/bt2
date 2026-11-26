# Engineer B — ecosystem signal ingestion V1 (source-only)

**State:** isolated, uninstalled, offline prototype. This package belongs to Engineer B's evidence/signal input lane. **BT2 retains the insight/decision policy.** There is no daemon, workflow, provider client, GitHub writer, notifier, or host action here.

## Usage

At the working-directory root containing `signal_ingest/`, run:

```sh
python -m unittest discover -s signal_ingest/tests -p 'test_*.py' -v
python -m signal_ingest.v1 signal_ingest/fixtures/synthetic_v1.json
```

The second command emits **one deterministic JSON document to stdout** from a locally supplied synthetic file. It performs no current GitHub lookups and does not authenticate the input. To avoid any input mutation or network access, an integrator supplies already-collected, versioned JSON. Output is an observation for later review, not a directive to initiate tasks. The reader must decide whether and how independent authentication is possible; this package cannot do so.

## JSON contract

Machine-readable field/enumeration contract: [`CONTRACT_V1.json`](CONTRACT_V1.json). An end-to-end synthetic input: [`fixtures/synthetic_v1.json`](fixtures/synthetic_v1.json).

- `snapshot.observed_at` and every `observations[].observed_at` are **provided explicit UTC second timestamps**; this source module does not consult the clock. A future-dated report is rejected.
- `snapshot.subjects[]` pins `(repository, subject, head)` and states whether that subject needs runtime evidence. A matching exact head makes source evidence current **to that supplied snapshot only**; the component does not independently check GitHub state.
- `observations[]` carry category, status, incident key, source reference, declared evidence class, claimed owner/reviewer, and self-asserted authentication. **None** of these text fields is trusted authority. `authenticated` is unverified and `owner_verified=false`, regardless of what a Bus comment says.
- The output groups by `(repository, subject, exact head, incident_key)`, not by arbitrary report ID, source URL, or Radar's payload hash. Reports with different source URLs may be grouped **provisionally**; equivalence remains an **unverified claim**. Same incident across changed heads never upgrades stale evidence.
- `candidate_observation` means a negative research signal survives **head qualification** (with a deliberate exception for a missing required runtime whose head is inherently unknown). It **does not authorize a task, a release, a cost, or a reviewer action**.
- `CI_RESULT PASSED` remains informational; `release_permission=false` globally and per observation. `RUNTIME_GAP` cannot make Lantern or any provider available; runtime output remains `UNKNOWN` until a separate authenticated verifier is integrated.
- Host cutoff is a source-level negative gate: after the stipulated deadline, `host_task_start_permitted=NO_EXPIRED_CUTOFF`, with no proposals. Before a deadline, the state is still `UNKNOWN_UNVERIFIED_AUTHORITY`, **not YES**.

Input rejects unknown fields, mismatched heads, noncanonical UTC, ambiguous/self-conflicting reused IDs, malformed source URLs, booleans masquerading as runtime flags, duplicate JSON keys in the CLI, and oversized input. Output is stable under observation and subject permutation. Source URL fields may contain a URL but are **never fetched**.

## Reuse and non-duplication

Reviewed current BT2 main `09a224105e26336df09e8787c1c99e9ea6298ffc`, current Bus main `eb315a5612ae99aadddb397891ffcf3a2b0433a6` and active BT2 draft PRs on 2026-11-20. Radar's binding [`RADAR_DEDUPE_V1`](https://github.com/thebrazenbeard/chat-communication-bus/blob/eb315a5612ae99aadddb397891ffcf3a2b0433a6/docs/protocol/RADAR_DEDUPE_V1.md) applies a fixed 500 ms *transport-level message* duplicate rule. It is not the reusable cross-report incident grouping this component needs; therefore no separate Bus/Radar runtime dedupe was recreated. Its source does, however, reinforce fail-closed validation, canonical field treatment and explicit provenance.

BT2 [`CURRENTNESS_BACKEND_STATUS_V1.json`](https://github.com/thebrazenbeard/bt2/blob/09a224105e26336df09e8787c1c99e9ea6298ffc/docs/runtime/CURRENTNESS_BACKEND_STATUS_V1.json) reports no active currentness provider and `lantern_currentness=UNKNOWN`. A source-only wrapper can carry those facts as inputs, but cannot check the live Lantern or override the source ceiling.

## RED → GREEN, falsifiers and evidence ceiling

An intentionally flawed grouping implementation used `source_ref` as its fourth grouping key. The frozen adversarial test `test_01_duplicate_reports_one_underlying_failure` **failed**: two reporters generated **two** candidate observations for the same source incident. The correction uses the provisional `incident_key` under the exact repo/subject/head scope. The test and complete negative suite passed on rerun; see included `red-test.log` and `green-test.log`.

The suite covers the seven required adversarial cases and additional replay, duplicate-ID conflict, canonical time, malformed provenance, conflicting head status, order independence and conservative runtime handling. All tests use public-safe *invented repositories* such as `example/app`; none consumes private project data or claims real-system observation.

**Not proven:** collector fidelity, authenticated provider binding, owner identity, production event equivalence, actual active Lantern runtime, remote machine state, independent peer review, or any policy/operation effect. This is an implementer-produced source test artifact for BT2 to review; no autonomous ecosystem agent exists by virtue of it.
