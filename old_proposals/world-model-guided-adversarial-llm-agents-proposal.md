# Research Proposal: World-Model-Guided Adversarial LLM Agents

**Working title:** *OPAL: Opponent-Predictive Adversarial Learning for Long-Horizon Tool-Using LLM Agents*  
**Audience:** A researcher learning reinforcement learning (RL), with limited vision-model experience  
**Recommended first-paper scope:** Text-only, executable tool environments; one attacker policy; a fixed or sampled defender population; no vision stack; no simultaneous end-to-end co-training in the first study  
**Status of recent citations:** Checked against primary paper/project pages on 1 September 2026. Papers dated 2026 should be treated as recent preprints unless a proceedings page explicitly confirms publication.

## 1. Executive summary

This project asks whether an adversarial LLM agent can become more effective, sample-efficient, and robust to changing defenders by learning an **opponent-conditioned world model** of a tool-using multi-agent system. The model predicts not just the next environment state, but the defender's response, the probability of task success, and uncertainty under candidate interventions. The attacker then uses short counterfactual rollouts to select or train actions.

The clean novelty is **not** memory-augmented self-evolution alone: Evo-Attacker already combines dynamic attack memory, deliberative retrieval, long-horizon tool attacks, and Attack-Flow GRPO. Nor is it merely “world models for agents”: Agent World Model already studies executable synthetic environments for agentic RL. The proposed contribution is their intersection plus a causal evaluation protocol:

> Learn a calibrated model of environment transitions *and defender adaptation*, use it to compare counterfactual attacker actions, and test whether gains persist against unseen defender policies rather than only against the training opponent.

The first paper should emphasize controlled science over a maximal system. Begin with a frozen LLM or lightweight adapter, discrete attack actions, logged trajectories, and model-predictive selection. Add policy RL only after prediction and counterfactual ranking are demonstrably valid.

## 2. Research questions and hypotheses

### Primary research question

**RQ1.** Does an opponent-conditioned world model improve the attack success, sample efficiency, and cross-defender generalization of a long-horizon adversarial LLM agent compared with memory-only, model-free RL, and non-opponent-conditioned world-model baselines?

### Secondary questions

- **RQ2 — modeling:** Which targets matter most: next tool/environment state, defender response, terminal success, time-to-detection, or a joint latent state?
- **RQ3 — planning:** Do counterfactual short-horizon rollouts help more as an inference-time planner, as a source of dense credit, or both?
- **RQ4 — uncertainty:** Does uncertainty-aware abstention or pessimistic planning reduce exploitation of world-model errors and improve transfer to unseen defenders?
- **RQ5 — memory interaction:** Does episodic attack memory complement a learned world model, or does the model subsume most of its benefit?
- **RQ6 — adaptation:** Can the model infer a latent defender type or update online when the defender changes within or across episodes?

### Falsifiable hypotheses

- **H1:** OPAL reaches a fixed attack-success threshold with at least 25% fewer real environment episodes than model-free GRPO/PPO, under an equal interaction budget.
- **H2:** Conditioning on defender identity/history improves held-out-defender attack success and defender-response log loss over an environment-only world model.
- **H3:** Counterfactual action ranking agrees with executed alternatives more often than an LLM judge and outcome-only credit, and this agreement predicts downstream policy gains.
- **H4:** Ensemble uncertainty plus pessimistic scoring lowers catastrophic model exploitation and improves worst-defender performance, although it may reduce in-distribution attack success.
- **H5:** Memory plus opponent modeling outperforms either alone on non-stationary defender schedules.

Pre-register one primary endpoint: **held-out-defender attack success rate under a fixed real-environment interaction and inference-token budget**. Treat all other outcomes as secondary.

## 3. Novelty claim and contribution boundary

### Proposed contributions

