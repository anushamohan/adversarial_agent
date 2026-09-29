# Prospective Qwen3-8B model-scale amendment

**Date:** 2026-09-29
**Timing:** Frozen before any Qwen3-8B AgentDojo task outcome
**Status:** Development-screen amendment; pre-training

## Decision

Use Qwen3-8B for every remaining model-based CoTA-Break experiment. Preserve
all Qwen3-4B artifacts and results as historical feasibility evidence; do not
reinterpret or replace them.

The frozen model configuration is:

- model: `Qwen/Qwen3-8B`;
- model and tokenizer revision:
  `b968826d9c46dd6066d109eabc6255188de91218`;
- 4-bit NF4 weights with double quantization and BF16 compute;
- thinking disabled, deterministic decoding, at most 256 new tokens per call;
- 8,192-token handled per-call context ceiling;
- seed 17 for the development screen;
- official model files cached under
  `/data/adversarial_agent/huggingface`, never the space-constrained root disk.

The Qwen3-8B tokenizer chat-template SHA-256 is
`a55ee1b1660128b7098723e0abcd92caa0788061051c62d51cbe87d9cf1974d8`.

## Rationale

Qwen3-4B passed the earlier Slack benign screen but failed the complete attack
gate. It subsequently achieved 7/20 Workspace utility with 17/28 valid tool
calls and 2/8 Banking utility with 8/8 valid calls. Scaling within the same
model family is the smallest prospective change that directly tests whether
the remaining blocker is model capacity while holding the benchmark,
tool schema, parser, prompts, decoding, splits, and decision thresholds fixed.

## Frozen sequence and gates

1. Verify the immutable snapshot and NF4 loader from committed code and record
   peak VRAM. This is a hardware feasibility check, not a competence result.
2. Run all 20 frozen Workspace development tasks.
3. Advance only if benign utility is at least 50%, valid tool calls are at least
   90%, traces are complete, and verifier/infrastructure integrity passes.
4. If Workspace advances, freeze and run its development-only static attack and
   five standalone trials per injection goal, then manually audit at least 25
   stratified episodes.
5. Screen Banking only if Workspace does not complete the full suite-selection
   gate or a second candidate is required. Travel remains ineligible because it
   provides only 49 sealed pairs.
6. Do not run SFT, RL, validation, or sealed evaluation until the existing
   protocol gates authorize them.

## What does not change

This amendment does not change C1 or C2, the validation-only historical-attacker
selection rule, the five-point SESOI, the one-sided confidence rule, the
50-sealed-pair minimum, the task-level split, verifier attribution, independent
C2 adaptation seeds, or the ceilings of 5,000 episodes, 30 million counted
tokens, and 150 GPU-hours. If 8B profiling threatens those ceilings, reduce or
drop conditional C2 before weakening protected C1 evaluation.

Inference fit does not establish training fit. Before any adapter warm start,
measure one representative 8K-context QLoRA forward/backward/optimizer step
with the registered adapter configuration and required VRAM margin.
