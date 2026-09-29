# CoTA-Break: Scaled ARLAS Reproduction

This repository contains a single-GPU, ARLAS-style reproduction that will later
support the historical-vulnerability audit described in
`docs/research-protocol-v0.3.md`.

The first milestone is deliberately small:

1. establish deterministic environment and verifier behavior;
2. reproduce benign and attacked trajectories without learning;
3. add a frozen attacker and historical-opponent evaluation;
4. warm-start small attacker and defender adapters;
5. enable alternating RL only after the earlier gates pass.

## Compute envelope

- One NVIDIA GPU with 24 GB VRAM
- Qwen3-8B attacker and defender backbone for remaining experiments
- 4-bit QLoRA for training
- Separate rollout, training, and evaluation phases
- One AgentDojo suite for the pilot
- Short contexts and small rollout groups initially

This is a scaled reproduction, not an exact reproduction of the published
ARLAS model sizes, episode budget, or full benchmark suite.

## Run the deterministic smoke tests

```bash
python3 -m unittest discover -s tests -v
```

The tests have no third-party dependencies and should pass before model or RL
dependencies are installed.

## Project layout

- `docs/research-protocol-v0.3.md`: refined historical-vulnerability pilot protocol
- `docs/weekly-execution-plan-v0.3.md`: week-by-week implementation and experiment plan
- `docs/research-protocol-v0.2.md`: superseded capability-factored pilot protocol
- `docs/research-protocol-v0.1.md`: superseded initial protocol retained for history
- `configs/single_gpu_24gb.json`: conservative initial compute profile
- `src/cotabreak/toy_env.py`: deterministic environment and independent verifiers
- `tests/test_toy_env.py`: replay, utility, and security checks

## Week 0 Qwen + AgentDojo probe

The first GPU target is `Qwen/Qwen3-0.6B`. It is a pipeline smoke-test model,
not yet the scientific baseline. Keep the environment, package cache, model
cache, and run artifacts on a volume with adequate free space; this machine
uses `/data/adversarial_agent`.

All remaining model-based experiments use the immutable Qwen3-8B snapshot
registered in their manifests and load it with 4-bit NF4 quantization. Model
files must remain in the `/data/adversarial_agent/huggingface` cache; the root
filesystem does not have enough space for the official checkpoint.

```bash
export COTABREAK_DATA_ROOT=/data/adversarial_agent
export HF_HOME="$COTABREAK_DATA_ROOT/huggingface"
export UV_CACHE_DIR="$COTABREAK_DATA_ROOT/uv-cache"

uv venv "$COTABREAK_DATA_ROOT/.venv" --python 3.11
uv pip install --python "$COTABREAK_DATA_ROOT/.venv/bin/python" \
  -r requirements-week0.txt

PYTHONPATH=src "$COTABREAK_DATA_ROOT/.venv/bin/python" \
  scripts/probe_qwen.py --qlora-step \
  --output "$COTABREAK_DATA_ROOT/results/qwen3-0.6b-probe.json"

PYTHONPATH=src "$COTABREAK_DATA_ROOT/.venv/bin/python" \
  scripts/run_agentdojo_baseline.py \
  --suite slack --user-task user_task_0 \
  --output-dir "$COTABREAK_DATA_ROOT/runs/week0"
```

Add `--attack direct --injection-task injection_task_1` to the final command
for the smallest attacked-trajectory smoke test. Each command prints a JSON
measurement record suitable for the Week 0 hardware and feasibility log.

Run the frozen 20-task competence screen and its trace-quality analysis with:

```bash
PYTHONPATH=src "$COTABREAK_DATA_ROOT/.venv/bin/python" \
  scripts/run_agentdojo_baseline.py \
  --manifest configs/manifests/agentdojo_slack_v1.2.2_week0_qwen3_0.6b.json \
  --output-dir "$COTABREAK_DATA_ROOT/runs/week0/slack-qwen3-0.6b-screen-v1" \
  --force

PYTHONPATH=src "$COTABREAK_DATA_ROOT/.venv/bin/python" \
  scripts/analyze_agentdojo_runs.py \
  --run-dir "$COTABREAK_DATA_ROOT/runs/week0/slack-qwen3-0.6b-screen-v1" \
  --manifest configs/manifests/agentdojo_slack_v1.2.2_week0_qwen3_0.6b.json
```

The manifest fixes the task block, held-out task, decoding settings, and model
promotion thresholds before the screen is run.

The paired Qwen capacity screen selected `Qwen/Qwen3-4B` as the provisional
Week 0 baseline: it achieved 13/20 benign task success and 69/72 valid tool
executions. See `docs/week0-feasibility-log-2026-09-08.md` for the complete
0.6B, 1.7B, and 4B comparison. Static-attack and intervention-depth gates are
still required before adversarial training.

The subsequent 100-episode direct-attack screen produced 11% ASR and 49%
attacked utility, but the registered gate did not pass: only 3/5 attack goals
were completed in standalone capability checks, and the selected Slack tasks
have median intervention depth one. This configuration is suitable for the
static reproduction but not yet for adversarial co-training. After Qwen3-4B
also failed the Workspace and Banking development competence gates, the
remaining study prospectively moved to Qwen3-8B NF4. The next action is the
frozen Workspace development screen, not SFT or RL.
