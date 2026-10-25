"""Qualification falsifiers for local atomic need/goal feedback."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest

from outcome_contract import NeedSnapshot
from durable_feedback import DurableFeedbackFixture, FeedbackClaim, GoalBinding, MeasuredEffect


class DurableFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "feedback.sqlite3"
        self.initial_need = NeedSnapshot("rest", "g1", 0, 0.2, 0.8)
        self.initial_goal = GoalBinding("g1", "c1", "rest", 0)
        self.claim = FeedbackClaim(
            event_id="event-1", attempt_id="attempt-1", need_id="rest", goal_id="g1",
            choice_id="c1", target_id="rest", expected_need_revision=0,
            expected_goal_revision=0, claimed_status="SUCCESS", claimant_kind="observer",
            evidence_ref="evidence-1", observed_at=10, expires_at=60,
        )
        self.observation = MeasuredEffect(
            physical_effect_id="physical-1", event_id="event-1", attempt_id="attempt-1",
            need_id="rest", goal_id="g1", choice_id="c1", target_id="rest",
            evidence_ref="evidence-1", observer_id="independent:fixture",
            measured_level=0.6, measured_at=12,
        )

    def fixture(self, measurement=None):
        callback = None if measurement is None else lambda claim: measurement
        return DurableFeedbackFixture(
            self.db, self.initial_need, self.initial_goal,
            verifier=callback, trusted_observers=frozenset({"independent:fixture"}),
        )

    def test_qualified_witness_commits_need_and_goal_atomically_once(self) -> None:
        journal = self.fixture(self.observation)
        applied = journal.admit(self.claim, now=20)
        self.assertEqual((applied.status, applied.reason), ("APPLIED", "INJECTED_TEST_WITNESS_ACCEPTED"))
        self.assertEqual((applied.need.current_level, applied.need.revision), (0.6, 1))
        self.assertTrue(applied.goal.completed)
        self.assertFalse(applied.effect_authority)
        replay = self.fixture(self.observation).admit(self.claim, now=25)
        self.assertEqual(replay.status, "REPLAY")
        self.assertEqual((replay.need.revision, replay.goal.completed), (1, True))

    def test_unsigned_success_and_fake_observer_label_never_satiate(self) -> None:
        journal = self.fixture()  # no independently configured verifier
        denied = journal.admit(self.claim, now=20)
        self.assertEqual((denied.status, denied.reason), ("HOLD", "NO_INDEPENDENT_VERIFIER"))
        self.assertEqual((denied.need.current_level, denied.need.revision), (0.2, 0))
        self.assertFalse(denied.goal.completed)

    def test_crash_after_need_update_rolls_back_goal_and_receipt(self) -> None:
        journal = self.fixture(self.observation)
        with sqlite3.connect(self.db) as db:
            db.execute("""CREATE TRIGGER abort_goal BEFORE UPDATE ON goals
                          BEGIN SELECT RAISE(ABORT, 'injected crash after need write'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            journal.admit(self.claim, now=20)
        # Reopen is intentionally a distinct process lifetime. The provisional
        # need update and receipt must both have rolled back with the goal.
        fresh = self.fixture(self.observation)
        need, goal = fresh.state()
        self.assertEqual((need.revision, need.current_level), (0, 0.2))
        self.assertFalse(goal.completed)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM receipts").fetchone()[0], 0)
            db.execute("DROP TRIGGER abort_goal")
        eventual = self.fixture(self.observation).admit(self.claim, now=21)
        self.assertEqual((eventual.status, eventual.need.revision, eventual.goal.completed),
                         ("APPLIED", 1, True))

    def test_old_goal_aba_same_target_never_completes_replacement(self) -> None:
        journal = self.fixture(self.observation)
        current = journal.replace_goal(GoalBinding("g2", "c2", "rest", 1))
        self.assertEqual((current.need.revision, current.goal.goal_id), (1, "g2"))
        stale = journal.admit(self.claim, now=20)
        self.assertEqual((stale.status, stale.reason), ("HOLD", "STALE_OR_CROSS_GOAL"))
        self.assertFalse(stale.goal.completed)

    def test_reminted_event_attempt_and_evidence_cannot_double_credit_physical_effect(self) -> None:
        journal = self.fixture(self.observation)
        first = journal.admit(self.claim, now=20)
        self.assertEqual(first.status, "APPLIED")
        new = journal.replace_goal(GoalBinding("g2", "c2", "rest", 2))
        reminted = replace(
            self.claim, event_id="event-2", attempt_id="attempt-2", evidence_ref="evidence-2",
            goal_id="g2", choice_id="c2", expected_need_revision=new.need.revision,
            expected_goal_revision=new.goal.revision,
        )
        reminted_observation = replace(
            self.observation, event_id="event-2", attempt_id="attempt-2",
            evidence_ref="evidence-2", goal_id="g2", choice_id="c2",
            # Same independently supplied physical effect identity.
            physical_effect_id="physical-1",
        )
        another = DurableFeedbackFixture(
            self.db, self.initial_need, self.initial_goal,
            verifier=lambda _claim: reminted_observation,
            trusted_observers=frozenset({"independent:fixture"}),
        )
        denied = another.admit(reminted, now=21)
        self.assertEqual((denied.status, denied.reason), ("HOLD", "DUPLICATE_PHYSICAL_EFFECT"))
        self.assertEqual((denied.need.revision, denied.goal.completed),
                         (new.need.revision, False))

    def test_explicit_protection_veto_dominates_verified_improvement(self) -> None:
        guarded = DurableFeedbackFixture(
            self.db, self.initial_need, replace(self.initial_goal, protection_veto=True),
            verifier=lambda _claim: self.observation,
            trusted_observers=frozenset({"independent:fixture"}),
        )
        denied = guarded.admit(self.claim, now=20)
        self.assertEqual((denied.status, denied.reason), ("HOLD", "PROTECTION_VETO"))
        self.assertEqual((denied.need.current_level, denied.need.revision), (0.2, 0))
        self.assertFalse(denied.goal.completed)
        self.assertFalse(denied.effect_authority)

    def test_fake_witness_identity_or_no_improvement_cannot_complete(self) -> None:
        forged = replace(self.observation, observer_id="model:observer-label")
        denied = self.fixture(forged).admit(self.claim, now=20)
        self.assertEqual((denied.status, denied.reason), ("HOLD", "UNTRUSTED_OBSERVER"))
        self.assertFalse(denied.goal.completed)

    def test_unverified_model_success_label_even_with_digest_shaped_ref_is_held(self) -> None:
        self.claim = replace(self.claim, claimant_kind="model_generated", evidence_ref="a" * 64)
        denied = self.fixture().admit(self.claim, now=20)
        self.assertEqual(denied.status, "HOLD")
        self.assertEqual(denied.need.revision, 0)

    def test_malformed_claim_identifiers_revisions_and_timestamps_fail_closed(self) -> None:
        for change in ({"event_id": ""}, {"expected_need_revision": True},
                       {"expected_goal_revision": -1}, {"observed_at": float("nan")},
                       {"expires_at": float("inf")}, {"expires_at": 9}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(self.claim, **change)
        with self.assertRaises(ValueError):
            replace(self.observation, physical_effect_id="")
        with self.assertRaises(ValueError):
            self.fixture(self.observation).admit(self.claim, now=10 ** 1000)

    def test_verifier_exception_is_sanitized_and_remains_rejected_on_replay(self) -> None:
        def untrusted_failure(_claim):
            raise RuntimeError("secret observer /home/alice/token.txt")

        journal = DurableFeedbackFixture(
            self.db, self.initial_need, self.initial_goal,
            verifier=untrusted_failure, trusted_observers=frozenset({"independent:fixture"}),
        )
        denied = journal.admit(self.claim, now=20)
        self.assertEqual((denied.status, denied.reason), ("HOLD", "VERIFIER_UNAVAILABLE"))
        self.assertNotIn("alice", repr(denied))
        later = self.fixture(self.observation).admit(self.claim, now=21)
        self.assertEqual((later.status, later.reason), ("HOLD", "VERIFIER_UNAVAILABLE"))
        self.assertEqual(later.need.revision, 0)

    def test_no_measured_improvement_still_cannot_complete(self) -> None:
        stagnant = replace(self.observation, measured_level=0.2)
        held = self.fixture(stagnant).admit(self.claim, now=20)
        self.assertEqual((held.status, held.reason), ("HOLD", "NO_MEASURED_IMPROVEMENT"))
        self.assertFalse(held.goal.completed)

    def test_cross_need_goal_target_cannot_receive_unrelated_need_credit(self) -> None:
        # Local qualification supports exactly one canonical need/target axis.
        with self.assertRaises(ValueError):
            DurableFeedbackFixture(
                self.db, self.initial_need, GoalBinding("g1", "c1", "battery"),
                verifier=lambda _claim: self.observation,
            )
        journal = self.fixture(self.observation)
        with self.assertRaises(ValueError):
            journal.replace_goal(GoalBinding("g2", "c2", "battery", 1))
        need, goal = journal.state()
        self.assertEqual((need.goal_id, need.revision, goal.goal_id), ("g1", 0, "g1"))

    def test_held_attempt_names_are_not_global_reservations(self) -> None:
        # If arbitrary unauthenticated HOLD claims globally reserved attempts,
        # attackers could poison legitimate physical evidence identifiers.
        no_verifier = self.fixture()
        held = no_verifier.admit(self.claim, now=20)
        self.assertEqual((held.status, held.reason), ("HOLD", "NO_INDEPENDENT_VERIFIER"))
        # Remint the event only; a different independent test witness must
        # still bind all observed fields to the *new* claim before any credit.
        legitimate = replace(self.claim, event_id="event-2")
        observed = replace(self.observation, event_id="event-2")
        accepted = self.fixture(observed).admit(legitimate, now=21)
        self.assertEqual((accepted.status, accepted.need.revision), ("APPLIED", 1))
        self.assertTrue(accepted.goal.completed)


if __name__ == "__main__":
    unittest.main()
