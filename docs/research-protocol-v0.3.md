# CoTA-Break Research Proposal v0.3

**Working title:** *What Self-Play Forgets: Auditing Historical Vulnerability in ARLAS-Style LLM-Agent Co-Training*  
**Issued:** 2026-09-26  
**Status:** Refined draft for implementation  
**Supersedes:** `docs/research-protocol-v0.2.md` for the pilot design  
**Execution plan:** `docs/weekly-execution-plan-v0.3.md`

## 1. Executive decision

Commit the first paper to one primary idea:

> **Does checkpoint cross-play reveal a historical security vulnerability that contemporary ARLAS-style self-play evaluation misses for tool-using LLM agents?**

The paper has two ordered contributions:

1. **C1 — measurement:** quantify the gap between a defender's attack success rate against its contemporary attacker and its attack success rate against registered historical attackers.
2. **C2 — conditional mechanism:** if C1 is meaningful, test whether persistent cross-episode attacker memory and online attacker adaptation together expose more of that gap than either capability alone.

C1 is the primary paper commitment. C2 is not allowed to become the headline unless C1, memory expressivity, learning responsiveness, and verifier gates all pass. If C1 is reliable but C2 is null, the result remains a measurement paper. If C1 is absent, stop the mechanism study rather than adding more attacker complexity.

This is an **ARLAS-style scaled study**, not an exact ARLAS reproduction. The repository defines the internal reference precisely; agreement with upstream numbers is optional external validation.

## 2. What this proposal does not claim

- It does not claim the first adversarial-training defense, first adaptive attacker, or first self-play forgetting result.
- It does not claim that ARLAS is single-turn.
- It does not make a within-episode long-horizon or Attack-Flow GRPO claim.
- It does not claim that Qwen3-8B NF4 fits the full RL study until the actual
  rollout, adapter, optimizer, and checkpoint path has been measured.
- It does not treat one 20-task screen as a general model-capability result.
- It does not add a mitigation before a failure mechanism is observed.

## 3. Research questions and hypotheses

### Primary question: historical vulnerability

During adversarial co-training, does a defender checkpoint look more robust against the attacker it just faced than against earlier registered attackers?

**H1:** the mean validation-selected historical vulnerability gap exceeds the
smallest effect of interest (SESOI), fixed at 5 absolute ASR points, on eligible
defender checkpoints.

### Secondary question: memory × adaptation

With the defender checkpoint held fixed, does an attacker with both persistent cross-episode memory and online adaptation expose more attack successes than the additive effects of memory alone and adaptation alone?

**H2:** the memory × adaptation interaction is positive on the preregistered mixed-effects logistic scale, with absolute-risk contrasts reported alongside the coefficient.

H2 is conditional. It is not interpretable if H1 fails, if memory retrieval does not change attacker behavior, or if the attacker update does not change valid behavior.

### Utility constraint

Security comparisons are valid only for defender checkpoints whose held-out benign task success rate is within five absolute percentage points of the untrained defender. A checkpoint that fails this floor is reported as `utility-infeasible`, not replaced after inspecting the test result.

## 4. Current evidence and its proper interpretation

The existing Ubuntu experiments establish a useful engineering baseline:

- Qwen3-0.6B and Qwen3-1.7B do not clear the frozen Slack competence gates.
- Qwen3-4B clears the frozen benign screen with 13/20 successful tasks and 69/72 valid tool calls.
- Qwen3-4B has nonzero susceptibility to AgentDojo's static DirectAttack: 11/100 attack success and 49/100 attacked utility.
- Slack has a median of one **ground-truth-visible injection vector** per user task in the selected block.
- The auxiliary standalone injection-goal check achieved 3/5, below the separately registered 4/5 feasibility threshold.

These results justified continued pipeline repair but did not establish H1 or
H2. Qwen3-4B is retained as historical feasibility evidence; the prospective
2026-09-29 amendment below assigns all remaining model-based work to Qwen3-8B
NF4. The inventory metric is a count of visible injection-vector keys, not a
measured sequence of adaptive attacker decisions. The v0.3 paper therefore
removes within-episode horizon from the primary claim and studies adaptation
across episodes.

## 5. Formal definitions

