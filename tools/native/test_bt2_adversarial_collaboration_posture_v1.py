from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_POSTURE_SHA256 = "828a3995dd0e49999c7ebc51753cfa17508935b45b99c01c79f456845994826f"


def canonical_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


class AdversarialCollaborationPostureQualification(unittest.TestCase):
    def test_exact_native_posture_is_preserved(self) -> None:
        path = ROOT / "native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md"
        self.assertTrue(path.is_file())
        self.assertEqual(
            hashlib.sha256(canonical_bytes(path)).hexdigest(),
            EXPECTED_POSTURE_SHA256,
        )

    def test_instruction_sequence_preserves_literal_first_rule(self) -> None:
        text = canonical_bytes(
            ROOT / "native/project/PROJECT_INSTRUCTIONS_V4.md"
        ).decode("utf-8")
        positions = [
            text.index("## Adversarial collaboration posture"),
            text.index("literal proposition as unproven"),
            text.index("Try to kill the literal proposition"),
            text.index("If the literal proposition survives serious adversarial review"),
            text.index("If it fails, do not stop at rejection"),
            text.index("Only then infer the underlying objective"),
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "Direct commands and factual requests with no embedded proposal do not trigger",
            text,
        )
        self.assertIn("UNKNOWN", text)
        self.assertIn("SURVIVES", text)
        self.assertIn("grants no protected-effect authority", text)

    def test_machine_readable_contract_keeps_authority_separate(self) -> None:
        text = canonical_bytes(
            ROOT / "specs/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.yaml"
        ).decode("utf-8")
        required_order = [
            "- id: LITERAL_PROPOSITION",
            "- id: KILL_ATTEMPT",
            "- id: VERDICT",
            "- id: RECOVERY",
            "- id: ACTION",
        ]
        positions = [text.index(token) for token in required_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("grants_protected_effect_authority: false", text)
        self.assertIn("overrides_safety_or_authority_rules: false", text)
        self.assertIn("- DIRECT_COMMAND", text)
        self.assertIn("- FACTUAL_REQUEST", text)
        self.assertIn("- TREAT_UNKNOWN_AS_SURVIVES", text)

    def test_installation_and_behavior_are_not_collapsed(self) -> None:
        text = canonical_bytes(ROOT / "native/project/INSTALL_V4.md").decode("utf-8")
        self.assertIn("SOURCE INSTALLATION CANDIDATE", text)
        self.assertIn("does not install it into ChatGPT Project settings/files", text)
        self.assertIn("BEHAVIOR_VERIFIED", text)
        self.assertIn("source/package conformance only", text)
        self.assertIn("protected effects blocked", text)


if __name__ == "__main__":
    unittest.main()
