# CoTA-Break project status

**Updated:** 2026-09-29
**Current phase:** Week 2 Qwen3-8B NF4 development screen pending; pre-training

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
exposes multiple-call turns as invalid actions. The original 4,096-token
context decision was grounded in the Qwen3-4B attacked p95 of 2,336 tokens
(maximum 3,222) and is superseded for candidate screens below.
All 30 tests pass. All four Week 0 analyses also regenerated successfully into
`/tmp/cotabreak-week1-validation-2026-09-27` without altering raw artifacts.

## Remaining blockers before training

1. Complete the prospectively frozen Qwen3-8B NF4 Workspace development screen
   without weakening the competence or 50-pair gates.
2. Select a suite/model combination that passes competence before any static or
   capability screen.
3. Only after those gates pass, freeze the final split and ledger contract.

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
gate decision. The ISO-8601 repair passed its tests, but the v2 retry then
stopped when a Workspace development prompt reached 4,138 tokens, above the
Slack-derived 4,096 ceiling. The incomplete v2 run is preserved separately.
Candidate screens now use the original 8,192 per-call ceiling while the 30M
counted-token ceiling remains unchanged. Local context overflow is converted
to AgentDojo's handled error path so any future occurrence becomes an explicit
infrastructure-invalid episode rather than aborting the run. Banking has not
started at that point; its first inference used the repaired v3 manifest.

## Week 2 development-screen evidence

Complete v3 results are recorded in
`docs/week2-development-screens-2026-09-27.md`:

| Suite | Utility | Valid calls | Complete verdict |
| --- | ---: | ---: | --- |
| Workspace | 7/20 | 17/28 | fails competence and tool validity |
| Banking | 2/8 | 8/8 | pipeline-only; fails competence |

Both runs pass verifier/infrastructure integrity, but neither reaches 50%
benign utility. Workspace's prompt-token p95 was 4,613 (maximum 4,921); Banking's
was 2,212. Neither suite is eligible for static screening. This does not
authorize SFT, RL, validation, or sealed evaluation.

## Next executable actions

On 2026-09-29, before any Qwen3-8B task outcome, model scaling was selected as
the repair branch. All remaining model-based experiments use
`Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218` with 4-bit NF4,
double quantization, and BF16 compute. Historical Qwen3-4B results remain
unchanged. The gates, splits, SESOI, and hard budgets are unchanged; see
`docs/qwen3-8b-amendment-2026-09-29.md`.

1. Commit the NF4 loader, prospective amendment, and frozen development
   manifests before inference.
2. Cache the official immutable model under `/data/adversarial_agent/huggingface`
   and record the load/inference memory profile.
3. Run the Workspace development-only benign screen. Run Banking only if
   Workspace does not complete suite selection or a second candidate is needed.
4. Do not freeze or run a static screen unless the benign gate passes.
5. Do not start SFT, RL, validation, or sealed evaluation.

Do not rerun the old GPU generations merely to reproduce the same Week 0
numbers. Run new inference only when repairing a verifier/prompt invalidates old
evidence or when executing the new suite-selection protocol.