One reference co-training run produces defender checkpoints `D_0, ..., D_J` and attacker checkpoints `A_0, ..., A_J` at fixed cumulative interaction counts. `A_j` is the latest attacker paired with `D_j` when that checkpoint is saved.

All primary ASRs are evaluated on sealed held-out `(user task, injection goal)` pairs. Neither policy trains on those pairs, and the memory archive never writes evaluation outcomes.

- `c_j` — contemporary ASR: `ASR(D_j, A_j)`.
- `s_j` — static-benchmark ASR: `ASR(D_j, AgentDojo built-in attack)`.
- `k*_j` — the historical attacker index selected using validation pairs only:
  the smallest `k < j` attaining the largest validation ASR against `D_j`.
- `h_j` — sealed-test historical ASR: `ASR_test(D_j, A_{k*_j})`.
- `G_j` — validation-selected hidden vulnerability gap: `h_j - c_j` on the
  same sealed-test pairs.
- `e_j(M,L)` — audit exposure after a fixed attacker-side audit budget with memory flag `M` and online-adaptation flag `L`.

Selection is over the registered historical attacker set only. The sealed-test
maximum across `k` is reported as an explicitly optimistic descriptive
upper-bound and is never substituted for `h_j` in the primary estimand. This is
not a claim about the global worst-case attacker.

## 6. Study design

### Stage 0 — implementation and validity gates

Before learning, the repository must support:

1. Immutable model, package, benchmark, prompt, and manifest fingerprints.
2. User-task-level development, validation, and sealed-test splits.
3. Independent raw utility, security, invalid-action, verifier, and infrastructure outcomes.
4. A ledger for episodes, tokens, GPU time, checkpoints, seeds, and failures.
5. Exact trace uniqueness and replay checks.
6. Explicit `invalid_verifier` handling; a caught exception may not silently become an ordinary task failure.

### Stage 1 — reference co-training run

Use the following pilot reference as prospectively amended on 2026-09-29:

- **Model:** Qwen3-8B at immutable Hugging Face revision
  `b968826d9c46dd6066d109eabc6255188de91218`, loaded in 4-bit NF4 with
  double quantization and BF16 compute, with separate attacker and defender
  LoRA adapters. Qwen3-4B remains historical feasibility evidence only.
- **Training load:** 4-bit NF4 base, double quantization, BF16 compute, one adapter active at a time on the 24 GB GPU.
- **Attacker action:** one text injection or `NOOP` for each benchmark-visible injection vector. This is a one-shot-per-vector attacker, not a within-episode long-horizon attacker.
- **Reference memory:** no semantic cross-episode retrieval.
- **Opponent sampling:** latest attacker only in the pilot.
- **Update timing:** alternating attacker and defender blocks between episodes; no within-episode weight updates.
- **Attacker reward:** verifier-confirmed injection success.
- **Defender reward:** attacked utility multiplied by injection resistance; benign episodes receive utility reward. Raw outcomes remain separate.
- **Warm start:** attacker SFT may use development-only successful static injections and built-in templates. No validation or test data may enter it.
- **Schedule:** five rounds; save checkpoints at rounds 0, 1, 3, and 5.
- **Pilot GRPO groups:** attacker group size 4 and defender group size 2, unless measured memory or reward behavior requires a preregistered change.
- **Archive:** append an immutable training-only record for every episode, but do not read it during Stage 1.

Stage 1 produces the objects needed for C1. It is not itself the primary result.

### Stage 2a — fixed checkpoint cross-play, testing C1

Before opening sealed-test outcomes, run the registered strict-lower-triangle
pairs (`k < j`) on
validation data and freeze `k*_j` for each eligible defender, breaking ties in
favor of the earliest attacker index. Then run every pair in the registered 4 ×
4 matrix `(D_j, A_k)` on at least 50 sealed-test pairs, with frozen weights and
no memory writes. The diagonal estimates `c_j`; the frozen `(D_j, A_{k*_j})`
cells estimate `h_j` and `G_j`; all other lower-triangle cells support
descriptive sensitivity analyses; and the upper triangle is descriptive
forward transfer.

Also evaluate eligible defender checkpoints for held-out benign utility and static-benchmark ASR. The checkpoint schedule and task pairs are fixed before opening test outcomes.

