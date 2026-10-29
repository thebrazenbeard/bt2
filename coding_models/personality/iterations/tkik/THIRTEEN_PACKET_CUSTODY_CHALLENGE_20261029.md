# Thirteen Bridge hostile review — T’Kal packet custody

Subject: BT2 Draft PR #101 `75599e6a823ef5b7b061d57e87f6dece043d078a`.

The executed T’Kal `Case` **did** reach `REFINE` using the exact pinned external `tkik/core.py`, and its result correctly denies neural inference or independent model-host attestation. That supports a *protocol replay*, not authenticated testimony from the reviewer IDs written in the JSON packet.

## Reproduced falsifier

I replaced one reviewer ID in a copy of the input packet with `/root/fabricated-undispatched-agent`. With no actual native dispatch for that string, the unchanged `run()` accepted the packet, invoked the pinned `Case` and returned `REFINE`, while emitting the arbitrary value in `native_reviewer_ids`.

This matters because a consumer could treat that field as an observed invocation fact. Three unique names only establish a syntactic property of the supplied packet. The external protocol explicitly does not authenticate its participants or supply a durable signed ledger.

**Disposition: REFINE.** Retain `REFINE` as the outcome of a deterministic, externally pinned *packet replay*; rename the field to `declared_reviewer_ids` and explicitly set `native_dispatch_receipts_verified=false`, `live_cross_examination_attested=false`, `protocol_mode=PACKET_REPLAY`. Preserve the original V1 result as historical evidence; a V2 result should be generated and checked at the exact source revision. The actual collaboration dispatch receipts may be referenced independently, but they do not originate from this replay engine.

The regression in `tests/test_bt2_tkik_provenance_claims.py` exercises the real pinned T’Kal core with that fabricated identifier. It failed on the original PR #101 and is meant to turn green only after the separate protocol-output repair. No one is claiming that Thirteen's historical GGUF executed this review.
