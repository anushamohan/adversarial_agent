import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cotabreak.toy_env import Action, DeterministicSecurityEnv


class DeterministicSecurityEnvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.env = DeterministicSecurityEnv()

    def test_benign_success(self) -> None:
        result = self.env.run([Action.COMPLETE_TASK])
        self.assertTrue(result.benign_task_success)
        self.assertFalse(result.attack_success)
        self.assertTrue(result.secure_task_success)

    def test_attack_and_utility_are_independent(self) -> None:
        result = self.env.run(
            [Action.FOLLOW_INJECTION, Action.COMPLETE_TASK]
        )
        self.assertTrue(result.benign_task_success)
        self.assertTrue(result.attack_success)
        self.assertFalse(result.secure_task_success)

    def test_refusal_is_not_robust_success(self) -> None:
        result = self.env.run([Action.REFUSE])
        self.assertFalse(result.benign_task_success)
        self.assertFalse(result.attack_success)
        self.assertFalse(result.secure_task_success)

    def test_invalid_action_is_reported(self) -> None:
        result = self.env.run([Action.INVALID])
        self.assertTrue(result.invalid_episode)
        self.assertEqual(
            result.transitions[-1].termination_reason, "invalid_action"
        )

    def test_replay_is_deterministic(self) -> None:
        actions = [Action.FOLLOW_INJECTION, Action.COMPLETE_TASK]
        self.assertEqual(self.env.run(actions), self.env.run(actions))


if __name__ == "__main__":
    unittest.main()

