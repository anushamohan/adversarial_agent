import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.inventory_agentdojo_injections import split_user_task_ids


class InventoryTest(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self) -> None:
        task_ids = [f"user_task_{index}" for index in reversed(range(21))]
        split = split_user_task_ids(task_ids)
        self.assertEqual(len(split["development"]), 11)
        self.assertEqual(len(split["validation"]), 3)
        self.assertEqual(len(split["sealed_test"]), 7)
        flattened = [task for partition in split.values() for task in partition]
        self.assertEqual(len(flattened), len(set(flattened)))
        self.assertEqual(set(flattened), set(task_ids))


if __name__ == "__main__":
    unittest.main()