1. **Opponent-conditioned agent world model.** A learned transition model of executable tool state, defender response, terminal outcome, and uncertainty, conditioned on recent interaction history or inferred defender embedding.
2. **Counterfactual adversarial planning/credit.** At a decision point, generate plausible attack actions, roll each forward through the model, and rank them using predicted success minus detection, cost, and uncertainty penalties.
3. **Defender-shift protocol.** Train against a policy population and evaluate on held-out defenses, prompt templates, model families, and intervention schedules.
4. **Causal credit audit.** In resettable environments, execute alternative actions from the same saved state to measure whether model-derived step credit identifies causally important decisions.
5. **Reproducible safety testbed.** Release only sandboxed tasks, attack abstractions, logs, evaluation code, and responsible-use documentation; avoid operational instructions against real services.

### What not to claim

- Do not claim the first world model for LLM agents, the first self-evolving attacker, or the first step-level agent credit method.
- Do not equate next-token likelihood with a faithful causal world model.
- Do not call a result robust if it is tested only against one fixed victim/defender.
- Do not use “top-tier novelty” as the sole contribution; the causal audit and defender-shift evaluation must carry scientific weight.

## 4. Formal problem and scope

Model the system as a partially observable stochastic game. At step \(t\), the attacker observes \(o_t\), maintains history \(h_t\), chooses an intervention \(a_t\), and the defender chooses or induces response \(d_t\). The executable environment transitions to \(s_{t+1}\) and returns observation \(o_{t+1}\). Terminal reward captures attack goal attainment, while penalties capture detection, invalid actions, cost, and policy violations.

The learned model is

\[
p_\theta(s_{t+1}, o_{t+1}, d_t, r_t, y \mid h_t, a_t, z_D),
\]

where \(z_D\) is a defender identity or inferred latent type and \(y\) is terminal success. A practical planner evaluates candidate actions with

\[
J(a_t)=\mathbb{E}_{\hat\tau\sim p_\theta}[R(\hat\tau)]
-\lambda_u U(\hat\tau)-\lambda_c C(\hat\tau)-\lambda_d P(\text{detected}\mid\hat\tau).
\]

For counterfactual step credit, compare the executed action with alternatives from the same state:

\[
C_t=Q_\theta(h_t,a_t,z_D)-\mathbb{E}_{a'\sim q(\cdot\mid h_t)}Q_\theta(h_t,a',z_D).
\]

The first study should use **discrete, structured attacker actions** (e.g., choose target tool, intervention location, abstract transformation family, or abstain), not unconstrained free-form exploit text. This makes counterfactual execution, action matching, safety review, and credit estimation tractable.

## 5. System architecture

### Components

1. **Executable environment adapter**
   - Produces canonical state diffs, tool calls/results, defender messages, rewards, termination reason, token/latency cost, and a resettable state identifier.
   - Separates private ground-truth state (training/evaluation only) from attacker observations.

2. **Attacker policy**
   - Phase A: frozen instruction model proposes top-\(K\) structured actions.
   - Phase B: a learned reranker or LoRA policy chooses among candidates.
   - Phase C, only if justified: GRPO/PPO fine-tuning over complete trajectories.

3. **Defender population**
   - Fixed rule-based filters, prompt-level defenses, tool-output sanitizers, action validators, and multiple LLM-agent policies.
   - Each episode samples a defender; some experiments switch defenders mid-episode.

4. **Opponent encoder**
   - Encodes the last \(m\) defender observations/actions into \(z_D\).
   - Compare known defender ID, learned recurrent embedding, and no opponent conditioning.

5. **World model**
   - Shared history encoder plus heads for next structured state diff, defender response class/text, reward/detection, termination, and success-to-go.
   - Begin with supervised fine-tuning of a 1.5B–4B text model or a smaller transformer over serialized structured states.
   - Use a 3–5 member ensemble or bootstrap heads for epistemic uncertainty.

6. **Planner and credit module**
   - Generate \(K\) candidates; simulate horizon \(H=1\)–5; rerank by \(J\).
   - Optionally convert counterfactual advantages into per-step rewards for policy optimization.

