# CoTA-Break project status

**Updated:** 2026-09-27  
**Current phase:** Week 1 measurement correctness; pre-training  
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

## Blocking decisions before expensive training

1. Define C1 inference so selecting the historical maximum on test data cannot
   create an upward-biased headline gap. Prefer validation selection plus sealed
   test estimation, or a registered max-statistic procedure.
2. Reconcile the minimum 50 sealed-pair requirement with the 30M-token ceiling;
   the present 30-pair budget expands to roughly 35M tokens at 50 pairs.
3. Record verifier failures at episode and `(user task, injection goal)` level.
4. Distinguish a pilot progression gate from confirmation that C1 exceeds the
   five-point SESOI.
5. Add independent audit-training seeds for a general C2 interaction claim.
6. Freeze immutable model revisions and complete the explicit outcome schema,
   context-limit decision, duplicate/missing-trace tests, and manifest template.

## Next executable actions

1. Finish the remaining Week 1 measurement-correctness tasks and tests.
2. Prospectively amend the statistical and compute sections of protocol v0.3.
3. Inventory Workspace, Banking, and Travel without model inference.
4. Freeze candidate-suite manifests, then screen Qwen3-4B on development data.

Do not rerun the old GPU generations merely to reproduce the same Week 0
numbers. Run new inference only when repairing a verifier/prompt invalidates old
evidence or when executing the new suite-selection protocol.
