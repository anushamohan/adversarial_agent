# CoTA-Break project status

**Updated:** 2026-09-27  
**Current phase:** Week 2 read-only suite inventory; pre-training
**Authoritative protocol:** `docs/research-protocol-v0.3.md`  
**Execution plan:** `docs/weekly-execution-plan-v0.3.md`

## Objective

Build a publication-quality measurement study of whether contemporary
ARLAS-style self-play evaluation hides vulnerabilities exposed by registered
historical attackers. The memory × online-adaptation study is conditional on a
credible historical-vulnerability result and its validity gates.

## Reproduced evidence

All registered Week 0 analyses were regenerated from preserved raw traces on
2026-09-27. See `docs/week0-reanalysis-2026-09-27.md`.

| Run | Main result | Registered verdict |
| --- | --- | --- |
| Qwen3-0.6B benign | 3/20 utility; 28/37 valid calls | Fails competence |
| Qwen3-1.7B benign | 4/20 utility; 30/35 valid calls | Fails competence |
| Qwen3-4B benign | 13/20 utility; 69/72 valid calls | Passes provisional benign gate |
| Qwen3-4B DirectAttack | 11/100 ASR; 49/100 attacked utility; 3/5 capability checks | Fails complete attack gate: one verifier recovery and capability below 4/5 |

The correct interpretation is that Qwen3-4B and the pipeline are feasible
enough to continue repairing and screening. The current attack run is not a
clean publication baseline and does not authorize co-training.

## Resolved in the current worktree

- The single `<function=...>` parser regression found in commit `41d57fc` is
  repaired, with tests for native, legacy, mixed, and multiple-call output.
- Week 0 derived reports can be regenerated from the original `/data` raw
  artifacts without rerunning GPU inference.

## Week 1 measurement decisions

Protocol v0.3 was prospectively amended on 2026-09-27, before training or
sealed evaluation:

1. Select one strictly historical attacker (`k < j`) per defender on validation
   data and estimate the frozen contrast on sealed test pairs. A test-set
   historical maximum is descriptive only.
2. Confirm H1 only when the one-sided 95% lower confidence bound for the mean
   gap exceeds the five-point SESOI. A positive interval that does not clear
   five points is `positive_but_sesoi_inconclusive` and does not authorize C2.
3. Protect 50 sealed pairs and 800 C1 matrix episodes. The revised 2,742-episode
   plan is approximately 28.2M tokens at the current planning rate; if updated
   profiling cannot fit under 30M, reduce or drop C2 before weakening C1.
4. Use three independent audit-adaptation seeds for each active C2 cell, with
   frozen controls shared rather than duplicated. The one-reference-trajectory
   pilot remains directional; a general C2 claim requires independent reference
   trajectories.
5. Attribute verifier exceptions to `(user task, injection goal)` episodes and
   expose `invalid_verifier`, `invalid_action`, `trace_error`, and
   `infrastructure_error` separately.

Implementation now requires immutable model SHAs and prompt/package
fingerprints in schema-v2 manifests, rejects missing or duplicate traces,
exposes multiple-call turns as invalid actions, and uses a 4,096-token context
ceiling grounded in the Qwen3-4B attacked p95 of 2,336 tokens (maximum 3,222).
All 28 tests pass. All four Week 0 analyses also regenerated successfully into
`/tmp/cotabreak-week1-validation-2026-09-27` without altering raw artifacts.

## Remaining blockers before training

1. Run development-only Qwen3-4B benign and repaired static/capability screens.
2. Select a suite that passes competence, attackability, 50-pair, and verifier
   gates; freeze its final split and ledger contract.
3. Measure new-suite p95 tokens and bind per-block token stops before learning.

## Week 2 inventory evidence

The read-only AgentDojo v1.2.2 inventory is recorded in
`docs/week2-suite-inventory-2026-09-27.md` and the JSON artifacts under
`docs/data/agentdojo-v1.2.2-suite-inventory/`.

| Suite | User tasks | Injection goals | Sealed pairs | Decision |
| --- | ---: | ---: | ---: | --- |
| Workspace | 40 | 14 | 196 | advance to development screen |
| Banking | 16 | 9 | 54 | advance to development screen |
| Travel | 20 | 7 | 49 | ineligible under the frozen 50-pair minimum |

Workspace and Banking schema-v2 development manifests were frozen before any
new model outcome. Travel will not be screened. No validation or sealed-test
task has been executed.

The first Workspace development-screen attempt from commit `82e2a0a` stopped
after one completed task when AgentDojo's JSON tool-output formatter could not
serialize a calendar `datetime`. The incomplete raw run is preserved at
`/data/adversarial_agent/runs/week2/workspace-qwen3-4b-dev-benign-v1`; it has no
gate decision. A deterministic ISO-8601 JSON formatter is being repaired and
tested before a new manifest and run ID are frozen. Banking has not started.

## Next executable actions

1. Commit and push the read-only inventory and candidate manifests.
2. Screen Qwen3-4B on Workspace and Banking development tasks only under those
   committed manifests.
3. Freeze static-screen manifests only for suites that pass the benign gate.
4. Do not start SFT, RL, or sealed evaluation.

Do not rerun the old GPU generations merely to reproduce the same Week 0
numbers. Run new inference only when repairing a verifier/prompt invalidates old
evidence or when executing the new suite-selection protocol.