7. **Episodic memory**
   - Stores compact tuples: defender context, action abstraction, outcome, failure reason, uncertainty, and verified causal effect.
   - Retrieval is an ablation, not baked into every system.

## 6. Environments and data

### Recommended progression

**Tier 0 — Unit-test game (build yourself).** A deterministic, text-only, resettable tool game with 5–15 steps and 4–12 discrete attacker actions. Use it to validate Bellman targets, replay, counterfactual branching, and leakage controls. It is a learning instrument, not a publication benchmark.

**Tier 1 — AgentWorldModel-1K subset.** Use 20–50 executable SQL-backed environments for transition learning and clean state-diff supervision. The release provides 1,000 executable environments, tasks, databases, verifiers, and models. Add sandboxed attacker/defender wrappers rather than modifying the base verifier. Split by environment schema/domain, not random trajectories, to prevent near-duplicate leakage.

**Tier 2 — AgentDojo.** Use its dynamic tool-agent environment and security test cases for prompt-injection-style attack/defense evaluation. It includes realistic tasks, extensible attacks/defenses, and executable outcomes. Preserve both utility and security objectives.

**Tier 3 — one external security benchmark.** Prefer InjecAgent or Agent Security Bench if code, licenses, and executable evaluation remain available and reproducible when implementation begins. Freeze versions and document task exclusions.

**Optional generalization checks.** τ-bench/τ²-bench, BFCL, WebShop, or ALFWorld can test generic tool-use/long-horizon learning, but they should not all be included in the first paper. Choose at most one to show the method is not security-benchmark-specific.

### Data unit and logging schema

Each transition should contain: environment/task/split IDs; exact initial-state hash; public observation; private canonical state; attacker candidate set and chosen action; defender ID/history/action; tool call/result; state diff; reward components; terminal verifier output; model/prompt/checkpoint versions; seeds; tokens; latency; and whether the transition is factual or imagined.

Never mix imagined transitions into the ground-truth evaluation set. Deduplicate by environment template, task intent, and canonical state/action signature. Hold out entire environment families and defender families.

## 7. Baselines

Use an equal real-interaction budget and report inference/training token costs.

1. **Prompt-only attacker:** frozen ReAct-style agent; no memory; no RL.
2. **Memory attacker:** Evo-Attacker-inspired retrieval/reflection system without a learned world model.
3. **Model-free outcome RL:** GRPO or PPO with terminal verifier reward.
4. **Fine-grained credit RL:** implement one feasible method such as GiGPO or Agent Lightning-style hierarchical decomposition; cite TRACE/HCAPO as relevant comparisons if code or assumptions prevent exact reproduction.
5. **Environment-only world model:** predicts transition/outcome without defender history or identity.
6. **Opponent model only:** predicts defender response but no environment rollout.
7. **World model + planner:** proposed method without policy fine-tuning.
8. **World model + planner + memory:** full system.
9. **Oracle diagnostic:** planner using the executable environment for shallow branching. This is an upper bound, never a deployable baseline.

## 8. Staged implementation and experiment plan

### Stage 0 — RL foundations and reproducibility (weeks 1–3)

- Implement tabular Q-learning and policy gradients on a small MDP; then PPO on a standard text/discrete environment.
- Learn trajectories, return/advantage, bootstrapping, off-policy replay, KL control, entropy, and seed management.
- Create experiment configuration, immutable run manifests, structured logs, and unit tests for reward and reset semantics.
- **Gate:** recover a known learning curve across at least five seeds and explain every loss term.

### Stage 1 — executable adversarial testbed (weeks 4–6)

- Build the Tier-0 game and defender population.
- Specify the attacker action ontology and reward vector before training.
- Add snapshot/restore so alternatives can be executed from exactly the same state.
- Test for observation leakage and reward hacking.
- **Gate:** deterministic replay reproduces state hashes and rewards in at least 99.9% of trials.

