# CoTA-Break: Scaled ARLAS Reproduction

This repository contains a single-GPU, ARLAS-style reproduction that will later
support the capability-factored CoTA-Break experiments described in
`co-training-stress-test-proposal-revised.md`.

The first milestone is deliberately small:

1. establish deterministic environment and verifier behavior;
2. reproduce benign and attacked trajectories without learning;
3. add a frozen attacker and historical-opponent evaluation;
4. warm-start small attacker and defender adapters;
5. enable alternating RL only after the earlier gates pass.

## Compute envelope

- One NVIDIA GPU with 24 GB VRAM
- 1.5B--4B attacker and defender backbones
- 4-bit QLoRA for training
- Separate rollout, training, and evaluation phases
- One AgentDojo suite for the pilot
- Short contexts and small rollout groups initially

This is a scaled reproduction, not an exact reproduction of the published
ARLAS model sizes, episode budget, or full benchmark suite.

## Run the deterministic smoke tests

```bash
python -m unittest discover -s tests -v
```

The tests have no third-party dependencies and should pass before model or RL
dependencies are installed.

## Project layout

- `docs/research-protocol-v0.1.md`: frozen pilot scope and gates
- `configs/single_gpu_24gb.json`: conservative initial compute profile
- `src/cotabreak/toy_env.py`: deterministic environment and independent verifiers
- `tests/test_toy_env.py`: replay, utility, and security checks

