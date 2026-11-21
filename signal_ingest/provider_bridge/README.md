# Engineer B — GitHub provider ingestion and semantic exchange

State: SOURCE-ONLY TESTABLE CANDIDATE, NOT INSTALLED. Stacked on Draft
BT2 PR123 HEAD 161ae030705fc6373774c57c4fc1b9d6ece8f788 (reconciled main).
BT2 owns decisions; Engineer A owns scanner PR125. This package does not
alter A code, BT2 governor, source memory, or any host service.

## Reproduce

From repository root with Python 3.11+:

    python -m unittest discover -s signal_ingest/tests -p test_*.py -v
    python -m unittest discover -s signal_ingest/provider_bridge/tests -p test_*.py -v
    python -m signal_ingest.provider_bridge.v1 signal_ingest/provider_bridge/fixtures/synthetic_github_observation.json

Optional explicit read-only GitHub API collection with an already connected
GitHub CLI, current UTC observation timestamp and separately determined cutoff:

    python -m signal_ingest.provider_bridge.collect_github --repo thebrazenbeard/bt2 --pr 123 --run 44802825444 --observed-at 2026-11-20T21:48:28Z --host-cutoff 2026-11-20T18:00:00Z

The example timestamp is HISTORICAL. A future operator must supply an actual
current observation timestamp and freshly determined access constraints.
The collector only invokes gh api on a canonical pull and optional CI run,
with bounded response, 15-second timeout, no shell and no writing.
It validates repo, PR number, API head, run identity and source URL.
For an optional PR-specific CI observation, the GitHub workflow run must
have event `pull_request` and its `pull_requests[]` association must contain
the exact requested PR number, canonical API PR URL and matching run head
SHA. Merely sharing a SHA or repository does not establish association.
Unassociated push-only CI, ambiguous links and fork-head PRs are not
qualified by this narrow V1 collector; they require a separate, evidence-
bound source adapter rather than a fabricated PR result.
Even an authenticated GitHub CLI session is not a signed downstream
receipt or proof of author/reviewer identity. It prints no token.

Contract: BT2_GITHUB_PROVIDER_BRIDGE_INPUT_V1 to
BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1, see CONTRACT_V1.json. Exact
signal_ingest.v1.normalize is reused, not forked. Dedupe is scoped to
repo, subject, head and incident key; source equivalence stays provisional.
Replay suppression uses a CALLER-PROVIDED digest list only. Cache overflow
fails closed. A forged/reset replay ledger can defeat cross-process replay,
so genuine durable anti-replay requires separately authorized, independently
authenticated host storage. No external effects or release permission.

Second contract: BT2_SEMANTIC_EVIDENCE_EXCHANGE_INPUT_V1 to
BT2_SEMANTIC_EVIDENCE_EXCHANGE_OUTPUT_V1. Three exact GitHub source
HEAD/locator pairs are required (Semantic Atlas, Vera VSNS, Empathy).
Only typed already-evaluated VSNS results and ephemeral response hints
are accepted; no utterance text or personal identifiers. High salience
cannot establish truth, consent, identity, phenomenology or memory
admission. All effect fields remain NONE, consent NOT_GRANTED and truth
NOT_DETERMINED. Semantic Atlas staging is not canonical adjudication.
The host must still authenticate source and currentness.

## Observed read-only evidence, Nov 20 2026

Connected gh API returned BT2 PR123 exact HEAD
3449ce3a94084722454345485cc12a10f0c91883.
PR JSON response SHA256:
0589b8b647a7bf77b5ecd3bf5f7d79e7ceb26b8b6efd7783effa3dfcbe1d81ef.
Private normalized output SHA256:
A4F70EFC23844EF33A78C83BCF757195D7ED7CDD470D923064329453C7BBB4DF.
CI run 44802825444 returned PASSED at the same head; CI provider
response SHA256:
b72c41ca967a1812a7d921009ceaa87fbd7d60a5057bdfacfa97eb0fe6acf928.
Exact combined input SHA256:
FC12B53910A57CB37F2EF6578847C490C8AEA77CBC51E5EF1D981D9580A79B18.
Normalized output SHA256:
C954569CEBD05B88E100C22360B5D5A4B6D5283372E336DC8475815DCD034ED1.
Actual API calls happened at UTC 21:43:09 and 21:48:28 respectively.
Release permission false, effects zero, actor identity still unverified.

Independent RAW Git blob SHA-1 readback, without Windows CRLF conversion:
Vera VSNS b74e1cbcd27b9062e59da8e6e0f6d59367bad4cf,
Empathy policy 18a23eef13e7b27965d76db18d2f48f4d1e6f907,
Empathy adapter e09f03ce6696be5ecae339b82f885efac3c1a632,
Semantic Atlas schema f4592c2ea71896296df29cb821dde317e086f77a.
Source HEAD snapshots:
vera 00cb40f86b0e355523d4c1a73d71c8c3f445b45c,
empathy b2186e8c9212139923c203a5ccb60e8b3d978f64,
semanticatlas c2ae36c1a2b3a27ee43bd9466a2ab04f8c9419bc.
Actual VSNS and Empathy source functions with synthetic input produced
VSNS salience 0.63, Empathy TASK_DIRECT advisory; exchange preserved
separate truth/consent/salience axes. Truth unknown, no consent,
autobiographical admission or actions. Receipt stored privately.

Read-only Supabase: Vera ACTIVE_HEALTHY Postgres 17.11, seven RLS-enabled
matching base memory tables with no anon/authenticated SELECT grant.
Of 22 matching functions, one has inherited public EXECUTE but those
client roles cannot USE semantic_atlas schema; not proof of a public
memory endpoint. Tattler has no Vera memory tables. These provider
observations cannot be forged as GitHub source refs in V1. PR126 is
the separate provider-catalog contract, stacked on PR124 memory lifecycle.

## Owner-safe merge sequence

1. Independent reviewer qualifies PR123. Merge B source normalizer to
   BT2 main, preserving exact reviewed head and source checks.
2. Rebase this stacked provider/semantic bridge onto that new main,
   rerun all tests and source hashes; merge only after independent review.
3. Engineer A reviews/rebases scanner PR125 against merged B contract and
   verifies exact original bridge tests. No edits to A branch from B.
4. Independently review memory lifecycle PR124, merge after acceptance;
   rebase PR126 provider catalog onto it and rerun provider privilege probes.
   Live memory admission is a separate held authority/privacy task.
5. UnboundVNC PR102 is a different host-control lane. Do not activate
   host input, install a daemon or reinterpret test approvals via this PR.

No Supabase DDL/DML, private rows, credentials, memory imports,
GitHub main merge, service activation, notification or publication
of private material is performed by this package.
## Current stacked-source reconciliation (Nov 20 2026)

The historical GitHub and semantic receipts above remain tied to their original SHA snapshots. PR #123 was later reconciled with BT2 main `7aed3b589a8a8f5370a0fe838d1ec571f1358346` through a two-parent source-only merge. Its current verified remote head is `161ae030705fc6373774c57c4fc1b9d6ece8f788`. PR #128 now merges that exact parent without rewriting original evidence or modifying Engineer A's branch. This changes source ancestry and test coverage, not authenticated provider trust, durable replay protection, or release permission.
