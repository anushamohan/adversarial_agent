# Research Proposal: Stress-Testing Adversarial Co-Training Against Long-Horizon Attackers

**Working title:** *CoTA-Break: Does Adversarial Co-Training for LLM Agent Safety Survive a Long-Horizon, Memory-Augmented Attacker?*
**Audience:** A researcher with strong RL fine-tuning background (GRPO/DPO/PPO, reward shaping), limited prior work in multi-agent/self-play settings
**Recommended first-paper scope:** Reuse two existing frameworks (ARLAS-style co-training loop, Evo-Attacker-style attacker); no new world model, no new environment stack, no vision component; single defender architecture family in the first study, extended to a small population only if time allows
**Status of recent citations:** Checked against primary paper/project pages; ARLAS (arXiv:2510.05442) and Evo-Attacker (arXiv:2605.25389 / ACL 2026) are both confirmed real, distinct papers as of this writing.

## 1. Executive summary

This project asks a narrower, more falsifiable question than "can we build a better adversarial agent": **does adversarial co-training — where an attacker and defender LLM improve together in a zero-sum self-play loop — remain effective once the attacker is given the capabilities that already exist in the published literature (long-horizon planning, persistent memory, credit assignment across multi-step attacks), or does the defender's learned robustness collapse against an attacker meaningfully more capable than the one it was trained against?**

ARLAS (Wang et al., 2025) demonstrates that co-training a defender against a *co-evolving but architecturally simple* attacker (single-turn prompt injection generation, no persistent memory) meaningfully improves robustness over static fine-tuning. Evo-Attacker (Yan et al., 2026) demonstrates, independently, that a *much more sophisticated* attacker — one with a dynamic attack memory, deliberative retrieval, and a custom long-horizon credit-assignment method (Attack-Flow GRPO) — consistently defeats every *static* defense it was tested against, including exactly the kind of fixed sanitizers and classifiers ARLAS's defender is validated to resist. **Neither paper tests the natural combination: an Evo-Attacker-capable attacker against an ARLAS-trained, co-evolving defender.** That gap is the entire contribution of this proposal — not a new mechanism, but an unresolved empirical question sitting directly between two existing, well-cited systems.

The first paper should prioritize a clean, well-instrumented empirical result over a novel algorithm. Reuse ARLAS's co-training loop and reward structure as-is; reuse (or closely reimplement) Evo-Attacker's memory module and Attack-Flow GRPO as-is. The contribution is the **combination and the finding**, plus — only if the first result shows a failure mode — a minimal, targeted fix to the defender's training procedure.

## 2. Research questions and hypotheses

### Primary research question

**RQ1.** When an LLM agent defender is co-trained (ARLAS-style, zero-sum self-play) against a memory-augmented, long-horizon attacker with Evo-Attacker-style capabilities, does the defender converge to a comparably robust policy, or does co-training destabilize, stall, or converge to a defender that is robust in-distribution but fails against out-of-distribution attack sequences the attacker's memory enables it to construct?

### Secondary questions

