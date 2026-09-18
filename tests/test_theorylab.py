import unittest
from pathlib import Path

from theorylab.catalog import load_json
from theorylab.engine import run_theory
from theorylab.propose import propose
from theorylab.replay import replay_history
from theorylab.validate import validate_repository, validate_theory

ROOT = Path(__file__).resolve().parents[1]


class TheoryLabTests(unittest.TestCase):
    def test_repository_contracts_are_valid(self):
        self.assertEqual(validate_repository(ROOT), [])

    def test_seed_theory_runs_and_attacker_collapses_effect(self):
        theory = load_json(ROOT / "theories/noncommuting_write.json")
        receipt = run_theory(theory)
        self.assertEqual(receipt["status"], "pass")
        self.assertGreater(
            receipt["measurements"]["b_then_a.response_norm"],
            receipt["measurements"]["a_then_b.response_norm"],
        )
        self.assertEqual(
            receipt["measurements"]["frozen_a_then_b.response_norm"],
            receipt["measurements"]["frozen_b_then_a.response_norm"],
        )

    def test_unknown_node_is_rejected(self):
        theory = load_json(ROOT / "theories/noncommuting_write.json")
        theory["nodes"][0]["node"] = "does.not.exist"
        errors = validate_theory(theory)
        self.assertTrue(any("unknown node definition" in error for error in errors))

    def test_replay_never_invents_attempts(self):
        history = load_json(ROOT / "data/discovery_history.json")
        result = replay_history(history, "best_first", budget=4)
        known = {item["id"] for item in history["attempts"]}
        self.assertTrue(set(result["visited"]).issubset(known))
        self.assertLessEqual(len(result["visited"]), 4)

    def test_replay_policies_are_available(self):
        history = load_json(ROOT / "data/discovery_history.json")
        for policy in ("breadth_first", "depth_first", "best_first"):
            result = replay_history(history, policy, budget=3)
            self.assertEqual(result["policy"], policy)
            self.assertEqual(len(result["visited"]), 3)

    def test_curated_genealogy_slice_is_small_and_explicit(self):
        knowledge = load_json(ROOT / "knowledge/genealogy_components.json")
        self.assertEqual(len(knowledge["components"]), 15)
        for item in knowledge["components"]:
            self.assertIn("reusable_object", item)
            self.assertIn("boundary", item)
            self.assertIn("source_pass", item)

    def test_basis_question_builds_grounded_proposal(self):
        result = propose(
            "Can useful computational coordinates and persistent write self-align through experience rather than being supplied?"
        )
        self.assertEqual(result["family"], "basis_alignment")
        repos = {item["repo"] for item in result["selected_components"]}
        self.assertIn("FrequencyAddressedState-dependentOperatorComposition", repos)
        self.assertIn("ThirdWay", repos)
        constraints = {item["id"] for item in result["selected_constraints"]}
        self.assertIn("constraint.learnability_open", constraints)
        self.assertTrue(result["execution"]["executable_now"])
        self.assertEqual(result["execution"]["missing_executors"], [])
        self.assertEqual(result["execution"]["theory_path"], "theories/learned_basis_alignment.json")

    def test_promoted_basis_theory_runs_the_predeclared_panel(self):
        theory = load_json(ROOT / "theories/learned_basis_alignment.json")
        receipt = run_theory(theory)
        self.assertEqual(receipt["status"], "pass")
        m = receipt["measurements"]
        self.assertGreater(
            m["matched_basis_panel.learned_operator_rank_min"],
            m["matched_basis_panel.random_operator_rank_max"],
        )
        self.assertGreater(
            m["matched_basis_panel.learned_composition_min"],
            m["matched_basis_panel.random_composition_max"],
        )
        self.assertGreater(m["matched_basis_panel.learned_alignment_min"], 0.95)
        self.assertEqual(m["matched_basis_panel.frozen_composition_median"], 0.0)

    def test_active_identification_question_pulls_boring_controls(self):
        result = propose(
            "When does active intervention identify a hidden mechanism better after probe cost and dense causes?"
        )
        self.assertEqual(result["family"], "active_identification")
        repos = {item["repo"] for item in result["selected_components"]}
        self.assertIn("EvoX", repos)
        constraint_ids = {item["id"] for item in result["selected_constraints"]}
        self.assertTrue(
            {"constraint.active_needs_boring_controls", "constraint.probe_cost_counts"} & constraint_ids
        )


if __name__ == "__main__":
    unittest.main()
