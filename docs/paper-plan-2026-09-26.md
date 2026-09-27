# Paper plan — memory × adaptation and hidden historical vulnerability

**Date:** 2026-09-26
**Status:** Superseded working draft. The decisions from this plan have been
folded into `docs/research-protocol-v0.3.md`; retain this file as the dated
design history.
**Inputs:** revised proposal v0.2, protocol v0.2, proposal review
(2026-09-07), Week 0 feasibility log, session summary 2026-09-24.

---

## 1. The question

> Does persistent cross-episode attack memory interact with online adaptation
> to expose historical defender vulnerabilities that contemporary self-play
> evaluation misses?

The question contains two claims that must be tested in order, because the
second is undefined if the first is false:

- **C1 — the phenomenon (measurement).** In adversarial co-training of an
  LLM tool-use agent, the attack success rate a defender checkpoint shows
  against its *contemporary* attacker underestimates its success rate against
  *historical* attackers. Call the difference the **hidden vulnerability gap**.
- **C2 — the mechanism (causal, primary contribution).** An attacker that
  combines persistent cross-episode memory with online adaptation recovers more
  of that hidden vulnerability than the additive combination of memory alone
  and adaptation alone, at matched interaction budget.
- **C3 — the training consequence (secondary).** Placing the memory +
  adaptation attacker *inside* the co-training loop changes the defender's
  hidden vulnerability gap relative to an adaptation-only attacker. This
  hypothesis is two-sided: rehearsal could shrink the gap, and memory-driven
  overfitting could widen it.

## 2. What the paper is — and is not

**One-sentence pitch.** Self-play curves in LLM-agent security training report
robustness against the attacker the defender just beat. We show how much
that hides, and that an attacker which both *remembers* and *learns* is the
thing that finds what was hidden.

**It is:** a controlled measurement paper with a single pre-registered causal
contrast (a 2 × 2 memory × adaptation factorial) run on a fixed set of
defender checkpoints.

**It is not:**
- a claim that self-play forgets (known — fictitious self-play, PSRO, league
  training);
- an ARLAS or Evo-Attacker reproduction (both are references, not targets);
- a horizon or credit-assignment paper. H1b, H4a/b, the C0–C4 ladder, and
  cycling are **dropped** from this paper (see §11);
- a new defense (a mitigation appears only as the conditional C3 result).

**Why this is novel if it holds.** Prior work shows (a) self-play forgets and
(b) adaptive attackers break static defenses. What is untested is the
*temporal* version in LLM agents: vulnerabilities the training process
itself once exposed and then stopped measuring. The specific bet is that
memory alone replays old attacks that no longer fit the current defender, and
adaptation alone rediscovers only what is near its current policy; the two
together retrieve an old strategy family and adapt it to the current
defender. That is a falsifiable interaction, not a combination claim.

## 3. Formal definitions (freeze these)

Let one co-training run produce defender checkpoints $D_0,\dots,D_J$ and
attacker checkpoints $A_0,\dots,A_J$ on a fixed interaction-count schedule,
where $A_j$ is the attacker the defender faced when $D_j$ was saved.

All ASRs are measured on the **sealed held-out (user task, injection goal)
pairs** $\mathcal{T}_{test}$. Neither policy is trained on these pairs, and
the memory never writes to them.

| Symbol | Name | Definition |
|---|---|---|
| $c_j$ | Contemporary ASR | $\mathrm{ASR}(D_j, A_j)$: what a self-play curve reports |
| $s_j$ | Static-benchmark ASR | $\mathrm{ASR}(D_j, \text{AgentDojo built-in attacks})$: what a benchmark table reports |
| $h_j$ | Historical ASR | $\max_{k \le j} \mathrm{ASR}(D_j, A_k)$ over the registered checkpoint set |
| $G_j$ | Hidden vulnerability gap | $h_j - c_j$ (absolute ASR points) |
| $e_j(m,\ell)$ | Audit exposure | $\mathrm{ASR}(D_j, \text{audit attacker}_{m,\ell})$ after a fixed audit budget $B$ |

