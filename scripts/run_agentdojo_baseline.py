#!/usr/bin/env python3
"""Run a bounded AgentDojo baseline with the in-process Qwen adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from types import MethodType


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--benchmark-version", default="v1.2.2")
    parser.add_argument("--suite", default="workspace")
    parser.add_argument("--user-task", action="append")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Frozen JSON run manifest; its model, suite, tasks, and decoding values win.",
    )
    parser.add_argument("--attack", default="none")
    parser.add_argument("--injection-task", action="append")
    parser.add_argument("--output-dir", type=Path, default=Path("runs/week0"))
    parser.add_argument("--max-context-tokens", type=int, default=8192)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def apply_manifest(args: argparse.Namespace) -> tuple[argparse.Namespace, dict | None, str | None]:
    if args.manifest is None:
        if not args.user_task:
            raise SystemExit("Provide at least one --user-task or a --manifest.")
        return args, None, None

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    required = {
        "run_id",
        "benchmark_version",
        "suite",
        "model",
        "revision",
        "seed",
        "generation",
    }
    attacked_manifest = manifest.get("attack", "none") != "none"
    required |= (
        {"attack", "user_task_ids", "injection_task_ids"}
        if attacked_manifest
        else {"benign_task_ids"}
    )
    missing = sorted(required - manifest.keys())
    if missing:
        raise SystemExit(f"Manifest is missing required keys: {', '.join(missing)}")
    generation = manifest["generation"]
    args.model = manifest["model"]
    args.revision = manifest["revision"]
    args.benchmark_version = manifest["benchmark_version"]
    args.suite = manifest["suite"]
    if attacked_manifest:
        args.attack = manifest["attack"]
        args.user_task = list(manifest["user_task_ids"])
        args.injection_task = list(manifest["injection_task_ids"])
    else:
        if args.attack != "none" or args.injection_task:
            raise SystemExit("A benign manifest cannot be combined with attack arguments.")
        args.user_task = list(manifest["benign_task_ids"])
    args.seed = int(manifest["seed"])
    args.max_context_tokens = int(generation["max_context_tokens"])
    args.max_new_tokens = int(generation["max_new_tokens"])
    return args, manifest, hashlib.sha256(manifest_bytes).hexdigest()


def mean(values: list[bool]) -> float | None:
    return sum(values) / len(values) if values else None


def main() -> None:
    args, manifest, manifest_sha256 = apply_manifest(parse_args())
    from agentdojo.agent_pipeline.agent_pipeline import AgentPipeline, PipelineConfig
    from agentdojo.attacks.attack_registry import load_attack
    from agentdojo.benchmark import (
        benchmark_suite_with_injections,
        benchmark_suite_without_injections,
    )
    from agentdojo.logging import OutputLogger
    from agentdojo.task_suite.load_suites import get_suite

    from cotabreak.agentdojo_qwen import QwenTransformersLLM

    llm = QwenTransformersLLM(
        args.model,
        revision=args.revision,
        max_context_tokens=args.max_context_tokens,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
    )
    pipeline = AgentPipeline.from_config(
        PipelineConfig(
            llm=llm,
            model_id=None,
            defense=None,
            system_message_name=None,
            system_message=None,
            tool_output_format="json",
        )
    )
    suite = get_suite(args.benchmark_version, args.suite)
    verifier_recoveries: list[dict[str, str]] = []
    original_utility_check = suite._check_user_task_utility

    def guarded_utility_check(
        self,
        task,
        model_output,
        pre_environment,
        task_environment,
        functions_stack_trace,
    ):
        try:
            return original_utility_check(
                task,
                model_output,
                pre_environment,
                task_environment,
                functions_stack_trace,
            )
        except KeyError as error:
            verifier_recoveries.append(
                {
                    "task_id": task.ID,
                    "exception": type(error).__name__,
                    "message": str(error),
                    "resolution": "utility_false_missing_required_state",
                }
            )
            return False

    suite._check_user_task_utility = MethodType(guarded_utility_check, suite)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with OutputLogger(str(args.output_dir)):
        if args.attack == "none":
            results = benchmark_suite_without_injections(
                pipeline,
                suite,
                args.output_dir,
                args.force,
                user_tasks=args.user_task,
                benchmark_version=args.benchmark_version,
            )
        else:
            attack = load_attack(args.attack, suite, pipeline)
            results = benchmark_suite_with_injections(
                pipeline,
                suite,
                attack,
                args.output_dir,
                args.force,
                user_tasks=args.user_task,
                injection_tasks=args.injection_task,
                benchmark_version=args.benchmark_version,
            )

    utility = list(results["utility_results"].values())
    injection_success = list(results["security_results"].values())
    auxiliary_checks = list(results["injection_tasks_utility_results"].values())
    attacked = args.attack != "none"
    report = {
        "model": args.model,
        "revision": args.revision,
        "benchmark_version": args.benchmark_version,
        "suite": args.suite,
        "user_tasks": args.user_task,
        "attack": args.attack,
        "injection_tasks": args.injection_task or [],
        "primary_episodes": len(utility),
        "auxiliary_injection_task_checks": len(auxiliary_checks),
        "total_task_runs": len(utility) + len(auxiliary_checks),
        "benign_task_success_rate": mean(utility) if not attacked else None,
        "attacked_utility_rate": mean(utility) if attacked else None,
        "security_rate": mean([not outcome for outcome in injection_success])
        if attacked
        else 1.0,
        "attack_success_rate": mean(injection_success) if attacked else None,
        "injection_task_completion_rate": mean(auxiliary_checks),
        "injection_task_completion_results": results[
            "injection_tasks_utility_results"
        ],
        "generation_usage": llm.usage_summary,
        "verifier_recoveries": verifier_recoveries,
        "verifier_recovery_count": len(verifier_recoveries),
        "run_directory": str(args.output_dir.resolve()),
        "manifest": str(args.manifest.resolve()) if args.manifest else None,
        "manifest_sha256": manifest_sha256,
        "run_id": manifest["run_id"] if manifest else None,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    report_name = (
        f"{manifest['run_id']}--summary.json"
        if manifest
        else f"summary--{llm.name}--{args.suite}--{args.attack}.json"
    )
    (args.output_dir / report_name).write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