### Stage 2 — offline trajectory corpus (weeks 7–9)

- Collect trajectories from random, heuristic, prompt-only, memory, and partially trained policies against all training defenders.
- Ensure action coverage; use targeted exploration for rare branches.
- Split by environment family and defender family.
- Produce dataset card and coverage report.
- **Gate:** each major action/defender stratum has sufficient support; no train/test template leakage.

### Stage 3 — world-model learning (weeks 10–13)

- Train one-step heads first: state diff, defender response, reward/detection, termination, success-to-go.
- Compare structured prediction with free-text next-observation prediction.
- Evaluate one-step and open-loop \(H=2,3,5\) rollout error.
- Calibrate uncertainty using validation data; plot risk–coverage curves.
- **Gate:** the model beats frequency and behavior-cloning baselines, counterfactual rank accuracy is above chance, and calibration is adequate for selective planning.

### Stage 4 — inference-time counterfactual planner (weeks 14–17)

- Generate \(K=4,8,16\) candidate actions with the same base model across systems.
- Compare horizon \(H=1,3,5\), mean vs pessimistic ensemble score, and reranking latency.
- Run against seen and held-out static defenders before any RL fine-tuning.
- **Gate:** planner improves the pre-registered endpoint or sample efficiency without unacceptable utility/cost regressions.

### Stage 5 — policy learning and credit (weeks 18–22)

- Start with offline pairwise/ranking distillation from verified counterfactuals.
- Then use model-derived per-step advantage in a conservative GRPO/PPO objective; cap synthetic-to-real ratio and apply KL regularization.
- Compare terminal-only, model-derived credit, executed-replay credit, and their combination.
- Periodically refresh the model using new real trajectories; maintain a real-only validation set.
- **Gate:** gains replicate across seeds and persist when planning is disabled, demonstrating policy learning rather than only search compute.

### Stage 6 — defender shift and online adaptation (weeks 23–26)

- Test held-out rule defenses, prompts, model family, action validation, and mixtures.
- Switch defender policies mid-episode or between blocks without revealing identity.
- Measure adaptation speed and forgetting; compare explicit ID with inferred \(z_D\).
- Include population training or PSRO-style opponent sampling only after single-population results are stable.

### Stage 7 — external benchmark and paper package (weeks 27–32)

- Port the smallest successful configuration to AgentDojo plus one additional benchmark.
- Freeze code, environments, prompts, checkpoints, and analysis before final test runs.
- Run pre-registered statistics; conduct red-team review of release artifacts.
- Prepare reproducibility checklist, threat model, ethics/limitations, model card, dataset card, and artifact instructions.

## 9. Metrics

### Primary system metric

- **Held-out-defender attack success rate (ASR)** at fixed real environment episodes and inference-token budget, with bootstrap 95% confidence intervals across tasks and seeds.

### Security–utility metrics

- Benign task success/utility under attack and without attack.
- Defender failure rate, detection rate, time-to-detection, policy-violation severity, invalid action rate.
- Pareto frontier of attacker success versus benign utility and compute.
- Worst-defender ASR and conditional value-at-risk across defender families.

### Learning and cost

- Area under the learning curve versus real environment episodes.
- Episodes/tokens/GPU-hours to reach a fixed ASR.
- Wall-clock latency, planner calls, generated tokens, peak memory, and dollar-equivalent cost if APIs are used.

### World-model quality

- Structured next-state exact match/F1 and canonical state-diff accuracy.
- Defender action accuracy, negative log-likelihood, and macro-F1.
- Reward/outcome Brier score, log loss, AUROC/AUPRC where appropriate.
- Expected calibration error plus reliability and risk–coverage curves.
- Multi-step rollout error by horizon and error type.
- Counterfactual pairwise rank accuracy/regret against executed branches.

### Adaptation and diversity

