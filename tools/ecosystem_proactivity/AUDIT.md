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


## Private Decision public-summary metadata leak (2026-11-20)

At exact main source 7aed3b589a8a8f5370a0fe838d1ec571f1358346,
the governor had an opt-in public Batch projection that omits private
Decisions, but callers could still invoke Decision.public_record() on a
private result. It hid the fingerprint and refs but returned private action,
domain, priority and policy reason codes; review_untrusted() did invoke it
for B's untrusted, private proposals. No evidence that this was published
externally; the exposure was a SOURCE API safety weakness.

Five newly authored synthetic focused tests: one batch omission control
PASS, one public Decision summary control PASS, and three failures RED on
the exact original source. An initial test timestamp mismatch was corrected
before the final valid RED, with no production code changed. The minimal
repair makes Decision.public_record() return a constant redaction marker
for private/local-only results; B's explicitly local dry-run record now
projects just an empty fingerprint and draft/silent action. Existing
private source review remains internal. Focused 5/5 and full 89/89 normal
and optimized Python tests passed locally. These are same-model authored
tests and not independent Engineer A/B review.

The local dry-run response still contains an action and reviewed_count,
so it must not be confused with an authenticated externally publishable
record. Neither API proves privacy classification, source authenticity,
recipient permission, owner acknowledgment, qualified runtime currentness,
notification delivery or memory admission. No runtime service activated.


## Strict Context trust-type gate regression (2026-11-20)

Original exact BT2 main: a43a1bfd93263c26ba5e337f11e4718b140e1608.
The governor's Signal flags were typed and visibility was default-private
after PR134, but the operator Context had type annotations only. Values such
as verified_signal_ids="s1" and owner_lanes="SECURITY" could satisfy Python
membership tests because "s1" in "s1" and "SECURITY" in "SECURITY" are True.
A malformed plain string could therefore bypass expected container
validation and contribute to a NOTIFY decision when other caller trust
claims were present. This is a SOURCE input contract failure, not
evidence of an active emitter or real unauthorized notification.

Six new synthetic test methods ran first on exact source before repair:
16 assertion failures and two type errors for strings/tuples replacing
frozen policy sets, mixed-type members, numeric booleans and history
lists; one valid frozenset control passed. The minimal fix enforces exact
frozenset/tuple container types, valid string members, subject/head
pair shape, and integer limits before consulting membership. After
repair: focused 6/6, full 95/95 normal and 95/95 optimized Python
source tests passed locally. Same-model tests do not replace Engineer
A/B independent review, live provider verification, owner signoff or
runtime qualification. Existing B untrusted ingress continues to
construct Context with empty trusted sets and no authority.

Old callers may need an explicit separately authorized input-schema
migration, not a silent conversion of legacy JSON lists into trusted
runtime facts. No host, scheduling, memory or notification effects.


## Signal type admission and release-prerequisite character spoof (2026-11-21)

Prior exact BT2 main: 9d24177bebad09c9720f5338ec202c3c8be6f3a3.
Context trust containers were hardened in PR136, but Signal policy
scores/time windows were not checked as true integers. Python accepted
True/False and fractional floats in score/time comparisons. Signal
needed_capabilities also permitted bare strings, which Python iterates
character-by-character. When purported release prerequisite "abc" was
passed as a string, an unrelated qualified-capability set containing
a,b,c could make the release dependency appear satisfied. Source
input-contract flaw, not an observed real released artifact or deployment.

Eight new adversarial synthetic test methods on original exact main were
RED with 24 assertion failures; one valid typed urgent signal control
passed. A minimal patch enforces actual integer types for six numeric
fields, tuple evidence containers, bounded tuple capability IDs and a
real string next-step. After fix, eight focused tests passed and full
103/103 normal and optimized source tests passed locally. Same-model
author/test verification is not independent review or runtime proof.

Intentional fail-closed compatibility break: caller JSON arrays, bare
strings, boolean/float numeric values and mutable evidence lists must
be explicitly vetted and converted under a separate authenticated owner
contract, never silently promoted into trusted state. No notifier,
scheduler, qualified Lantern backend, memory admission, external
publication or live execution has been installed by this code.


## Exact-incident first-input-wins source finding and quarantine (2026-11-21)

Reviewed exact canonical BT2 main source
1225db13202a5c0aee58cabff68b715e534c4631. Engineer A independently
reproduced an order-dependent same-incident suppression defect and
reported it on BT2 PR137 and Bus #423. We re-established red on an
isolated exact-head Lappy clone: six first-round tests, five failures,
one distinct-incident collision control passing. A low-score unverified
report before a severe verified report yielded stay_silent; reversing
the order yielded notify. These are model-evaluated source proposals,
not real notifications or runtime leaks.

A local implementation grouped exact incident reports and compared
all decision-relevant Signal dataclass fields except reporter ID and
evidence-reference location; reporter ID verification-membership must
also agree. Exact-key discrepancies quarantine into a fixed private
DRAFT (zero priority; no public projection, external effects false).
A benign duplicate retains the existing report coalescing behavior with
deterministic representative. Extended seven-test suite verified
all three-report permutations. The first implementation erroneously
removed conflicting coalesced IDs from the internal audit field and
caused three full-suite regression failures; we preserved the existing
internal audit contract and the full suite returned green. The
conflict status is recorded on the internal Decision reason, never as
authenticated evidence.

Evidence: focused 7/7, full 110/110 normal and optimized locally.
Exact-head CI and independent review of this new repair remain separate
gates. Negative assurance: an untrusted conflicting report can force
review hold, so this is not an authenticated event resolution system.
No live provider, notifier, scheduler, memory, source-currentness,
recipient permission, branch protection or deployment was changed.
