# BT2 ecosystem proactivity governor — source-only review candidate

Status: NOT INSTALLED. No autonomous monitor, authenticated currentness provider, notification emitter, production consent, or effect authority.

The pure evaluate(signals, context) function returns stay_silent, draft, question, or notify PROPOSALS. No result sends messages, schedules tasks, changes memory, grants consent or authorizes release. Its source-claim fields and the Context trusted fields remain caller assertions: never ingest them directly from a model, webhook, unverified Bus comment, or untrusted B adapter. Real host authentication and independent source readback are required outside this package.

The governor limits proposed interruptions, checks evidence freshness and exact-head bindings, preserves writer ownership, quarantines same-batch fingerprint collisions, and produces privacy-minimized public summaries. Typed history and feedback now key on (fingerprint, subject, exact_head), so another repository sharing a fingerprint cannot inherit a cooldown, ACK, known observation, or NOISY label. A missing Git head is represented by an empty string, never a fabricated SHA.

V4 BREAKING INPUT SCHEMA: known_observations and trusted_owner_ack_keys require three fields; notification_log requires four (fingerprint, subject, exact_head, offset-aware time); feedback requires four (fingerprint, subject, exact_head, label). Ambiguous older shapes REJECT; do not automatically convert old records to trusted suppression. The portfolio.explicit_feedback helper takes Context, fingerprint, subject, exact_head, label.

From this directory, with Python 3.11+ standard library:

    python -B -m unittest discover -s tests -v
    python -OB -m unittest discover -s tests -q
    python -B demo.py

The demo is fictional. measure() requires incident-keyed synthetic ground truth and explicitly reports independent_ground_truth false.

BT2 owns policy; Engineer B owns source/semantic signal adaptation; Engineer A owns hostile verification. Neither existing branch is touched. Operational adoption requires an independently reviewed V4 input migration, authenticated Context admission and recipient, current source/head checking, persistent replay safeguards, real notification calibration, separate explicit permission for emission, and real readback. Lantern currentness UNKNOWN. A source merge does not install this software.


## Untrusted Engineer B signal dry-run boundary

The optional pure function governor.untrusted_b_ingress.review_untrusted(document, now=...)
accepts a synthetic or caller-supplied structurally plausible Engineer B
BT2_ECOSYSTEM_SIGNAL_OUTPUT_V1 or BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1
envelope. It never authenticates the source, imports Engineer B's still-draft
implementation, or contacts a provider.

- At most 40 grouped observations and 512,000 bytes of serializable input.
- Contradictory candidate_observation and head_currentness claims, tampered
  provisional grouping hashes, and unsupported authority claims reject.
  A matching hash remains an untrusted caller assertion, not proof.
- Noncandidate claims remain stay_silent; a fresh candidate may at most
  create a private draft requiring independent source inspection.
- Returned public summary contains no repository, raw observation text,
  source references, subject identifiers, fingerprint, owner claims or
  recipient authority. It declares trusted_context_admitted=false,
  release_permission=false, notifier_active=false,
  currentness_qualified=false and external_effects=[].
- No monitor, scheduler, background task, host authentication, memory effect
  or notification emission is installed.

This is NOT a deployed ingress integration, and synthetic tests do not prove
compatibility with Engineer B's final implementation. Real authorized admission
must establish provider, ownership, source/head and time separately.

## Public batch projection

The pure governor returns a rich internal Batch whose raw fields include
Decision subjects, source heads, and dropped_duplicate_signal_ids.
These fields can contain caller-controlled identifying text. Never send or
JSON/dataclass-serialize the raw Batch outside its authorized process.

Batch.public_record() is a deliberately narrower presentation surface:
it omits private decisions entirely and calls Decision.public_record() for
each remaining result. It includes only source-only/no-monitor/no-effects guards. It omits raw
subjects, heads, references, next steps, duplicate IDs and raw observation
counts. This is explicit opt-in safe projection, NOT a change to internal
deduplication, any automatic serializer, upstream privacy classification,
or authenticated notification authorization.

## Public projection noninterference (2026-11-20)

The existing Batch.public_record() filtered private Decision objects, but
that alone did not prevent leaks: evaluate() calculates fingerprint collisions,
deduplication, and notice slots across *all* input signals. A private signal
sharing a fingerprint with a separate public signal could change the public
action and reason codes even though the private Decision itself was omitted.

The governor now evaluates public output from a separate public-only source
slice, before collision handling, dedupe and notification-slot allocation.
The internal Batch.decisions remains computed from the complete input and is
unchanged for authorized internal analysis. For the public slice, any
(fingerprint, subject, exact-head) incident containing a private or
externally-invisible report is excluded entirely, even if another input claims
that same incident is public. This is conservative declassification refusal,
not verified source identity or proof that separate fingerprints describe
separate real-world events.

Batch.public_record() remains opt-in and must not be confused with raw Batch
serialization, which includes internal IDs and private decisions. Tests show
that a private *different* incident with an identical fingerprint no longer
changes the public projection. A conflicting privacy label for the *same*
incident is intentionally withheld. A missing public result in that situation
does not prove an authenticated private event; it may reflect untrusted inputs.
No provider admission, monitor, notifier, or recipient is installed.


## Visibility and boolean admission (2026-11-20)