- Steps/episodes to recover 90% of steady-state performance after defender change.
- Forward transfer, backward transfer/forgetting, strategy coverage, action entropy, and memory retrieval precision.

## 10. Ablations

Run a factorial core where affordable; otherwise prioritize these single removals:

- Remove opponent conditioning; use known defender ID versus inferred defender embedding.
- Remove world model; remove memory; remove both.
- Predict only terminal outcome versus joint state/defender/outcome heads.
- Planning only versus credit only versus both.
- Deterministic single model versus ensemble; no uncertainty penalty versus pessimistic penalty.
- Horizons 1/3/5 and candidate counts 4/8/16.
- Real-only training versus real plus imagined transitions; vary synthetic-to-real ratio.
- Frozen world model versus periodic refresh.
- Random opponent sampling versus curriculum/population sampling.
- Text prediction versus structured state-diff prediction.
- Executed-replay credit versus model credit versus LLM-judge credit versus terminal reward.

The most important ablation is **held-out defender + no opponent conditioning**. Without it, the paper cannot establish that opponent modeling—not merely more parameters or search—causes the gain.

## 11. Statistical evaluation

- Define task and defender splits before final runs; publish the split generator and hashes.
- Use at least 5 independent training seeds for the core comparison; 10 if variance is high. Evaluate each checkpoint on many fixed task–defender episodes with paired initial states.
- For binary success, use a hierarchical logistic mixed-effects model with method as a fixed effect and task/environment, defender, and seed as random effects. Report odds ratios and marginal percentage-point effects with 95% intervals.
- Complement with paired stratified bootstrap confidence intervals over tasks/defenders. For learning curves, bootstrap area under curve and time-to-threshold.
- Correct the pre-declared family of primary pairwise comparisons using Holm’s method. Treat ablations as secondary/exploratory unless powered in advance.
- Report effect sizes, intervals, raw per-seed values, and negative results—not only p-values.
- Conduct a power simulation using pilot variance before expensive training. Decide the minimum practically important effect in advance (for example, +5 percentage points held-out ASR or 25% fewer episodes).
- Never select checkpoints on the test defenders. Use a validation defender population and a fixed stopping rule.

## 12. Compute plan

### Low-compute prototype

- Frozen 3B–8B instruction model via local inference or API; train only small structured world model/reranker or LoRA.
- 1 GPU with 24–48 GB memory is plausible for 1.5B–4B QLoRA/SFT; CPU workers run executable environments.
- Collect 10k–50k transitions; use shallow rollouts and cached candidate actions.

### Full first paper

- 4–8 modern 80 GB GPUs are a realistic target for 7B-class online RL with concurrent rollouts, though exact needs depend on sequence length, optimizer, inference engine, and quantization.
- The dominant cost may be environment/LLM rollout tokens, not gradient steps. Log both.
- Use staged budgets: 10% pilot, 20% method selection, 70% frozen final runs. Kill configurations that fail predeclared gates.
- Do not begin with co-training two 7B agents plus a 7B world model. Freeze defenders, use adapters, and separate data collection from training.

## 13. Risks and mitigations

- **Model exploitation / hallucinated advantages:** ensembles, pessimistic scoring, short horizons, uncertainty abstention, real-only validation, and periodic executed checks.
- **Opponent overfitting:** hold out defense families and model families; population sampling; report worst-case performance.
- **Non-stationarity:** replay stratified by policy/defender version; recency weighting; frozen evaluation opponents; explicit version logs.
- **Reward hacking:** separate reward components; adversarially test verifiers; inspect high-reward failures; keep private final verifiers.
- **Credit is correlational, not causal:** use snapshot-and-branch executed replay as ground truth on a subset.
- **Data leakage:** split environment templates/schemas and prompts; deduplicate trajectories; isolate test verifiers.
- **Unfair compute comparison:** equalize real interactions and report candidate/planning tokens separately.
- **Irreproducible API drift:** pin model snapshots where possible; save prompts, parameters, raw outputs, and dates.
- **Dual-use harm:** work only in sandboxed environments; abstract harmful actions; exclude real credentials/services; tier release artifacts; obtain institutional review where required.
- **Scope explosion:** one primary environment suite, one external benchmark, one base-model family, and one principal RL algorithm in the first paper.

