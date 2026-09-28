# Week 2 Qwen3-4B development screens

**Date:** 2026-09-27
**Model snapshot:** `Qwen/Qwen3-4B@1cfa9a7208912126459214e8b04321603b3df60c`
**AgentDojo:** 0.1.35 (`v1.2.2` suites)
**Data scope:** development user tasks only

## Complete v3 results

| Suite | Utility | Valid tool calls | Integrity | Registered decision |
| --- | ---: | ---: | --- | --- |
| Workspace | 7/20 (35%) | 17/28 (60.7%) | pass; no verifier or infrastructure errors | fail competence and tool validity |
| Banking | 2/8 (25%) | 8/8 (100%) | pass; no verifier or infrastructure errors | pipeline-only; fail competence |

Workspace contained seven episodes classified `invalid_action`; Banking had
none. These labels remain separate from raw utility. Neither result reaches the
registered 50% benign-task-success threshold, so neither suite advances to a
static-attack or standalone-capability screen. This is a Week 2 competence-gate
stop, not evidence about C1 or C2.

## Token and runtime profile

| Suite | Model calls | Input tokens | Output tokens | Input p95 | Input max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Workspace | 46 | 180,763 | 3,615 | 4,613 | 4,921 |
| Banking | 16 | 28,061 | 841 | 2,212 | 2,212 |

Workspace confirms that the earlier 4,096-token ceiling was not portable from
Slack. The v3 screen used an 8,192 per-call ceiling while counting actual tokens
against the unchanged 30M pilot limit.

## Infrastructure attempts and provenance

- Workspace v1, from commit `82e2a0a`, stopped after one completed task because
  AgentDojo's JSON formatter could not serialize a calendar `datetime`.
- Commit `92ac44f` added deterministic ISO-8601 JSON tool serialization.
- Workspace v2 then stopped when a development prompt reached 4,138 tokens,
  above the 4,096 ceiling.
- Commit `a611549` changed candidate screens to 8,192 tokens and routed future
  local context overflows through AgentDojo's explicit infrastructure-error
  path.
- The successful v3 manifests were committed in `6501fb2` before either v3 run.

The incomplete v1 and v2 raw directories remain preserved and have no gate
decision. Complete raw traces and derived analyses are separate:

| Suite | Raw traces | Derived analysis | Analysis SHA-256 |
| --- | --- | --- | --- |
| Workspace | `/data/adversarial_agent/runs/week2/workspace-qwen3-4b-dev-benign-v3` | `/data/adversarial_agent/analysis/week2/workspace-qwen3-4b-dev-benign-v3.json` | `32f243acb037a239ff268679d1e153c3ef2649917a6381785528bdbb5b6f5850` |
| Banking | `/data/adversarial_agent/runs/week2/banking-qwen3-4b-dev-benign-v3` | `/data/adversarial_agent/analysis/week2/banking-qwen3-4b-dev-benign-v3.json` | `1f3921b091dea9abf9b863dc06a9d53065abc4a3a42cd3c52df8af47e31e66d1` |

No validation task, sealed-test task, SFT, RL, static attack, or capability
screen was run.
