# CoTA-Break v0.3 — weekly execution plan

**Companion proposal:** `docs/research-protocol-v0.3.md`  
**Pilot length:** 10 weeks  
**Pilot purpose:** establish whether a historical vulnerability gap exists and, only if it does, test the memory × adaptation mechanism.

The earlier 6–8 week estimate is replaced by 10 weeks because the current repository has no training loop, checkpoint manager, memory archive, or cross-play runner. The pilot may finish sooner, but the schedule should not assume those components already exist.

## Standing rules for every week

- Start each experiment from a committed code revision and frozen manifest.
- Record manifest hash, model snapshot, package versions, seed, task IDs, prompt/template settings, token counts, wall time, GPU time, and failures.
- Never write validation or sealed-test outcomes into prompts, memory, model selection, or checkpoints.
- Keep raw utility, raw security, invalid verifier, malformed action, refusal, and infrastructure outcomes separate.
- End each week with a short decision note: proceed, repair, reduce scope, or stop.
- Back up checkpoints and the append-only ledger before changing the training code.

## Week 1 — freeze the question and repair measurement correctness

### Tasks

- [x] Create and prospectively amend the v0.3 protocol with the C1 primary
  endpoint, validation-only historical-attacker selection, five-point SESOI
  rule, C2 conditional endpoint and independent audit seeds, utility floor,
  protected 50-pair sample, compute reconciliation, and stop rules.
- [x] Replace the mutable `EmptyEnv()` default in the Qwen adapter with `None`
  handling.
- [x] Require immutable model revisions in schema-v2 manifests and record the
  requested and resolved model snapshot identifiers.
- [x] Add an explicit run schema for `invalid_verifier`, `invalid_action`,
  `trace_error`, and `infrastructure_error`.
- [x] Attribute caught verifier exceptions to the episode and mark them
  `invalid_verifier` rather than allowing a silent ordinary utility failure.
- [x] Add duplicate-trace detection to both analysis scripts.
- [x] Enforce one tool call per assistant turn and expose violations as invalid
  actions.
- [x] Resolve candidate screens to an 8,192-token per-call ceiling with counted
  token stops. The initial 4,096 choice from Slack's p95 of 2,336 and maximum
  of 3,222 was prospectively superseded after a Workspace development prompt
  reached 4,138 tokens; no validation or sealed outcome was opened.
- [x] Add tests for verifier exceptions, duplicate traces, multiple calls,
  missing fields, and invalid episodes.

### Deliverables

- corrected trace schema;
- updated unit tests;
- v0.3 decision record;
- immutable experiment-manifest template.

### Exit gate

The same synthetic traces produce the same aggregates, verifier exceptions are visible as invalid, and no analysis script silently chooses among duplicates.

## Week 2 — inventory suites and select the environment

### Tasks

- [x] Run the injection-vector inventory read-only on Workspace, Banking, and Travel at AgentDojo v1.2.2.
- [x] Report task count, goal count, visible-vector count, vector identities, and resulting sealed pair count for each suite.
- [x] Label the metric `visible_injection_vector_count`; do not call it intervention depth.
- [x] Freeze candidate suite manifests before model outcome screens.
- [x] Run Qwen3-4B benign screens on shortlisted suites using development tasks only.
- [ ] Run the prospectively frozen Qwen3-8B NF4 benign screen on Workspace;
  screen Banking only if Workspace does not complete the full suite-selection
  gate or a second candidate is required.
- [ ] Before any task outcome, verify the immutable 8B revision, NF4 load,
  cache location, peak inference VRAM, and manifest fingerprints from a
  committed revision.
- [ ] Run the repaired static screen on at most two candidate suites.
- [ ] Run five standalone capability trials per injection goal on a new manifest, preserving the original Slack 3/5 result unchanged.
- [ ] Manually audit at least 25 stratified episodes, including utility, security, tool errors, refusals, and verifier exceptions.

### Deliverables

- suite inventory JSON;
- frozen candidate-screen manifests;
- competence/static/capability summaries;
- verifier audit worksheet;
- suite selection decision.

### Exit gate

One suite meets the v0.3 competence, attackability, pair-count, and verifier criteria. If none does, stop and repair or pivot the environment before training.

## Week 3 — freeze splits, ledger, and environment contract

### Tasks

- [ ] Freeze user-task-level 50/15/35 development/validation/test splits, stratified by injection goal.
- [ ] Confirm every injection goal appears in every split.
- [ ] Confirm the sealed test pair count and write it into the manifest.
- [ ] Freeze the selected Qwen3-8B model snapshot, tokenizer, chat template,
  NF4 configuration, tool format, context limit, generation limit, and decoding
  policy.
- [ ] Implement the append-only episode ledger.
- [ ] Log retrieved memory IDs, generated injection text, vector ID, checkpoint, reward components, raw verifier outcomes, and token usage.
- [ ] Implement exact replay checks for saved traces and verifier fixtures.
- [ ] Implement the one-shot-per-visible-vector attacker interface with a `NOOP` action.
- [ ] Implement separate attacker and defender adapter identities.