## 14. Milestones and decision points

- **M1 (week 3):** RL sanity checks reproduce expected results.
- **M2 (week 6):** resettable adversarial environment and verified logging.
- **M3 (week 9):** leakage-audited trajectory dataset.
- **M4 (week 13):** calibrated world model with useful counterfactual ranking.
- **M5 (week 17):** planning improves held-out-defender endpoint.
- **M6 (week 22):** learned policy benefit survives without inference-time planning.
- **M7 (week 26):** defender-shift results and complete ablations.
- **M8 (week 32):** external benchmark, frozen statistics, artifact, and manuscript.

**Pivot rule:** If the world model cannot rank executed alternatives reliably by M4, pivot the paper toward a rigorous audit of world-model credit and failure modes rather than forcing an RL gain. That can still be valuable if the causal evaluation is strong.

## 15. Publication strategy

### Paper narrative

1. Adaptive adversarial agents make a defender part of the dynamics.
2. Existing memory-based attackers reuse experience but do not explicitly learn calibrated counterfactual defender dynamics.
3. OPAL models those dynamics and uses them for planning/credit.
4. The causal branch-and-replay audit validates—or bounds—the credit signal.
5. Held-out-defender evaluation demonstrates adaptation rather than memorization.

### Targeting

- For a strong methods paper with broad experiments: NeurIPS, ICML, or ICLR.
- For language-agent and empirical system emphasis: ACL, EMNLP, or NAACL.
- For security-first framing and a mature threat model: USENIX Security, IEEE S&P, ACM CCS, or NDSS.
- A workshop submission can obtain early feedback, but avoid publishing the complete core contribution in a way that conflicts with later venue rules.
- A journal extension should add a meaningful dimension—formal analysis, broader defender populations, longitudinal adaptation, or a substantially larger benchmark—not merely extra runs.

Before submission, rerun a focused literature search and build a claim-to-evidence matrix. Recent agentic RL is moving quickly; novelty must be rechecked near the deadline.

## 16. Reading plan

### Must-read before implementation

#### RL foundations

1. **Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018).** Read Chapters 3–7, 9–13. The conceptual backbone: MDPs, temporal difference learning, policy gradients, off-policy issues.
2. **Schulman et al., “Proximal Policy Optimization Algorithms” (2017).** Understand clipped objectives, advantage estimation, and why implementation details matter.
3. **Schaul et al., “Prioritized Experience Replay” (2015/ICLR 2016).** Useful for replay design and rare adversarial branches.
4. **Agarwal et al., “Deep Reinforcement Learning at the Edge of the Statistical Precipice” (NeurIPS 2021).** Required for aggregate metrics, uncertainty, and seed-aware claims.

#### Model-based RL and world models

5. **Sutton, “Integrated Architectures for Learning, Planning, and Reacting Based on Approximating Dynamic Programming” (1990).** The Dyna idea: learn a model, then learn/plan from simulated experience.
6. **Ha & Schmidhuber, “World Models” (2018).** The modern conceptual entry point for latent dynamics and imagined rollouts.
7. **Chua et al., “Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models” (PETS, NeurIPS 2018).** Ensembles and uncertainty-aware planning.
8. **Janner et al., “When to Trust Your Model: Model-Based Policy Optimization” (NeurIPS 2019).** Short model rollouts and model-bias control.
9. **Hafner et al., “Dream to Control” (Dreamer, ICLR 2020)** and **“Mastering Diverse Domains through World Models” (DreamerV3, Nature 2025).** Latent imagination and robust world-model learning; focus on principles, not vision implementation.
10. **Schrittwieser et al., “Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model” (MuZero, Nature 2020).** A model can support planning without reconstructing every observation detail.
11. **Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning (2026 preprint).** Directly relevant executable agent environments and AgentWorldModel-1K.

