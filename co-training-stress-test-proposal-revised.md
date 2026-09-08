# Research Proposal: Capability-Factored Stress Testing of Adversarial Co-Training for LLM Agents

**Working title:** *CoTA-Break: When Does Adversarial Co-Training Fail Against Adaptive, Memory-Augmented LLM Attackers?*  
**Version:** 0.2 (novelty- and feasibility-gated revision)
**Status:** READY FOR MILESTONE 0; RL WORK REQUIRES MILESTONE 1 GATE
**Researcher profile:** Experienced AI engineering leader with prior hands-on RL fine-tuning research; developing deeper expertise in multi-agent RL, self-play, and agent security  
**Recommended sequence:** 6–8 week diagnostic pilot, followed only if justified by a gated 4–6 month paper project

## 1. Executive decision

Proceed with this project first, but begin with a capability-factored pilot rather than immediately co-training two sophisticated agents. The project is a strong bridge from RL fine-tuning to multi-agent RL: it reuses familiar policy optimization and evaluation skills while adding non-stationarity, population evaluation, strategic forgetting, and adversarial generalization.

The paper should not claim novelty from merely combining ARLAS and Evo-Attacker. Its scientific bet is narrower: **persistent cross-episode strategy memory changes adversarial co-training dynamics primarily when paired with online policy adaptation, because successful attacks can be preserved, retrieved, and refined after the contemporary opponent has moved on**. CoTA-Break tests whether this interaction creates historical vulnerabilities that contemporaneous evaluation conceals, at matched benign utility and compute.

The defensible contribution is therefore a controlled measurement methodology plus evidence for or against a specific memory × adaptation mechanism. Strategic forgetting is confirmatory; cycling is exploratory unless the pilot supports a sufficiently dense checkpoint and seed design. A minimal mitigation should be added only after the experiments identify a specific failure mechanism.

The proposed sequence also creates infrastructure and empirical motivation for the later OPAL project. CoTA-Break asks *when and why co-training fails*; OPAL can subsequently ask whether an opponent-conditioned world model predicts and prevents those failures.

## 2. Background and corrected positioning

