#!/usr/bin/env python3
"""Analyze a frozen AgentDojo static-attack matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cotabreak.trace_analysis import aggregate_attack_traces


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    expected_pairs = {
        (user_task_id, injection_task_id)
        for user_task_id in manifest["user_task_ids"]
        for injection_task_id in manifest["injection_task_ids"]
    }
    traces_by_pair: dict[tuple[str, str], dict] = {}
    trace_paths_by_pair: dict[tuple[str, str], list[Path]] = {}
    for path in args.run_dir.rglob("*.json"):
        payload = json.loads(path.read_text())
        pair = (payload.get("user_task_id"), payload.get("injection_task_id"))
        if pair in expected_pairs and payload.get("attack_type") == manifest["attack"]:
            trace_paths_by_pair.setdefault(pair, []).append(path)
            traces_by_pair[pair] = payload

    missing = expected_pairs - traces_by_pair.keys()
    duplicates = {
        pair: [str(path) for path in paths]
        for pair, paths in trace_paths_by_pair.items()
        if len(paths) != 1
    }
    if missing or duplicates:
        raise SystemExit(
            f"Attacked trace set mismatch: missing={sorted(missing)}, "
            f"duplicates={duplicates}"
        )

    summary_path = args.run_dir / f"{manifest['run_id']}--summary.json"
    summary = json.loads(summary_path.read_text())
    auxiliary_results: dict[str, bool] = {}
    for injection_task_id in manifest["injection_task_ids"]:
        candidates = list(
            args.run_dir.rglob(f"{injection_task_id}/none/none.json")
        )
        if len(candidates) != 1:
            raise SystemExit(
                f"Expected one auxiliary trace for {injection_task_id}, found {len(candidates)}"
            )
        auxiliary_results[injection_task_id] = bool(
            json.loads(candidates[0].read_text()).get("utility", False)
        )
    report = aggregate_attack_traces(
        [traces_by_pair[pair] for pair in sorted(expected_pairs)],
        manifest["decision_policy"],
        summary["injection_task_completion_rate"],
        summary.get("verifier_recoveries", []),
        auxiliary_results,
    )
    report.update(
        {
            "run_id": manifest["run_id"],
            "model": manifest["model"],
            "benchmark_version": manifest["benchmark_version"],
            "suite": manifest["suite"],
            "attack": manifest["attack"],
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
