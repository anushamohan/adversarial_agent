# Milestone 0 checklist

Complete this checklist on the 24 GB NVIDIA machine before beginning SFT or RL.

## A. Upstream artifact and novelty record

- [ ] Record the current ARLAS paper/project URL, code availability, checkpoint
      availability, license, base models, data budget, and update schedule.
- [ ] Record the same information for Evo-Attacker.
- [ ] Create the self-play literature matrix covering fictitious self-play,
      PSRO, population training, forgetting, and cycling.
- [ ] Confirm that the proposal's capability delta and expected mechanism remain
      unsupported by a directly equivalent prior experiment.
- [ ] Record every reference-component deviation in a fidelity matrix.

## B. GPU and software profile

- [ ] Record GPU name, VRAM, driver, CUDA, operating system, Python, RAM, and
      available disk.
- [ ] Record PyTorch CUDA availability and supported bfloat16 behavior.
- [ ] Pin compatible Transformers, PEFT, TRL, Accelerate, bitsandbytes, and
      AgentDojo versions from current primary documentation.
- [ ] Run one 4-bit model load and generation with `Qwen/Qwen3-1.7B`.
- [ ] Run one QLoRA forward, backward, and optimizer step.
- [ ] Record peak VRAM, input/output tokens, and wall time.

## C. Environment suitability

- [ ] Inventory candidate AgentDojo suites and version identifiers.
- [ ] Run 20–30 representative benign episodes per candidate configuration.
- [ ] Record BTSR, valid tool-action rate, episode length, and model tokens.
- [ ] Record the full distribution of eligible injection opportunities and
      distinct attacker decisions.
- [ ] Select a suite only if benign competence, attackability, intervention
      depth, and executable verifier quality support the planned claims.

## D. Worked budget

- [ ] Replace the 6,000-token planning assumption with measured episode values.
- [ ] Estimate training episodes, optimizer steps, and GPU-hours per factorial
      cell.
- [ ] Calculate cross-play episodes from checkpoints × attackers × task blocks ×
      repeats.
- [ ] Reserve at least 35% for evaluation and cross-play.
- [ ] Confirm the total remains under 5,000 episodes, 30 million tokens, and 150
      GPU-hours.
- [ ] Reduce scope according to the proposal's priority order if any ceiling is
      exceeded.

## E. Freeze before Milestone 1

- [ ] Name the attacker and defender base models.
- [ ] Define `online learning` as between-episode-block weight updates.
- [ ] Freeze the reference update ratio, population sampling rule, checkpoint
      counts, and preliminary reward definitions.
- [ ] Freeze initial competence, attackability, memory-expressivity, and verifier
      thresholds.
- [ ] Write a dated Milestone 0 decision: proceed, repair, change environment,
      reduce scope, or stop.

## Exit statement

Milestone 0 passes only when the reference is independently reproducible, the
novelty thesis survives the literature check, the environment can express the
planned contrasts, and the measured design fits all compute ceilings.

