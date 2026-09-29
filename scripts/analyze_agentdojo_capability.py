#!/usr/bin/env python3
"""Analyze a frozen repeated standalone injection-goal capability run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cotabreak.trace_analysis import aggregate_capability_trials


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    trials: list[tuple[int, dict]] = []
    missing: list[str] = []
    duplicates: dict[str, list[str]] = {}
    for trial_index in range(int(manifest["trials_per_goal"])):
        trial_dir = args.run_dir / f"trial_{trial_index}"
        for goal_id in manifest["injection_task_ids"]:
            candidates = list(trial_dir.rglob(f"{goal_id}/none/none.json"))
            key = f"trial_{trial_index}:{goal_id}"
            if not candidates:
                missing.append(key)
            elif len(candidates) > 1:
                duplicates[key] = [str(path) for path in candidates]
            else:
                trials.append((trial_index, json.loads(candidates[0].read_text())))
    if missing or duplicates:
        raise SystemExit(
            f"Capability trace set mismatch: missing={missing}, duplicates={duplicates}"
        )
    summary_path = args.run_dir / f"{manifest['run_id']}--summary.json"
    summary = json.loads(summary_path.read_text())
    report = aggregate_capability_trials(
        trials,
        {
            **manifest["decision_policy"],
            "trials_per_goal": manifest["trials_per_goal"],
        },
        summary.get("verifier_recoveries", []),
    )
    report.update(
        {
            "run_id": manifest["run_id"],
            "model": manifest["model"],
            "benchmark_version": manifest["benchmark_version"],
            "suite": manifest["suite"],
            "manifest": str(args.manifest.resolve()),
            "run_directory": str(args.run_dir.resolve()),
        }
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    output = args.output or args.run_dir / f"{manifest['run_id']}--analysis.json"
    output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