- **RQ2 — stability:** Does the non-stationarity introduced by a *learning* long-horizon attacker (as opposed to ARLAS's simpler attacker) cause training instability (reward oscillation, mode collapse to a narrow attack/defense clique) that isn't present in the original ARLAS setup?
- **RQ3 — credit assignment:** ARLAS's defender reward is comparatively simple (task completion + injection resistance per episode). Does a defender trained with this reward structure fail specifically against long-horizon attacks whose payoff is only realized many steps after the injection point — i.e., is the defender's *credit assignment*, not just its capacity, the bottleneck?
- **RQ4 — generalization direction:** Does robustness gained against a long-horizon attacker transfer back to simple single-turn attacks (asymmetric generalization), or only in one direction?
- **RQ5 — population vs. single-opponent:** Does training the defender against a *population* of attackers at varying capability levels (simple → memory-augmented) produce a more robust final policy than training directly against the strongest attacker from step one?

### Falsifiable hypotheses

- **H1:** A defender co-trained against a static (non-learning) long-horizon attacker snapshot achieves lower held-out attack-resistance than one co-trained in a fully dynamic loop, holding attacker capability fixed — i.e., co-evolution itself (not just attacker sophistication) matters.
- **H2:** Defender robustness against long-horizon attacks does *not* emerge as a side effect of ARLAS's original training recipe; it requires either reward reshaping, curriculum ordering (simple → complex attacker), or explicit multi-step credit signals.
- **H3:** Training stability (measured by reward variance and policy KL drift across co-training rounds) degrades measurably once the attacker has memory, relative to ARLAS's reported training curves against its simpler attacker.
- **H4:** A curriculum that gradually increases attacker capability (start ARLAS-simple, introduce memory/Attack-Flow GRPO in later rounds) yields a more robust and more stable final defender than starting co-training at full attacker capability.

Pre-register one primary endpoint: **defender attack-resistance rate against a held-out long-horizon attack suite, under a fixed co-training compute budget**, matched to ARLAS's original evaluation protocol wherever possible for direct comparability.

## 3. Novelty claim and contribution boundary

### Proposed contributions

1. **First reported combination of co-evolving defense (ARLAS) with a long-horizon, memory-augmented attacker (Evo-Attacker-class capability)** — an empirical stress test, not a new algorithm, of an assumption both papers leave implicit (that their respective setups generalize to the other's opponent sophistication).
2. **A diagnosis of *why* co-training does or doesn't hold up** — training-dynamics analysis (stability, credit assignment, curriculum effects) grounded in your existing GRPO/GDPO background, rather than a black-box benchmark comparison.
3. **(Conditional, only if RQ1 reveals a failure mode) A minimal, targeted fix** — e.g., a curriculum schedule or a defender-side credit-assignment change — motivated directly by the diagnosed failure, not designed speculatively in advance.
4. **A reusable evaluation protocol** for testing adversarial co-training defenses against attackers of escalating capability, intended to be a standard robustness check the field currently lacks.

### What not to claim

- Do not claim to be the first adversarial-training defense for LLM agents (ARLAS already is) or the first long-horizon attacker (Evo-Attacker already is).
- Do not claim a fully general "solved" defense if a fix is found — frame any proposed fix as addressing the specific failure mode observed, with explicit scope limits.
- Do not treat a single defender architecture or single benchmark as sufficient evidence of generalization; the population/held-out-attacker evaluation (RQ5) is what gives the finding scientific weight, not the headline number alone.
- Do not overstate real-world implications — this is a controlled study of a training paradigm, not a claim about production agent safety.

## 4. Formal problem and scope

Frame the setting as a two-player zero-sum game between attacker policy \(\pi_A\) and defender policy \(\pi_D\), following ARLAS's original formulation, but with the attacker's action space and reward extended to match Evo-Attacker's long-horizon, memory-conditioned setting:

\[
\pi_A: (o_t, M_t) \to a_t, \qquad \pi_D: (o_t) \to d_t
\]

where \(M_t\) is the attacker's dynamic attack memory (as in Evo-Attacker) and reward for the attacker is realized only at episode termination or a designated intervention point, requiring the same **Attack-Flow GRPO**-style credit assignment Evo-Attacker introduces to handle delayed payoff. The defender is trained with ARLAS's original co-training objective (task completion + injection resistance), unmodified in the first experiment, so that any degradation observed is attributable to attacker capability rather than a confounded change to the defender's own training procedure.

**Scope constraints for the first study:** text-only tool-use environments (reuse AgentDojo or ARLAS's own environment where licensing/code permits); a single defender base model family to start, extended to 2–3 only if compute allows; no new world model or planning component — this project studies *training dynamics under adversarial pressure*, not model-based planning (which is the separate OPAL-style direction, if you want to compare).

## 5. Experimental design

### Conditions to compare

1. **ARLAS baseline** — reproduce as closely as possible: co-training against the original simple attacker.
2. **Static long-horizon attack** — defender faces a *frozen* Evo-Attacker-class attacker (no co-training on the attacker side); isolates whether the defender can learn robustness against a hard but non-adapting opponent.
3. **Full co-training, no curriculum** — both attacker and defender co-trained from initialization, attacker has full long-horizon/memory capability from round one.
4. **Full co-training, curriculum** — attacker capability introduced gradually (H4).
5. **Population training** — defender trained against a mixture of attacker capability levels simultaneously (RQ5).

### Evaluation

- Held-out attack suite: attack strategies not seen during training, including both single-turn and long-horizon variants, to test the asymmetric-generalization question (RQ4).
- Training-dynamics diagnostics: reward variance across rounds, policy KL drift, and (if feasible) a qualitative check for mode collapse — the defender learning to counter only a narrow slice of the attacker's actual strategy space.
- Match ARLAS's original metrics (task completion rate under attack, injection success rate) so results are directly comparable to their reported numbers, not just internally comparable across your own conditions.

## 6. Staged implementation plan

**Stage 0 (weeks 1–4): Reproduce ARLAS.** Get the original co-training loop running end-to-end against the original simple attacker; confirm you can reproduce their reported robustness numbers before changing anything. This is the most important gate — if reproduction fails, the whole comparison is unreliable.

**Stage 1 (weeks 5–9): Reproduce or closely reimplement Evo-Attacker's attacker.** Memory module, deliberative retrieval, Attack-Flow GRPO. Validate against their reported attack-success numbers on at least one shared task domain if possible.

**Stage 2 (weeks 10–13): Static long-horizon attack condition.** Plug the frozen Evo-Attacker-class attacker into the ARLAS defender's training loop as a fixed opponent (condition 2 above). This is the lowest-risk experiment and should be run before attempting full co-training.

**Stage 3 (weeks 14–19): Full co-training conditions.** Conditions 3 and 4 (no curriculum vs. curriculum). This is where instability risk is highest — budget extra time for debugging non-convergence.

**Stage 4 (weeks 20–24): Population training and held-out evaluation.** Condition 5, plus the full held-out attack suite evaluation across all conditions.

**Stage 5 (weeks 25–28): Analysis, writing, and — only if warranted — a targeted fix.** If a clear failure mode emerged in Stage 3, design and test a minimal intervention; otherwise report the (still valuable) finding that co-training holds up, with the training-dynamics analysis as the main contribution.

*(~28 weeks of the ~39-week runway to NeurIPS 2027, leaving buffer for setbacks — a much tighter margin than a from-scratch system build would allow.)*

## 7. Key risks

- **Reproduction risk is the dominant risk.** Both ARLAS and Evo-Attacker are recent, and neither may have fully released code; budget real time for this in Stage 0–1, and have a fallback (reimplement from the method section, validate against reported numbers on a subset) ready.
- **Compute for co-training runs** — self-play/co-training is typically more expensive per experiment than single-policy RL, since both models are updating; scope the defender/attacker model sizes to what's actually feasible solo.
- **Null result is a real possibility** — co-training might simply hold up fine, in which case the paper's contribution shifts entirely to the training-dynamics diagnosis (RQ2/RQ3) and the reusable evaluation protocol, which is still a legitimate contribution but a less dramatic headline than a discovered failure mode.

## 8. Core reading list

1. **Wang et al., "Adversarial Reinforcement Learning for Large Language Model Agent Safety" (ARLAS, arXiv:2510.05442).** The defense-side co-training loop this project reuses and stress-tests.
2. **Yan et al., "Evo-Attacker: Memory-Augmented Reinforcement Learning for Long-Horizon Tool Attacks on LLM-MAS" (arXiv:2605.25389, ACL 2026).** The attacker-side capability being introduced into ARLAS's loop.
3. **Heinrich & Silver, "Fictitious Self-Play" (2016) and Jaderberg et al., "Population-Based Training" (2017).** Population-based self-play stability techniques relevant to RQ5.
4. **Foerster et al., "Learning with Opponent-Learning Awareness" (LOLA, AAMAS 2018).** Why a learning opponent changes optimization dynamics — directly relevant to why RQ2/RQ3 matter.
5. **AgentDojo (arXiv:2406.13352) and InjecAgent.** Candidate executable environments for the shared evaluation suite.
6. **Chen et al., "SPAG: Self-Playing Adversarial Language Game" (2024).** Cited by ARLAS as the most relevant prior self-play work; useful for understanding established self-play stability results in the LLM setting before extending to a harder attacker.

## 9. First concrete next step

Attempt Stage 0 reproduction of ARLAS on the smallest feasible shared task domain (ideally reusing their released code/checkpoints if available) and confirm the reported robustness gap between their trained defender and a static baseline is reproducible in your setup. This single gate determines whether the rest of the plan is viable before any new capability is introduced.
