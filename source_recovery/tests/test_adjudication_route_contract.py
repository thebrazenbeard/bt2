"""Synthetic, non-publishing classification-to-adjudication contract tests."""
import unittest

from source_recovery.adjudication_route_contract import (
    ClassEvidenceAssertion,
    propose_private_adjudication_route,
)


class AdjudicationRouteContractTests(unittest.TestCase):
    def evidence(self, cls="semantic_research", artifact="ARCHIVE_001"):
        return ClassEvidenceAssertion(
            artifact_id=artifact,
            classification=cls,
            evidence_class="SOURCE_INSPECTION",
            private_review_record_id="REVIEW_0001",
        )

    def test_requires_separate_evidence_and_explicit_selection(self):
        missing = propose_private_adjudication_route(
            "ARCHIVE_001", None, selected_repository="semanticatlas")
        self.assertIsNone(missing.target_repo_candidate)
        self.assertEqual(missing.public_admission, "HOLD")
        unselected = propose_private_adjudication_route("ARCHIVE_001", self.evidence())
        self.assertIsNone(unselected.target_repo_candidate)
        selected = propose_private_adjudication_route(
            "ARCHIVE_001", self.evidence(), selected_repository="semanticatlas")
        self.assertEqual(selected.target_repo_candidate, "semanticatlas")
        self.assertEqual(selected.rights, "UNVERIFIED")
        self.assertEqual(selected.public_admission, "HOLD")
        self.assertFalse(selected.raw_material_git_eligible)

    def test_ambiguous_class_never_auto_selects(self):
        evidence = self.evidence("historical_project_packet")
        no_choice = propose_private_adjudication_route("ARCHIVE_001", evidence)
        self.assertIsNone(no_choice.target_repo_candidate)
        self.assertEqual(set(no_choice.possible_repositories), {"vera-control-plane", "bt2"})
        chosen = propose_private_adjudication_route(
            "ARCHIVE_001", evidence, selected_repository="bt2")
        self.assertEqual(chosen.target_repo_candidate, "bt2")
        self.assertEqual(chosen.public_admission, "HOLD")

    def test_filenames_and_private_classes_are_unroutable(self):
        for label in ("vera.zip", "C:/Downloads/vera.zip", "private_conversation",
                      "model_artifact", "mixed_archive", "executable_bundle"):
            with self.subTest(label=label):
                proposal = propose_private_adjudication_route(
                    "ARCHIVE_001", self.evidence(label), selected_repository="bt2")
                self.assertIsNone(proposal.target_repo_candidate)
                self.assertEqual(proposal.public_admission, "HOLD")

    def test_artifact_identity_and_evidence_class_must_match(self):
        wrong_id = propose_private_adjudication_route(
            "ARCHIVE_001", self.evidence(artifact="OTHER_001"),
            selected_repository="semanticatlas")
        self.assertIsNone(wrong_id.target_repo_candidate)
        evidence = ClassEvidenceAssertion("ARCHIVE_001", "semantic_research", "INVENTORY", "REVIEW_0001")
        unreviewed = propose_private_adjudication_route(
            "ARCHIVE_001", evidence, selected_repository="semanticatlas")
        self.assertIsNone(unreviewed.target_repo_candidate)

    def test_untrusted_structures_and_subclasses_cannot_route(self):
        class EvilString(str):
            def __hash__(self):
                raise RuntimeError("no hash from untrusted subclass")

        invalid = (dict(artifact_id="ARCHIVE_001", classification="semantic_research"),
                   self.evidence(EvilString("semantic_research")),
                   self.evidence(artifact=EvilString("ARCHIVE_001")))
        for evidence in invalid:
            with self.subTest(evidence=type(evidence).__name__):
                outcome = propose_private_adjudication_route(
                    "ARCHIVE_001", evidence, selected_repository="semanticatlas")
                self.assertIsNone(outcome.target_repo_candidate)
        spoof = propose_private_adjudication_route(
            "ARCHIVE_001", self.evidence(), selected_repository=EvilString("semanticatlas"))
        self.assertIsNone(spoof.target_repo_candidate)


if __name__ == "__main__":
    unittest.main()
