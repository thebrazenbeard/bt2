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
