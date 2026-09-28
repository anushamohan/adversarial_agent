# Repository agent guidance

## Required research startup

For work involving the paper, AgentDojo, experiments, analysis, research design,
or result interpretation, read these files before acting:

1. `.codex/skills/cotabreak-research/SKILL.md`
2. `docs/project-status.md`

Treat `docs/research-protocol-v0.3.md` as the authoritative current protocol and
`docs/weekly-execution-plan-v0.3.md` as its execution sequence.
`docs/paper-plan-2026-09-26.md` is design history and is explicitly superseded
where it conflicts with protocol v0.3.

Do not describe a run as passing merely because it has a promising headline
metric. Apply its complete registered gate, including verifier integrity,
capability, utility, and trace-completeness checks. Preserve raw artifacts and
regenerate derived analysis into a new location unless replacement was
explicitly requested.

After a material experiment, protocol decision, or evidence-changing code
change, update `docs/project-status.md`. Do not update it for ordinary questions
that do not change project state.

## Project session summaries

When the user asks to summarize, checkpoint, hand off, pause, resume, or transfer
work between coding agents or computers, use the globally installed
`session-summary` skill. Generated summaries always belong to the active
repository under `docs/session-summaries/`; never store project summaries in the
global skill directory.

Do not create a session summary after every ordinary response. Create or update
one when requested, before an intended handoff, or when a long-running task is
about to lose important working context.

This guidance applies to the entire repository.