### Deliverables

- final suite manifest;
- split manifest and hash;
- ledger schema and writer;
- replay/verifier fixtures;
- adapter/interface contract.

### Exit gate

Development, validation, and test data are mechanically separated; the ledger can reconstruct every episode; no model or memory code can write to test data.

## Week 4 — frozen baselines and adapter warm start

### Tasks

- [ ] Rerun the selected suite's benign and static screens on development and validation tasks under the final model/prompt configuration.
- [ ] Do not open sealed-test outcomes yet.
- [ ] Implement 4-bit NF4 QLoRA loading and adapter save/reload.
- [ ] Verify that only registered adapter parameters are trainable.
- [ ] Build attacker SFT data from development-only successful static injections.
- [ ] Train a short attacker warm start; record data hashes and adapter hash.
- [ ] Optionally warm-start the defender only from registered development data.
- [ ] Reload each adapter and verify identical frozen evaluation on validation fixtures.
- [ ] Measure rollout, forward, backward, optimizer, save, and reload VRAM.

### Deliverables

- baseline report;
- attacker warm-start adapter;
- adapter reload test;
- measured training memory profile;
- initial token/GPU-hour ledger.

### Exit gate

Both adapters load and reload correctly, produce valid actions, and fit the measured single-GPU training path with the required safety margin.

## Week 5 — learning responsiveness and memory expressivity

### Tasks

- [ ] Run a short attacker update against a frozen defender.
- [ ] Run a short defender update against a frozen attacker.
- [ ] Verify that updates change valid behavior or ASR without malformed actions dominating.
- [ ] Implement the immutable attack archive with the v0.3 record schema.
- [ ] Implement deterministic retrieval: same goal, task-context similarity, capped successes/failures, and token cap.
- [ ] Run frozen attacker development pairs with memory disabled versus enabled.
- [ ] Measure changed strategy distribution and ASR difference.
- [ ] Confirm memory reads are logged and evaluation pairs never write.
- [ ] Freeze the replay/recombination similarity threshold on development data.

### Deliverables

- learning-responsiveness report;
- memory-expressivity report;
- archive/retrieval implementation;
- retrieval and similarity thresholds;
- updated budget estimate.

### Exit gate

Learning responsiveness and memory expressivity both pass. If either fails, remove C2 from the pilot and continue only with the C1 measurement study.

## Week 6 — reference co-training implementation and pilot run

### Tasks

- [ ] Implement alternating attacker and defender update blocks.
- [ ] Ensure no weights change during an episode.
- [ ] Use latest-opponent sampling only for the pilot.
- [ ] Use attacker group size 4 and defender group size 2 unless a frozen amendment is required by measured feasibility.
- [ ] Include benign defender episodes to monitor the utility floor.
- [ ] Separate raw reward components from optimization rewards.
- [ ] Save checkpoints at fixed interaction counts for rounds 0, 1, 3, and 5.
- [ ] Run a short partial co-training test first.
- [ ] If valid, run the full one-seed five-round reference trajectory.
- [ ] Keep archive recording on but memory retrieval off during Stage 1.

### Deliverables

- reference run manifest;
- attacker/defender checkpoints;
- per-round ledger;
- reward/action validity report;
- crash-resume test result.

### Exit gate

The reference run completes or fails for a diagnosable reason; checkpoints reload; interaction counts and token budgets reconcile; no test data was consumed.

## Week 7 — checkpoint eligibility and reference audit

### Tasks

- [ ] Evaluate defender checkpoints on validation benign tasks.
- [ ] Mark each checkpoint eligible or `utility-infeasible` using the frozen five-point floor.
- [ ] Do not substitute checkpoints after seeing sealed-test security.
- [ ] Evaluate validation static ASR and refusal/invalid-action rates.
- [ ] Audit at least 25 stratified validation episodes manually.
- [ ] Inspect reward hacking, malformed injections, retrieval leakage, and premature stopping.
- [ ] Verify that every checkpoint/adapter hash maps to exactly one ledger position.
- [ ] Freeze the 4 × 4 cross-play schedule and sealed-test execution plan.

### Deliverables

- checkpoint eligibility report;
- manual audit report;
- frozen cross-play manifest;
- final pre-test ledger snapshot.

### Exit gate

At least one eligible defender checkpoint exists and the reference is suitable for sealed cross-play. If none is eligible, report utility infeasibility and stop the primary claim rather than weakening the floor.

## Week 8 — sealed checkpoint cross-play and C1 analysis

### Tasks

- [ ] Run all registered `(D_j, A_k)` pairs on sealed test task-goal pairs.
- [ ] Freeze weights, prompts, decoding, seeds, and memory during evaluation.
- [ ] Run static-benchmark ASR and benign utility for eligible checkpoints.
- [ ] Verify no test result entered the archive or training ledger as usable training data.
- [ ] Produce the 4 × 4 cross-play matrix.
- [ ] Compute `c_j`, `h_j`, and `G_j`.
- [ ] Run the 10,000-resample pair-clustered bootstrap, recomputing historical maxima within each resample.
- [ ] Report the C1 gate against the frozen 5-point SESOI.

