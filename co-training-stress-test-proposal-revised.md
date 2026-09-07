# Research Proposal: Capability-Factored Stress Testing of Adversarial Co-Training for LLM Agents

**Working title:** *CoTA-Break: When Does Adversarial Co-Training Fail Against Adaptive, Memory-Augmented LLM Attackers?*  
**Status:** DRAFT — READY FOR PILOT; FULL STUDY REQUIRES PILOT GATE  
**Researcher profile:** Experienced AI engineering leader with prior hands-on RL fine-tuning research; developing deeper expertise in multi-agent RL, self-play, and agent security  
**Recommended sequence:** 4–6 week diagnostic pilot, followed by a gated 4–6 month paper project  

## 1. Executive decision

Proceed with this project first, but begin with a capability-factored pilot rather than immediately co-training two sophisticated agents. The project is a strong bridge from RL fine-tuning to multi-agent RL: it reuses familiar policy optimization and evaluation skills while adding non-stationarity, population evaluation, strategic forgetting, and adversarial generalization.

The paper should not claim novelty from merely combining ARLAS and Evo-Attacker. Its defensible contribution is a **controlled stress-testing methodology that isolates which attacker capabilities break adversarially trained defenders, detects cycling and forgetting through checkpoint cross-play, and evaluates robustness at matched benign utility**. A minimal mitigation should be added only after the experiments identify a specific failure mechanism.

The proposed sequence also creates infrastructure and empirical motivation for the later OPAL project. CoTA-Break asks *when and why co-training fails*; OPAL can subsequently ask whether an opponent-conditioned world model predicts and prevents those failures.

## 2. Background and corrected positioning

