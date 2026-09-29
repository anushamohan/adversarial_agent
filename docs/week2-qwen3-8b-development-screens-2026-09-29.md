# Week 2 Qwen3-8B NF4 development screens

**Date:** 2026-09-29
**Model:** `Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218`
**Quantization:** 4-bit NF4, double quantization, BF16 compute
**AgentDojo:** 0.1.35 (`v1.2.2` suites)
**Data scope:** development user tasks only

## Hardware and cache verification

The official snapshot occupies 16 GB in
`/data/adversarial_agent/huggingface/hub/models--Qwen--Qwen3-8B`. The
non-task probe loaded the immutable revision, returned `QWEN_PROBE_OK`, and
measured 7,812 MiB peak allocated VRAM on the RTX 4090. Its artifact is
`/data/adversarial_agent/results/qwen3-8b-nf4-inference-probe-2026-09-29.json`
(SHA-256 `84bd91348e123cd2c37258ad68123f90674f903642c3d9f93a353a356f28f049`).
This does not establish QLoRA training fit.

## Complete benign results

| Suite | Utility | Valid tool calls | Integrity | Complete verdict |
| --- | ---: | ---: | --- | --- |
| Workspace | 9/20 (45%) | 40/58 (69.0%) | pass | fail competence and tool validity |
| Banking | 5/8 (62.5%) | 22/22 (100%) | pass | pass benign development gate |

Neither run contains a verifier recovery, invalid verifier episode, trace
error, or infrastructure error. Workspace has six invalid-action episodes
caused by tool execution errors and cannot advance. Banking has no invalid
actions and is eligible for the development static and standalone-capability
screens. This is not authorization for SFT, RL, validation, or sealed
evaluation.

## Token and runtime profile

| Suite | Model calls | Input tokens | Output tokens | Peak VRAM | Generation time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Workspace | 78 | 330,998 | 4,131 | 7,313 MiB | 129.8 s |
| Banking | 30 | 58,510 | 1,409 | 6,476 MiB | 34.6 s |

Workspace reached 6,217 input tokens, remaining within the frozen 8,192-token
handled ceiling. Banking reached 2,624 input tokens.

## Provenance

| Suite | Manifest SHA-256 | Raw traces | Derived analysis | Analysis SHA-256 |
| --- | --- | --- | --- | --- |
| Workspace | `3a9c401c3f675df5eec65a8dd240248affa10dd41b329489269d858ea2cf18e9` | `/data/adversarial_agent/runs/week2/workspace-qwen3-8b-nf4-dev-benign-v1` | `/data/adversarial_agent/analysis/week2/workspace-qwen3-8b-nf4-dev-benign-v1.json` | `9acc679508c1e5b973d1fcba9cc942f2054b06e21cbab9ae30d0f40e3250a3ed` |
| Banking | `af92a9d4888f986628e3c8be9d1bbb16cfb0b1bb451d18d19fb3f8e797cc818b` | `/data/adversarial_agent/runs/week2/banking-qwen3-8b-nf4-dev-benign-v1` | `/data/adversarial_agent/analysis/week2/banking-qwen3-8b-nf4-dev-benign-v1.json` | `96489e070ee77a8d2bf20469058d5d37e451c34ae5ec6f86938be25ce9e01c16` |

Both runs started from clean pushed commit
`da3cc73acd9b7deaacb1a0994c83a66da5c19724`. Validation and sealed-test tasks
were not executed.
