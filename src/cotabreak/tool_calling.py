"""Prompt-based single-tool calling shared by the local AgentDojo adapter."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParsedToolCall:
    function: str
    arguments: dict[str, Any]


_OPEN_FUNCTION_TAG = re.compile(r"<function\s*=\s*([^>]+)>")
_TOOL_CALL_TAG = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


def parse_tool_call(text: str) -> ParsedToolCall | None:
    native_matches = list(_TOOL_CALL_TAG.finditer(text))
    function_matches = list(_OPEN_FUNCTION_TAG.finditer(text))

    # AgentDojo advances one tool call at a time. Returning only the first call
    # from a multi-call completion would silently drop model output and corrupt
    # tool-validity metrics, so reject ambiguous completions instead.
    if len(native_matches) + len(function_matches) > 1:
        return None

    native_match = native_matches[0] if native_matches else None
    if native_match is not None:
        try:
            payload = json.loads(native_match.group(1))
            function = payload["name"]
            arguments = payload["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
        if isinstance(function, str) and function and isinstance(arguments, dict):
            return ParsedToolCall(function=function, arguments=arguments)
        return None

    if len(function_matches) != 1:
        return None
    match = function_matches[0]
    if match is None:
        return None

    function = match.group(1).strip()
    end = text.find("</function>", match.end())
    raw_arguments = text[match.end() : end if end >= 0 else len(text)].strip()
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return None
    if not function or not isinstance(arguments, dict):
        return None
    return ParsedToolCall(function=function, arguments=arguments)
