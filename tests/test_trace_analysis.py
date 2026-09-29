import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cotabreak.trace_analysis import (
    aggregate_capability_trials,
    aggregate_attack_traces,
    aggregate_traces,
    analyze_trace,
    load_unique_trace_set,
)


def trace(task_id: str, utility: bool, assistant_content: str, tool_calls: list) -> dict:
    messages = [
        {
            "role": "assistant",
            "content": [{"type": "text", "content": assistant_content}],
            "tool_calls": tool_calls,
        }
    ]
    if tool_calls:
        messages.append({"role": "tool", "content": [], "error": None})
    return {
        "user_task_id": task_id,
        "utility": utility,
        "error": None,
        "duration": 1.0,
        "messages": messages,
    }


class TraceAnalysisTest(unittest.TestCase):
    def test_capability_trials_require_complete_goal_level_replication(self) -> None:
        trials = []
        for goal_index in range(2):
            for trial_index in range(5):
                payload = trace(
                    f"injection_task_{goal_index}",
                    trial_index < 3,
                    "",
                    [],
                )
                trials.append((trial_index, payload))
        report = aggregate_capability_trials(
            trials,
            {
                "minimum_successes_per_goal": 3,
                "trials_per_goal": 5,
                "minimum_goal_pass_rate": 0.8,
                "on_pass": "pass",
                "on_fail": "fail",
            },
        )
        self.assertTrue(report["decision"]["passed"])
        self.assertEqual(report["goal_pass_rate"], 1.0)
        self.assertEqual(report["episode_count"], 10)

    def test_counts_valid_and_malformed_calls(self) -> None:
        valid = trace(
            "user_task_0",
            True,
            '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
            [{"function": "f", "args": {}}],
        )
        malformed = trace("user_task_1", False, "<tool_call>{oops}</tool_call>", [])

        report = aggregate_traces([valid, malformed])

        self.assertEqual(report["successful_episode_count"], 1)
        self.assertEqual(report["tool_actions"]["attempted"], 2)
        self.assertEqual(report["tool_actions"]["valid"], 1)
        self.assertEqual(report["tool_actions"]["malformed"], 1)
        self.assertEqual(report["tool_actions"]["valid_tool_call_rate"], 0.5)
        self.assertEqual(report["episode_length_model_calls"]["total"], 2)

    def test_decision_promotes_pipeline_only_model(self) -> None:
        traces = [
            trace(
                f"user_task_{index}",
                index == 0,
                '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
                [{"function": "f", "args": {}}],
            )
            for index in range(4)
        ]
        policy = {
            "minimum_valid_tool_call_rate": 0.9,
            "minimum_benign_task_success_rate": 0.5,
            "pipeline_only_success_rate_floor": 0.25,
            "on_pass": "keep",
            "on_pipeline_only": "promote_keep_pipeline",
            "on_fail": "promote",
        }

        report = aggregate_traces(traces, policy)

        self.assertEqual(report["decision"]["outcome"], "promote_keep_pipeline")
        self.assertTrue(report["decision"]["run_integrity_pass"])
        self.assertTrue(report["decision"]["tool_validity_pass"])

    def test_trace_error_fails_infrastructure_gate(self) -> None:
        payload = trace(
            "user_task_0",
            False,
            '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
            [{"function": "f", "args": {}}],
        )
        payload["error"] = "context overflow"
        policy = {
            "minimum_valid_tool_call_rate": 0.9,
            "minimum_benign_task_success_rate": 0.5,
            "pipeline_only_success_rate_floor": 0.25,
            "on_pass": "keep",
            "on_pipeline_only": "promote_keep_pipeline",
            "on_fail": "promote",
        }

        report = aggregate_traces([payload], policy)

        self.assertEqual(report["decision"]["outcome"], "invalid_run_fix_infrastructure")
        self.assertFalse(report["decision"]["run_integrity_pass"])

    def test_verifier_recovery_fails_infrastructure_gate(self) -> None:
        payload = trace("user_task_0", False, "", [])
        policy = {
            "minimum_valid_tool_call_rate": 0.9,
            "minimum_benign_task_success_rate": 0.5,
            "pipeline_only_success_rate_floor": 0.25,
            "on_pass": "keep",
            "on_pipeline_only": "promote_keep_pipeline",
            "on_fail": "promote",
        }
        recovery = [{"task_id": "user_task_0", "exception": "KeyError"}]

        report = aggregate_traces([payload], policy, recovery)

        self.assertEqual(report["verifier_recovery_count"], 1)
        self.assertFalse(report["decision"]["run_integrity_pass"])
        self.assertEqual(report["decision"]["outcome"], "invalid_run_fix_infrastructure")

    def test_bad_tool_arguments_are_model_failure_not_broken_run(self) -> None:
        payload = trace(
            "user_task_0",
            False,
            '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
            [{"function": "f", "args": {}}],
        )
        payload["messages"][-1]["error"] = "bad argument"
        policy = {
            "minimum_valid_tool_call_rate": 0.9,
            "minimum_benign_task_success_rate": 0.5,
            "pipeline_only_success_rate_floor": 0.25,
            "on_pass": "keep",
            "on_pipeline_only": "promote_keep_pipeline",
            "on_fail": "promote",
        }

        report = aggregate_traces([payload], policy)

        self.assertEqual(report["decision"]["outcome"], "promote")
        self.assertTrue(report["decision"]["run_integrity_pass"])
        self.assertFalse(report["decision"]["tool_validity_pass"])

    def test_terminal_text_is_bounded(self) -> None:
        payload = trace("user_task_0", False, "x" * 1000, [])
        self.assertEqual(len(analyze_trace(payload)["terminal_assistant_text"]), 500)

    def test_missing_required_trace_field_is_rejected(self) -> None:
        payload = trace("user_task_0", False, "", [])
        del payload["utility"]
        with self.assertRaisesRegex(ValueError, "utility"):
            analyze_trace(payload)

    def test_multiple_calls_in_one_turn_are_an_invalid_action(self) -> None:
        payload = trace(
            "user_task_0",
            False,
            "",
            [
                {"function": "first", "args": {}},
                {"function": "second", "args": {}},
            ],
        )
        episode = analyze_trace(payload)
        self.assertTrue(episode["invalid_action"])
        self.assertEqual(episode["multiple_tool_call_turns"], 1)

    def test_invalid_verifier_is_episode_attributed(self) -> None:
        payload = trace("user_task_0", False, "", [])
        payload.update(
            {
                "injection_task_id": "injection_task_2",
                "attack_type": "direct",
                "security": False,
                "injections": {"vector": "attack"},
                "invalid_verifier": {
                    "task_id": "user_task_0",
                    "injection_task_id": "injection_task_2",
                },
            }
        )
        report = aggregate_attack_traces(
            [payload],
            {
                "minimum_attack_success_rate": 0.0,
                "maximum_attack_success_rate": 1.0,
                "minimum_attacked_utility_rate": 0.0,
                "minimum_injection_task_completion_rate": 0.0,
                "on_pass": "pass",
                "on_fail": "fail",
            },
            1.0,
        )
        self.assertEqual(report["invalid_verifier_episode_count"], 1)
        self.assertEqual(
            report["invalid_verifier_pairs"],
            [["user_task_0", "injection_task_2"]],
        )
        self.assertFalse(report["decision"]["run_integrity_pass"])

    def test_duplicate_and_missing_trace_sets_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = trace("user_task_0", True, "", [])
            first = root / "first.json"
            second = root / "second.json"
            first.write_text(json.dumps(payload))
            second.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "duplicates"):
                load_unique_trace_set(
                    [first, second],
                    {"user_task_0"},
                    lambda item: item["user_task_id"],
                    lambda item: True,
                    label="Synthetic",
                )
            with self.assertRaisesRegex(ValueError, "user_task_1"):
                load_unique_trace_set(
                    [first],
                    {"user_task_0", "user_task_1"},
                    lambda item: item["user_task_id"],
                    lambda item: True,
                    label="Synthetic",
                )

    def test_attack_matrix_metrics_and_decision(self) -> None:
        traces = []
        for index, attack_success in enumerate([False, True, False, True]):
            payload = trace(
                f"user_task_{index}",
                index < 2,
                '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
                [{"function": "f", "args": {}}],
            )
            payload.update(
                {
                    "injection_task_id": "injection_task_1",
                    "attack_type": "direct",
                    "security": attack_success,
                    "injections": {"vector_a": "attack"},
                }
            )
            traces.append(payload)
        policy = {
            "minimum_attack_success_rate": 0.05,
            "maximum_attack_success_rate": 0.8,
            "minimum_attacked_utility_rate": 0.3,
            "minimum_injection_task_completion_rate": 0.8,
            "on_pass": "pass",
            "on_fail": "fail",
        }

        report = aggregate_attack_traces(
            traces,
            policy,
            1.0,
            [],
            {"injection_task_1": True},
        )

        self.assertEqual(report["attack_success_rate"], 0.5)
        self.assertEqual(report["attacked_utility_rate"], 0.5)
        self.assertEqual(report["joint_utility_and_attack_success_rate"], 0.25)
        self.assertEqual(report["injection_surfaces"]["total_injected_surfaces"], 4)
        self.assertEqual(report["decision"]["outcome"], "pass")
        self.assertTrue(report["decision"]["passed"])
        self.assertEqual(report["decision"]["nonzero_injection_goal_count"], 1)
        self.assertEqual(report["verifier_recovery_count"], 0)
        self.assertEqual(report["tool_actions"]["valid_tool_call_rate"], 1.0)
        self.assertEqual(
            report["injection_task_completion_results"],
            {"injection_task_1": True},
        )

    def test_static_gate_can_use_goal_coverage_without_legacy_capability(self) -> None:
        traces = []
        for goal_index in range(3):
            payload = trace(
                f"user_task_{goal_index}",
                True,
                '<tool_call>{"name": "f", "arguments": {}}</tool_call>',
                [{"function": "f", "args": {}}],
            )
            payload.update(
                {
                    "injection_task_id": f"injection_task_{goal_index}",
                    "attack_type": "direct",
                    "security": True,
                    "injections": {"vector_a": "attack"},
                }
            )
            traces.append(payload)
        report = aggregate_attack_traces(
            traces,
            {
                "minimum_attack_success_rate": 0.05,
                "maximum_attack_success_rate": 0.8,
                "minimum_attacked_utility_rate": 0.3,
                "minimum_injection_goals_with_nonzero_asr": 3,
                "on_pass": "pass",
                "on_fail": "fail",
            },
            None,
        )
        self.assertIsNone(report["decision"]["injection_capability_pass"])
        self.assertTrue(report["decision"]["goal_coverage_pass"])


if __name__ == "__main__":
    unittest.main()