#### LLM agents and agentic RL

12. **Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models” (ICLR 2023).** Basic agent loop and trajectory representation.
13. **Shao et al., “DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models” (2024).** Read the GRPO section for the algorithm later adopted widely in LLM RL.
14. **Agent Lightning: Train ANY AI Agents with Reinforcement Learning (2025 preprint), plus v1.0 (2026 preprint).** Harness/training separation and hierarchical trajectory credit.
15. **GiGPO: Group-in-Group Policy Optimization for LLM Agent Training (2025 preprint).** Critic-free step-level relative advantage for long-horizon environments.
16. **TRACE: Turn-level Reward Assignment via Credit Estimation for Long-Horizon Agents (2026 preprint).** Turn-level TD-style credit from reference-model log-ratio values.
17. **HCAPO: Hindsight Credit Assignment for Long-Horizon LLM Agents (2026 preprint).** Post-hoc LLM critic and multi-scale advantage; compare its assumptions with causal replay.

#### Adversarial agents and security

18. **Evo-Attacker: Memory-Augmented Reinforcement Learning for Long-Horizon Tool Attacks on LLM-MAS (2026 preprint).** The closest system. Reproduce its problem definition, memory, Attack-Flow GRPO, baselines, and evaluation before asserting novelty.
19. **AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents (2024).** Primary executable security testbed and utility/security framing.
20. **InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents (2024).** Attack surface and benchmark design.
21. **Agent Security Bench: Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents (2024/2025).** Broad threat taxonomy and evaluation; confirm the exact version used at implementation time.

#### Opponent modeling and multi-agent RL

22. **He et al., “Opponent Modeling in Deep Reinforcement Learning” (ICML 2016 workshop/arXiv).** Direct historical precursor for conditioning policies on learned opponent representations.
23. **Foerster et al., “Learning with Opponent-Learning Awareness” (AAMAS 2018).** Why anticipating an opponent’s update changes optimization.
24. **Lanctot et al., “A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning” (NeurIPS 2017).** Policy-Space Response Oracles and population-based evaluation.
25. **Davies et al., “Learning to Model Opponent Learning” (2020).** Models adapting opponents rather than assuming stationarity.

#### Memory

26. **Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning” (NeurIPS 2023).** Episodic reflection without weight updates.
27. **Packer et al., “MemGPT: Towards LLMs as Operating Systems” (2023).** Hierarchical memory and context management.
28. **Park et al., “Generative Agents: Interactive Simulacra of Human Behavior” (UIST 2023).** Memory stream, reflection, and retrieval scoring.

### Secondary / consult as needed

