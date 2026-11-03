"""Bounded, in-memory, held-only parser for one ChatGPT export graph shape.

This is a *synthetic/source-only* contract, not an archive downloader,
extractor, verified custody mechanism, transcript publisher, memory importer,
or training-data admission gate. Unsupported export variants fail closed.
No filesystem, network, or persistence operations occur in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import math


class ChatExportParseError(ValueError):
    """Input is unsupported, malformed, or exceeds a review bound."""


_ROLES = frozenset({"user", "assistant", "system", "developer", "tool"})
_STATUS = "PRIVATE_HOLD_UNVERIFIED"


@dataclass(frozen=True)
class HeldConversation:
    opaque_id: str
    node_count: int
    message_count: int
    text_part_count: int
    text_character_count: int
    status: str = _STATUS

    def __post_init__(self) -> None:
        if not (type(self.opaque_id) is str and self.opaque_id.startswith("CONV_")
                and len(self.opaque_id) == 37
                and all(char in "0123456789ABCDEF" for char in self.opaque_id[5:])
                and type(self.status) is str and self.status == _STATUS
                and all(type(value) is int and value >= 0 for value in
                        (self.node_count, self.message_count,
                         self.text_part_count, self.text_character_count))
                and self.node_count >= 1 and self.message_count <= self.node_count):
            raise ChatExportParseError("INVALID_HELD_SUMMARY")


@dataclass(frozen=True)
class HeldChatExport:
    records: tuple[HeldConversation, ...]
    conversation_count: int
    message_count: int
    text_part_count: int
    text_character_count: int
    status: str = _STATUS

    def __post_init__(self) -> None:
        if (type(self.records) is not tuple
                or not all(type(row) is HeldConversation for row in self.records)
                or type(self.status) is not str or self.status != _STATUS
                or any(type(value) is not int or value < 0 for value in
                       (self.conversation_count, self.message_count,
                        self.text_part_count, self.text_character_count))
                or self.conversation_count != len(self.records)
                or self.message_count != sum(r.message_count for r in self.records)
                or self.text_part_count != sum(r.text_part_count for r in self.records)
                or self.text_character_count != sum(r.text_character_count for r in self.records)):
            raise ChatExportParseError("INVALID_HELD_EXPORT")

    def to_public_json(self) -> str:
        raise ChatExportParseError("PUBLIC_SERIALIZATION_FORBIDDEN")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    row: dict[str, object] = {}
    for key, value in pairs:
        if key in row:
            raise ChatExportParseError("DUPLICATE_JSON_KEY")
        row[key] = value
    return row


def _reject_constant(_: str) -> object:
    raise ChatExportParseError("NONFINITE_JSON_NUMBER")


def _finite_float(value: str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise ChatExportParseError("NONFINITE_JSON_NUMBER")
    return converted


def _id(value: object) -> str:
    if (type(value) is not str or not (1 <= len(value) <= 256)
            or not value.isprintable()):
        raise ChatExportParseError("INVALID_GRAPH_ID")
    return value


def _node_message_counts(node: dict, *, max_text_chars: int) -> tuple[int, int, int]:
    message = node.get("message")
    if message is None:
        return 0, 0, 0  # The export graph may contain a structural root.
    if type(message) is not dict:
        raise ChatExportParseError("INVALID_MESSAGE")
    author = message.get("author")
    content = message.get("content")
    role = author.get("role") if type(author) is dict else None
    if (type(author) is not dict or type(role) is not str or role not in _ROLES
            or type(content) is not dict
            or content.get("content_type") != "text"
            or type(content.get("parts")) is not list):
        raise ChatExportParseError("UNSUPPORTED_MESSAGE_SHAPE")
    parts = content["parts"]
    if len(parts) > 128:
        raise ChatExportParseError("TOO_MANY_TEXT_PARTS")
    characters = 0
    for part in parts:
        if type(part) is not str:
            raise ChatExportParseError("UNSUPPORTED_TEXT_PART")
        characters += len(part)
        if characters > max_text_chars:
            raise ChatExportParseError("TEXT_LIMIT_EXCEEDED")
    return 1, len(parts), characters


def _conversation_summary(record: object, key: bytes, *, position: int,
                          max_nodes: int, max_messages: int,
                          max_text_chars: int) -> HeldConversation:
    if type(record) is not dict:
        raise ChatExportParseError("INVALID_CONVERSATION")
    conversation_id = _id(record.get("id"))
    mapping = record.get("mapping")
    if type(mapping) is not dict or not 1 <= len(mapping) <= max_nodes:
        raise ChatExportParseError("INVALID_GRAPH_SIZE")

    parents: dict[str, str | None] = {}
    children: dict[str, tuple[str, ...]] = {}
    messages = parts = chars = 0
    for raw_node_id, node in mapping.items():
        node_id = _id(raw_node_id)
        if type(node) is not dict or _id(node.get("id")) != node_id:
            raise ChatExportParseError("MAPPING_NODE_ID_MISMATCH")
        parent = node.get("parent")
        if parent is not None:
            parent = _id(parent)
        raw_children = node.get("children")
        if type(raw_children) is not list or len(raw_children) > max_nodes:
            raise ChatExportParseError("INVALID_CHILDREN")
        outgoing = tuple(_id(child) for child in raw_children)
        if len(set(outgoing)) != len(outgoing):
            raise ChatExportParseError("DUPLICATE_CHILD")
        parents[node_id] = parent
        children[node_id] = outgoing
        m, p, c = _node_message_counts(node, max_text_chars=max_text_chars)
        messages += m
        parts += p
        chars += c
        if messages > max_messages or chars > max_text_chars:
            raise ChatExportParseError("MESSAGE_OR_TEXT_LIMIT_EXCEEDED")

    roots = [node for node, parent in parents.items() if parent is None]
    if len(roots) != 1:
        raise ChatExportParseError("INVALID_ROOT_COUNT")
    for node_id, parent in parents.items():
        if parent is not None and (parent not in children
                                   or node_id not in children[parent]):
            raise ChatExportParseError("MISSING_REVERSE_PARENT_LINK")
        for child in children[node_id]:
            if child not in parents or parents[child] != node_id:
                raise ChatExportParseError("MISSING_REVERSE_CHILD_LINK")

    # A single connected, rooted tree excludes dangling subgraphs and cycles.
    visited: set[str] = set()
    pending = [roots[0]]
    while pending:
        node_id = pending.pop()
        if node_id in visited:
            raise ChatExportParseError("GRAPH_CYCLE_OR_DUPLICATE_PATH")
        visited.add(node_id)
        pending.extend(children[node_id])
    if len(visited) != len(parents):
        raise ChatExportParseError("DISCONNECTED_GRAPH")

    # Keyed ID is only a pseudonym for the caller's observation. No source
    # revision, license, principal, or authenticity is attested by this HMAC.
    pseudonym = hmac.new(key, f"{position}\0{conversation_id}".encode(),
                         hashlib.sha256).hexdigest()[:32].upper()
    return HeldConversation(f"CONV_{pseudonym}", len(mapping), messages, parts, chars)


def scan_conversations_json(payload: bytes, *, custody_key: bytes,
                            max_bytes: int = 8 * 1024 * 1024,
                            max_conversations: int = 256,
                            max_nodes: int = 4096,
                            max_messages: int = 8192,
                            max_text_chars: int = 1_000_000) -> HeldChatExport:
    """Validate bounded JSON bytes without exposing titles or message text.

    Accepts only a list with ``id`` + ``mapping`` tree records and text-only
    messages. It deliberately does not normalize all historical export
    versions. Unknown shapes raise a generic hold error.
    """
    if (type(payload) is not bytes or type(custody_key) is not bytes
            or not 16 <= len(custody_key) <= 512
            or any(type(limit) is not int or limit < 1 for limit in
                   (max_bytes, max_conversations, max_nodes, max_messages, max_text_chars))):
        raise ChatExportParseError("INVALID_PARSER_INPUT")
    if len(payload) > max_bytes:
        raise ChatExportParseError("BYTE_LIMIT_EXCEEDED")
    parse_failed = False
    decoded: object = None
    try:
        decoded = json.loads(payload, object_pairs_hook=_object_pairs,
                             parse_constant=_reject_constant,
                             parse_float=_finite_float)
    except (ValueError, UnicodeError, RecursionError):
        # JSONDecodeError.doc and UnicodeDecodeError.object can retain the
        # complete private input. Raising outside the handler prevents the
        # public error's cause/context from holding those exceptions.
        parse_failed = True
    if parse_failed:
        raise ChatExportParseError("INVALID_JSON")
    if type(decoded) is not list or len(decoded) > max_conversations:
        raise ChatExportParseError("UNSUPPORTED_EXPORT_ROOT")

    records: list[HeldConversation] = []
    ids: set[str] = set()
    messages = parts = chars = 0
    for index, item in enumerate(decoded):
        if type(item) is not dict:
            raise ChatExportParseError("INVALID_CONVERSATION")
        identifier = _id(item.get("id"))
        if identifier in ids:
            raise ChatExportParseError("DUPLICATE_CONVERSATION_ID")
        ids.add(identifier)
        result = _conversation_summary(item, custody_key, position=index,
                                       max_nodes=max_nodes,
                                       max_messages=max_messages,
                                       max_text_chars=max_text_chars)
        records.append(result)
        messages += result.message_count
        parts += result.text_part_count
        chars += result.text_character_count
        if messages > max_messages or chars > max_text_chars:
            raise ChatExportParseError("EXPORT_LIMIT_EXCEEDED")
    return HeldChatExport(tuple(records), len(records), messages, parts, chars)