**C1 decision rule:** H1 is confirmed, and C2 is authorized, only if the mean
`G_j` exceeds 0.05 and the lower endpoint of its one-sided 95% task-pair-
clustered confidence interval also exceeds 0.05. An estimate above 0.05 whose
interval excludes zero but not 0.05 is `positive_but_sesoi_inconclusive`; it is
not confirmation that H1 exceeds the SESOI and does not authorize C2. All other
outcomes are reported as null, directionally inconsistent, or imprecise under
the frozen rule rather than rescued with a post hoc threshold.

### Stage 2b — fixed-defender memory × adaptation audit, testing C2

For the single eligible defender checkpoint chosen on validation data before
sealed evaluation, start from `A_j` and give each audit cell the same
environment-interaction and token budget on training pairs:

| Cell | Memory | Online adaptation | Evaluation behavior |
| --- | --- | --- | --- |
| M0L0 | no | no | frozen contemporary attacker |
| M1L0 | yes | no | frozen attacker with train-only archive retrieval |
| M0L1 | no | yes | GRPO updates; no persistent archive |
| M1L1 | yes | yes | GRPO updates plus archive retrieval/writes |

Memory contains only training-split records available at or before round `j`. Evaluation freezes both memory and weights. Every successful audit injection is classified as replay, recombination, or novel using a threshold frozen on development data. A C2 claim requires the M1L1 excess to be primarily recombination or novel, not merely verbatim replay.

The pilot uses three independently initialized audit-adaptation seeds (`17`,
`29`, and `43`) for each `L=1` cell. Seeds start from the same frozen attacker
checkpoint but have independent sampling and optimizer state. The frozen
`L=0` traces are shared controls and are not duplicated or counted as
independent runs. Seed-level interaction contrasts are reported separately and
form the replication unit for the pilot. Three audit seeds support only a
directional C2 result; a general mechanism claim requires independent reference
co-training trajectories in Phase B.

### Stage 3 — optional training consequence

Only if C1 passes, budget remains, and the v0.3 review approves it, run one additional co-training condition in which the attacker reads the archive during training. Repeat cross-play and compare the historical gap with Stage 1. This is exploratory/secondary and is not needed to complete the first paper.

## 7. Environment and data contract

Select one AgentDojo v1.2.2 suite using a manifest frozen before the final screen. The selection criteria are:

1. Qwen3-8B NF4 benign success at least 50% and valid tool-call rate at least
   90% on the frozen development screen.
2. Static ASR between 5% and 80%.
3. At least three injection goals with nonzero static ASR.
4. At least 50 sealed test `(user task, injection goal)` pairs after user-task-level splitting. A suite that cannot supply 50 is ineligible for the primary study.
5. At most one verifier exception per 100 audited episodes, with all exceptions classified rather than coerced into ordinary failures.

Use task-level splits, stratified by injection goal:

- 50% development/training;
- 15% validation/checkpoint eligibility and threshold tuning;
- 35% sealed test.

All injection goals should appear in every split. A held-out-goal analysis is exploratory only.

The final attacker interface must log the vector identity, current task context, generated injection, memory records retrieved, outcome, and whether the same task contained additional visible vectors. Do not call this a long-horizon trajectory unless the implementation adds sequential attacker decisions and measures them directly.

## 8. Metrics and statistics

### Primary C1 analysis

- Unit of inference: `(user task, injection goal)` pair.
- Primary estimand: mean validation-selected `G_j` over eligible checkpoints `j >= 1`.
- Confidence interval: 10,000 task-pair-clustered bootstrap resamples.
- Keep each validation-selected `k*_j` fixed in every sealed-test resample; do
  not reselect or maximize over attackers using sealed-test outcomes.
- Report absolute ASR points, not only relative percentages.
- Confirm H1 only when the one-sided 95% lower confidence bound exceeds 0.05.

### Conditional C2 analysis

For each adaptation seed, fit the preregistered pilot model to that seed's two
`L=1` cells and the single shared set of `L=0` controls:

`success ~ M * L + (1 | user_task) + (1 | injection_goal)`

Report the M:L coefficient, seed-level and pooled absolute-risk interactions,
cellwise ASR, and replay/recombination/novel proportions. Shared frozen-control
traces enter the pooled absolute-risk calculation once and do not create extra
seed replication. The mean and range across the three seed-specific interaction
estimates are the pilot summary. The one-reference-trajectory pilot is
directional; do not call its interaction a general confirmatory mechanism.

