from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ModeType = Literal["auto", "json_object", "search", "validate_text", "image", "pptx"]


class QueryRequest(BaseModel):
    mode: ModeType = "auto"
    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class ObjectGenerateRequest(BaseModel):
    query: str
    object_type: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class TextValidateRequest(BaseModel):
    text: str
    policy: str | None = None


class GenericResponse(BaseModel):
    task_id: str
    trace_id: str
    mode: str
    result: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


class ArtifactResponse(BaseModel):
    id: int
    task_id: str
    artifact_type: str
    path: str | None
    metadata: dict[str, Any]