**Primary C1 estimand:** mean $G_j$ across registered checkpoints $j \ge 1$,
with a task-pair-clustered bootstrap 95% CI.
**Primary C2 estimand:** the $M \times L$ interaction coefficient on the
log-odds scale in the model in §8. Report the absolute-risk interaction
$e(1,1) - e(1,0) - e(0,1) + e(0,0)$ alongside it for interpretation.
**Secondary:** the recovered share $\big(e_j(m,\ell) - c_j\big)/G_j$, reported
only where $G_j \ge$ SESOI (a ratio is unstable when its denominator is
small); and the novel exposure, meaning audit successes on pairs where
$\max_{k\le j}$ historical cross-play failed.

**Utility guardrail (unchanged from protocol v0.2):** a defender checkpoint is
eligible only if its held-out benign task success rate (BTSR) is within 5
absolute points of the untrained defender. Ineligible checkpoints are
reported as `utility-infeasible` and are never swapped out after the fact.

## 4. Experimental design

### 4.1 Stage 1 — Reference co-training run (produces the objects to audit)

ARLAS-style alternating co-training, defined by this repository and
independent of upstream code:

- **Defender:** Qwen3-4B + LoRA adapter "D". Reward per attacked episode:
  $r_D = u \cdot (1 - s)$, where $u$ = utility verifier and $s$ = security
  verifier. Each defender block also includes benign episodes, with
  $r_D = u$, to hold BTSR.
- **Attacker:** Qwen3-4B + LoRA adapter "A", sharing one 4-bit base with
  the defender through an adapter switch (the Week 0 runs measured ~8.4 GB
  peak for inference, so both adapters fit). Input: user-task prompt,
  injection goal, and injection-vector identity. Output: one injection text
  per visible vector, or `NOOP`. Reward $r_A = s$.
  The attacker reads no semantic memory in Stage 1.
- **Opponent sampling:** **latest-opponent** (pure self-play) in the pilot.
  See decision D2 for whether the ARLAS population variant runs as well.
- **Warm start:** attacker SFT on development-split successful injections
  from the static screen plus AgentDojo's built-in templates. The reason is
  sparsity: at 11% base ASR and GRPO group size 2, only
  $1-(0.89^2+0.11^2)\approx 20\%$ of groups carry any gradient. With group
  size 4 it is ≈37%. **Use G = 4 for the attacker and G = 2 for the
  defender.**
- **Schedule:** 5 rounds × (attacker block → defender block). Save both
  adapters at the end of each round on a fixed interaction count. Register 4
  defender and 4 attacker checkpoints for cross-play: rounds {0, 1, 3, 5}.
  This is log-spaced and frozen before training.
- **Archive (always on, used only in Stage 2):** every training episode
  appends an immutable record to the attack archive (schema in §5).
  Recording never changes Stage 1 behaviour.

### 4.2 Stage 2a — Cross-play (tests C1)

Run all 16 pairs $(D_j, A_k)$ of the 4 × 4 registered matrix on
$\mathcal{T}_{test}$ with frozen weights. Also run $s_j$ for each $D_j$ and
BTSR for each $D_j$ on held-out benign tasks.

- The diagonal gives $c_j$; the lower triangle gives $h_j$ and $G_j$; the
  upper triangle gives forward transfer (descriptive).
- **Gate G-C1:** if the mean $G_j$ CI lies entirely below the SESOI (proposed:
  5 absolute ASR points), C2 is uninterpretable. Branch per §10.

### 4.3 Stage 2b — The memory × adaptation audit (tests C2)

For each audited defender checkpoint $D_j$, $j \in \{1, 3, 5\}$, which is
frozen, start from its contemporary attacker $A_j$ and give each of four
audit attackers the **same budget $B$** of environment interactions on
**audit-train pairs** (training-split tasks), then evaluate on
$\mathcal{T}_{test}$:

| Cell | Memory $M$ | Adaptation $L$ | What happens during the $B$ audit interactions |
|---|---|---|---|
| M0L0 | none | frozen $A_j$ | nothing (identical to $c_j$; costs no budget) |
| M1L0 | archive from rounds $\le j$ + audit writes | frozen $A_j$ | outcomes written to memory; weights unchanged |
| M0L1 | none | GRPO on $A_j$ | weights updated; outcomes discarded after the update |
| M1L1 | archive + audit writes | GRPO on $A_j$ | both |

