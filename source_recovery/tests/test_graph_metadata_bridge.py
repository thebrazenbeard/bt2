"""Synthetic list-child/Get-Drive-Item metadata pairing; no cloud interaction."""

import dataclasses
import unittest

from source_recovery.cloud_metadata_inventory import CloudInventoryError
from source_recovery.graph_metadata_bridge import build_held_inventory_from_graph_metadata


KEY = b"synthetic-private-hmac-key-for-testing"


def child(n, kind="file", **changes):
    row = {"id": f"synthetic-item-{n}", "name": f"example-{n}.txt",
           "size": 9 if kind == "file" else 0,
           "parent_reference": {"drive_id": "synthetic!drive"}, kind: {}}
    row.update(changes)
    return row


def exact(item, *, tag="synthetic-v1", **changes):
    updated = dict(item)
    updated["e_tag"] = tag
    updated.update(changes)
    return {"request": {"drive_id": item["parent_reference"]["drive_id"],
                        "item_id": item["id"]},
            "status": 200, "item": updated}


def bridge(children, lookups=None, *, page_sizes=None, **options):
    if lookups is None:
        lookups = [exact(row) for row in children]
    if page_sizes is None:
        page_sizes = (len(children),)
    call = dict(custody_key=KEY, page_sizes=page_sizes,
                expected_count=len(children), exhausted=True)
    call.update(options)
    return build_held_inventory_from_graph_metadata(children, lookups, **call)


class GraphMetadataBridgeTests(unittest.TestCase):
    def test_exact_metadata_lookup_adds_etag_without_output_leakage(self):
        rows = [child(1), child(2, "folder")]
        output = bridge(rows)
        self.assertEqual((output.total_entries, output.files, output.folders, output.total_bytes),
                         (2, 1, 1, 9))
        self.assertEqual(output.status, "PRIVATE_HOLD_UNVERIFIED")
        self.assertTrue(all(x.public_admission == "HOLD" for x in output.records))
        printed = repr(output) + repr(dataclasses.asdict(output))
        for raw in ("synthetic!drive", "synthetic-item-1", "example-1.txt", "synthetic-v1"):
            self.assertNotIn(raw, printed)
        with self.assertRaises(CloudInventoryError):
            output.to_public_json()

    def test_every_child_requires_a_unique_exact_id_lookup(self):
        rows = [child(1), child(2)]
        bads = (
            [exact(rows[0])],
            [exact(rows[0]), exact(rows[0])],
            [exact(rows[0]), dict(exact(rows[1]), request={
                "drive_id": "synthetic!drive", "item_id": "not-same"})],
            [exact(rows[0]), dict(exact(rows[1]), status=304)],
            [exact(rows[0]), dict(exact(rows[1]), status=None)],
        )
        for lookups in bads:
            with self.subTest(shape=len(lookups)):
                with self.assertRaises(CloudInventoryError):
                    bridge(rows, lookups)

    def test_exact_response_must_match_list_name_size_kind_and_drive(self):
        row = child(1)
        wrongs = (
            exact(row, id="synthetic-other"),
            exact(row, name="renamed.txt"),
            exact(row, size=10),
            exact(row, folder={}),
            exact(row, parent_reference={"drive_id": "synthetic-other"}),
            exact(row, e_tag=""),
            exact(row, e_tag=None),
        )
        for lookup in wrongs:
            with self.subTest(case=tuple(lookup["item"])):
                with self.assertRaises(CloudInventoryError):
                    bridge([row], [lookup])

    def test_missing_revision_304_shortcut_and_secret_fields_fail_closed(self):
        row = child(1)
        risky_list = (
            child(1, remote_item={}), child(1, remoteItem={}),
            child(1, shortcut=True), child(1, content="secret"),
            child(1, web_url="https://synthetic.invalid/private"),
            child(1, e_tag="already-in-list"),
            child(1, **{"@odata.nextLink": "https://synthetic.invalid/cursor"}),
            child(1, name="secrets-token.txt"),
            child(1, name="bad\ud800.txt"),
            child(1, file={"@microsoft.graph.downloadUrl": "secret"}),
        )
        for risky in risky_list:
            with self.subTest(keys=tuple(risky)):
                with self.assertRaises(CloudInventoryError) as caught:
                    bridge([risky])
                self.assertNotIn("synthetic.invalid", str(caught.exception))
        for get in (exact(row, remoteItem={}), exact(row, access_token="secret"),
                    exact(row, e_tag=""), exact(row, e_tag=None),
                    dict(exact(row), item=row),
                    exact(row, file={"hashes": {"sha1Hash": "secret"}})):
            with self.assertRaises(CloudInventoryError):
                bridge([row], [get])

    def test_stability_pass_rejects_etag_and_metadata_drift(self):
        rows = [child(1), child(2)]
        first = [exact(row) for row in rows]
        self.assertEqual(bridge(rows, first, verification_children=rows,
                                verification_lookups=first).total_entries, 2)
        for verification in (
            [exact(rows[0], tag="synthetic-v2"), exact(rows[1])],
            [exact(rows[0]), exact(rows[1], size=8)],
            [exact(rows[0])],
        ):
            with self.assertRaises(CloudInventoryError):
                bridge(rows, first, verification_lookups=verification)
        for relisted in ([child(1, name="changed.txt"), child(2)],
                         [child(1), child(3)],
                         [child(1)]):
            with self.assertRaises(CloudInventoryError):
                bridge(rows, first, verification_children=relisted,
                       verification_lookups=first)

    def test_pagination_ambiguity_remains_held(self):
        rows = [child(i) for i in range(200)]
        with self.assertRaises(CloudInventoryError):
            bridge(rows)
        good = [child(i) for i in range(205)]
        self.assertEqual(bridge(good, page_sizes=(200, 5)).total_entries, 205)
        with self.assertRaises(CloudInventoryError):
            bridge(good, page_sizes=(200, 5), exhausted=False)

    def test_type_spoofing_and_graph_null_fail_closed(self):
        row = child(1)
        malformed = (child(1, parent_reference=None), child(1, file=None),
                     child(1, id=""), child(1, size=True),
                     child(1, parent_reference={"drive_id": "synthetic!drive", "extra": "secret"}))
        for bad in malformed:
            with self.assertRaises(CloudInventoryError):
                bridge([bad], [exact(row)])
        with self.assertRaises(CloudInventoryError):
            bridge([row], [dict(exact(row), status="200")])
        with self.assertRaises(CloudInventoryError):
            bridge([row], [dict(exact(row), item=None)])


if __name__ == "__main__":
    unittest.main()
