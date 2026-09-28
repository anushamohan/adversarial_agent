"""Deterministic JSON serialization for AgentDojo tool results."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from enum import Enum
from typing import Any


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def dumps_iso8601_json(value: dict | list[dict]) -> str:
    return json.dumps(value, default=_json_default)