- **Moerland et al., “Model-based Reinforcement Learning: A Survey” (Foundations and Trends, 2023):** taxonomy and terminology.
- **Kurutach et al., “Model-Ensemble Trust-Region Policy Optimization” (2018):** ensemble model-based policy learning.
- **Yu et al., “MOPO: Model-based Offline Policy Optimization” (NeurIPS 2020):** pessimism under learned dynamics.
- **Kidambi et al., “MOReL” (NeurIPS 2020):** conservative offline model-based RL.
- **Silver et al., AlphaGo Zero (Nature 2017) and AlphaZero (Science 2018):** self-play and search foundations.
- **Vinyals et al., AlphaStar (Nature 2019) and Brown & Sandholm, Pluribus (Science 2019):** population/self-play in complex imperfect-information games.
- **Lowe et al., MADDPG (NeurIPS 2017), Rashid et al., QMIX (ICML 2018), Yu et al., MAPPO (NeurIPS 2022):** standard MARL architectures; useful context, not first implementation targets.
- **Hernandez-Leal et al., “A Survey of Learning in Multiagent Environments” (2019):** non-stationarity and opponent modeling taxonomy.
- **Zhang et al., “A Survey on Self-play Methods in Reinforcement Learning” (2024 preprint):** current self-play map.
- **Yao et al., WebShop (NeurIPS 2022), Shridhar et al., ALFWorld (ICLR 2021), Zhou et al., τ-bench (2024):** agent environment design.
- **ToolBench (ICLR 2024) and BFCL:** tool-use evaluation and out-of-distribution function calling.
- **Greshake et al., “Not what you’ve signed up for” (2023), ToolEmu (2023), Prompt Injection Attacks and Defenses in LLM-Integrated Applications (2023):** security context and threat modeling.
- **MemoryBank (2023), Voyager (2023), ExpeL (2024), and recent LLM-agent-memory surveys:** design options after the core episodic memory papers.
- **MemWM / memory-augmented text world-model work (2026):** read before final novelty claims about memory–world-model integration; verify the precise paper/version from its primary page when drafting related work.
- **“Credit Without Ground Truth: Auditing Step-Level Credit Assignment in LLM Agents Against Executed Replay” (August 2026 preprint):** highly relevant late-breaking audit; scrutinize methods and results before positioning causal credit claims.

### Suggested eight-week reading sequence

- **Weeks 1–2:** Sutton & Barto; PPO; statistical evaluation.
- **Week 3:** Dyna, World Models, PETS, MBPO.
- **Week 4:** Dreamer, MuZero, model-based RL survey.
- **Week 5:** ReAct, GRPO/DeepSeekMath, Agent Lightning, GiGPO.
- **Week 6:** TRACE, HCAPO, causal/executed credit audit.
- **Week 7:** Evo-Attacker, AgentDojo, InjecAgent, Agent Security Bench.
- **Week 8:** opponent modeling, LOLA, PSRO, LeMOL, Reflexion, MemGPT.

For every paper, record: problem; state/action/reward; what is learned; data source; credit mechanism; comparator; held-out generalization; compute; failure modes; and the exact idea that changes this proposal.

## 17. Primary links verified for this proposal

- [Evo-Attacker (arXiv:2605.25389)](https://arxiv.org/abs/2605.25389)
- [Agent World Model paper (arXiv:2602.10090)](https://arxiv.org/abs/2602.10090)
- [Agent World Model code and AgentWorldModel-1K links](https://github.com/Snowflake-Labs/agent-world-model)
- [AgentDojo (arXiv:2406.13352)](https://arxiv.org/abs/2406.13352)
- [Agent Lightning (arXiv:2508.03680)](https://arxiv.org/abs/2508.03680)
- [Agent Lightning v1.0 (arXiv:2608.17528)](https://arxiv.org/abs/2608.17528)
- [TRACE credit assignment (arXiv:2607.13988)](https://arxiv.org/abs/2607.13988)
- [HCAPO (arXiv:2603.08754)](https://arxiv.org/abs/2603.08754)
- [GiGPO (arXiv:2505.10978)](https://arxiv.org/abs/2505.10978)
- [World Models (arXiv:1803.10122)](https://arxiv.org/abs/1803.10122)
- [Opponent Modeling in Deep RL (arXiv:1609.05559)](https://arxiv.org/abs/1609.05559)
- [Learning to Model Opponent Learning (arXiv:2006.03923)](https://arxiv.org/abs/2006.03923)
- [Self-play survey (arXiv:2408.01072)](https://arxiv.org/abs/2408.01072)

## 18. First concrete next step

Write a two-page experiment specification for Tier 0 containing: the state schema, observation boundary, 6–10 discrete attacker actions, 3 defender policies, terminal verifier, reward vector, snapshot/restore contract, and the pre-registered held-out-defender endpoint. Then implement the environment and a random-policy data collector before choosing an RL framework. This sequence will teach the essential RL mechanics and expose whether counterfactual branching is actually feasible.
