from __future__ import annotations

import json
from typing import Any

from app.db import pg
from app.services.llm_client import llm_client
from app.services.schema_service import schema_service


def postgres_query(payload: dict[str, Any]) -> dict[str, Any]:
    sql = payload.get("sql", "SELECT 1 as ok")
    lowered = sql.lower().strip()
    if not lowered.startswith("select"):
        raise ValueError("postgres_query supports read-only SELECT statements only")
    rows = pg.fetch_all(sql)
    return {"rows": rows, "count": len(rows)}


def yandex_search(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "query": payload.get("query", ""),
        "results": [],
        "warning": "TODO: integrate Yandex Search API",
    }


def image_gen(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "stub",
        "input": payload,
        "artifact": {"type": "image", "path": None},
        "warning": "TODO: connect image model/provider",
    }


def pptx_gen(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "stub",
        "input": payload,
        "artifact": {"type": "pptx", "path": None},
        "warning": "TODO: connect pptx generation backend",
    }


def object_type_resolver(payload: dict[str, Any]) -> dict[str, Any]:
    result = llm_client.call_json(
        "object_type_resolver_system.md",
        payload.get("variables", {}),
        payload.get("query", ""),
    )
    return {"object_type": result.get("object_type"), "raw": result}


def object_key_extractor(payload: dict[str, Any]) -> dict[str, Any]:
    result = llm_client.call_json(
        "object_key_extractor_system.md",
        payload.get("variables", {}),
        payload.get("query", ""),
    )
    return {"keys": result.get("keys", []), "raw": result}


def object_schema_loader(payload: dict[str, Any]) -> dict[str, Any]:
    object_type = payload["object_type"]
    row = pg.fetch_one(
        "SELECT object_type, schema_json, version FROM object_schemas WHERE object_type = %s ORDER BY version DESC LIMIT 1",
        (object_type,),
    )
    if not row:
        raise ValueError(f"Schema for object_type={object_type} not found")
    return {"object_type": object_type, "schema": row["schema_json"], "version": row["version"]}


def relations_resolver(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "object_type": payload.get("object_type"),
        "relations": [],
        "warning": "TODO: connect relations from data catalog",
    }


def entity_resolver(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query", "")
    sql = "SELECT id::text as id, name, 0.5::float as score FROM entity_catalog WHERE name ILIKE %s LIMIT 10"
    rows = pg.fetch_all(sql, (f"%{query}%",))
    return {"candidates": rows}


def object_template_selector(payload: dict[str, Any]) -> dict[str, Any]:
    object_type = payload["object_type"]
    row = pg.fetch_one(
        "SELECT object_type, template_json, version FROM object_templates WHERE object_type = %s ORDER BY version DESC LIMIT 1",
        (object_type,),
    )
    if not row:
        raise ValueError(f"Template for object_type={object_type} not found")
    return {"template": row["template_json"], "version": row["version"]}


def object_template_filler(payload: dict[str, Any]) -> dict[str, Any]:
    result = llm_client.call_json(
        "object_template_filler_system.md",
        payload.get("variables", {}),
        json.dumps(payload, ensure_ascii=False),
    )
    return {"candidate_json": result}


def json_schema_validator(payload: dict[str, Any]) -> dict[str, Any]:
    schema = payload["schema"]
    instance = payload["instance"]
    is_valid, errors = schema_service.validate_inline(schema, instance) if hasattr(schema_service, "validate_inline") else (True, [])
    if not hasattr(schema_service, "validate_inline"):
        from jsonschema import Draft202012Validator

        validator = Draft202012Validator(schema)
        errors_obj = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        errors = [e.message for e in errors_obj]
        is_valid = len(errors) == 0
    return {"valid": is_valid, "errors": errors}


def json_repair(payload: dict[str, Any]) -> dict[str, Any]:
    response = llm_client.call_json(
        "json_repair_system.md",
        payload.get("variables", {}),
        json.dumps(payload, ensure_ascii=False),
    )
    return {"candidate_json": response}


def text_segmenter(payload: dict[str, Any]) -> dict[str, Any]:
    return llm_client.call_json(
        "text_segmenter_system.md",
        payload.get("variables", {}),
        payload.get("text", ""),
    )


def text_block_validator(payload: dict[str, Any]) -> dict[str, Any]:
    return llm_client.call_json(
        "text_block_validator_system.md",
        payload.get("variables", {}),
        json.dumps(payload, ensure_ascii=False),
    )
