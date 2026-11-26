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

## Private meaning-ID projection (2026-11-20 source correction)

The semantic exchange previously echoed `vsns.candidates[].meaning_id` unchanged into `candidate_meaning_ids`. A typed caller could hide a personal name or location in that freeform ID and obtain it back despite the no-person-identifiers contract. A synthetic adversarial test reproduced this output leak on the prior exact branch source. The revised exchange validates uniqueness of the incoming IDs internally but emits only response-local ordinal aliases `candidate_1` through `candidate_8` in candidate order, never original ID strings or deterministic hashes that may be guessed. Aliases **do not support cross-call identity matching**. Inputs must still omit personal text, should never be logged raw, and no inference of consent, identity, truth, autobiographical memory or runtime integration is authorized by the change. This is a source privacy-boundary fix, not a deployed or signed provider.


## 2026-11-21 — strict GitHub response identity and JSON validity

Exact prior PR128 head `06529e94243420a8588b6723d6c081c58e7d3b9f`:
the read-only `collect_github.py` collector compared provider `pr.number`
and `run.id` with requested integer IDs using equality alone. In Python,
`True == 1` and `1.0 == 1`, so syntactically malformed JSON identity
fields for PR/run number 1 passed the expected GitHub provider binding.
The same parser permitted nonstandard JSON `NaN`, `Infinity`, and
`-Infinity` values in otherwise parseable provider responses. No
successful exploit or memory read was observed; this is a source input
validation defect.

Three additional tests were recorded **RED** on the prior exact source,
with seven rejected-case assertions failing: bool/float PR identity,
bool/float run identity, and three nonfinite JSON constants. The
new source requires `type(...) is int` on both provider IDs *before*
testing identity equality, and rejects nonfinite JSON constants in
`_parse`. Existing duplicate-key validation remains in place. A
separate **positive control** passes authentic integer PR/run 1 through
the collector and full offline bridge, preserving `memory_admission =
NONE`, `independently_authenticated = false`, and
`release_permission = false`.

Verification on an isolated Lappy checkout: bridge **46/46 tests**
normal and optimized, parent signal normalizer **21/21 tests**
normal and optimized, compileall and git diff --check PASS. An additional
**actual read-only GitHub API** collection against current BT2 PR #128
and its previously completed workflow run `44935096176` observed
two associated receipts at source HEAD
`06529e94243420a8588b6723d6c081c58e7d3b9f`, CI status PASSED,
`memory_admission = NONE`, `release_permission = false`, and
`external_effects = []`. The request was executed with the already
authenticated GitHub CLI, but does **not** establish a signed downstream
actor identity, persistent replay fence, or runtime admission. The
observed input/output digests were
`f38cad81b2d76bdb50d332ddeec10d97ae93ad5ab27213b0308f927ef3dbe0ef`
and
`e314bca7bb0487b52fe8629c5f719d064d7ac1d659cb6d0f4415fd723d040b9b`
respectively. Source-head and timestamp changes would produce different
digests. This is **SOURCE/TEST/READ-ONLY_PROVIDER_OBSERVATION**, not
merged code or a qualified memory provider.

Do not turn GitHub CI, semantic salience, Empathy policy hint, raw
feedback, or historical source into a memory, current preference,
consent, release permission, or runtime attestation on this evidence.


## 2026-11-21 — optional adjacent-batch replay consistency, NOT trusted persistence

The V1 GitHub signal bridge checks conflicting `event_id` values *within*
one document, but `seen_receipt_digests` is a caller-owned hash list.
When two bridge calls are processed separately, V1 can accept a changed
report under the same event ID, even when the later caller reports
having seen the old receipt digest. An empty reset cache similarly
makes an exact replay appear new. This is a **bounded consistency
gap**, not proof of a real-world attacker or memory corruption.

New source-only `bridge_with_predecessor(previous, current)` explicitly
revalidates **both** V1 input documents through the existing `bridge`,
requires that the current caller's replay cache contains *all* hashes
from the predecessor's `next_seen_receipt_digests`, and refuses a
same-`event_id` report whose canonical SHA-256 changes between the
two documents. It then returns **exactly the original V1 bridge
output** for the current document: same schema, same source-authentication
ceiling, same no-memory-admission and no-release fields. No current
consumer or provider route invokes it automatically.

