#!/usr/bin/env python3
"""Summarize AgentDojo trace quality and apply a frozen decision policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cotabreak.trace_analysis import aggregate_traces, load_unique_trace_set


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def task_number(task_id: str) -> int:
    return int(task_id.rsplit("_", 1)[-1])


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    expected_ids = set(manifest["benign_task_ids"])
    try:
        traces_by_id = load_unique_trace_set(
            args.run_dir.rglob("*.json"),
            expected_ids,
            lambda payload: payload.get("user_task_id"),
            lambda payload: "messages" in payload
            and payload.get("injection_task_id") is None,
            label="Benign",
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    traces = [traces_by_id[task_id] for task_id in sorted(expected_ids, key=task_number)]
    summary_path = args.run_dir / f"{manifest['run_id']}--summary.json"
    summary = json.loads(summary_path.read_text())
    report = aggregate_traces(
        traces,
        manifest["decision_policy"],
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
