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
