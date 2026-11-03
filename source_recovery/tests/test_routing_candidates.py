"""Pure source-only routing decisions; no export files are opened."""

import unittest

from source_recovery.routing_candidates import propose_route


class RoutingCandidatesTests(unittest.TestCase):
    def test_unrecognized_labels_and_filenames_have_no_repo_candidate(self):
        for value in (None, "", "chatgpt-history.zip", "semantic_research/../../private",
                      "SOURCE_CODE", "unknown", "anything-else"):
            with self.subTest(value=value):
                result = propose_route(value)
                self.assertEqual(result.classification, "UNKNOWN")
                self.assertEqual(result.candidate_repositories, ())
                self.assertEqual(result.publication, "HOLD")

    def test_hostile_string_subclass_is_never_used_as_dict_key(self):
        class HostileString(str):
            def __hash__(self):
                raise AssertionError("caller controlled hash executed")

        result = propose_route(HostileString("semantic_research"))
        self.assertEqual(result.classification, "UNKNOWN")
        self.assertEqual(result.candidate_repositories, ())

    def test_known_private_categories_do_not_route_raw_material_to_git(self):
        for category in ("private_conversation", "model_artifact", "executable_bundle", "mixed_archive"):
            with self.subTest(category=category):
                result = propose_route(category)
                self.assertEqual(result.candidate_repositories, ())
                self.assertEqual(result.publication, "HOLD")
                self.assertFalse(result.raw_material_git_eligible)

    def test_research_categories_only_offer_review_candidates(self):
        expected = {
            "historical_project_packet": ("vera-control-plane", "bt2"),
            "semantic_research": ("semanticatlas",),
            "training_evaluation": ("model-training", "labyrinth"),
            "visual_reference": ("selfimage",),
            "temporal_research": ("temporal",),
        }
        for category, candidates in expected.items():
            with self.subTest(category=category):
                result = propose_route(category)
                self.assertEqual(result.candidate_repositories, candidates)
                self.assertEqual(result.publication, "HOLD")
                self.assertFalse(result.raw_material_git_eligible)
                self.assertTrue(result.requires_exact_head_review)

    def test_no_route_can_be_construed_as_authority_or_admission(self):
        for category in ("historical_project_packet", "semantic_research", "training_evaluation",
                         "visual_reference", "temporal_research", "private_conversation",
                         "model_artifact", "executable_bundle", "mixed_archive", None):
            result = propose_route(category)
            self.assertEqual(result.rights, "UNVERIFIED")
            self.assertEqual(result.currentness, "HISTORICAL_NOT_INSTALLED")
            self.assertEqual(result.source_basis, "CLASSIFICATION_ONLY")
            self.assertEqual(result.publication, "HOLD")
            self.assertFalse(result.raw_material_git_eligible)


if __name__ == "__main__":
    unittest.main()