Five new synthetic hostile/positive tests were RED before implementation
(the function did not exist) and GREEN afterward. They include a
conflicting ID re-used with a changed CI result, omitted prior cache,
valid replay plus a new event, malformed predecessor, and exact
legacy-V1 output preservation. Source-level tests alone cannot prove
honest predecessor custody.

**Critical limits:** The predecessor is supplied by the caller and
may be forged, truncated, swapped or omitted. Reconciliation only
compares the **two explicitly provided documents**, not a durable
multi-process history. No encrypted/signed host checkpoint, trusted
provider key, immutable replay registry, provenance attestation,
semantic truth, memory write, consent, or runtime authority is created.
A host-approved durable verifier and a separately authenticated
predecessor readback are needed before any continuity claim. Do not
silently replace the original V1 bridge API, its CONTRACT_V1.json,
or the shared Radar/Bus lane with this optional research helper.


## 2026-11-21 — rollback fence and the three-batch falsifier

The opt-in `bridge_with_predecessor` previously checked replay hashes and
event-ID consistency but did **not** order the batches' own snapshot
observation times. Two individually valid documents could report
`21:30:00Z` and `21:29:30Z` respectively and still pass as adjacent
predecessor/successor.

One new hostile test was **RED** on the old source, then **GREEN**
after the helper required the successor's `snapshot.observed_at`
to be no earlier than its predecessor's. Both source times already
pass the V1 strict UTC timestamp validator; the comparison uses
canonical fixed-width timestamp strings. A non-decreasing successor
still passes and returns **exactly** the original V1 output.

An additional **negative-control test** confirmed a more material
limit: a three-batch chain with an event recorded in batch 1,
no reports in batch 2, and the *same event ID with changed content*
in batch 3 passes the two-batch helper when asked to compare only
batches 2 and 3. The original digest may remain in the reported
cache, but its event-ID binding is unavailable. This was **not
repaired or falsely described as protected**; reconstructing
multi-batch identity requires an independently authenticated history,
not simply another method over arbitrary caller-provided documents.

**Claim ceiling:** the clock values, predecessor document, digest
cache and source identity remain caller claims. A consistently
forged timeline can pass. No trusted time service, durable history,
provider signature, memory admission, consent, permission, model
training or production activation was added. Review this as a
source-only adjacent-batch consistency improvement, and preserve
the three-batch falsifier as a release blocker for any claimed
persistent replay or autobiographical continuity.


## 2026-11-21 — opt-in bounded multi-batch source consistency

The prior two-document `bridge_with_predecessor` can miss an event ID
that appears in A, disappears from B's report list (while its digest
remains in the caller's seen cache), then reappears with changed
contents in C. The earlier three-batch negative control demonstrated
this gap. This turn adds `bridge_with_history(history, current)` as
a **separate optional, pure source-only** check; no original V1
bridge behavior, field, adapter, provider or consumer is changed.

It accepts **1–8 explicitly caller-supplied predecessor documents**,
validates every adjacency using the existing two-batch helper
(including snapshot ordering and digest continuity), then refuses
a repeated event ID whose canonical report digest differs anywhere
in the *supplied* chain. For a valid chain, it returns **exactly**
`bridge(current)` unchanged. It never claims persistent independent
authentication, trusted timestamps, action permission, or
memory admission.

Five new TDD fixtures initially RED due to the missing function,
then GREEN: previously invisible A/B/C event-ID substitution;
valid three-batch newest-report and exact V1 output; empty,
malordered or over-eight history; and a deliberately **passing**
fully fabricated but self-consistent sequence whose resulting
authentication, memory and permission status all remain negative.
The original two-batch negative test remains a meaningful expected
limitation of that earlier API.

**Unresolved falsifier:** If the caller omits an entire historical
batch, supplies a manufactured history, or reuses an older event
ID outside the bounded eight-document window, this function cannot
establish authenticity or detect it. A host-owned independently
authenticated durable history/checkpoint and real producer identity
are needed before claims about persistent replay safety or Vera
continuity. The method is **not** installed into Radar/Bus or
memory admission; PR remains source research only.
