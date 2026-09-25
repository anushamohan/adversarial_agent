#!/usr/bin/env python3
"""Measure Qwen generation and an optional single QLoRA update."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--qlora-step", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable; run this probe where the GPU is exposed")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.reset_peak_memory_stats()

    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        revision=args.revision,
        quantization_config=quantization,
        device_map={"": 0},
        low_cpu_mem_usage=True,
    )
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None
    load_seconds = time.perf_counter() - started

    messages = [{"role": "user", "content": "Reply with exactly: QWEN_PROBE_OK"}]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    input_tokens = int(inputs["input_ids"].shape[-1])
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=args.max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
        )
    generation_seconds = time.perf_counter() - started
    output_ids = output[0, input_tokens:]

    result: dict[str, object] = {
        "model": args.model,
        "revision": args.revision,
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "bf16_supported": torch.cuda.is_bf16_supported(),
        "load_seconds": load_seconds,
        "generation_seconds": generation_seconds,
        "input_tokens": input_tokens,
        "output_tokens": int(output_ids.shape[-1]),
        "completion": tokenizer.decode(output_ids, skip_special_tokens=True).strip(),
    }

    if args.qlora_step:
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=False
        )
        model = get_peft_model(
            model,
            LoraConfig(
                r=16,
                lora_alpha=32,
                lora_dropout=0.05,
                bias="none",
                task_type="CAUSAL_LM",
                target_modules="all-linear",
            ),
        )
        trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
        optimizer = torch.optim.AdamW(trainable, lr=2e-4)
        training_inputs = tokenizer(
            "User: Complete this tool-safety probe.\nAssistant: QWEN_PROBE_OK",
            return_tensors="pt",
        )
        training_inputs = {
            key: value.to(model.device) for key, value in training_inputs.items()
        }
        labels = training_inputs["input_ids"].clone()
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        loss = model(**training_inputs, labels=labels).loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        result["qlora"] = {
            "loss": float(loss.detach().cpu()),
            "step_seconds": time.perf_counter() - started,
            "trainable_parameters": sum(parameter.numel() for parameter in trainable),
            "tokens": int(labels.numel()),
        }

    result["peak_vram_mib"] = torch.cuda.max_memory_allocated() / (1024**2)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
