# ChatGPT export graph parser — synthetic source candidate

`chat_export_parser.scan_conversations_json(payload, custody_key=...)` is a
**bounded, in-memory, no-I/O validator**, not a deployed export importer.
It handles one narrow ChatGPT `conversations.json`-style JSON shape:
an array of records with an `id` and a rooted `mapping` of parent/child node
identities. Message nodes must have a recognized `author.role` and text-only
`content.parts` containing strings. Empty structural root messages are allowed.
Other historical or multimodal export variants fail closed rather than being
silently interpreted as text. No actual private export was used to establish
coverage of those variants.

The caller must provide a byte string under the default 8 MiB cap and a
secret 16–512 byte HMAC key. Conversation, node, message, text-part, and
character caps apply; malformed graphs, duplicate IDs, duplicate JSON keys,
non-finite constants, and unsupported shapes raise `ChatExportParseError`.
The returned frozen summary carries counts, an HMAC-derived opaque ID and
`PRIVATE_HOLD_UNVERIFIED` only. Raw titles, message contents, and source IDs are
not returned. The opaque IDs are pseudonyms that can be correlated if the same
key and order are reused; they are not anonymous, durable content hashes,
signed source receipts, or proof of authenticity. A malicious Python caller
can still inspect input bytes or serialize the benign summary manually.

The parser does **not** open or extract ZIP files, stream downloads, pin an
immutable provider revision, prove coherent bytes, protect memory from a
same-process actor, persist transcripts, decide rights, admit model training,
write to STM or DeepMemoryStorage, or publish to GitHub. Production use needs
private source acquisition, byte custody, schema version review, independent
host security qualification, privacy and license adjudication, and explicit
downstream authorization. The existing Windows/WSL intake HOLD is unchanged.

Run synthetic tests:

```sh
python -m unittest source_recovery.tests.test_chat_export_parser -v
python -m unittest discover -s source_recovery/tests -p 'test_*.py' -q
```
