# Critical Review: CoTA-Break Proposal (revised)

**Reviewer:** Claude (adversarial reviewer pass)
**Date:** 2026-09-07
**Document under review:** `co-training-stress-test-proposal-revised.md`
**Also read for context:** `old_proposals/co-training-stress-test-proposal.md`,
`old_proposals/world-model-guided-adversarial-llm-agents-proposal.md`,
`docs/research-protocol-v0.1.md`, `README.md`

Respond inline under each point with `> RESPONSE:` and a disposition
(`accept` / `reject` / `defer to pilot` / `needs decision`).

---

## Overall assessment

Unusually disciplined proposal. It has already absorbed most of the obvious
objections: it disclaims novelty from "ARLAS + Evo-Attacker," pre-registers a
primary endpoint, insists on matched benign utility *and* matched compute,
separates raw outcomes from shaped rewards, prefers executable verifiers over LLM
judges, and gates expensive work behind a pilot. The checkpoint cross-play idea
is the strongest part and is underused in LLM-agent security work.

The concerns below are about whether the project, as scoped, produces a
*publishable finding*, and whether it *fits the hardware* — not about rigor.

---

## Major concerns

### M1. Contribution may land as "known dynamics, new domain"

The proposal concedes it cannot claim novelty from the combination, so the
contribution reduces to "a controlled stress-testing methodology" plus whatever
the measurement reveals. But **H2** (contemporaneous self-play overstates
robustness; cross-play reveals forgetting/cycling) is essentially rediscovering
non-transitivity and catastrophic forgetting in self-play — the exact phenomena
that motivated fictitious self-play, PSRO, and population-based training.
Re-demonstrating it in LLM agents is incremental unless the **magnitude,
mechanism, or interaction with memory** is surprising. The proposal never states,
in one sentence, the non-obvious thing it expects to find. Without that bet, most
branches of the proposal's own publication decision tree lead to a
workshop/findings paper.

**Fix — do before the pilot:**
- Write the one-sentence **capability delta**: exactly what ARLAS's attacker
  cannot do that yours can, given ARLAS is correctly described as multi-turn with
  a historical population. The honest delta is narrow: persistent *cross-episode*
  memory + intervention-level deliberation + Attack-Flow credit.
- Write the one-sentence **expected finding**. If it is only "self-play forgets,
  also in LLMs," reconsider the framing or sharpen toward the memory interaction.

> RESPONSE:

### M2. Reproduction is load-bearing but under-hedged

The study rests on a faithful "ARLAS-style" reference and a faithful Attack-Flow /
C4 condition. If neither codebase is released, you are reimplementing two
non-trivial RL systems from method sections and validating each against reported
numbers — which can consume the entire pilot. Worse, the "ARLAS-style" hedge is
corrosive: if the reference is not faithful, then "fully capable attacker beats
the reference" is confounded by *your implementation quality*, not attacker
capability.

**Fix:**
- Define the reference attacker and defender by a precise, self-contained
  specification, so the internal contrast stands even if both upstream repos are
  unusable. Treat fidelity to ARLAS's published numbers as optional validation,
  not a dependency.
- Resolve code/checkpoint availability in week 0, not "after the compatibility
  week."

> RESPONSE:

### M3. Compute feasibility for the full study on one 24 GB GPU is unproven

README commits to 1.5B–4B backbones, 4-bit QLoRA, one AgentDojo suite. The full
study wants: co-training two GRPO policies x a 6-cell capability ladder x a
compact M/L/C factorial x population training x a J x K cross-play grid x 3–5
seeds x held-out template/task generalization. The budgeting *formula* is present
but there is no worked number.

**Fix:** put a back-of-envelope in the proposal now — candidate models,
tokens/episode, episodes/condition, multiplied out over the factorial + cross-play
+ seeds, against a stated GPU-hour ceiling. Scope the paper from that number
rather than discovering it mid-project.

> RESPONSE:

### M4. The scaled-down regime may not exhibit the phenomenon

