"""Offline fail-closed tests for exact donor and companion license custody."""

from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import personality_donor_provenance as p  # noqa: E402


class DonorProvenanceTests(unittest.TestCase):
    def test_exact_official_snapshot_constants(self):
        self.assertEqual(len(p.DONOR_REVISION), 40)
        self.assertEqual(p.DONOR_REPO, "Qwen/Qwen2.5-Coder-1.5B-Instruct")
        self.assertEqual(p.DONOR_WEIGHTS_SHA256,
                         "c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8")
        self.assertEqual(p.DONOR_LICENSE_SHA256,
                         "832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e")

    def test_missing_tampered_license_and_false_revision_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "bt2"
            source.mkdir()
            with self.assertRaisesRegex(ValueError, "missing from BT2"):
                p.verify_donor_identity(base, p.DONOR_WEIGHTS_SHA256, bt2=source)
            license_file = source / p.UPSTREAM_LICENSE_SOURCE
            license_file.parent.mkdir(parents=True)
            license_file.write_bytes((Path(__file__).resolve().parents[1] /
                                      p.UPSTREAM_LICENSE_SOURCE).read_bytes())
            receipt = p.verify_donor_identity(base, p.DONOR_WEIGHTS_SHA256, bt2=source)
            self.assertEqual(receipt["license_sha256"], p.DONOR_LICENSE_SHA256)
            with self.assertRaisesRegex(ValueError, "not the pinned Qwen"):
                p.verify_donor_identity(base, "a" * 64, receipt, bt2=source)
            with self.assertRaisesRegex(ValueError, "provenance receipt"):
                p.verify_donor_identity(base, p.DONOR_WEIGHTS_SHA256,
                                        dict(receipt, repo_revision="1" * 40), bt2=source)
            license_file.write_bytes(license_file.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "LICENSE differs"):
                p.verify_donor_identity(base, p.DONOR_WEIGHTS_SHA256, receipt, bt2=source)

    def test_companion_files_are_copied_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "donor"
            base.mkdir()
            upstream_license = (Path(__file__).resolve().parents[1] /
                                p.UPSTREAM_LICENSE_SOURCE).read_bytes()
            source = root / "bt2"
            notice = source / p.NOTICE_SOURCE
            notice.parent.mkdir(parents=True)
            notice.write_text(
                f"Modification of {p.DONOR_REPO} revision {p.DONOR_REVISION}\n",
                encoding="utf-8")
            license_file = source / p.UPSTREAM_LICENSE_SOURCE
            license_file.parent.mkdir(parents=True)
            license_file.write_bytes(upstream_license)
            output = root / "fresh-gguf"
            output.mkdir()
            receipt = p.verify_donor_identity(base, p.DONOR_WEIGHTS_SHA256, bt2=source)
            hashes = p.copy_attribution_companions(
                base=base, bt2=source, output=output, provenance=receipt)
            self.assertEqual((output / p.LICENSE_COMPANION).read_bytes(), upstream_license)
            self.assertEqual(hashes[p.NOTICE_COMPANION],
                             p.sha256_file(output / p.NOTICE_COMPANION))
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                p.copy_attribution_companions(
                    base=base, bt2=source, output=output, provenance=receipt)


if __name__ == "__main__":
    unittest.main()
