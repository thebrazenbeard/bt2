# TWO — architecture/provenance hostile review of T'Kal bridge

Review input: BT2 Draft PR #101 at `75599e6a823ef5b7b061d57e87f6dece043d078a`;
external T'Kal-in-ket checkout `b0af150c2405b519fd921bac33e5f9f1f35f92d7`,
core blob `69e85a62672e1dfffacec08fde98e9df26716300`.
Reviewer: native child agent `/root/identity_two`, same ChatGPT runtime; **not**
an independently authenticated neural-model or host review.

## Falsification attempt and disposition

1. **FAILS before patch — conclusion injection.** An attacker-controlled
   `refined_claim` asserting thirteen independently verified and production-ready
   neural models passed `validate_packet` and appeared verbatim in a
   `CLOSED/REFINE` result even though `independent_model_or_host_attestation`
   was `false`. Changing `review_custody_limitations` to claim cryptographic
   independence and changing a review finding to assert real weights were
   tested also passed.
2. **FAILS before patch — attribution/lens spoofing.** An invented reviewer ID
   and all challenges assigned to the Purist Logic lens passed validation and
   yielded the original `CLOSED/REFINE` determination. Reviewers were distinct
   strings but never authenticated; challenge participation was not enforced.
3. **LIMITED freeze before patch.** Changing `refined_claim` left
   `frozen_claim_sha256` unchanged. This is expected from the upstream core's
   stated claim-domain scope, but dangerous if that hash is treated as binding
   the *derived* conclusion. `packet_sha256` does bind the changed packet.
4. **SURVIVES — no false SUSTAIN through this bridge.** `run()` hard-codes
   `case.determine("REFINE", ...)`; the input schema allows no verdict override.
   A malicious packet could misstate success as text, but not return `SUSTAIN`.
5. **SURVIVES — pinned external code / no vendored source.** `checked_checkout`
   verifies HEAD, cleanliness, every tracked blob's bytes, non-symlinks and a
   pinned core blob before import. The upstream project has **no chosen
   license**. This bridge imports from a separate checkout and copies no code;
   redistribution/permission conclusions are **UNKNOWN** and must not be
   inferred from the technical pin alone.

## Fix and test evidence

The bridge is a single, already-audited REFINE proceeding, not a general-purpose
deliberative authority. It now rejects packets with any change from the
audited canonical SHA-256
`b226e459125887bc7d27f6d4887471a34ef8e54d01cd44887d8e46185fcc49fa`;
it also explicitly binds the three reviewed lens/ID pairs and all three
challenge lens assignments. A fresh claim requires a new reviewed packet and
source pin. Existing distinct-ID, nonempty evidence, concession and
`execution_ref: null` validations remain.

- RED: three new regression methods produced **five assertion failures** before
  the bridge fix (tampered conclusion, custody, rationale, review finding,
  forged reviewer).
- GREEN: `TKIK_EXACT_REPO=... python -m unittest discover -s tests
  -p test_bt2_tkik_proceeding.py -v` — **9/9 PASS**, including real pinned
  upstream protocol execution.
- Full source suite: `python -m unittest discover -s tests -q` — **154 tests
  PASS**, one skipped because optional external checkout environment was not
  set for that run.
- Original source packet still produces its exact persisted REFINE result.

## Residual uncertainty

Packet integrity is **not** reviewer authenticity. The expected reviewer IDs
are self-attributed strings in the historical ChatGPT conversation; no signed
receipt, external provider identity, independent runtime, neural inference or
peer challenge attestation is established. This patch prevents new unsigned
input from **changing this proceeding's claims**; it does not prove that the
original claims were independently witnessed. The published result correctly
reports all model/host independence qualification flags as `false`.

**Post-fix verdict:** packet-to-result claim integrity **SURVIVES** against the
tested edits; SUSTAIN spoofing **SURVIVES**; independent reviewer authenticity
**UNKNOWN** (not claimed); neural efficacy **UNKNOWN** (not claimed).