At 1.5B–4B, the defender may be too weak for benign task success to clear an
interpretable floor (the proposal's own stop rule), and a 1.5B–4B *attacker* may
be unable to construct genuinely memory-dependent long-horizon strategies — so
**H1**'s "memory x online learning is super-additive" could fail to register
because the models cannot express it, not because it is false.

**Fix:** add an explicit early check that the effect of interest survives
scale-down, and state now what a null at this scale does and does not mean.

> RESPONSE:

### M5. AgentDojo may not have enough per-episode injection decision points

The attacker is (correctly, for safety) restricted to benchmark-sanctioned text
injections at known insertion points. If a typical AgentDojo task has one or two
injection points, then **C1-H vs C0** is a weak contrast and the horizon/credit
factors are close to dead on arrival.

**Fix:** measure the injection-opportunity distribution across the chosen suite
in week 1, before committing. If shallow, pick or construct a different
environment and say so.

> RESPONSE:

### M6. The matched-utility endpoint is fragile

"Compare only at checkpoints within 5 pp BTSR of base" assumes such checkpoints
exist for every condition. If the fully capable attacker drives the defender into
a utility-destroying regime and no checkpoint clears the floor, the primary
endpoint is *undefined* for that condition.

**Fix:** specify the Pareto-frontier fallback now, not just the ideal case.

> RESPONSE:

### M7. "Cycling" needs an operational test and a power analysis

"Non-monotonic dominance patterns that repeat across checkpoints" — with 4–6
checkpoints per side and 3 seeds, separating genuine cycling from noise is hard,
and the down-selection from all checkpoints to 4–6 for the grid reintroduces a
researcher degree of freedom.

**Fix:** pre-register a log-spaced-by-interaction checkpoint schedule and the
down-selection rule; power-analyze how many checkpoints x seeds are needed to
claim cycling at all. If infeasible on budget, narrow to forgetting (easier to
detect) and mark cycling exploratory.

> RESPONSE:

### M8. H4 (credit assignment) probably cannot be isolated online

"Holding trajectories and attacker capabilities fixed, does delayed credit
explain the long-horizon advantage?" In an online loop the credit signal changes
the policy which changes the trajectories; the stated controls (same raw
outcomes, same budget) do not fix this.

**Fix:** reformulate H4 as an offline / fixed-trajectory experiment (same logged
data, swap only the advantage estimator, measure sample efficiency to a target),
or move it out of the confirmatory set and label it exploratory.

> RESPONSE:

---

## Smaller issues

### S1. "Super-additive" (H1) is undefined on a scale
Interaction on probability vs. odds/logit gives different answers for a binary
outcome. Pre-specify the scale and the interaction test (the mixed-effects
logistic model already mentioned is the natural home).

> RESPONSE:

### S2. Worst-case ASR as primary metric is high-variance
The CI on a maximum over a registered attacker population is wide. Consider a
pre-registered upper quantile (e.g. 90th-percentile ASR) as primary with
worst-case as secondary, or explicitly budget seeds for the max.

> RESPONSE:

### S3. Base defender starting point is unspecified
Starting from a model already RLHF'd for injection resistance leaves small
headroom; starting from a raw instruction model makes benign utility the binding
constraint. Specify it.

> RESPONSE:

### S4. "Verifier ambiguity" as a pre-declared failure category
Slightly undercuts the executable-verifier-primary stance. Tighten verifier
definitions in the pilot so this is rare rather than a taxonomy bucket.

> RESPONSE:

### S5. Self-play literature missing from the RQ framing
Position H2/H3 explicitly against fictitious self-play, PSRO, PBT, and
strategy-cycling results, and say what is different in the LLM-agent case
(semantic strategies, cross-episode memory, discrete injection points, the
utility constraint). Otherwise the response is "known result."

> RESPONSE:

### S6. Pilot Week 1 is 2–3 weeks of real work
Read both papers deeply, compatibility sheet, domain choice, freeze splits,
threat model, deterministic adapter + smoke test. Either pad the pilot to 8–10
weeks or cut Week 1's scope.

> RESPONSE:

### S7. BrowserGym
Flagged optional, which is right, but even "if compute permits" invites scope
creep. For a first paper on this hardware, consider cutting the mention entirely.

> RESPONSE:

### S8. OPAL section
Reads slightly as justifying this project to build infra for a paper already
planned. Fine internally; delete before any of it migrates into the paper.

> RESPONSE:

---

## What to keep (do not water down)

- Raw vs. shaped reward separation.
- Executable-verifier primacy with stratified manual audit.
- Three-mode memory evaluation and train/test store isolation.
- The "claims to avoid" section.
- Pre-registration + Holm correction.
- Stop rules and the pilot gate.

---

## Verdict

Proceed to the pilot — the structure is right and the gate genuinely de-risks it
— but do three pieces of week-0 pre-work first:

1. Confirm ARLAS / Evo-Attacker code status, and write the capability-delta +
   expected-finding sentences (M1, M2).
2. Produce a worked compute budget and scope the paper from it (M3).
3. Write a self-contained reference spec so the study does not depend on either
   upstream repo (M2).

Frame the target as measurement / evaluation methodology from the start; let the
pilot *raise* the ambition to a main-conference gap-plus-mitigation story rather
than assuming it.
