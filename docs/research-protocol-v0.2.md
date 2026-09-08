# Scaled ARLAS Reproduction Protocol v0.2

**Issued:** 2026-09-07  
**Hardware envelope:** one 24 GB NVIDIA GPU  
**Status:** Milestone 0 approved; learning is not yet approved  
**Supersedes:** `docs/research-protocol-v0.1.md`

## Scientific bet

Persistent cross-episode attack memory may interact with between-episode policy
adaptation to preserve, retrieve, and refine exploitable strategies across
co-training rounds. This can produce historical defender vulnerabilities that
same-round evaluation conceals.

The project does not claim novelty from generic self-play forgetting or from
combining ARLAS and Evo-Attacker.

## Pilot primary question

With horizon fixed long and terminal credit fixed, what are the separate and
joint effects of persistent cross-episode memory and online attacker learning on
held-out attack success at matched compute and benign utility?

The confirmatory effect is the memory × learning interaction on the log-odds
scale. Absolute-risk contrasts remain the primary interpretation.

## Primary endpoint

Select checkpoints using validation data. A checkpoint is eligible only when
its benign task success is no more than five absolute percentage points below
the unmodified defender. The primary outcome is worst-case held-out ASR over a
fixed registered attacker population at the selected eligible checkpoint.

If no checkpoint is eligible, report the condition as
`utility-infeasible/dominated`. Do not weaken the floor after seeing results.
Report the security–utility Pareto curve as a secondary outcome.

The pilot primary comparison is the self-contained ARLAS-style reference versus
C3-ML, which combines persistent memory and learning with terminal credit. C4
credit training is conditional and not part of the initial primary comparison.

## Self-contained reference

The reference is defined by this repository, independently of upstream code:

1. One version-pinned AgentDojo suite with executable utility and security
   verifiers.
2. Declared instruction-tuned base models with separate PEFT adapters for the
   attacker and defender.
3. Alternating attacker and defender update blocks between episodes; no
   within-episode weight changes.
4. Attacker actions only at benchmark-authorized insertion points.
5. Current-episode history is available to the attacker; semantic
   cross-episode retrieval memory is not.
6. Terminal executable-verifier reward for the reference RL update.
7. A registered latest-attacker condition and a separately registered immutable
   historical-attacker population condition.
8. Fixed interaction-count checkpoint schedule and validation-only selection.
9. Matched environment interactions and maximum generated-token budgets.
10. Separate raw security, utility, refusal, invalid-action, and infrastructure
    outcomes.

Use `ARLAS-style` unless model, environment, data, training, and evaluation
fidelity justify stronger reproduction language.

## Confirmatory and exploratory scope

### Confirmatory pilot core

- Long-horizon 2 × 2 memory × learning factorial.
- Reference-versus-C3-ML comparison.
- Historical forgetting from fixed-schedule checkpoint cross-play.

### Gated diagnostics

- Short-versus-long horizon, only if intervention depth is adequate.
- Offline intervention-credit quality on fixed trajectories or saved states.
- Online intervention-credit training only if the offline estimators differ
  meaningfully and budget remains.

### Exploratory

- Cyclic dominance.
- Embedding-based strategy diversity.
- External benchmark or model-family transfer.
- Any mitigation selected after failure diagnosis.

## Scale-validity gates

Learning begins only after these gates pass:

- **Defender competence:** base BTSR exceeds a threshold frozen after suite
  inventory but before attack outcome experiments.
- **Attackability:** a scripted or prompted attacker produces a non-floor,
  non-ceiling ASR.
- **Intervention depth:** the selected task blocks have a median of at least
  three eligible insertion opportunities and at least two distinct attacker
  decisions for the horizon comparison.
- **Memory expressivity:** retrieved development-only information changes an
  attacker's action and produces a measurable behavioral contrast against empty
  memory on controlled tasks.
- **Learning responsiveness:** a short adapter update changes valid behavior or
  ASR without malformed actions dominating.
- **Verifier reliability:** ambiguity and manual-audit disagreement remain below
  thresholds frozen before learning.

A failed gate triggers repair, environment change, model adjustment, or removal
of the affected claim. A null at 1.7B–4B applies only to the tested scale and
compute envelope.

## Compute limits

- Maximum 5,000 pilot environment episodes.
- Maximum 30 million counted model input/output tokens.
- Maximum 150 GPU-hours.
- At least 35% of the episode/token budget reserved for cross-play and final
  evaluation when learned-condition training begins.
- At most a 4 × 4 attacker/defender checkpoint matrix in the initial pilot.
- One seed for pipeline and directional feasibility; two additional seeds only
  for the two most informative comparisons.

Initial model profile:

- `Qwen/Qwen3-1.7B` first; 4B only after competence and memory profiling.
- 4-bit NF4 QLoRA with double quantization.
- 2,048-token initial context.
- Micro-batch size one and GRPO group size two.
- Separate rollout, optimizer, and evaluation phases where needed.

Measured target-GPU throughput replaces planning assumptions but does not
automatically raise these ceilings.

## Milestone sequence

### Milestone 0 — novelty, reference, and feasibility

Complete `docs/milestone-0-checklist.md`. No model training is permitted yet.

### Milestone 1 — environment and verifier integrity

Freeze development, validation, and sealed pilot-test manifests; implement the
adapter, ledger, replay, leakage controls, and verifier fixtures. Require exact
replay and independent security/utility outcomes.

### Milestone 2 — frozen baseline and reference

Measure base competence and static attackability. Establish the self-contained
reference, audit at least 25 stratified episodes, and reconcile token/episode
counts.

### Milestone 3 — memory × learning core

Run frozen memory conditions first, then one-seed learning feasibility. Expand
only after rewards, actions, compute, and adapter reload are valid.

### Milestone 4 — fixed-schedule cross-play

Evaluate the pre-registered checkpoint matrix on identical task blocks and
seeds. Confirm forgetting; report cycling only descriptively unless powered.

### Milestone 5 — replication and publication gate

Add seeds to the two most informative comparisons, audit failures, reconcile
the compute ledger, and issue a proceed/pivot/stop report.

## Full-paper gate

Proceed only if all validity gates pass and at least one signal is replicated:

- a practically meaningful memory × learning interaction;
- a historical vulnerability hidden by contemporaneous evaluation;
- a capability-specific generalization failure supported by trajectories; or
- a diagnosis-matched mitigation that improves historical robustness without
  violating the benign-utility floor.

Proceed with a narrower measurement paper if cross-play yields a reliable lesson
without a resolved mechanism. Stop or pivot if effects remain below the smallest
effect of interest, scale-validity fails, verifier uncertainty prevents
attribution, or the design exceeds the fixed compute ceiling.