### Deliverables

- sealed cross-play matrix;
- C1 bootstrap analysis;
- utility/security figures;
- leakage audit;
- C1 proceed/null decision.

### Exit gate

If C1 passes, authorize Week 9 C2. If C1 is below the SESOI, use Week 9 for sensitivity analysis and finalize a narrower measurement/null report.

## Week 9 — conditional memory × adaptation audit

### Tasks if C1 passes

- [ ] Select one eligible defender checkpoint on validation data before sealed
  evaluation, then instantiate M0L0, M1L0, M0L1, and M1L1.
- [ ] Give each active cell identical audit interactions, generation budget, task pairs, and starting attacker checkpoint.
- [ ] Use training pairs for audit adaptation only.
- [ ] Freeze weights and memory before sealed-test evaluation.
- [ ] Evaluate all cells on the same sealed pairs.
- [ ] Compute cellwise ASR and a separate M:L interaction for each of the three
  independent audit-adaptation seeds; do not duplicate frozen controls as
  independent seed runs.
- [ ] Classify successes as replay, recombination, or novel.
- [ ] Run the mixed-effects logistic model and absolute-risk bootstrap.

### Tasks if C1 fails

- [ ] Do not run an expensive mechanism study.
- [ ] Run only preregistered sensitivity checks: eligible-checkpoint rules, static benchmark comparison, invalid-verifier handling, and pair-clustered intervals.
- [ ] Record C2 as uninterpretable rather than null.

### Deliverables

- C2 audit matrix or C1 sensitivity package;
- replay/recombination/novel analysis;
- compute reconciliation;
- updated paper decision.

## Week 10 — replication gate and paper package

### Tasks

- [ ] Reconcile all episode, token, wall-time, GPU-hour, checkpoint, and seed counts against the hard ceilings.
- [ ] Re-run analysis from raw ledger files in a clean environment.
- [ ] Perform sensitivity analyses for invalid verifier episodes and task/goal clustering.
- [ ] Run a post-pilot power simulation at the frozen SESOI, not only at the observed effect.
- [ ] Write the proceed/pivot/stop report.
- [ ] Decide whether Phase B can afford two additional seeds.
- [ ] Freeze figures, tables, aggregate matrices, and a safe artifact package.
- [ ] Draft the paper introduction around the result branch actually observed.

### Deliverables

- pilot report;
- reproducible analysis bundle;
- compute ledger;
- paper figures and tables;
- Phase B decision.

## Conditional Phase B — weeks 11–18

Phase B happens only if the Week 10 gate passes. It is not part of the initial commitment and cannot be used to rescue a failed C1 gate by adding unregistered conditions.

### Week 11 — preregister confirmatory expansion

- [ ] Freeze the two most informative comparisons and seed count.
- [ ] Freeze any change to the suite, task block, SESOI, or budget before new outcomes.
- [ ] Decide whether to retain latest-opponent only or add the ARLAS historical population as a separate secondary condition.
- [ ] Freeze the Phase B analysis and release plan.

### Week 12 — reference replication seed 2

- [ ] Run the reference co-training trajectory with a new seed.
- [ ] Verify checkpoint schedule, utility eligibility, and ledger integrity.
- [ ] Do not inspect sealed-test results until the run is complete.

### Week 13 — reference replication seed 3

- [ ] Repeat the selected reference comparison with a third seed.
- [ ] Reconcile checkpoint availability and compute.
- [ ] Stop if the reference itself is not reproducible.

### Week 14 — C1 replication cross-play

- [ ] Run the registered checkpoint matrices for seeds 2 and 3.
- [ ] Estimate the mean historical gap across seeds.
- [ ] Update the pair-clustered bootstrap and heterogeneity analysis.

### Week 15 — C2 replication

- [ ] Repeat only the two most informative memory/adaptation cells and their necessary controls.
- [ ] Keep the same audit budget and archive isolation.
- [ ] Test whether replay/recombination composition replicates.

### Week 16 — optional C3 training consequence

- [ ] Run the archive-in-the-loop co-training condition only if C1/C2 remain credible and the remaining budget is sufficient.
- [ ] Compare historical gaps with the latest-only reference.
- [ ] Keep this result secondary.

### Week 17 — final analysis and failure taxonomy

- [ ] Classify failures into instruction override, tool misuse, delayed effect, memory reuse, retrieval mismatch, refusal/utility collapse, verifier ambiguity, and infrastructure failure.
- [ ] Produce final security–utility plots, cross-play heatmaps, and compute tables.
- [ ] Run all analyses from clean raw artifacts.

### Week 18 — writing and release review

- [ ] Write the paper using only the registered result branch.
- [ ] State all scale, suite, seed, and compute limitations.
- [ ] Release manifests, aggregate matrices, analysis code, and safe traces.
- [ ] Review attack artifacts for misuse risk before release.