Constructing a governor Signal without specifying externally_visible now
produces **private/local-only** visibility by default. Public visibility
requires an explicit Python boolean externally_visible=True; it is still
only a caller assertion, never proof of authentication or permission to
publish. All ten boolean policy, trust and privacy flags are rejected if
they are strings, integers, nulls or other non-boolean values. In particular,
strings such as "false" are truthy in Python and must not accidentally
become a public-visibility or authenticated-source assertion.

This intentional fail-closed change may require existing synthetic or
authorized public callers to set externally_visible=True explicitly.
The fixture helper and synthetic demo do so; B's untrusted bridge remains
private via its existing explicit False. Signal is still a source-only
proposal and the governor has no authenticated recipient, active monitor,
notification emitter, qualified runtime currentness or memory admission.
Use Batch.public_record() only when the caller has independently
established the public classification; never serialize the raw Batch.


## Private individual Decision projection (2026-11-20)

Decision.public_record() is now fail-closed for a private/local-only
Decision. It returns the same fixed redaction marker regardless of that
Decision's action, domain, priority, reason codes, subject, source head or
other metadata. Masking only the fingerprint was not sufficient: a direct
caller could learn or publish private classification details through the
remaining fields, even though Batch.public_record() filtered private
Decisions out correctly.

The untrusted B dry-run ingress remains an INTERNAL local-review interface,
not a public transport. It now explicitly returns only an empty fingerprint
and draft/stay_silent action per private proposal, without calling
Decision.public_record() or disclosing private domain, priority or reasons.
This does NOT authorize sending that local review to others. The returned
reviewed_count and action may themselves reveal that a caller submitted a
proposal; handle within the already authorized local review scope. For public
exposure use the conservative Batch.public_record() boundary, not a raw
Batch or the B dry-run record. Upstream privacy classification is still
a caller claim, not independent authentication, and Lantern live currentness
is UNKNOWN.


## Strict Context trust and policy container admission (2026-11-20)

Operator-supplied Context does **not** become authenticated merely because
a field has a trust-oriented name. The governor now rejects malformed
Python container types for its seven typed frozenset policy/history fields.
In particular, a string can no longer replace verified_signal_ids,
owner_lanes, or qualified_capabilities: Python considers substring
membership against a string true, silently making malformed caller input
look like a verified-id, owner, or qualified-capability allowlist. The
required sets must be real frozensets; text member values must satisfy
the bounded incident-ID grammar, and verified head bindings must be
subject/head pairs. Feedback and notification logs must be tuples.
Policy limit numbers must be actual integers, not Python boolean values.

This is a **breaking fail-closed source-input validation** for callers
that previously supplied lists, tuples, strings, sets or untyped JSON
directly. Such callers must explicitly validate and construct the
documented Python types using independent authenticated authority
before creating Context. Do not coerce bad inputs into trusted sets.
The synthetic demo and untrusted-B dry run already build correctly
typed Context. Syntax is not attestation: verified_signal_ids and
other trusted fields must still come from a separately verified
authorized host. No producer, notifier or live currentness backend
is created by this source change.


## Signal integer, evidence, and release-capability admission (2026-11-21)

The Signal dataclass now fails closed on malformed values in six discrete
numeric policy fields (four 0..5 scores, freshness_hours, hours_to_impact).
Boolean values are not valid integers for these fields, and fractional
floats cannot silently change urgency thresholds.

Release dependency IDs must be a tuple of bounded string IDs. Python
iterates a bare string by character; a caller supplying
needed_capabilities="abc" could incorrectly satisfy a release prerequisite
when Context.qualified_capabilities contained the unrelated individual
letters a, b, and c. Bare-string prerequisites and invalid tuple members
are now rejected before decide_one runs. A valid tuple ("abc",) still
requires the actual capability "abc" in the separately provided Context.
Evidence references and evidence classes require tuple containers rather
than accepting a string or mutable list; next steps must be actual text.

This is a SOURCE input-contract change. It may intentionally reject older
untyped caller values; adapters must validate source inputs and construct
the documented types without granting any new authority. Correct types do
not authenticate a source, owner, evidence, dependency, recipient, or
currentness backend. All decisions remain read-only proposals, not effects.


## Exact-incident conflicts fail closed (2026-11-21)

Previously the governor grouped reports with identical
(fingerprint, subject, exact_head) by first-arrival-wins. If two reports
disagreed on severity, trust assertion, visibility or release inputs,
reversing the input order could silently change a severe notification
proposal to stay_silent or vice versa. Exact incident IDs are not
sufficient proof that the reports' claims are equivalent.

The governor now groups same-incident reports before evaluation. It
coalesces a benign duplicate only if all policy-relevant fields match
and both reporter IDs have the same membership in the operator-supplied
verified_signal_ids set. IDs and evidence-reference locations may differ
for benign duplicates; their representative is chosen by stable ordering
rather than arrival order. Conflicting reports produce one private
review-only DRAFT with a constant priority zero and
EXACT_INCIDENT_CONFLICT reason. No public Decision is generated,
even if each conflicting source claims public visibility. The existing
internal coalesced-ID audit field is preserved, with deterministic IDs;
it remains private and must not be serialized as a public Batch.

This is deliberately conservative. An adversary who can inject an
equal-incident report may block a public proposal by forcing a conflict.
The remedy is independent authenticated provider and incident admission,
not silently trusting the higher-scored report. Source authentication,
recipient permission, release qualification, runtime monitoring,
notifier delivery and qualified Lantern currentness are still absent.
