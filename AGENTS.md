# Repository agent guidance

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
