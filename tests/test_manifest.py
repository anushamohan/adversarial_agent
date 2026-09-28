import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_agentdojo_baseline import apply_manifest


class ManifestTest(unittest.TestCase):
    def args_for(self, manifest: Path) -> argparse.Namespace:
        return argparse.Namespace(
            manifest=manifest,
            user_task=None,
            model="unused",
            revision="unused",
            benchmark_version="unused",
            suite="unused",
            attack="none",
            injection_task=None,
            seed=0,
            max_context_tokens=0,
            max_new_tokens=0,
        )

    def manifest(self, revision: str) -> dict:
        return {
            "schema_version": 2,
            "outcome_schema_version": 1,
            "run_id": "test",
            "benchmark_version": "v1.2.2",
            "agentdojo_package_version": "0.1.35",
            "suite": "workspace",
            "model": "Qwen/Qwen3-4B",
            "revision": revision,
            "model_snapshot_sha": revision,
            "prompt_template_sha256": "a" * 64,
            "packages": {"agentdojo": "0.1.35"},
            "seed": 17,
            "generation": {"max_context_tokens": 4096, "max_new_tokens": 256},
            "benign_task_ids": ["user_task_0"],
        }

    def test_schema_v2_requires_immutable_revision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(self.manifest("main")))
            with self.assertRaisesRegex(SystemExit, "immutable 40-character"):
                apply_manifest(self.args_for(path))

    def test_schema_v2_accepts_snapshot_sha(self) -> None:
        revision = "1cfa9a7208912126459214e8b04321603b3df60c"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(self.manifest(revision)))
            args, manifest, digest = apply_manifest(self.args_for(path))
        self.assertEqual(args.revision, revision)
        self.assertEqual(manifest["model_snapshot_sha"], revision)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
