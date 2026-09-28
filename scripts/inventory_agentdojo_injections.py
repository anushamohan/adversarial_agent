#!/usr/bin/env python3
"""Inventory injection surfaces visible on AgentDojo ground-truth trajectories."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--benchmark-version", default="v1.2.2")
    parser.add_argument("--suite")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (args.manifest is None) == (args.suite is None):
        parser.error("Provide exactly one of --manifest or --suite.")
    return args


def task_number(task_id: str) -> int:
    return int(task_id.rsplit("_", 1)[-1])


def split_user_task_ids(task_ids: list[str]) -> dict[str, list[str]]:
    """Create the registered 50/15/35 split with largest-remainder rounding."""
    ordered = sorted(task_ids, key=task_number)
    names = ("development", "validation", "sealed_test")
    fractions = (0.50, 0.15, 0.35)
    quotas = [len(ordered) * fraction for fraction in fractions]
    counts = [int(quota) for quota in quotas]
    remainder = len(ordered) - sum(counts)
    priorities = sorted(
        range(len(names)), key=lambda index: (-(quotas[index] - counts[index]), index)
    )
    for index in priorities[:remainder]:
        counts[index] += 1

    first = counts[0]
    second = first + counts[1]
    return {
        "development": ordered[:first],
        "validation": ordered[first:second],
        "sealed_test": ordered[second:],
    }


def main() -> None:
    args = parse_args()
    from agentdojo.attacks.baseline_attacks import DirectAttack
    from agentdojo.task_suite.load_suites import get_suite

    manifest = json.loads(args.manifest.read_text()) if args.manifest else None
    benchmark_version = (
        manifest["benchmark_version"] if manifest else args.benchmark_version
    )
    suite_name = manifest["suite"] if manifest else args.suite
    suite = get_suite(benchmark_version, suite_name)
    attack = DirectAttack(suite, None)
    user_task_ids = (
        list(manifest["user_task_ids"])
        if manifest and "user_task_ids" in manifest
        else list(suite.user_tasks)
    )
    injection_task_ids = (
        list(manifest["injection_task_ids"])
        if manifest and "injection_task_ids" in manifest
        else list(suite.injection_tasks)
    )
    tasks = {}
    for task_id in user_task_ids:
        vectors = attack.get_injection_candidates(suite.get_user_task_by_id(task_id))
        tasks[task_id] = {
            "visible_injection_vector_count": len(vectors),
            "vector_ids": vectors,
        }

    per_episode_counts = Counter(
        task["visible_injection_vector_count"] for task in tasks.values()
    )
    task_surface_counts = [
        task["visible_injection_vector_count"] for task in tasks.values()
    ]
    injection_task_count = len(injection_task_ids)
    split = split_user_task_ids(user_task_ids)
    pair_counts = {
        name: len(ids) * injection_task_count for name, ids in split.items()
    }
    report = {
        "inventory_schema_version": 1,
        "run_id": manifest["run_id"] if manifest else None,
        "benchmark_version": benchmark_version,
        "suite": suite_name,
        "attack": manifest.get("attack", "direct") if manifest else "direct",
        "user_task_count": len(tasks),
        "injection_task_count": injection_task_count,
        "injection_task_ids": sorted(injection_task_ids, key=task_number),
        "attacked_episode_count": len(tasks) * injection_task_count,
        "visible_injection_vectors_per_user_task": tasks,
        "user_tasks_by_visible_injection_vector_count": {
            str(count): frequency for count, frequency in sorted(per_episode_counts.items())
        },
        "visible_injection_vector_count_per_user_task": {
            "minimum": min(task_surface_counts),
            "maximum": max(task_surface_counts),
            "mean": mean(task_surface_counts),
            "median": median(task_surface_counts),
        },
        "visible_injection_vectors_per_injection_goal_matrix": sum(
            task["visible_injection_vector_count"] for task in tasks.values()
        ),
        "total_visible_injection_vectors_across_matrix": sum(
            task["visible_injection_vector_count"] for task in tasks.values()
        )
        * injection_task_count,
        "distinct_vector_ids": sorted(
            {vector for task in tasks.values() for vector in task["vector_ids"]}
        ),
        "prospective_user_task_split": split,
        "prospective_pair_counts": pair_counts,
        "minimum_50_sealed_pairs_eligible": pair_counts["sealed_test"] >= 50,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
