# Internal source audit and unresolved gates (V4)

All scenarios are fictional/synthetic. No user records, credentials or raw private checkpoints are included.

V2 false-silence: distinct subjects sharing fingerprint and Git head could both disappear after an earlier notification or known observation. V3 corrected same-batch collision quarantine without reactivating stale/future reports. V4 makes prior notification logs, known observations, owner ACK, noise/acceptance feedback, and synthetic evaluation labels all subject/head bound. Older fingerprint-only history inputs now reject, rather than accidentally attributing a prior event to another subject.

Test-driven evidence in isolated Lappy source: baseline V3 43/43; new V4 subject/history tests initially failed (six failed assertions and four interface errors) before implementation. Portfolio helper tests failed until the writer was updated. A metric identity test initially scored zero of two same-fingerprint subjects before correction. V4 local 56/56 normal and optimized on Python 3.14, fictional demo exit 0. Same-author tests are NOT independent hostile review.

Remaining holds: a hostile direct caller can still forge trusted Context fields, severity and time scores remain assertions, Git head can move, no durable authenticated notification log or emission, no cross-process exactly-once behavior, potential urgent alert starvation by daily budget, and no independent A/B approval or qualified runtime backend. No protected effects.
