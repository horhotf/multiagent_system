from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    timeout_seconds: int
    retry_count: int
    fn: ToolFn
