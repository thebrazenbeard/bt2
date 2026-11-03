"""Synthetic, metadata-only cloud inventory contract; no connector or local files."""

import dataclasses
import json
import unittest

from source_recovery.cloud_metadata_inventory import (
    CloudInventoryError,
    HeldCloudArtifact,
    HeldCloudInventory,
    build_held_cloud_inventory,
)


KEY = b"synthetic-custody-key-for-tests-only"


def item(number, *, kind="file", size=3, **changes):
    row = {
        "drive_id": "synthetic-drive",
        "item_id": f"synthetic-item-{number}",
        "name": f"example-{number}.txt" if kind == "file" else f"example-{number}",
        "kind": kind,
        "size": size if kind == "file" else 0,
        "e_tag": f"version-{number}",
    }
    row.update(changes)
    return row


def inventory(rows, *, page_sizes=None, **options):
    if page_sizes is None:
        page_sizes = (len(rows),)
    arguments = dict(custody_key=KEY, page_sizes=page_sizes,
                     expected_count=len(rows), exhausted=True)
    arguments.update(options)
    return build_held_cloud_inventory(rows, **arguments)


class CloudMetadataInventoryTests(unittest.TestCase):
    def test_hold_records_are_schema_compatible_and_contain_no_raw_identifiers(self):
        rows = [item(1), item(2, kind="folder")]
        result = inventory(rows)
        self.assertEqual((result.total_entries, result.files, result.folders, result.total_bytes),
                         (2, 1, 1, 3))
        self.assertNotEqual(result.records[0].artifact_id, result.records[1].artifact_id)
        self.assertTrue(result.records[0].artifact_id.startswith("CLD_"))
        self.assertTrue(result.records[0].raw_material_git_eligible is False)
        self.assertEqual(result.records[0].public_admission, "HOLD")
        self.assertEqual(result.records[0].rights, "UNVERIFIED")
        self.assertEqual(result.records[0].evidence_class, "INVENTORY")
        self.assertEqual(result.records[0].source_state, "HISTORICAL_NOT_INSTALLED")
        self.assertEqual(result.records[0].privacy, "PRIVATE_HOLD")
        private = result.to_private_adjudication_records()
        self.assertEqual(private[0]["private_locator"], "REDACTED")
        self.assertEqual(private[0]["schema"], "BT2_HISTORICAL_EXPORT_ADJUDICATION_V1")
        self.assertEqual(private[0]["target_repo_candidate"], None)
        text = repr(result) + str(private) + repr(dataclasses.asdict(result))
        for secret in ("synthetic-drive", "synthetic-item-1", "example-1.txt", "version-1"):
            self.assertNotIn(secret, text)
        self.assertRaises(CloudInventoryError, result.to_public_json)
        self.assertRaises(TypeError, json.dumps, result)

    def test_rejects_duplicate_missing_and_ambiguous_identities(self):
        bad_rows = ([item(1), item(1)], [item(1, drive_id="")],
                    [item(1, item_id=None)], [item(1, drive_id="d/invalid")],
                    [item(1, item_id=" a ")], [item(1, item_id="../escape")])
        for rows in bad_rows:
            with self.subTest(case=len(rows), rows=type(rows[0].get("item_id")).__name__):
                with self.assertRaises(CloudInventoryError):
                    inventory(rows)

    def test_rejects_shortcuts_unknown_keys_secret_fields_and_names(self):
        for changes in (
            {"remote_item": {}}, {"shortcut": True}, {"content": "secret bytes"},
            {"access_token": "secret bytes"}, {"password": "secret bytes"},
            {"name": "../unsafe"}, {"name": "nested/file"},
            {"name": "C:\\unsafe"}, {"name": "password-store.txt"},
            {"name": ".env"}, {"name": "notes\x00x"}, {"name": "CON"},
            {"name": "file. "}, {"kind": "shortcut"},
            {"name": "unsafe-\ud800.txt"},
        ):
            with self.subTest(case=tuple(changes)):
                with self.assertRaises(CloudInventoryError) as caught:
                    inventory([item(1, **changes)])
                self.assertNotIn("secret bytes", str(caught.exception))

    def test_rejects_completeness_ambiguity_and_cap_200(self):
        rows = [item(i) for i in range(200)]
        with self.assertRaises(CloudInventoryError):
            inventory(rows)
        with self.assertRaises(CloudInventoryError):
            inventory(rows, page_sizes=(100, 100), exhausted=False)
        with self.assertRaises(CloudInventoryError):
            build_held_cloud_inventory(rows, custody_key=KEY, page_sizes=(199,),
                                       expected_count=200, exhausted=True)
        with self.assertRaises(CloudInventoryError):
            build_held_cloud_inventory(rows, custody_key=KEY, page_sizes=(200,),
                                       expected_count=201, exhausted=True)
        with self.assertRaises(CloudInventoryError):
            inventory(rows, failed_pages=1)
        with self.assertRaises(CloudInventoryError):
            inventory(rows, capped=True)
        accepted = inventory([item(i) for i in range(355)], page_sizes=(200, 155))
        self.assertEqual(accepted.total_entries, 355)

    def test_version_tag_changes_and_missing_second_pass_fail_closed(self):
        current = [item(1), item(2)]
        self.assertEqual(inventory(current, previous_items=current).total_entries, 2)
        for previous in ([item(1, e_tag="older"), item(2)],
                         [item(1, name="renamed.txt"), item(2)],
                         [item(1)], [item(1), item(2), item(3)]):
            with self.subTest(previous_count=len(previous)):
                with self.assertRaises(CloudInventoryError):
                    inventory(current, previous_items=previous)
        for row in (item(1, e_tag=""), item(1, e_tag=None)):
            with self.assertRaises(CloudInventoryError):
                inventory([row])

    def test_untrusted_subclasses_and_bad_limits_fail_closed(self):
        class HostileText(str):
            def __hash__(self):
                raise AssertionError("must not use a hostile hash")

        for row in (item(1, name=HostileText("harmless.txt")),
                    item(1, size=-1), item(1, size=True),
                    item(1, size=2**64), item(1, kind="folder") | {"size": 1}):
            with self.assertRaises(CloudInventoryError):
                inventory([row])
        with self.assertRaises(CloudInventoryError):
            build_held_cloud_inventory([item(1)], custody_key=b"short",
                                       page_sizes=(1,), expected_count=1, exhausted=True)
        with self.assertRaises(CloudInventoryError):
            build_held_cloud_inventory([item(1)], custody_key=KEY,
                                       page_sizes=(1,), expected_count=1, exhausted="yes")

    def test_unknown_nested_graph_data_never_implicitly_allowed(self):
        for row in (item(1, parent_reference={"drive_id": "x"}),
                    item(1, e_tag={"value": "v"}),
                    item(1, name="share-link.url"),
                    item(1, name=".ssh")):
            with self.assertRaises(CloudInventoryError):
                inventory([row])

    def test_manual_record_spoofing_does_not_bypass_held_constants(self):
        for constructed in (
            lambda: HeldCloudArtifact("raw-drive-and-item"),
            lambda: HeldCloudArtifact("CLD_" + "A" * 32, rights="VERIFIED"),
            lambda: HeldCloudArtifact("CLD_" + "A" * 32, public_admission="APPROVED"),
            lambda: HeldCloudArtifact("CLD_" + "A" * 32, raw_material_git_eligible=True),
        ):
            with self.assertRaises(CloudInventoryError):
                constructed()

    def test_graph_like_bang_identifiers_are_hmaced_without_public_echo(self):
        held = inventory([item(1, drive_id="synthetic!drive", item_id="synthetic!item")])
        self.assertNotIn("synthetic!", repr(held))

    def test_opaque_observation_id_changes_with_revision_name_size_and_kind(self):
        baseline = inventory([item(1)]).records[0].artifact_id
        variants = (
            item(1, e_tag="new-version"),
            item(1, name="renamed.txt"),
            item(1, size=4),
            item(1, kind="folder"),
        )
        for changed in variants:
            with self.subTest(changed=tuple(changed)):
                self.assertNotEqual(inventory([changed]).records[0].artifact_id, baseline)

    def test_manual_inventory_status_and_counter_forgery_fail_closed(self):
        real_record = inventory([item(1)]).records[0]
        forged = (
            lambda: HeldCloudInventory((), 0, 0, 0, 0, "VERIFIED"),
            lambda: HeldCloudInventory((real_record,), 1, 1, 0, 3, True),
            lambda: HeldCloudInventory((real_record,), 0, 0, 0, 0),
            lambda: HeldCloudInventory((real_record,), 1, 0, 0, 0),
            lambda: HeldCloudInventory((real_record,), True, 1, 0, 3),
            lambda: HeldCloudInventory((real_record,), 1, -1, 2, 3),
            lambda: HeldCloudInventory((real_record,), 1, 1, 0, -3),
            lambda: HeldCloudInventory((real_record, real_record), 2, 2, 0, 6),
            lambda: HeldCloudInventory(("CLD_" + "A" * 32,), 1, 1, 0, 3),
            lambda: HeldCloudInventory([real_record], 1, 1, 0, 3),
        )
        for construct in forged:
            with self.assertRaises(CloudInventoryError):
                construct()


if __name__ == "__main__":
    unittest.main()
