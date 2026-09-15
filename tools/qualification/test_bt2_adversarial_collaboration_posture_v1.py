from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native" / "project"
UPLOAD_SHA256 = "828a3995dd0e49999c7ebc51753cfa17508935b45b99c01c79f456845994826f"
V3_INSTRUCTIONS_SHA256 = "b00eb5fa3815ecddcc66cc29c646311bfe41095ab17a91c6f8c6d6ab7cb056bb"
V3_MANIFEST_SHA256 = "0886fd0b7521e89ca7b1367db2d130b9511ec508c41fe9dadef7cea05a670566"
V3_INSTALL_SHA256 = "bd0344b2072a927f0936bef25198a1e8bc1fe592cbeb1e9d3ee984a4d73a73a2"

INSTRUCTION_BLOCK = """## Adversarial collaboration posture
When Patrick advances a proposal, proposed solution, architecture, mechanism, workflow, or implementation path, every BT2 role/lane must take his words literally first and treat the literal proposition as unproven.
Direct commands and factual requests with no embedded proposal do not trigger this review sequence.
Attack its assumptions, necessity, architecture, consequences, alternatives, failure modes, hidden dependencies, and whether the proposed way is desirable. Try to kill the literal proposition without weakening, reinterpreting, or quietly improving it.
If the literal proposition survives serious adversarial review, say so, support it, and help make it work. Do not manufacture objections merely to appear adversarial.
If it fails, do not stop at rejection. Only then infer the underlying objective, preserve that objective while discarding the failed implementation assumption, and search for a stronger solution.
Do not substitute inferred intent or a repaired proposition before the literal proposition has been tested. UNKNOWN is not SURVIVES.
This changes evaluation discipline only; it grants no protected-effect authority.
"""


def canonical_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = canonical_bytes(path)
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_bytes(ref: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)


class AdversarialCollaborationPostureQualification(unittest.TestCase):
    def test_v3_subjects_are_unchanged(self) -> None:
        self.assertEqual(sha256(NATIVE / "PROJECT_INSTRUCTIONS_V3.md"), V3_INSTRUCTIONS_SHA256)
        self.assertEqual(sha256(NATIVE / "PROJECT_FILES_MANIFEST_V3.json"), V3_MANIFEST_SHA256)
        self.assertEqual(sha256(NATIVE / "INSTALL_V3.md"), V3_INSTALL_SHA256)

    def test_exact_posture_is_preserved_as_native_project_file(self) -> None:
        posture = NATIVE / "BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md"
        self.assertTrue(posture.is_file())
        self.assertEqual(sha256(posture), UPLOAD_SHA256)

    def test_v4_instructions_carry_operational_rule(self) -> None:
        instructions = NATIVE / "PROJECT_INSTRUCTIONS_V4.md"
        self.assertTrue(instructions.is_file())
        text = canonical_bytes(instructions).decode("utf-8")
        self.assertIn(INSTRUCTION_BLOCK, text)
        self.assertLessEqual(len(text), 8000)
        self.assertIn("Current Lantern free-shared runtime package source binding", text)
        self.assertIn("Do not force-push, delete canonical evidence", text)

    def test_v4_manifest_binds_exact_subjects(self) -> None:
        manifest_path = NATIVE / "PROJECT_FILES_MANIFEST_V4.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(canonical_bytes(manifest_path))
        self.assertEqual(manifest["schema"], "BT2_NATIVE_PROJECT_FILES_MANIFEST_V4")
        self.assertEqual(manifest["predecessor_manifest"]["sha256"], V3_MANIFEST_SHA256)
        pi = manifest["project_instructions"]
        self.assertEqual(pi["path"], "native/project/PROJECT_INSTRUCTIONS_V4.md")
        self.assertEqual(pi["sha256"], sha256(ROOT / pi["path"]))
        self.assertEqual(pi["git_blob"], git_blob_sha(ROOT / pi["path"]))
        entries = {item["path"]: item for item in manifest["required_project_files"]}
        posture_path = "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md"
        self.assertIn(posture_path, entries)
        posture = entries[posture_path]
        self.assertEqual(posture["sha256"], UPLOAD_SHA256)
        self.assertEqual(posture["git_blob"], git_blob_sha(ROOT / posture_path))

        payload_entries = [pi, *manifest["required_project_files"]]
        lines = sorted(
            f'{entry["path"]}|{entry["git_blob"]}|{entry["sha256"]}'
            for entry in payload_entries
        )
        digest = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
        self.assertEqual(manifest["payload_digest"], digest)

        payload_commit = manifest["payload_source_commit"]
        payload_tree = subprocess.check_output(
            ["git", "rev-parse", f"{payload_commit}^{{tree}}"], cwd=ROOT, text=True
        ).strip()
        self.assertEqual(manifest["payload_source_tree"], payload_tree)
        for entry in payload_entries:
            data = git_bytes(payload_commit, entry["path"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
            header = f"blob {len(data)}\0".encode("ascii")
            self.assertEqual(hashlib.sha1(header + data).hexdigest(), entry["git_blob"])

    def test_v4_install_contract_does_not_overclaim(self) -> None:
        install = NATIVE / "INSTALL_V4.md"
        self.assertTrue(install.is_file())
        text = canonical_bytes(install).decode("utf-8")
        self.assertIn("SOURCE INSTALLATION CANDIDATE", text)
        self.assertIn("PROJECT_INSTRUCTIONS_V4.md", text)
        self.assertIn("BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md", text)
        self.assertIn("does not establish native Project installation", text)
        self.assertIn("preserve", text.lower())
        self.assertIn("V3", text)


if __name__ == "__main__":
    unittest.main()
