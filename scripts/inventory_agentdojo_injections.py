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
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from agentdojo.attacks.baseline_attacks import DirectAttack
    from agentdojo.task_suite.load_suites import get_suite

    manifest = json.loads(args.manifest.read_text())
    suite = get_suite(manifest["benchmark_version"], manifest["suite"])
    attack = DirectAttack(suite, None)
    tasks = {}
    for task_id in manifest["user_task_ids"]:
        vectors = attack.get_injection_candidates(suite.get_user_task_by_id(task_id))
        tasks[task_id] = {"count": len(vectors), "vector_ids": vectors}

    per_episode_counts = Counter(task["count"] for task in tasks.values())
    task_surface_counts = [task["count"] for task in tasks.values()]
    injection_task_count = len(manifest["injection_task_ids"])
    report = {
        "run_id": manifest["run_id"],
        "benchmark_version": manifest["benchmark_version"],
        "suite": manifest["suite"],
        "attack": manifest["attack"],
        "user_task_count": len(tasks),
        "injection_task_count": injection_task_count,
        "attacked_episode_count": len(tasks) * injection_task_count,
        "ground_truth_visible_surfaces_per_user_task": tasks,
        "user_tasks_by_surface_count": {
            str(count): frequency for count, frequency in sorted(per_episode_counts.items())
        },
        "surface_count_per_user_task": {
            "minimum": min(task_surface_counts),
            "maximum": max(task_surface_counts),
            "mean": mean(task_surface_counts),
            "median": median(task_surface_counts),
        },
        "surfaces_per_injection_task_matrix": sum(task["count"] for task in tasks.values()),
        "total_injected_surfaces_across_matrix": sum(task["count"] for task in tasks.values())
        * injection_task_count,
        "distinct_vector_ids": sorted(
            {vector for task in tasks.values() for vector in task["vector_ids"]}
        ),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
