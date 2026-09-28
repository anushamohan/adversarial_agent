"""Direct Transformers adapter for running Qwen inside AgentDojo."""

from __future__ import annotations

import json
import hashlib
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionCall, FunctionsRuntime
from agentdojo.types import (
    ChatAssistantMessage,
    ChatMessage,
    get_text_content_as_str,
    text_content_block_from_string,
)

from cotabreak.tool_calling import parse_tool_call


@dataclass(frozen=True)
class GenerationUsage:
    input_tokens: int
    output_tokens: int
    wall_time_seconds: float
    peak_vram_mib: float


class QwenTransformersLLM(BasePipelineElement):
    """AgentDojo pipeline element backed by an in-process Qwen model."""

    def __init__(
        self,
        model_id: str = "Qwen/Qwen3-0.6B",
        *,
        revision: str = "main",
        max_context_tokens: int = 8192,
        max_new_tokens: int = 256,
        seed: int = 17,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is required for the Week 0 AgentDojo probe")

        self.name = model_id.replace("/", "--")
        self.model_id = model_id
        self.requested_revision = revision
        self.max_context_tokens = max_context_tokens
        self.max_new_tokens = max_new_tokens
        self.seed = seed
        self.usage: list[GenerationUsage] = []
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        self.chat_template_sha256 = hashlib.sha256(
            self.tokenizer.chat_template.encode()
        ).hexdigest()
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            revision=revision,
            torch_dtype=torch.bfloat16,
            device_map={"": 0},
            low_cpu_mem_usage=True,
        )
        self.resolved_revision = getattr(self.model.config, "_commit_hash", None)
        self.model.generation_config.temperature = None
        self.model.generation_config.top_p = None
        self.model.generation_config.top_k = None
        self.model.eval()

    @property
    def usage_summary(self) -> dict[str, Any]:
        records = [asdict(item) for item in self.usage]
        return {
            "calls": len(records),
            "input_tokens": sum(item["input_tokens"] for item in records),
            "output_tokens": sum(item["output_tokens"] for item in records),
            "wall_time_seconds": sum(item["wall_time_seconds"] for item in records),
            "peak_vram_mib": max(
                (item["peak_vram_mib"] for item in records), default=0.0
            ),
            "generations": records,
        }

    @staticmethod
    def _function_specs(runtime: FunctionsRuntime) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": function.name,
                    "description": function.description,
                    "parameters": function.parameters.model_json_schema(),
                },
            }
            for function in runtime.functions.values()
        ]

    def _format_messages(
        self, messages: Sequence[ChatMessage], runtime: FunctionsRuntime
    ) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        for message in messages:
            role = message["role"]
            content = get_text_content_as_str(message["content"] or [])
            if role == "tool":
                error = message.get("error")
                payload = {"error": error} if error else {"result": content}
                content = json.dumps(payload)
            formatted_message: dict[str, Any] = {"role": role, "content": content}
            if role == "assistant" and message.get("tool_calls"):
                formatted_message["content"] = content.split("<tool_call>", 1)[0].strip()
                formatted_message["tool_calls"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": call.function,
                            "arguments": call.args,
                        },
                    }
                    for call in message["tool_calls"] or []
                ]
            formatted.append(formatted_message)
        return formatted

    def _generate(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> str:
        import torch

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_tokens = int(inputs["input_ids"].shape[-1])
        if input_tokens > self.max_context_tokens:
            import httpx
            from openai import BadRequestError

            message = (
                f"Prompt has {input_tokens} tokens, exceeding the registered "
                f"{self.max_context_tokens}-token context ceiling"
            )
            raise BadRequestError(
                message,
                response=httpx.Response(
                    400,
                    request=httpx.Request("POST", "http://localhost/cotabreak"),
                ),
                body={
                    "code": "context_length_exceeded",
                    "message": message,
                    "param": "max_context_tokens",
                    "type": "invalid_request_error",
                },
            )
        inputs = {key: value.to(self.model.device) for key, value in inputs.items()}

        torch.manual_seed(self.seed + len(self.usage))
        torch.cuda.manual_seed_all(self.seed + len(self.usage))
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        with torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        elapsed = time.perf_counter() - started
        output_ids = generated[0, input_tokens:]
        self.usage.append(
            GenerationUsage(
                input_tokens=input_tokens,
                output_tokens=int(output_ids.shape[-1]),
                wall_time_seconds=elapsed,
                peak_vram_mib=torch.cuda.max_memory_allocated() / (1024**2),
            )
        )
        return self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    def query(
        self,
        query: str,
        runtime: FunctionsRuntime,
        env: Env | None = None,
        messages: Sequence[ChatMessage] | None = None,
        extra_args: dict[str, Any] | None = None,
    ) -> tuple[str, FunctionsRuntime, Env, Sequence[ChatMessage], dict]:
        message_history = [] if messages is None else messages
        query_env = EmptyEnv() if env is None else env
        query_args = {} if extra_args is None else extra_args
        completion = self._generate(
            self._format_messages(message_history, runtime), self._function_specs(runtime)
        )
        parsed = parse_tool_call(completion)
        tool_calls = (
            [FunctionCall(function=parsed.function, args=parsed.arguments)]
            if parsed is not None
            else []
        )
        output = ChatAssistantMessage(
            role="assistant",
            content=[text_content_block_from_string(completion)],
            tool_calls=tool_calls,
        )
        return query, runtime, query_env, [*message_history, output], query_args
