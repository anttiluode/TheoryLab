import json
import unittest
from pathlib import Path

from theorylab.catalog import load_json
from theorylab.engine import run_theory
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


if __name__ == "__main__":
    unittest.main()
