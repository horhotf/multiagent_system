from __future__ import annotations

from app.config import settings
from app.tools.base import ToolSpec
from app.tools.qdrant_tools import QdrantSearchTools
from app.tools.toolkit import (
    entity_resolver,
    image_gen,
    json_repair,
    json_schema_validator,
    object_key_extractor,
    object_schema_loader,
    object_template_filler,
    object_template_selector,
    object_type_resolver,
    postgres_query,
    pptx_gen,
    relations_resolver,
    text_block_validator,
    text_segmenter,
    yandex_search,
)


qdrant_tools = QdrantSearchTools()


def _empty_schema() -> dict:
    return {"type": "object", "additionalProperties": True}


TOOL_REGISTRY: dict[str, ToolSpec] = {
    "qdrant_search_docs": ToolSpec("qdrant_search_docs", "Search docs_space", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, qdrant_tools.search_docs),
    "qdrant_search_tables": ToolSpec("qdrant_search_tables", "Search tables_space", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, qdrant_tools.search_tables),
    "postgres_query": ToolSpec("postgres_query", "Read-only SQL query", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, postgres_query),
    "yandex_search": ToolSpec("yandex_search", "Yandex search tool", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 0, yandex_search),
    "image_gen": ToolSpec("image_gen", "Image generation contract stub", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 0, image_gen),
    "pptx_gen": ToolSpec("pptx_gen", "PPTX generation contract stub", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 0, pptx_gen),
    "object_type_resolver": ToolSpec("object_type_resolver", "Resolve object type", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, object_type_resolver),
    "object_key_extractor": ToolSpec("object_key_extractor", "Extract keys from request", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, object_key_extractor),
    "object_schema_loader": ToolSpec("object_schema_loader", "Load object schema", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, object_schema_loader),
    "relations_resolver": ToolSpec("relations_resolver", "Resolve relations", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 0, relations_resolver),
    "entity_resolver": ToolSpec("entity_resolver", "Resolve candidate entities", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, entity_resolver),
    "object_template_selector": ToolSpec("object_template_selector", "Select template", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, object_template_selector),
    "object_template_filler": ToolSpec("object_template_filler", "Fill template using LLM", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, object_template_filler),
    "json_schema_validator": ToolSpec("json_schema_validator", "Validate JSON by schema", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, json_schema_validator),
    "json_repair": ToolSpec("json_repair", "Repair invalid JSON", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, json_repair),
    "text_segmenter": ToolSpec("text_segmenter", "Split text into blocks", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, text_segmenter),
    "text_block_validator": ToolSpec("text_block_validator", "Validate each block", _empty_schema(), _empty_schema(), settings.default_tool_timeout_seconds, 1, text_block_validator),
}


def run_tool(tool_name: str, payload: dict) -> dict:
    spec = TOOL_REGISTRY[tool_name]
    return spec.fn(payload)