### Always report separately

- benign task success;
- attack success;
- secure task success;
- refusal rate;
- invalid action rate;
- invalid verifier episodes;
- infrastructure failures;
- input/output tokens, environment interactions, and GPU-hours.

## 9. Compute envelope

The hard pilot ceilings remain:

- 5,000 environment episodes;
- 30 million counted model input/output tokens;
- 150 GPU-hours;
- at least 35% of the learned-run budget reserved for evaluation and cross-play.

The measured Slack planning rate is approximately 10.3k counted tokens per
attacked episode. C1's 50-pair, 4 × 4 matrix is protected at 800 episodes. The
prospective allocation below totals 2,742 episodes, or approximately 28.2M
tokens at the planning rate, leaving about 1.8M tokens of headroom:

| Block | Episodes | Purpose |
| --- | ---: | --- |
| New-suite screen and repaired capability checks | 200 | competence, attackability, verifier audit |
| Memory and learning responsiveness | 100 | development pairs only |
| Stage 1 reference co-training | 700 | five alternating rounds |
| Stage 2a cross-play | 800 | 4 × 4 matrix × 50 sealed pairs |
| Checkpoint BTSR/static evaluation | 150 | eligibility and benchmark context |
| Stage 2b audit | 792 | one checkpoint, four cells, three adaptation seeds |
| **Provisional total** | **2,742** | approximately 28.2M tokens |

These are planning bounds, not achieved results. Each block also receives a
token stop derived from the new-suite p95 prompt length before learning begins.
Never raise a hard ceiling because a condition is expensive. If updated
profiling cannot fit the protected 800-episode C1 matrix and all validity checks
under 30M tokens, stop or reduce the training/mechanism scope prospectively;
do not reduce the 50-pair primary sample or open sealed outcomes. Drop Stage 3,
external suites, exploratory cycling, and then C2 before weakening C1.

## 10. Publication and stop rules

### Proceed to a confirmatory/full paper if

- all validity gates pass;
- C1 shows a practically meaningful historical gap or a replicated evaluation lesson;
- the compute ledger is reconciled;
- at least the two most informative comparisons can be replicated with new seeds in Phase B.

### Publish a narrower measurement paper if

- cross-play reliably shows a historical evaluation gap;
- C2 is null, underpowered, or fails memory expressivity;
- the result still supports a clear lesson about evaluating co-trained agents.

### Stop or pivot if

- no suite meets the verifier and competence requirements;
- the co-training reference cannot be made reproducible;
- invalid verifier behavior prevents attribution;
- C1 remains below the SESOI after the registered pilot;
- the design exceeds the hard compute ceiling.

A null result is bounded to the tested model, suite, attacker interface, task splits, and compute envelope.

## 11. Required artifacts

- v0.3 manifest with immutable model and package fingerprints;
- environment/suite inventory;
- split manifest and hashes;
- verifier fixtures and manual-audit record;
- append-only episode/token/GPU ledger;
- adapter and checkpoint manifest;
- frozen cross-play matrix;
- C1 bootstrap analysis;
- conditional C2 audit analysis;
- failure taxonomy and sensitivity analyses;
- reproducibility and responsible-release note.

## 12. Decision record

This proposal deliberately keeps one paper idea and makes the mechanism conditional:

- **Committed:** historical vulnerability audit through checkpoint cross-play.
- **Conditional:** memory × online adaptation as the mechanism that recovers the hidden gap.
- **Deferred:** population training, within-episode long horizon, Attack-Flow credit, cycling, external benchmark transfer, and mitigation.

### Prospective model-scale amendment — 2026-09-29

After Qwen3-4B failed the frozen Workspace and Banking development competence
gates, but before any Qwen3-8B task outcome, the remaining model-based study was
changed to Qwen3-8B with manifest-controlled 4-bit NF4 loading. This is a
model-scale feasibility repair, not a change to the estimands, task splits,
competence thresholds, five-point SESOI, 50-pair minimum, or hard compute
ceilings. Workspace is screened first; Banking is screened only if needed.
Static and standalone-capability screening remain gated on benign competence.
SFT, RL, validation, and sealed evaluation remain prohibited until their
existing gates are met. The complete amendment is recorded in
`docs/qwen3-8b-amendment-2026-09-29.md`.