[ARLAS](https://arxiv.org/abs/2510.05442) studies attacker–defender reinforcement learning in a two-player zero-sum formulation and uses a population containing historical attacker checkpoints to improve defender robustness. Its evaluation includes multi-turn agent environments such as AgentDojo and BrowserGym. It should therefore **not** be described as a purely single-turn system. The narrower distinction relevant here is that ARLAS does not provide Evo-Attacker's complete combination of persistent attack memory, intervention-level deliberation, and Attack-Flow GRPO for long-horizon attack credit.

[Evo-Attacker](https://aclanthology.org/2026.acl-long.330/) introduces a self-evolving attacker for long-horizon tool attacks on LLM multi-agent systems, combining dynamic attack memory with Attack-Flow GRPO. It primarily establishes attacker capability; it does not answer whether an adaptively trained defender remains robust under each of those capabilities.

[AgentDojo](https://arxiv.org/abs/2406.13352) provides executable tool-use tasks with prompt-injection attacks and utility/security evaluation, making it the preferred initial environment. BrowserGym can serve as a later external environment if engineering and compute permit.

The unresolved scientific problem is not simply whether a stronger attacker lowers defense accuracy. It is:

> Which properties of an adaptive attacker—interaction horizon, persistent memory, online policy learning, or delayed-reward credit assignment—cause robustness loss, instability, or strategic forgetting in adversarially trained LLM-agent defenders?

## 3. Research questions and hypotheses

### Primary question

**RQ1.** At a fixed training-compute budget and matched benign utility, how does defender robustness change as attacker horizon, memory, online learning, and credit-assignment capability are introduced separately and jointly?

**H1.** The fully capable attacker produces a higher held-out attack success rate (ASR) than the ARLAS-style reference attacker, but the interaction is super-additive: the joint effect of memory and online learning exceeds the sum of their individual effects.

### Training dynamics

**RQ2.** Does apparent improvement during contemporaneous self-play represent general robustness, or does it conceal cycling and forgetting against earlier opponent strategies?

**H2.** Same-round evaluation overstates robustness. Checkpoint cross-play will reveal defender checkpoints that resist their contemporary attacker but regress against one or more earlier or held-out attackers.

### Generalization

**RQ3.** Does robustness transfer across capability levels and attack families?

**H3.** Training against a mixture of capability levels improves worst-case held-out robustness over training only against the strongest current attacker, at the same number of environment interactions.

### Credit assignment

**RQ4.** Holding trajectories and attacker capabilities fixed, does delayed credit—not merely greater task difficulty—explain any long-horizon advantage?

**H4.** Intervention-aware or Attack-Flow-style credit improves the attacker's sample efficiency and final ASR over terminal-only reward on identical tasks and comparable trajectory budgets. This hypothesis concerns attacker credit assignment. A defender-side credit claim requires a separate controlled intervention and must not be inferred from long-horizon failure alone.

### Minimal remediation

**RQ5.** If the pilot identifies cycling, forgetting, or coverage failure, does a targeted historical-opponent mixture or capability curriculum reduce that failure without unacceptable benign-utility loss?

**H5.** Historical-opponent mixture training reduces worst-case cross-play ASR more reliably than a monotonic simple-to-strong curriculum, because it continues rehearsing earlier strategies.

### Pre-registered primary endpoint

Use **worst-case held-out ASR at a pre-specified benign task-success floor** as the primary endpoint. For example, compare methods only at checkpoints with benign task success rate (BTSR) no more than 5 percentage points below the unmodified defender. Fix the exact floor before confirmatory runs.

The primary comparison is the ARLAS-style reference condition versus the fully capable attacker condition, under equal environment-interaction or token budgets. Report absolute risk difference and confidence intervals, not only relative improvement.

## 4. Contribution boundary

### Intended contributions

1. A capability-factored evaluation protocol separating horizon, memory, online adaptation, and credit assignment.
2. Checkpoint cross-play and historical-opponent evaluation that expose cycling, forgetting, and overfitting hidden by contemporaneous reward.
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

### Action definition

For the pilot, constrain attacker actions to benchmark-sanctioned text injections at known insertion points. Do not begin with unrestricted tool execution by the attacker. Define a long-horizon attack as a sequence of coordinated interventions or adaptive choices across multiple interaction points—not merely a longer prompt. Record the number of intervention opportunities and effective decisions per episode.

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
- **cycling evidence:** non-monotonic dominance patterns that repeat across checkpoints.

Use a fixed checkpoint schedule based on environment interactions, not favorable training events.

## 8. Metrics

### Primary

- Worst-case held-out ASR among attackers in the registered evaluation population, subject to the BTSR floor.

### Security and utility

- ASR with exact verifier definition.
- BTSR without attack.
- Task success under attack.
- Unauthorized tool-call or side-effect rate.
- Refusal rate on benign tasks.
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
3. Run at least three independent training seeds for pilot estimates; target five for confirmatory headline conditions if compute permits.
4. For binary outcomes, report task-clustered bootstrap 95% confidence intervals and absolute risk differences. A mixed-effects logistic regression with condition as a fixed effect and task/domain and seed as random effects can estimate factorial main effects and interactions.
5. For the security–utility endpoint, bootstrap the entire selection/evaluation procedure by task block. Do not choose the best checkpoint on the confirmatory set.
6. Correct the limited set of confirmatory secondary comparisons using Holm's procedure. Label unregistered analyses exploratory.
7. Report all seeds and failed runs. Distinguish infrastructure failures from divergent training using a rule written before the run.
8. Conduct a power simulation after pilot effect sizes are available. Do not choose sample size from the most favorable observed effect. The smallest effect of interest should be set in absolute ASR points.

## 10. Detailed staged instructions

### Phase A — 4–6 week pilot

#### Week 1: Specification and environment contract

1. Read ARLAS and Evo-Attacker method, experimental, and appendix sections side by side.
2. Build a compatibility sheet for observations, insertion points, actions, episode termination, rewards, and checkpoint formats.
3. Choose one AgentDojo domain with executable utility and security verifiers.
4. Freeze a small development task set and a disjoint pilot evaluation set.
5. Write the threat model, success definitions, benign-utility floor, and data-leakage rules before running RL.
6. Implement a deterministic environment adapter and a random/scripted attacker smoke test.

**Exit criterion:** the same recorded trajectory replays to the same verifier outcome, and benign task success is measured independently from security.

#### Week 2: Reference defender and logging

1. Evaluate the base defender on benign, short-attack, and long-attack suites.
2. Reproduce one small ARLAS-style result or, if code/checkpoints are unavailable, establish a faithful reference implementation and label it explicitly “ARLAS-style.”
3. Save checkpoints on a fixed interaction schedule.
4. Log every observation, generated action, tool result, injection, verifier output, reward component, token count, seed, and code/config identifier.
5. Manually inspect at least 25 stratified episodes to validate the verifier and trajectory parser.

**Exit criterion:** the reference direction is reproducible across at least three evaluation seeds, or discrepancies are documented and scoped.

#### Week 3: Frozen capability ladder

1. Implement C0 and C1-H without memory or attacker updates.
2. Match prompts, model, decoding, attack opportunities, and inference-token budget; horizon is the intended difference.
3. Implement memory behind an interface, populate it only from development episodes, freeze it, and run C2-M.
4. Compare ASR, BTSR, task success under attack, token cost, and failure categories.

**Exit criterion:** horizon and memory can be toggled independently, with no evaluation-set writes to memory.

#### Week 4: Learning and credit controls

1. Enable attacker learning without memory (C2-L).
2. Enable learning with memory (C3-ML).
3. Compare terminal-only and intervention-aware credit on identical environment/task budgets (C4-Credit).
4. Inspect advantage and reward distributions; check for all-zero reward, reward hacking, invalid actions, or length confounding.

**Exit criterion:** learning curves differ from frozen behavior for a reason visible in valid trajectories, and credit variants receive the same raw outcomes and interaction budget.

#### Week 5: Cross-play and causal readout

1. Evaluate the cross-product of selected attacker and defender checkpoints.
2. Run the compact factorial analysis.
3. Produce security–utility curves and per-domain breakdowns.
4. Classify failures into at least: instruction-following override, tool misuse, delayed payload, memory reuse, retrieval mismatch, refusal/utility collapse, and verifier ambiguity.

**Exit criterion:** the team can state which capability changes outcomes and whether same-round evaluation hid forgetting or cycling.

#### Week 6: Replication and gate review

1. Replicate the two most informative comparisons with fresh training seeds.
2. Audit a blinded sample of claimed attack successes and failures.
3. Reconcile interaction, token, and GPU budgets.
4. Write a two-page pilot report containing effect sizes, uncertainty, failures, and the recommendation to proceed, pivot, or stop.

### Pilot-to-full-project gate

Proceed only if all mandatory conditions hold:

- The reference implementation is sufficiently faithful and stable to support comparison.
- At least one isolated capability or interaction produces a practically meaningful robustness or dynamics gap, or cross-play uncovers a clear failure hidden by contemporaneous evaluation.
- Verifiers and logs support causal diagnosis rather than anecdotal examples.
- Estimated confirmatory compute fits the available budget.

Proceed conditionally if the main value is the evaluation protocol but effects are uncertain; narrow the paper to cross-play/measurement. Stop or pivot if outcomes are dominated by integration mismatch, verifier noise, or benign-utility collapse that cannot be corrected without changing the research question.

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

## 11. Compute and token budgeting

Use accounting units that remain meaningful across model sizes: environment episodes, input tokens, output tokens, and GPU-hours.

### Pilot envelope

- One environment/domain and one defender family.
- Six capability conditions, emphasizing frozen evaluation before co-training.
- Three small training seeds for the most important learning conditions; evaluation-only conditions need repeated task/decoding seeds rather than independent training seeds.
- Start with parameter-efficient tuning of the smallest model that can execute the tasks reliably.
- Reserve approximately 40% of the pilot token budget for evaluation and cross-play. Cross-play grows as \(J\times K\times N\), so use 4–6 scientifically meaningful checkpoints per policy rather than every checkpoint.

### Full-study budgeting formula

Estimate total tokens before launch:

\[
T_{total}=\sum_c S_c(E^{train}_c\bar{T}^{train}_c + J_cK_cE^{eval}_c\bar{T}^{eval}_c),
\]

where \(c\) indexes conditions, \(S\) seeds, \(E\) episodes, \(\bar T\) average tokens per episode, and \(J,K\) selected defender/attacker checkpoints. Add 20–30% engineering and rerun reserve, not extra exploratory conditions.

Set three stop rules before training: maximum tokens, maximum environment interactions, and maximum wall-clock/GPU-hours. Compare methods at matched primary budget; present any larger-compute result separately. Cache deterministic environment/tool outputs when valid, but never reuse model outputs across stochastic policy conditions.

## 12. Reproducibility and artifact plan

- Version-control code, configs, task manifests, prompts, verifier logic, and analysis scripts.
- Record model/checkpoint identifiers, quantization, adapters, generation parameters, library/container hashes, hardware, seeds, and dataset revision.
- Store immutable raw trajectories and derive tables through scripted analysis.
- Include a machine-readable run manifest and one-command small-scale reproduction.
- Publish split identifiers and aggregate cross-play matrices.
- Report unavailable upstream artifacts and deviations from the papers; use “ARLAS-style” or “Evo-Attacker-inspired” when fidelity cannot be established.
- Use sanitized attack templates or gated release if detailed trajectories materially increase misuse risk.

## 13. Risks and mitigations

- **Framework incompatibility:** treat ARLAS and Evo-Attacker as conceptual references; build a thin common environment contract before integrating training code.
- **Non-stationary debugging:** validate frozen opponents first, checkpoint frequently, and use cross-play to distinguish learning from cycling.
- **Reward hacking/verifier error:** prefer executable checks and manually audit stratified disagreements.
- **Utility collapse:** enforce a benign-utility floor and report Pareto trade-offs.
- **Data leakage through memory:** maintain separate training and evaluation stores; freeze memory during evaluation.
- **Confounded horizon:** match model calls/token budgets and define horizon by decisions/interventions, not prompt length.
- **Compute explosion:** stage conditions, cap checkpoints, use PEFT, and stop at the pilot gate if effects are too small.
- **Null result:** a well-powered null constrains the capability envelope, but publication strength will depend on the cross-play protocol and uncertainty bounds.
- **Dual-use release:** disclose enough for scientific verification without publishing turnkey harmful payloads; follow benchmark and institutional policies.

## 14. Publication strategy

The strongest paper narrative is:

1. Contemporary self-play scores are an incomplete measure of adversarial robustness.
2. A controlled capability ladder identifies which attacker capabilities create failure.
3. Cross-play reveals whether the mechanism is coverage failure, cycling, or forgetting.
4. A diagnosis-matched intervention improves the registered security endpoint without sacrificing benign utility.

A pure “ARLAS + Evo-Attacker” integration is better suited to a workshop or findings-style empirical contribution. A rigorous factorial protocol, cross-play dataset, and mechanistically justified mitigation could support a main-conference submission in NLP, ML safety, or agents. Select the venue after the pilot establishes whether the primary contribution is agent security, multi-agent learning dynamics, or evaluation methodology. Avoid committing the full project to a venue deadline before reproduction and compute estimates stabilize.

### Publication decision tree

- **Large isolated gap + clear mitigation:** full conference paper.
- **Gap + strong diagnosis, no mitigation:** empirical/evaluation paper or strong workshop submission while developing the remedy.
- **No average gap, but cross-play exposes cycling:** center the paper on measurement and checkpoint-population evaluation.
- **No credible effect and no diagnostic insight:** release a reproduction report and redirect effort to OPAL.

## 15. Learning and career outcomes

This project adds demonstrable skills beyond the researcher's prior RL fine-tuning work:

- designing and diagnosing multi-agent/self-play training;
- reasoning about non-stationary opponents and historical populations;
- building secure executable-agent evaluations;
- separating causal factors through factorial experiments;
- measuring robustness jointly with utility and compute;
- creating reproducible, auditable RL infrastructure;
- translating safety-critical engineering habits—verification, failure analysis, simulation fidelity, and change control—into frontier-agent research.

The tangible portfolio should include a paper/preprint, reproducible repository, benchmark adapter, cross-play visualization, failure taxonomy, and concise technical talk. These artifacts support a profile as a technical research leader who can both formulate experiments and execute systems work, without overstating RL theory expertise.

## 16. Relationship to OPAL

CoTA-Break should precede OPAL because it supplies the trajectories, opponent populations, failure categories, and evaluation endpoint OPAL needs. The projects should remain scientifically distinct:

- **CoTA-Break:** observes and isolates failures under adaptive adversarial training.
- **OPAL:** learns an opponent-conditioned transition/outcome model and uses counterfactual rollouts for planning or credit.

If CoTA-Break finds cycling, strategic forgetting, or costly sampling of opponent responses, OPAL gains a concrete target: predict exploitability against historical and plausible counterfactual opponents. If CoTA-Break finds no meaningful gap, do not force a world-model solution; redirect OPAL toward a failure or efficiency bottleneck actually supported by evidence.

## 17. Immediate next actions

1. Create the ARLAS/Evo-Attacker compatibility sheet.
2. Select one AgentDojo domain and define train/development/pilot-test splits.
3. Write the threat model and primary endpoint in a dated protocol.
4. Implement deterministic replay and the experiment ledger.
5. Establish the base-defender and ARLAS-style reference results.
6. Run C0, C1-H, and C2-M before enabling any attacker learning.
7. Hold the Week 6 gate review before approving full-study compute.

## Flagged

- Exact base models, domain, benign-utility floor, smallest effect of interest, seed count, and compute ceiling must be fixed after the compatibility/reproduction week.
- Confirm code and checkpoint availability directly from the ARLAS and Evo-Attacker project repositories before promising exact reproduction; otherwise use “style” or “inspired” terminology.
- Attack-Flow GRPO must be implemented from the primary paper/released code and validated before treating C4 as a faithful Evo-Attacker condition.
- BrowserGym is an optional external-validity extension, not part of the pilot success criterion.
