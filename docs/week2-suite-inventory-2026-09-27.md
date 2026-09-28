# Week 2 AgentDojo suite inventory

**Date:** 2026-09-27
**AgentDojo version:** 0.1.35 (`v1.2.2` suites)
**Mode:** read-only; no model inference

## Results

| Suite | User tasks | Injection goals | Visible vectors | Median per task | Sealed pairs | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Workspace | 40 | 14 | 14 | 1.0 | 196 | candidate |
| Banking | 16 | 9 | 4 | 1.0 | 54 | candidate |
| Travel | 20 | 7 | 13 | 1.5 | 49 | ineligible: below 50-pair minimum |

`Visible vectors` is the number of distinct vector identities. The full JSON
records report `visible_injection_vector_count` per user task and must not be
interpreted as intervention depth or a sequence of attacker decisions.

The deterministic prospective split uses user-task-level 50/15/35 allocation
with largest-remainder rounding. All injection goals are crossed with every
task in a partition, so every goal appears in every nonempty split.

## Frozen candidate decision

Workspace and Banking advance to development-only benign screens. Travel does
not advance because its registered split yields 49 sealed `(user task,
injection goal)` pairs; the protocol forbids relaxing the minimum after seeing
the inventory.

The two candidate manifests pin the Qwen3-4B model snapshot, tokenizer chat
template, package versions, generation limits, seed, complete task split, and
inventory hash. They contain no model outcomes. Static-attack manifests will be
frozen only after the benign candidate gate identifies which suites remain
eligible, and before any static inference.

## Inventory artifacts

- `docs/data/agentdojo-v1.2.2-suite-inventory/workspace.json`
  (`sha256:9a0983218d9c0ca5cbf044595acd23080d8bf39d508c1048d1490e1aea772798`)
- `docs/data/agentdojo-v1.2.2-suite-inventory/banking.json`
  (`sha256:81cb9e281c93e62047473b57671edc3aed5f64b7c1e000189b81b2ef717b8420`)
- `docs/data/agentdojo-v1.2.2-suite-inventory/travel.json`
  (`sha256:e1576c0990e8d8c0fa9ed94e5408ac0aa687b55aba366a20ac8dcf40ec7b1ab1`)
