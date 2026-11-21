# Internal source audit and unresolved gates (V4)

All scenarios are fictional/synthetic. No user records, credentials or raw private checkpoints are included.

V2 false-silence: distinct subjects sharing fingerprint and Git head could both disappear after an earlier notification or known observation. V3 corrected same-batch collision quarantine without reactivating stale/future reports. V4 makes prior notification logs, known observations, owner ACK, noise/acceptance feedback, and synthetic evaluation labels all subject/head bound. Older fingerprint-only history inputs now reject, rather than accidentally attributing a prior event to another subject.

Test-driven evidence in isolated Lappy source: baseline V3 43/43; new V4 subject/history tests initially failed (six failed assertions and four interface errors) before implementation. Portfolio helper tests failed until the writer was updated. A metric identity test initially scored zero of two same-fingerprint subjects before correction. V4 local 56/56 normal and optimized on Python 3.14, fictional demo exit 0. Same-author tests are NOT independent hostile review.

Remaining holds: a hostile direct caller can still forge trusted Context fields, severity and time scores remain assertions, Git head can move, no durable authenticated notification log or emission, no cross-process exactly-once behavior, potential urgent alert starvation by daily budget, and no independent A/B approval or qualified runtime backend. No protected effects.


## Private-local-only output boundary regression (2026-11-20)

The merged V4 source treated either contains_private_data=True or
externally_visible=False as private while scoring, but redacted identifiers,
evidence refs and next steps only under the former flag. This could expose the
fingerprint via Decision.public_record() and retain an internal evidence
reference or next step in Decision for an externally invisible signal.

Three test-first cases were added: two failed against the exact merged main
and one public-signal control passed. The implementation now computes
private_local = contains_private_data or not externally_visible once and
uses it consistently for returned evidence refs, next step and public-record
identifier masking. All 59 source tests pass locally under normal and
optimized Python. This is scoped privacy hardening, NOT proof of upstream
privacy classification, authenticated caller identity, recipient filtering,
or an installed notification runtime.


## Untrusted B signal boundary (2026-11-20)

Bounded source review used Engineer B's draft PR128 at
d9dcc6f5df1f105c1b3d0b5d62f94bdf1c0689e6 (stacked on PR123
3449ce3a94084722454345485cc12a10f0c91883). B's provider output
explicitly marks source authentication UNVERIFIED and replay state
CALLER_PROVIDED_CACHE_NOT_INDEPENDENT.

Added only a policy-owner dry-run review adapter WITHOUT importing B's
still-draft implementation. Initial stub nine-test run was RED (five failed
assertions, three missing-result errors, one unrelated pass). First source
implementation exposed a local regex escaping error and four tests errored;
fixed exact regex syntax. Then focused 9/9 and full 68/68 passed normal and
optimized. Three additional adversarial tests exposed: (1) oversized input
had no direct bound; (2) source-provided noncandidate reports were still
drafted; (3) contradictory head-currentness claims were accepted.
These three failed before fixes. Final focused 12/12, full 71/71 normal and
optimized source tests passed in an isolated Lappy workspace.

Synthetic tests are written by this same model; do not interpret as
independent hostile review or authentication of the actual provider.
Caller-supplied SHA hashes can be recomputed by the caller. Group fields,
private original reports and user-provided symbolic material never become
trusted Context, public source references, memory, user consent, release
authority, notifications or a live monitor. Real Engineer A/B review and
authenticated trust admission remain outstanding.

## Batch-level public redaction regression (2026-11-20)

Post-PR131 source inspection identified a boundary gap: Decision.public_record()
existed, but a caller preparing a public result from Batch had no explicit
safe counterpart, while the raw internal Batch retains
dropped_duplicate_signal_ids. A generic dataclass serializer can therefore
copy caller-provided private source identifiers. This is a potential misuse
boundary, not evidence of an actual notification leak.

Three new synthetic tests first errored on the absent public_record method:
one duplicated private signal ID, one public control and one mixed-visibility
batch. The source adds an explicit Batch.public_record() that omits all private
Decisions and uses each remaining Decision's existing public projection,
plus fixed no-runtime/no-effect guards. A second RED check proved that merely
masking the private fingerprint leaked private decision counts, domain and
priority; filtering local-only decisions made the second check GREEN.
The tests then passed; existing source tests still pass. The raw Batch remains
internal and unchanged for debugging; it is NOT safe to send via asdict().
Privacy classification still depends on caller-supplied flags; no recipient
authenticator or downstream notification transport exists in this package.

## Public decision side-channel regression (2026-11-20)

Exact prior source: BT2 main 2129f9db7f0ff97393c21874458d67fe1235b0e7.
Post-PR132 Batch.public_record() filtered private decisions but still used
public decisions produced from the full mixed input batch. Private signals
could therefore influence a visible decision without revealing their own ID:
a shared fingerprint across different subjects generated
FINGERPRINT_COLLISION and demoted the public action; a same-incident
privacy-label conflict could leak the public decision based on input order.

Four synthetic tests on the exact main source initially had four failing
assertions (including order variants), plus a passing private-noncollision
control. No real private records were used. Repair preserves full internal
batch decisions and separately computes public decisions from public-only
input signals, excluding any key that is also private. GREEN focused 4/4,
full 78/78 normal and optimized Python. Source-only tests are not independent
privacy certification, nor proof of upstream privacy-classification integrity.
If inputs conflict on the exact key, the public view fails closed; public
decision omission is not independent evidence that a private signal existed.

The output is not a general-purpose authenticated notification contract.
Keep raw Batch private. The source still lacks independently verified producer,
recipient authorization, persistent replay, and a qualified live runtime.


## Default-private and strict-boolean input boundary (2026-11-20)

Exact source baseline BT2 main 6a3417603a62cc7502753c9c04018fa4c3328c04.
The Signal dataclass previously declared externally_visible=True and
did not validate its boolean-typed fields. A caller's omitted visibility
field could enter public projection implicitly; a string "false" was
truthy in Python and could be misinterpreted as explicit disclosure or
trusted attestation. This is an input-contract vulnerability in source,
not a verified production leak.

Six targeted synthetic test methods first produced fourteen failing
assertions on exact baseline source (missing private default; textual and
integer visibility; untyped corroboration, authenticity and all other
boolean flags). After the change, six focused tests passed. The full
suite passed 84/84 normal and 84/84 optimized; the synthetic demo and
workflow security tests were checked separately. Existing public
synthetic fixtures and demo now use explicit True. B untrusted ingress
already sets externally_visible=False; it remains private.

Strict typing is not independent authentication. An attacker can still
supply literal True where source authority is not verified. This library
performs no external actions, privacy attestation, notification, service
activation or Lantern currentness qualification. Runtime admission and
review therefore remain held.
