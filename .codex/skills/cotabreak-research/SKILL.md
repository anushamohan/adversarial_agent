---
name: cotabreak-research
description: Execute and review CoTA-Break AgentDojo research, experiments, analysis, and paper claims in this repository while preserving preregistration, evidence provenance, and publication-valid inference.
---

# CoTA-Break research

Use this skill for research planning, experiment implementation or execution,
result analysis, paper writing, and decisions about whether evidence supports a
claim in this repository.

## Establish current state

Read `docs/project-status.md` first. Read the latest indexed session summary only
when historical handoff detail is needed.

Route deeper work as follows:

- Protocol, hypotheses, estimands, or claims: read
  `docs/research-protocol-v0.3.md`.
- Sequencing or next actions: read `docs/weekly-execution-plan-v0.3.md`.
- Week 0 provenance: read `docs/week0-reanalysis-2026-09-27.md` and the frozen
  manifests under `configs/manifests/`.
- Earlier rationale: consult `docs/paper-plan-2026-09-26.md` only as superseded
  design history.

## Preserve research validity

- Begin experiments from committed code and a frozen manifest with immutable
  model, package, prompt, split, decoding, and seed identifiers.
- Keep development, validation, and sealed-test data mechanically separated.
- Preserve raw traces. Write reanalysis to a new location and record the code
  revision, manifest hash, artifact location, and exclusions.
- Keep utility, security, invalid action, invalid verifier, refusal, and
  infrastructure outcomes separate. A recovered verifier exception invalidates
  the registered run unless the protocol explicitly defines another treatment.
- Distinguish feasibility evidence from publication-valid evidence. Apply every
  registered gate before describing a run as passing.
- Do not change endpoints, SESOI, eligibility rules, budgets, or stop rules after
  inspecting relevant outcomes. Record prospective amendments before running
  affected experiments.
- Treat a one-seed or one-policy pilot as directional. Do not infer training-run
  variability from repeated task pairs.

## Work toward a publishable paper

Prioritize measurement correctness, identifiable estimands, clean baselines,
independent replication, and reproducible artifacts over adding mechanisms.
Resolve blockers listed in `docs/project-status.md` before expensive training.
For statistical changes, state the estimand, inference unit, selection process,
and source of independent replication explicitly.

After material work, update `docs/project-status.md` with the evidence produced,
the decision it supports, unresolved blockers, and the next executable action.
Use the repository's session-summary workflow only for handoffs or requested
checkpoints.