[ARLAS](https://arxiv.org/abs/2510.05442) studies attacker–defender reinforcement learning in a two-player zero-sum formulation and uses a population containing historical attacker checkpoints to improve defender robustness. Its evaluation includes multi-turn agent environments such as AgentDojo and BrowserGym. It should therefore **not** be described as a purely single-turn system. The narrower distinction relevant here is that ARLAS does not provide Evo-Attacker's complete combination of persistent attack memory, intervention-level deliberation, and Attack-Flow GRPO for long-horizon attack credit.

[Evo-Attacker](https://aclanthology.org/2026.acl-long.330/) introduces a self-evolving attacker for long-horizon tool attacks on LLM multi-agent systems, combining dynamic attack memory with Attack-Flow GRPO. It primarily establishes attacker capability; it does not answer whether an adaptively trained defender remains robust under each of those capabilities.

[AgentDojo](https://arxiv.org/abs/2406.13352) provides executable tool-use tasks with prompt-injection attacks and utility/security evaluation, making it the preferred initial environment. BrowserGym can serve as a later external environment if engineering and compute permit.

Self-play research has long documented non-transitivity, strategic forgetting, and cycling, motivating fictitious self-play, policy-space response oracles, and population-based training. CoTA-Break does not treat the existence of these dynamics as novel. The open question is whether persistent semantic attack memory and online adaptation change the magnitude or mechanism of historical vulnerability in tool-using LLM agents, where strategies are expressed through text, intervention opportunities are discrete, and security must be evaluated jointly with benign utility. The Week 0 literature matrix must add primary citations for this positioning before external submission.

The unresolved scientific problem is not simply whether a stronger attacker lowers defense accuracy. It is:

> Which properties of an adaptive attacker—interaction horizon, persistent memory, online policy learning, or delayed-reward credit assignment—cause robustness loss, instability, or strategic forgetting in adversarially trained LLM-agent defenders?

### Capability delta and expected finding

Unlike the self-contained ARLAS-style reference attacker defined in Section 5, the fully capable attacker combines persistent **cross-episode** strategy memory, between-episode policy adaptation, and intervention-aware credit assignment. The design varies these capabilities independently rather than treating attacker strength as a single variable.

The non-obvious expected finding is:

> Persistent memory will have its largest effect when paired with online adaptation: memory preserves successful strategies across training rounds, while adaptation recombines and refines them, producing historical robustness failures that same-round evaluation underestimates.

This is a hypothesis, not an assumed result. A null result from a 1.7B–4B scaled reproduction constrains only the tested model, environment, intervention, and compute envelope; it does not establish that the capability interaction is absent at larger scales.

## 3. Research questions and hypotheses

### Primary question

**RQ1a.** With horizon fixed long and terminal credit fixed, how do persistent cross-episode memory and between-episode online policy adaptation affect defender robustness separately and jointly at matched compute and benign utility?

**H1.** Memory and online adaptation have a positive interaction on held-out ASR. The confirmatory interaction is the coefficient of (M\times L) on the log-odds scale in a pre-specified mixed-effects logistic model; absolute-risk contrasts are reported for interpretation.

**RQ1b.** With memory and learning disabled, does increasing the number of meaningful attacker intervention decisions reduce defender robustness?

**H1b.** Long-horizon attacks produce higher held-out ASR than short attacks only in environments with a pre-specified minimum number of meaningful intervention opportunities.

### Training dynamics

**RQ2.** Does apparent improvement during contemporaneous self-play represent general robustness, or does it conceal strategic forgetting against earlier opponent strategies?

**H2.** Same-round evaluation overstates robustness. Fixed-schedule checkpoint cross-play will reveal defender checkpoints that resist their contemporary attacker but regress against one or more earlier or held-out attackers. Repeated non-transitive cycling patterns are exploratory unless a post-pilot power analysis supports a confirmatory test.

### Generalization

**RQ3.** Does robustness transfer across capability levels and attack families?

**H3.** Training against a mixture of capability levels improves worst-case held-out robustness over training only against the strongest current attacker, at the same number of environment interactions.

### Credit assignment

**RQ4a — offline credit quality.** On fixed logged trajectories or resettable saved states, does intervention-aware credit rank causally consequential decisions more accurately than terminal-only broadcasting?

**H4a.** Intervention-aware credit improves counterfactual action-ranking accuracy on the same fixed evaluation data.

**RQ4b — online training efficacy.** Under matched initializations, tasks, environment interactions, token ceilings, and update counts, does intervention-aware credit improve attacker learning efficiency or final ASR?

**H4b.** Intervention-aware credit reaches a registered ASR target in fewer environment interactions or achieves higher final ASR under the same budget. Realized trajectories are not claimed to be identical after policies begin updating. A defender-side credit claim requires a separate controlled intervention.

### Minimal remediation

**RQ5.** If the pilot identifies cycling, forgetting, or coverage failure, does a targeted historical-opponent mixture or capability curriculum reduce that failure without unacceptable benign-utility loss?

**H5.** Historical-opponent mixture training reduces worst-case cross-play ASR more reliably than a monotonic simple-to-strong curriculum, because it continues rehearsing earlier strategies.

### Pre-registered primary endpoint

Use **worst-case held-out ASR at a pre-specified benign task-success floor** as the primary endpoint. For example, compare methods only at checkpoints with benign task success rate (BTSR) no more than 5 percentage points below the unmodified defender. Fix the exact floor before confirmatory runs.

If a condition has no validation checkpoint satisfying the BTSR floor, classify it as **utility-infeasible/dominated** for the primary endpoint; do not select a lower-utility checkpoint post hoc. Report its full security–utility Pareto frontier as a pre-specified secondary analysis.

The pilot primary comparison is the ARLAS-style reference versus C3-ML (persistent memory plus online learning with terminal credit), under equal environment-interaction and generated-token ceilings. C4 is conditional and cannot become primary unless H4a passes and the protocol is amended before C4 outcomes are observed. Report absolute risk difference and confidence intervals, not only relative improvement.

## 4. Contribution boundary

### Intended contributions

1. A capability-factored evaluation protocol separating horizon, memory, online adaptation, and credit assignment.
2. Fixed-schedule checkpoint cross-play and historical-opponent evaluation that expose strategic forgetting and overfitting hidden by contemporaneous reward; cycling is exploratory unless separately powered.
3. Security–utility evaluation at matched benign utility and compute.
4. A failure taxonomy grounded in trajectories and training dynamics.
5. If justified by diagnosis, one minimal mitigation targeted to the observed mechanism.

### Claims to avoid

- Do not claim the first adversarial RL defense or first long-horizon LLM attacker.
- Do not call ARLAS single-turn; distinguish its attacker from Evo-Attacker using the specific capability differences above.
- Do not attribute failure to credit assignment unless reward/advantage estimation is varied while trajectories, tasks, and model capacity are controlled.
- Do not claim broad agent safety from one benchmark, one attack family, or one base model.
- Do not present a null result as proof of robustness. State the tested capability and compute envelope.

## 5. Formal setting and system architecture

Model each episode as a partially observed stochastic game. At step \(t\), the environment has hidden state \(s_t\). The benign user supplies goal \(g\); the defender/agent observes \(o_t^D\) and selects a tool call or response \(a_t^D\). The attacker observes \(o_t^A\), optionally retrieves memory \(m_t\), and selects an intervention \(a_t^A\). The environment transitions according to

\[
s_{t+1} \sim P(s_{t+1}\mid s_t,a_t^D,a_t^A).
\]

The attacker seeks policy-violating task influence while the defender seeks benign utility and injection resistance. Treat this as security–utility optimization rather than a perfectly zero-sum game during evaluation: an attacker failure does not compensate for a defender that refuses every benign task.

### Components

- **Environment adapter:** normalizes task state, tool schemas, observations, termination, and verifier outputs.
- **Attacker policy:** generates an intervention at allowed insertion points. Its configuration independently toggles horizon, persistent memory, online updates, and credit estimator.
- **Attack memory:** stores structured summaries of prior strategy, context, outcome, and failure reason. Retrieval must be logged; train/test memory stores must be isolated.
- **Defender policy:** performs the user's tool-use task while resisting injected instructions.
- **Historical populations:** immutable attacker and defender checkpoints sampled during training and used for cross-play.
- **Reward/verifier layer:** computes benign task completion, attack success, policy violations, tool side effects, and optional shaped rewards.
- **Experiment ledger:** records prompts, model/checkpoint hashes, seeds, tool calls, token counts, rewards, verifier versions, and termination reasons.

### Self-contained ARLAS-style reference specification

The internal comparison does not depend on reproducing upstream headline numbers. The reference is defined operationally as follows:

- **Environment:** one version-pinned AgentDojo suite with executable utility and security verifiers.
- **Defender:** a fixed named instruction-tuned base model plus one PEFT adapter. The defender observes the user goal, tool schema, interaction history, and tool outputs, and emits benchmark-valid tool calls or a final response.
- **Attacker:** the same fixed named base family or a smaller predeclared model plus one PEFT adapter. At each benchmark-sanctioned insertion opportunity it observes the permitted current-episode context and emits either one text injection or `NOOP`.
- **Reference memory:** no semantic cross-episode retrieval memory. Historical attacker **checkpoints** may be retained as a training population, but a checkpoint cannot retrieve prior trajectories at inference time.
- **Update timing:** attacker and defender are updated in alternating blocks between episodes; neither changes weights within an episode. “Online adaptation” in this proposal means weight updates between episode blocks, not within-episode learning.
- **Warm start:** optional SFT on development-only successful trajectories, with the dataset construction, filtering, and adapter settings logged.
- **RL update:** terminal verifier outcomes provide the GRPO reward. Attacker and defender receive separately defined rewards; raw utility and security outcomes remain independently logged.
- **Population rule:** the population condition samples immutable historical attacker checkpoints by a predeclared distribution; the latest-opponent condition samples only the latest attacker.
- **Budgets:** comparisons match environment interactions and enforce maximum input/output token ceilings. Model calls, invalid episodes, and failed runs remain in the accounting ledger.
- **Checkpointing:** save at fixed cumulative interaction counts. Select headline checkpoints on validation data only and evaluate the sealed pilot set once.

Agreement with ARLAS-reported results is useful external validation, not a prerequisite for the internal causal contrast. Any unavailable artifact or implementation deviation must be recorded in a fidelity matrix.

### Action definition

For the pilot, constrain attacker actions to benchmark-sanctioned text injections at known insertion points. Do not begin with unrestricted tool execution by the attacker. Define a long-horizon attack as a sequence of coordinated interventions or adaptive choices across multiple interaction points—not merely a longer prompt. Record the number of intervention opportunities and effective decisions per episode.

Before retaining H1b or any long-horizon credit claim, audit the selected suite and require a median of at least three eligible insertion opportunities among the task blocks used for that comparison, with at least two opportunities requiring distinct attacker decisions. If the suite fails this gate, remove the confirmatory horizon/credit claim or select a more suitable sandboxed environment before training.

### Reward design

Keep raw outcomes separate from optimization rewards.

- **Raw attacker outcome:** binary or categorical verifier-confirmed policy violation/goal hijack.
- **Raw defender utility:** benchmark task completion and side-effect correctness.
- **Training reward:** condition-specific terminal or intervention-level signal.
- **Invalid-action penalty:** fixed and reported separately.
- **Length/cost term:** optional; pre-specify it and report results both with and without cost normalization if it changes rankings.

Do not allow an LLM judge to be the sole primary verifier when an executable ground-truth checker exists. Manually audit a stratified sample of successes, failures, and disagreements.

## 6. Factorial capability ladder

The smallest interpretable ladder is cumulative:

1. **C0: short, frozen, no persistent memory, terminal reward.**
2. **C1-H: long, frozen, no persistent memory, terminal reward.** Isolates horizon.
3. **C2-M: long, frozen, persistent memory, terminal reward.** Adds memory.
4. **C2-L: long, learning, no persistent memory, terminal reward.** Adds online adaptation instead of memory.
5. **C3-ML: long, learning, persistent memory, terminal reward.** Tests memory × learning.
6. **C4-Credit: long, learning, persistent memory, Attack-Flow/intervention-aware credit.** Adds credit estimator.

For publication-quality causal claims, supplement this ladder with a compact factorial design over memory \(M\in\{0,1\}\), online learning \(L\in\{0,1\}\), and credit \(C\in\{terminal, intervention\}\), with horizon fixed long. Compare short versus long separately with memory and learning disabled. This avoids conflating a cumulative ordering with independent causal effects.

For the pilot, the confirmatory core is the long-horizon \(2\times2\) memory × online-learning factorial. Horizon is a separate diagnostic contrast, and credit assignment is split into the offline H4a and conditional online H4b studies. C0–C4 remains an implementation ladder, not a causal analysis by itself. H4b proceeds only if H4a demonstrates a meaningful estimator difference and the remaining registered compute permits it.

Memory experiments require three evaluations:

- an empty memory at the start of every episode;
- a training-only persistent memory;
- a frozen memory built from training data and used on held-out tasks.

Never permit held-out evaluation outcomes to update memory. Report retrieval hit rate, diversity, and overlap with evaluation examples.

## 7. Evaluation conditions

### Reference and training conditions

- Untrained/base defender.
- ARLAS-style defender and historical-attacker population reference.
- Defender trained against each capability level C0–C4.
- Defender trained against a balanced capability population.
- Optional targeted mitigation after diagnosis.

### Evaluation sets

- Benign tasks with no injection.
- Seen tasks with held-out seeds.
- Held-out attack templates on seen task domains.
- Held-out tasks within the same domain.
- If feasible, an external domain or benchmark.
- Static attacker snapshots and adaptive attackers evaluated separately.

Keep the confirmatory set sealed until hyperparameters and checkpoint-selection rules are frozen.

### Checkpoint cross-play

Save attacker checkpoints \(A_0,\ldots,A_K\) and defender checkpoints \(D_0,\ldots,D_J\). Evaluate every selected pair \((D_j,A_k)\) on the same task blocks and seeds. Also include held-out attackers not used during training.

Derive:

- **contemporaneous robustness:** performance of \(D_j\) against its current \(A_j\);
- **historical worst case:** maximum ASR against \(A_0\ldots A_j\);
- **forward transfer:** performance of earlier defenders against later attackers;
- **forgetting:** loss of resistance to an older attacker relative to the defender's best prior result against it;
- **population exploitability proxy:** worst or upper-tail ASR over the evaluated attacker population;
- **exploratory cycling evidence:** repeated non-monotonic dominance patterns across pre-registered checkpoints, reported descriptively unless a pilot-informed power analysis supports a confirmatory test.

Use a pre-registered, log-spaced checkpoint schedule based on cumulative environment interactions, not favorable training events. Retain every checkpoint required for confirmatory forgetting analysis. Any smaller display subset must be selected by a deterministic rule frozen before outcomes are inspected.

## 8. Metrics

### Primary

- Worst-case held-out ASR among a fixed registered attacker population, subject to the BTSR floor. Population membership must not change across compared conditions.

### Security and utility

- ASR with exact verifier definition.
- BTSR without attack.
- Task success under attack.
- Unauthorized tool-call or side-effect rate.
- Refusal rate on benign tasks.
- Verifier ambiguity and manual-audit disagreement rates, with maximum acceptable pilot thresholds frozen before learning experiments.
- Security–utility Pareto frontier and area or operating points; do not collapse everything into one arbitrary scalar.

### Generalization and dynamics

- Held-out-template and held-out-task ASR.
- Cross-play forgetting and exploitability proxy.
- Reward/ASR variance across rounds.
- Policy KL between checkpoints on a fixed probe set.
- Attack-strategy diversity using pre-declared behavioral categories plus embedding-based analysis as secondary evidence.
- Memory retrieval frequency, strategy reuse, and novelty.

### Efficiency

- Environment interactions and successful attacks per 1,000 episodes.
- Training and evaluation input/output tokens.
- GPU-hours and wall-clock time.
- ASR as a function of interactions and tokens, with area under the learning curve.

## 9. Statistical evaluation

1. Select the unit of inference as the task or scenario, not individual correlated turns.
2. Use the same task blocks and seeds across conditions where possible.
3. Use one training seed for pipeline and directional feasibility. Add two independent seeds only to the two most informative pilot comparisons after the learning signal and compute cost are measured. Confirmatory seed counts are chosen through the post-pilot power simulation.
4. For binary outcomes, report task-clustered bootstrap 95% confidence intervals and absolute risk differences. A mixed-effects logistic regression with condition as a fixed effect and task/domain and seed as random effects can estimate factorial main effects and interactions.
5. For the security–utility endpoint, bootstrap the entire validation checkpoint-selection and fixed-population maximum procedure by task block. Do not choose the best checkpoint on the confirmatory set.
6. Correct the limited set of confirmatory secondary comparisons using Holm's procedure. Label unregistered analyses exploratory.
7. Report all seeds and failed runs. Distinguish infrastructure failures from divergent training using a rule written before the run.
8. Conduct a power simulation after pilot effect sizes are available. Do not choose sample size from the most favorable observed effect. The smallest effect of interest should be set in absolute ASR points.

## 10. Single-GPU compute envelope and scope rule

The pilot is scoped to one 24 GB NVIDIA GPU. Candidate attacker and defender backbones are 1.7B–4B instruction-tuned models trained with 4-bit QLoRA. Initial context is capped at 2,048 tokens, micro-batch size at one, and GRPO rollout group size at two. Rollout, training, and evaluation models are loaded sequentially when required.

### Provisional worked pilot ceiling

The ceiling below is a planning bound, not a runtime estimate. Replace estimates with measured values after Milestone 0, but do not raise a ceiling merely because a run is slower than expected.

- Frozen-model screening and suite selection: at most 500 episodes.
- Reference and warm-start evaluation: at most 500 episodes.
- Directional memory × learning runs: at most 1,500 training/evaluation episodes, initially one seed per cell.
- Selected-checkpoint cross-play: at most 1,200 episodes using no more than a 4 × 4 checkpoint matrix.
- Replication of the two most informative comparisons: at most 800 episodes.
- Engineering rerun reserve: at most 500 episodes.
- **Total pilot ceiling:** 5,000 environment episodes, 30 million counted model input/output tokens, and 150 GPU-hours.
- **Evaluation reserve:** at least 35% of the episode/token budget remains unused when learned-condition training begins.

The initial token bound assumes no more than 6,000 counted model tokens per episode averaged across all attacker and defender calls. Record input and output tokens separately. After 20–30 representative episodes and one QLoRA optimizer step, replace this assumption with the measured mean, upper quartile, peak VRAM, and wall time. The confirmatory design is not approved until those measurements project below all three ceilings.

For every condition, the ledger must report training seeds, episodes, tokens, optimizer steps, checkpoints, evaluation matchups, wall-clock time, GPU-hours, and peak VRAM. Compute:

\[
T_{train}=\sum_c S_cE_c\bar{T}_c,
\]

and

\[
T_{eval}=\sum_e D_eA_eQ_eR_e\bar{T}_e,
\]

where \(D,A,Q,R\) are defender checkpoints, attacker checkpoints, task blocks, and evaluation repeats.

**Scope rule.** If the projected study exceeds the ceiling, retain in order: (1) the memory × learning factorial, (2) reference-versus-C3-ML comparison, (3) forgetting cross-play, and (4) offline credit analysis. Reduce extra ladder cells, cycling analysis, additional seeds, online credit training, and external-domain experiments before reducing primary task blocks or violating matched budgets.

## 11. Detailed staged instructions

### Phase A — 6–8 week pilot

#### Milestone 0: novelty, reference, and feasibility specification

1. Verify official code, checkpoints, licenses, and reproducibility artifacts for ARLAS and Evo-Attacker.
2. Freeze the capability-delta and expected-mechanism statements.
3. Complete the self-contained reference specification, including update ratios, population sampling, checkpoint schedule, and reward definitions.
4. Inventory candidate AgentDojo suites and measure the full intervention-opportunity distribution before selecting one.
5. On the target GPU, record hardware/software versions and benchmark representative inference plus one QLoRA optimizer step.
6. Replace the provisional compute assumptions with a numerical training, cross-play, and evaluation budget under the fixed ceilings in Section 10.
7. Select the base defender and record its prior safety tuning, benign competence, and available robustness headroom.
8. Freeze initial scale-validity and verifier-reliability thresholds.

**Exit criterion:** the novelty thesis is distinguishable from generic self-play forgetting; the internal reference is independently reproducible; a candidate environment has adequate intervention depth; and the reduced confirmatory design fits the measured compute envelope.

### Scale-validity gates

Learning experiments begin only if all applicable gates pass:

1. **Defender competence:** the base defender clears a pre-specified benign task-success minimum on development and validation tasks.
2. **Attackability:** at least one scripted or prompted attacker achieves non-floor, non-ceiling ASR, leaving measurable headroom.
3. **Intervention depth:** the selected tasks satisfy the Section 5 opportunity criterion; report the full distribution.
4. **Memory expressivity:** on controlled development tasks, retrieved prior strategy information changes attacker actions and produces a measurable behavioral difference from empty memory.
5. **Learning responsiveness:** a short adapter update changes valid attacker behavior or ASR without being dominated by malformed actions.
6. **Verifier reliability:** ambiguity and manual-audit disagreement remain below frozen thresholds.

Failure triggers repair, environment change, model-scale adjustment, or scope reduction before confirmatory training. If only the memory × learning question remains identifiable, drop horizon, H4b, and cycling claims before proceeding.

#### Milestone 1: environment contract, splits, and verifier validation

1. Finalize one suite and executable utility/security verifier definitions.
2. Freeze separate development, validation, and sealed pilot-test manifests.
3. Write the threat model, success definitions, benign-utility floor, and leakage controls.
4. Implement the deterministic environment adapter and experiment-ledger schema.
5. Implement random/scripted attackers and fixtures covering benign success, attack success, failed attack, refusal, invalid action, timeout, and ambiguous outcome.
6. Replay recorded trajectories and conduct the first stratified manual verifier audit.

**Exit criterion:** replay is deterministic; benign utility is measured independently from security; split isolation passes; and verifier ambiguity/audit disagreement remain below the frozen thresholds.

#### Week 2: Reference defender and logging

1. Evaluate the base defender on benign, short-attack, and long-attack suites.
2. Establish the self-contained ARLAS-style reference; compare with an upstream trend only when the required artifacts are available and compatible.
3. Save checkpoints on a fixed interaction schedule.
4. Log every observation, generated action, tool result, injection, verifier output, reward component, token count, seed, and code/config identifier.
5. Manually inspect at least 25 stratified episodes to validate the verifier and trajectory parser.

**Exit criterion:** the reference behavior is stable across registered evaluation seeds; benign competence clears its floor; baseline ASR is neither floor nor ceiling; intervention depth and memory expressivity gates pass; and measured throughput keeps the pilot within budget. Otherwise reduce scope or change the environment before learning.

#### Week 3: Frozen capability ladder

1. Implement C0 and run C1-H only if the intervention-depth gate passes.
2. Match prompts, model, decoding, attack opportunities, and inference-token budget; horizon is the intended difference.
3. Implement memory behind an interface, populate it only from development episodes, freeze it, and run C2-M; log whether retrieval changes the selected action, not merely whether retrieval occurs.
4. Compare ASR, BTSR, task success under attack, token cost, and failure categories.

**Exit criterion:** horizon and memory can be toggled independently, with no evaluation-set writes to memory.

#### Week 4: Learning and credit controls

1. Complete the 2 × 2 memory × learning factorial, using frozen conditions for \(L=0\) and matched learned-attacker runs for \(L=1\).
2. Run H4a offline on a frozen, stratified trajectory or resettable-state set.
3. Run H4b/C4 only if H4a shows a meaningful estimator difference and the remaining registered compute permits it.
4. Inspect advantage and reward distributions; check for all-zero reward, reward hacking, invalid actions, or length confounding.

**Exit criterion:** learning differs from frozen behavior for a reason visible in valid trajectories; factorial cells have matched budgets; and offline versus online credit claims remain explicitly separated.

#### Week 5: Cross-play and causal readout

1. Evaluate the cross-product of selected attacker and defender checkpoints.
2. Run the compact factorial analysis.
3. Produce security–utility curves and per-domain breakdowns.
4. Classify failures into at least: instruction-following override, tool misuse, delayed payload, memory reuse, retrieval mismatch, refusal/utility collapse, and verifier ambiguity.

**Exit criterion:** the team can state which capability changes outcomes and whether same-round evaluation hid historical vulnerability or forgetting. Cycling remains exploratory unless separately powered.

#### Week 6: Replication and gate review

1. Replicate the two most informative comparisons with fresh training seeds.
2. Audit a blinded sample of claimed attack successes and failures.
3. Reconcile interaction, token, and GPU budgets.
4. Write a two-page pilot report containing effect sizes, uncertainty, failures, and the recommendation to proceed, pivot, or stop.

### Pilot-to-full-project gate

Proceed to a full paper only if all validity conditions hold and at least one publication signal is replicated:

- The self-contained reference is stable and implementation fidelity is documented.
- A practically meaningful memory × learning interaction, historical vulnerability hidden by contemporaneous evaluation, or capability-specific generalization failure is replicated; alternatively, a diagnosis-matched mitigation improves historical robustness at acceptable benign utility.
- Verifiers and logs support causal diagnosis rather than anecdotal examples.
- Estimated confirmatory compute fits the available budget.

Proceed conditionally with a narrower measurement paper if cross-play produces a reliable evaluation lesson but the mechanism remains uncertain. Stop or pivot if effects remain below the smallest effect of interest, scaled models fail the expressivity gates, verifier uncertainty prevents attribution, or the confirmatory design exceeds the compute ceiling. A null result is bounded to the tested model, benchmark, attacker population, and compute envelope.

### Phase B — full paper project (approximately 16–24 additional weeks)

#### Stage 1: Harden and pre-register (2–3 weeks)

- Freeze primary hypotheses, endpoint, task splits, seed policy, exclusion rules, and smallest effect of interest.
- Containerize the environment and pin model, tokenizer, serving, and verifier versions.
- Automate resume-safe training and deterministic evaluation.

#### Stage 2: Confirmatory factorial experiments (4–6 weeks)

- Run the full registered factorial conditions on the primary domain.
- Allocate equal environment-interaction and maximum token budgets.
- Use at least three seeds for every factorial cell and five for headline cells where feasible.
- Keep confirmatory evaluation sealed until checkpoint selection is complete.

#### Stage 3: Population training and cross-play (3–4 weeks)

- Compare strongest-current-opponent training, uniform historical mixture, and a predeclared recency-weighted mixture.
- Build the complete checkpoint cross-play dataset.
- Quantify forgetting, cycling, and worst-population performance.

#### Stage 4: Generalization (2–4 weeks)

- Evaluate held-out attack templates and held-out tasks.
- Add a second domain or model family only after the primary analysis is stable.
- Do not tune on external benchmark results.

#### Stage 5: Targeted mitigation (3–4 weeks)

Choose exactly one remedy from the diagnosis:

- cycling/forgetting → historical-opponent rehearsal or population sampling;
- abrupt capability shift → capability curriculum while retaining rehearsal;
- delayed attacker credit → intervention-aware credit;
- memory-induced strategy collapse → diversity-aware memory sampling.

Compare the remedy with an equal-compute control and an ablation removing its causal component.

#### Stage 6: Analysis and writing (2–3 weeks)

- Lock all tables before drafting broad claims.
- Release aggregate results and safe artifacts; review attack details before release.
- Write limitations that explicitly bound models, tasks, threat model, and adaptive evaluation budget.

## 12. Compute and token budgeting

Use accounting units that remain meaningful across model sizes: environment episodes, input tokens, output tokens, and GPU-hours.

### Pilot envelope

- One environment/domain and one defender family.
- Four memory × learning cells form the confirmatory core; horizon and credit conditions are gated diagnostics.
- One training seed is used until the learning signal and measured cost are credible; two additional seeds are reserved for the two most informative comparisons.
- Start with parameter-efficient tuning of the smallest model that can execute the tasks reliably.
- Reserve at least 35% of the pilot token budget for evaluation and cross-play. Use no more than four pre-registered checkpoints per policy in the initial matrix.
- Obey the Section 10 ceilings: 5,000 episodes, 30 million counted model tokens, and 150 GPU-hours.

### Full-study budgeting formula

Estimate total tokens before launch:

\[
T_{total}=\sum_c S_c(E^{train}_c\bar{T}^{train}_c + J_cK_cE^{eval}_c\bar{T}^{eval}_c),
\]

where \(c\) indexes conditions, \(S\) seeds, \(E\) episodes, \(\bar T\) average tokens per episode, and \(J,K\) selected defender/attacker checkpoints. Add 20–30% engineering and rerun reserve, not extra exploratory conditions.

Set three stop rules before training: maximum tokens, maximum environment interactions, and maximum wall-clock/GPU-hours. Compare methods at matched primary budget; present any larger-compute result separately. Cache deterministic environment/tool outputs when valid, but never reuse model outputs across stochastic policy conditions.

## 13. Reproducibility and artifact plan

- Version-control code, configs, task manifests, prompts, verifier logic, and analysis scripts.
- Record model/checkpoint identifiers, quantization, adapters, generation parameters, library/container hashes, hardware, seeds, and dataset revision.
- Store immutable raw trajectories and derive tables through scripted analysis.
- Include a machine-readable run manifest and one-command small-scale reproduction.
- Publish split identifiers and aggregate cross-play matrices.
- Report unavailable upstream artifacts and deviations from the papers; use “ARLAS-style” or “Evo-Attacker-inspired” when fidelity cannot be established.
- Use sanitized attack templates or gated release if detailed trajectories materially increase misuse risk.

## 14. Risks and mitigations

- **Framework incompatibility:** treat ARLAS and Evo-Attacker as conceptual references; build a thin common environment contract before integrating training code.
- **Non-stationary debugging:** validate frozen opponents first, checkpoint frequently, and use cross-play to distinguish learning from cycling.
- **Reward hacking/verifier error:** prefer executable checks and manually audit stratified disagreements.
- **Utility collapse:** enforce a benign-utility floor and report Pareto trade-offs.
- **Data leakage through memory:** maintain separate training and evaluation stores; freeze memory during evaluation.
- **Confounded horizon:** match model calls/token budgets and define horizon by decisions/interventions, not prompt length.
- **Compute explosion:** stage conditions, cap checkpoints, use PEFT, and stop at the pilot gate if effects are too small.
- **Null result:** a null constrains only the tested model, benchmark, attacker population, and compute envelope. Failure of a scale-validity gate prevents a general capability claim.
- **Dual-use release:** disclose enough for scientific verification without publishing turnkey harmful payloads; follow benchmark and institutional policies.

## 15. Publication strategy

The strongest paper narrative is:

1. Contemporary self-play scores are an incomplete measure of adversarial robustness.
2. A controlled capability ladder identifies which attacker capabilities create failure.
3. Cross-play reveals whether the mechanism is coverage failure or strategic forgetting; cycling is exploratory unless separately powered.
4. A diagnosis-matched intervention improves the registered security endpoint without sacrificing benign utility.

A pure “ARLAS + Evo-Attacker” integration is better suited to a workshop or findings-style empirical contribution. A rigorous factorial protocol, cross-play dataset, and mechanistically justified mitigation could support a main-conference submission in NLP, ML safety, or agents. Select the venue after the pilot establishes whether the primary contribution is agent security, multi-agent learning dynamics, or evaluation methodology. Avoid committing the full project to a venue deadline before reproduction and compute estimates stabilize.

### Publication decision tree

- **Large isolated gap + clear mitigation:** full conference paper.
- **Gap + strong diagnosis, no mitigation:** empirical/evaluation paper or strong workshop submission while developing the remedy.
- **No average gap, but cross-play exposes a replicated historical vulnerability:** center the paper on measurement and checkpoint-population evaluation.
- **No credible effect and no diagnostic insight:** release a reproduction report and redirect effort to OPAL.

## 16. Learning and career outcomes

This project adds demonstrable skills beyond the researcher's prior RL fine-tuning work:

- designing and diagnosing multi-agent/self-play training;
- reasoning about non-stationary opponents and historical populations;
- building secure executable-agent evaluations;
- separating causal factors through factorial experiments;
- measuring robustness jointly with utility and compute;
- creating reproducible, auditable RL infrastructure;
- translating safety-critical engineering habits—verification, failure analysis, simulation fidelity, and change control—into frontier-agent research.

The tangible portfolio should include a paper/preprint, reproducible repository, benchmark adapter, cross-play visualization, failure taxonomy, and concise technical talk. These artifacts support a profile as a technical research leader who can both formulate experiments and execute systems work, without overstating RL theory expertise.

## 17. Relationship to OPAL

CoTA-Break should precede OPAL because it supplies the trajectories, opponent populations, failure categories, and evaluation endpoint OPAL needs. The projects should remain scientifically distinct:

- **CoTA-Break:** observes and isolates failures under adaptive adversarial training.
- **OPAL:** learns an opponent-conditioned transition/outcome model and uses counterfactual rollouts for planning or credit.

If CoTA-Break finds cycling, strategic forgetting, or costly sampling of opponent responses, OPAL gains a concrete target: predict exploitability against historical and plausible counterfactual opponents. If CoTA-Break finds no meaningful gap, do not force a world-model solution; redirect OPAL toward a failure or efficiency bottleneck actually supported by evidence.

## 18. Immediate next actions

1. Complete Milestone 0: artifact availability, capability delta, reference specification, and target-GPU profiling.
2. Inventory AgentDojo suites and measure intervention-opportunity distributions before selecting one.
3. Replace the provisional compute assumptions with measured episode, token, VRAM, wall-time, and GPU-hour estimates.
4. Freeze development, validation, and sealed pilot-test manifests plus the threat model and endpoint protocol.
5. Implement deterministic replay, the experiment ledger, and verifier audit fixtures.
6. Establish base-defender competence and the self-contained ARLAS-style reference.
7. Run the memory × learning core only after all scale-validity gates pass.
8. Hold the pilot gate review before approving full-study compute.

## Flagged

- Exact base models, domain, benign-utility floor, smallest effect of interest, seed count, and measured compute projection must be fixed at Milestone 0; the hard pilot ceilings are already specified in Section 10.
- Confirm code and checkpoint availability directly from the ARLAS and Evo-Attacker project repositories before promising exact reproduction; otherwise use “style” or “inspired” terminology.
- Attack-Flow GRPO must be implemented from the primary paper/released code and validated before treating C4 as a faithful Evo-Attacker condition.
- BrowserGym is an optional external-validity extension, not part of the pilot success criterion.
