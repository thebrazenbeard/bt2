"""Synthetic-only tests for the held ChatGPT conversation graph parser."""

import json
import unittest

from source_recovery.chat_export_parser import (
    ChatExportParseError,
    HeldChatExport,
    HeldConversation,
    scan_conversations_json,
)


KEY = b"synthetic-parser-key-not-for-production"


def sample():
    return [{
        "id": "synthetic-conversation-1",
        "title": "PRIVATE_TITLE_SENTINEL",
        "mapping": {
            "root": {"id": "root", "parent": None,
                     "children": ["user"], "message": None},
            "user": {"id": "user", "parent": "root",
                     "children": ["assistant"], "message": {
                         "author": {"role": "user"},
                         "content": {"content_type": "text", "parts": ["PRIVATE_CONTENT_SENTINEL"]}}},
            "assistant": {"id": "assistant", "parent": "user",
                          "children": [], "message": {
                              "author": {"role": "assistant"},
                              "content": {"content_type": "text", "parts": ["reply"]}}},
        }
    }]


def parse(data):
    return scan_conversations_json(json.dumps(data).encode(), custody_key=KEY)


class ChatExportParserTests(unittest.TestCase):
    def test_valid_synthetic_tree_returns_held_content_free_summary(self):
        result = parse(sample())
        self.assertEqual(result.conversation_count, 1)
        self.assertEqual(result.message_count, 2)
        self.assertEqual(result.text_part_count, 2)
        self.assertEqual(result.records[0].status, "PRIVATE_HOLD_UNVERIFIED")
        self.assertTrue(result.records[0].opaque_id.startswith("CONV_"))
        rendered = repr(result) + str(result.__dict__)
        self.assertNotIn("PRIVATE_CONTENT_SENTINEL", rendered)
        self.assertNotIn("PRIVATE_TITLE_SENTINEL", rendered)
        self.assertNotIn("synthetic-conversation-1", rendered)
        with self.assertRaises(ChatExportParseError):
            result.to_public_json()

    def test_top_level_and_repeated_json_fields_fail_closed(self):
        bad_float = json.dumps(sample()).encode().replace(b'"mapping":', b'"time": 1e9999, "mapping":')
        for payload in (b"{}", b"null", b"[{\"id\":\"a\",\"id\":\"b\"}]",
                        b"[NaN]", bad_float):
            with self.subTest(payload=payload), self.assertRaises(ChatExportParseError):
                scan_conversations_json(payload, custody_key=KEY)

    def test_bytes_and_record_limits_apply_before_expansion(self):
        payload = json.dumps(sample()).encode()
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(payload, custody_key=KEY, max_bytes=len(payload) - 1)
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(payload, custody_key=KEY, max_conversations=0)
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(payload, custody_key=KEY, max_messages=1)
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(payload, custody_key=KEY, max_text_chars=5)

    def test_bad_graph_reference_cycle_and_bidirectional_mismatch_rejected(self):
        data = sample()
        data[0]["mapping"]["assistant"]["children"] = ["root"]
        with self.assertRaises(ChatExportParseError):
            parse(data)
        data = sample()
        data[0]["mapping"]["user"]["parent"] = "missing"
        with self.assertRaises(ChatExportParseError):
            parse(data)
        data = sample()
        data[0]["mapping"]["root"]["children"] = []
        with self.assertRaises(ChatExportParseError):
            parse(data)

    def test_unknown_content_shape_and_unsupported_role_hold(self):
        data = sample()
        data[0]["mapping"]["user"]["message"]["content"]["parts"] = [{"image": "private"}]
        with self.assertRaises(ChatExportParseError):
            parse(data)
        data = sample()
        data[0]["mapping"]["user"]["message"]["author"]["role"] = "unexpected"
        with self.assertRaises(ChatExportParseError):
            parse(data)
        for malformed_role in ({}, [], 7, None):
            data = sample()
            data[0]["mapping"]["user"]["message"]["author"]["role"] = malformed_role
            with self.subTest(role=repr(malformed_role)):
                with self.assertRaises(ChatExportParseError):
                    parse(data)

    def test_key_required_and_pseudonyms_depend_on_key(self):
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(json.dumps(sample()).encode(), custody_key=b"short")
        alt = scan_conversations_json(json.dumps(sample()).encode(), custody_key=b"other-synthetic-key-for-test-only")
        self.assertNotEqual(parse(sample()).records[0].opaque_id, alt.records[0].opaque_id)

    def test_held_status_cannot_be_forged_through_dataclass_construction(self):
        valid = parse(sample())
        with self.assertRaises(ChatExportParseError):
            HeldConversation(valid.records[0].opaque_id, 3, 2, 2, 5, status="VERIFIED")
        with self.assertRaises(ChatExportParseError):
            HeldConversation(valid.records[0].opaque_id, -1, 2, 2, 5)
        with self.assertRaises(ChatExportParseError):
            HeldChatExport(valid.records, 1, 2, 2, 5, status="PUBLIC_APPROVED")
        with self.assertRaises(ChatExportParseError):
            HeldChatExport(valid.records, 1, 999, 2, 5)

    def test_duplicate_conversation_and_non_utf8_hold(self):
        with self.assertRaises(ChatExportParseError):
            parse(sample() + sample())
        with self.assertRaises(ChatExportParseError):
            scan_conversations_json(b"\xff", custody_key=KEY)

    def test_invalid_utf8_error_carries_no_raw_content_in_cause_or_context(self):
        for private in (b"\xffPRIVATE_INVALID_UTF8_BYTES",
                        b'{"s":"PRIVATE_MALFORMED_JSON",}'):
            with self.subTest(kind=private[:1]):
                with self.assertRaises(ChatExportParseError) as caught:
                    scan_conversations_json(private, custody_key=KEY)
                self.assertEqual(str(caught.exception), "INVALID_JSON")
                self.assertIsNone(caught.exception.__cause__)
                self.assertIsNone(caught.exception.__context__)


if __name__ == "__main__":
    unittest.main()