At evaluation both memory and weights are frozen. The M1 archive contains
**only rounds ≤ j** (no future leakage) and **only training-split pairs**.

Why this design (a change from the proposal's co-training factorial):

1. **Clean causal contrast.** The defender is held fixed, so only attacker
   capabilities vary. In a co-training factorial the defender co-evolves
   with each attacker, which confounds "the attacker exposes more" with "the
   defender became different".
2. **Directly answers the question.** "Expose vulnerabilities that
   contemporary evaluation misses" means comparing $e_j(m,\ell)$ against
   $c_j$, with $h_j$ as ground truth.
3. **~4× cheaper.** Four co-training runs per seed are replaced by one
   co-training run plus short audits. The saved budget buys the cross-play
   ground truth.

**Circularity control.** M1L0 could win trivially by replaying the archive's
old successful injections verbatim. Two protections:
(a) the archive holds training-split pairs and evaluation uses held-out pairs,
so no verbatim replay exists for the evaluated task;
(b) every successful audit injection is classified by nearest-neighbour
similarity to the archive as **replay** (≥ threshold) or **recombination /
novel**. The threshold is frozen on the dev split. The C2 story requires the
M1L1 excess to sit mainly in recombination / novel.

### 4.4 Stage 3 — Training consequence (tests C3; conditional)

This stage runs only if G-C1 passes and budget remains. It adds one extra
co-training run in which the attacker reads the archive (M1L1-in-loop), then
repeats cross-play and compares mean $G_j$ against Stage 1.
Two-sided test. This becomes the paper's mitigation result, or its warning
result.

## 5. Memory specification

- **Record:** `{split, user_task_id, injection_goal_id, vector_id, injection_text,
  strategy_tag, security, utility, defender_ckpt, round, failure_reason}`.
- **strategy_tag:** a closed taxonomy frozen on dev, e.g. authority
  impersonation, task-continuation framing, tool-output spoofing,
  urgency/threat, delimiter/format break, benign-cover request, other.
  It is assigned by a deterministic rubric prompt with a manual audit of 50
  entries. Tags are for analysis only and never feed rewards.
- **failure_reason:** derived from the trace (defender ignored; defender
  refused; tool error; partial execution; task hijacked).
- **Retrieval:** a deterministic rule, frozen on dev. Take the top-k = 4
  records with the same injection goal, ranked by embedding similarity of the
  user-task prompt. Include up to 2 successes and 2 most-recent failures
  against the latest checkpoint seen. Cap the memory block at 800 tokens.
- **Isolation:** never writes from validation/test pairs; the archive file is
  append-only, and each read is hashed into the ledger.
- **Memory expressivity gate (must pass before Stage 2b):** on dev pairs, a
  frozen attacker with memory versus without must show (i) a changed
  strategy-tag distribution (χ² or total-variation distance > frozen
  threshold) and (ii) a measurable ASR difference in either direction. If the
  4B attacker ignores memory, C2 cannot be tested at this scale. Report this
  as a scale-validity failure, not a null.

## 6. Environment and splits

**The horizon gate no longer blocks this paper.** In AgentDojo the attack is
written before the episode for a (task, goal) pair. The attacker makes one
decision per visible vector, and all adaptation happens *across* episodes —
exactly the axis this question studies. Slack's median depth of 1 is
therefore acceptable.

**The binding constraint is pair count.** Slack has 21 user tasks × 5
injection goals, and only 20 × 5 are usable after the task-20 hold-out. After
a train / val / test split, $\mathcal{T}_{test}$ would hold ~30 pairs,
which is too few to detect an interaction.

**Revised suite-selection criteria** (replaces the depth-based shortlist in
the 2026-09-24 next actions):

1. Qwen3-4B BTSR ≥ 50% and valid-tool-call rate ≥ 90% on a frozen 20-task
   benign screen (same gates as Slack).
2. Static ASR between 5% and 80% with ≥ 3 injection goals above 0%. This
   removes Slack's pattern where one goal produced 8 of the 11 successes.
3. The most (user task × injection goal) pairs, after (1) and (2).
4. Verifier sanity: ≤ 1 verifier exception per 100 episodes. This is the
   same narrow handling as the Slack `KeyError`.

Run the read-only inventory (task and goal counts per suite, vectors per
task) for Workspace, Banking, and Travel first. Then screen at most two
suites against (1)–(2). Workspace is the likely winner on pair count if
Qwen3-4B clears competence there; confirm this with the inventory before
relying on it.

**Splits** (by user task, stratified by injection goal; frozen in a new
manifest before any learning):
- 50% train: co-training, archive writes, audit-train;
- 15% validation: checkpoint eligibility (BTSR floor) and threshold tuning;
- 35% sealed test: $\mathcal{T}_{test}$, touched only in Stages 2a/2b/3.
All injection goals appear in every split. A held-out-goal analysis is
exploratory.

**Standalone injection-goal gate repair.** Replace the n = 1 standalone check
with 5 sampled standalone trials per goal (T = 0.7) on a *new* manifest. A goal
passes at ≥ 3/5. Preserve the original Slack 3/5 result unchanged.

## 7. Budget — measured values, and the ceiling that actually binds

Measured on the 4090 (Slack direct-attack screen, 105 runs):
**~8.3k counted tokens and ~5.1 s of generation per defender episode.**
Adding an attacker call (~1.5k prompt incl. memory + ≤256 output) gives a
planning figure of **~10.3k counted tokens per attacked episode**.

At that rate the **30 M-token ceiling allows ~2,900 episodes**. It binds
long before the 5,000-episode or 150 GPU-hour ceilings: rollout is ~6–8
GPU-hours per 3k episodes, and QLoRA updates on ≤ 4k-token trajectories add
a small multiple of that.

One-seed pilot, sized to the ceiling:

| Block | Episodes | Notes |
|---|---:|---|
| Suite screen (benign + static) on new suite | 300 | includes repaired standalone-goal trials |
| Memory-expressivity + learning-responsiveness gates | 150 | dev pairs only |
| Stage 1 co-training (5 rounds) | 880 | per round: attacker 24 prompts × G4 = 96; defender 24 × G2 attacked + 16 × G2 benign = 80 |
| Stage 2a cross-play 4 × 4 on ~30 test pairs | 480 | + included BTSR/static below |
| BTSR + static-benchmark ASR per defender ckpt | 240 | 4 ckpts × (30 benign + 30 static) |
| Stage 2b audit, 3 ckpts × 3 active cells × (B = 48 + 30 eval) + M0L0 eval | 792 | $B$ is identical across cells |
| **Subtotal** | **2,842** | ≈ 29.3 M tokens |
| Evaluation share (2a + BTSR/static + 2b) | 1,512 (53%) | satisfies the ≥ 35% reserve |

**Consequences to accept or change (decision D3):**
- As scoped, this pilot is **directional, not confirmatory**. ~30 test pairs
  × 3 checkpoints gives an interaction CI that is only informative for large
  effects (roughly ≥ 10 absolute points). Replication (a second seed) and
  Stage 3 do **not** fit under 30 M tokens.
- The context cap in `configs/single_gpu_24gb.json` (2,048) is below
  measured episode length. The Slack screens already ran with 8,192. Amend the
  config to the measured p95 trajectory length and record the amendment date.

## 8. Statistical analysis plan

- **Unit of inference:** the (user task, injection goal) pair. Turns are
  never units.
- **C1:** mean $G_j$ with a pair-clustered bootstrap (10k resamples,
  resampling pairs jointly across checkpoints). Recompute the max over $k$
  inside every resample so the maximum's selection bias is carried into the
  CI.
- **C2:** mixed-effects logistic regression
  `success ~ M * L + (1 | user_task) + (1 | injection_goal) + (1 | checkpoint)`
  on audit-eval episodes. The primary test is the $M{:}L$ coefficient,
  one-sided (positive), α = 0.05. Report absolute-risk contrasts with bootstrap
  CIs. Stochasticity comes from attacker sampling (T = 0.7); defender
  decoding stays deterministic, as in Week 0.
- **Secondary (Holm-corrected as one family):** C1 against the static
  benchmark ($h_j - s_j$); M1L1 versus M0L0 main effect; novel-exposure rate
  for M1L1 versus M0L1.
- **Exploratory, labelled as such:** strategy-tag drift across rounds
  (which families the defender "forgets"), forward transfer, per-goal
  breakdowns, and C3.
- **Power:** after Stage 1, simulate the C2 test from the pilot's observed
  base rates *at the SESOI*, not at the observed effect, to size the Phase B
  confirmatory run.

## 9. Paper outline

**Working title options**
1. *What Self-Play Forgets: Memory and Adaptation Expose Hidden Historical
   Vulnerabilities in LLM Agent Defenders*
2. *Contemporary Robustness Is Not Robustness: Auditing Adversarially
   Co-Trained Tool-Use Agents with Remembering, Learning Attackers*

**Abstract skeleton (fill numbers after results):** Adversarial co-training
of LLM agents is typically evaluated against the current attacker or a static
benchmark. On AgentDojo with Qwen3-4B attacker and defender, contemporary ASR
understates historical worst-case ASR by [G] points. A 2 × 2 audit shows that
persistent cross-episode memory and online adaptation [interact / do not
interact]: together they recover [x]% of the hidden gap, versus [y]% and [z]%
alone, mostly via [recombined / replayed] strategies. We release the
checkpoint cross-play matrix and audit protocol.

**Sections**
1. Introduction — self-play curves are the standard progress signal; the
   temporal blind spot; the memory × adaptation bet; contributions.
2. Related work — (a) self-play non-transitivity and forgetting: fictitious
   self-play, PSRO, league training with exploiters; (b) adversarial RL for
   LLM agents: ARLAS; (c) memory-augmented and self-evolving attackers:
   Evo-Attacker, lifelong strategy-library jailbreakers, quality-diversity
   attack archives; (d) adaptive-attack evaluation of prompt-injection
   defenses. *Every citation must be verified from its primary source in the
   W1 literature matrix. Do not cite from this plan.*
3. Setting and definitions — threat model, $c_j, s_j, h_j, G_j, e_j$, the
   utility floor.
4. Method — reference co-training, archive, audit factorial, circularity
   controls.
5. Experimental setup — suite, splits, models, budgets, ledger.
6. Results
   - 6.1 C1: the hidden gap (cross-play heatmap; $c_j$ vs $s_j$ vs $h_j$).
   - 6.2 C2: the interaction (2 × 2 plot, logit + absolute; recovered share).
   - 6.3 Mechanism: replay vs recombination; strategy-family forgetting.
   - 6.4 Utility: BTSR per checkpoint, eligibility.
   - 6.5 (conditional) C3: memory in the loop.
7. Limitations — one suite, 4B scale, one co-training seed in the pilot,
   deterministic defender, text-only injections; a null is bounded to this
   envelope.
8. Broader impact — gated release of the archive; aggregate matrices public.

**Figures and tables**
- F1: pipeline diagram (co-training timeline → archive → audit cells).
- F2: 4 × 4 cross-play heatmap with the diagonal highlighted.
- F3: per-checkpoint bars: $s_j$, $c_j$, $h_j$, and the four audit cells.
- F4: 2 × 2 interaction plot with CIs.
- F5: stacked bars of replay / recombination / novel successes by cell.
- T1: security–utility at the BTSR floor per checkpoint.
- T2: compute ledger (episodes, tokens, GPU-h) per stage.

## 10. Outcome branches (pre-registered)

| Result | Paper |
|---|---|
| C1 ✓, C2 ✓ (interaction > 0, mostly recombination) | Full paper as outlined; add C3 in Phase B |
| C1 ✓, C2 ✗ (memory or adaptation alone suffices) | Measurement paper: "contemporary eval hides X points; here is which cheap audit recovers it" — still useful |
| C1 ✓, C2 only via replay | Report honestly: memory is an archive-replay audit, not a mechanism; weaker but publishable as workshop |
| C1 ✗ (no gap at 4B / latest-opponent) | No C2. Workshop negative result bounded to scale; or pivot to the population regime question |
| Memory-expressivity gate fails | Scale-validity failure; move attacker to a larger model on the 2-GPU machine before any claim |
| Defender utility collapses (no eligible ckpt) | Tune defender reward mix on validation, *new* manifest, before Stage 2 |

## 11. What changes relative to the existing proposal

| Proposal element | Status in this paper |
|---|---|
| H1 / RQ1a memory × learning | **Kept**, but run as an attacker-side audit on fixed defenders (§4.3) |
| H2 contemporaneous eval overstates robustness | **Kept** as C1 |
| H5 historical-mixture mitigation | Becomes conditional C3 |
| H1b horizon, C0/C1-H | **Dropped** (Slack's depth failure no longer matters) |
| H4a/H4b credit, C4 / Attack-Flow GRPO | **Dropped** (future work) |
| H3 capability-mixture generalization | **Dropped** |
| Cycling | **Dropped** (4 checkpoints cannot power it) |
| BrowserGym, OPAL section | **Dropped** from paper |
| Primary endpoint "worst-case held-out ASR at BTSR floor" | Replaced by $G_j$ (C1) and the $M{:}L$ interaction (C2), each still subject to the BTSR floor |

## 12. Decisions needed before protocol v0.3

- **D1. Adopt the audit framing** (§4.3) as the primary C2 design instead of
  a co-training factorial? *Recommended: yes.*
- **D2. Co-training regime.** Latest-opponent only (cheapest; most likely to
  show a gap), or also ARLAS population sampling (pre-empts the "strawman"
  review)? *Recommended: latest-opponent in the pilot; population regime as
  the first Phase B extension.*
- **D3. Token ceiling.** Keep 30 M (one-seed directional pilot, no C3), or
  amend before any learning, with written justification, to ~60 M (second
  seed + C3)? The ceiling was set from a 6k-token assumption that measurement
  replaced. Amending before outcomes is legitimate; amending after is not.
- **D4. SESOI** for $G_j$ and the interaction. *Proposed: 5 absolute ASR
  points.*
- **D5. Attacker base.** Same Qwen3-4B base with a separate adapter
  (recommended: memory fits, single load), or Qwen3-1.7B (weaker attacker, may
  fail memory expressivity)?
- **D6. Second machine.** Use the 2-GPU box to run audit cells in parallel
  with Stage 1? This helps wall-clock time, not the token ceiling.

## 13. Timeline (Ubuntu machine; weeks from protocol v0.3 freeze)

| Week | Work | Exit gate |
|---|---|---|
| 1 | Suite inventory (Workspace/Banking/Travel); literature matrix; freeze splits + v0.3 | suite chosen by §6 criteria |
| 2 | Benign + static screen on chosen suite; repaired standalone-goal check; archive + retrieval module; 25-episode verifier audit | competence, attackability, verifier gates |
| 3 | Attacker SFT warm start; learning-responsiveness (attacker vs frozen defender; defender vs frozen attacker); memory-expressivity gate | both gates |
| 4–5 | Stage 1 co-training, checkpoints at rounds {0,1,3,5} | BTSR eligibility on validation |
| 6 | Stage 2a cross-play → C1 readout | G-C1 |
| 7 | Stage 2b audit → C2 readout; replay/novel classification | — |
| 8 | Ledger reconciliation, power simulation, pilot report, go/no-go per §10 | Phase B decision |

## 14. Immediate next steps on Ubuntu

1. Answer D1–D6, then write `docs/research-protocol-v0.3.md` from this plan.
2. Parameterize `scripts/inventory_agentdojo_injections.py` to accept a suite
   name without a model manifest, and run it on Workspace, Banking, and Travel
   at v1.2.2. Record task and goal counts, which the current script does not
   emit directly.
3. Amend `configs/single_gpu_24gb.json`: context cap from measured trajectory
   p95; attacker group size 4; the ceiling from D3.
4. Start the literature matrix with the related-work axes in §9, including
   checking whether any prior work already audits co-training checkpoints
   with a memory-augmented attacker. That is the one result that would
   collapse the novelty claim.
