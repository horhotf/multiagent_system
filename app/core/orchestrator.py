from __future__ import annotations

import json
import uuid
from typing import Any

from app.config import settings
from app.db import pg
from app.services.llm_client import llm_client
from app.services.schema_service import schema_service
from app.tools.registry import run_tool


class Orchestrator:
    def run_query(self, mode: str, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        task_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        warnings: list[str] = []
        pg.log_task(task_id, trace_id, mode, {"query": query, "context": context})

        result: dict[str, Any]
        if mode == "search":
            result = self._run_search(task_id, query)
        elif mode == "json_object":
            result, wrn = self._run_object_generation(task_id, query, context)
            warnings.extend(wrn)
        elif mode == "validate_text":
            result = self._run_text_validation(task_id, query)
        elif mode == "image":
            result = self._call(task_id, "image_gen", {"prompt": query})
        elif mode == "pptx":
            result = self._call(task_id, "pptx_gen", {"prompt": query})
        else:
            result = self._run_auto(task_id, query, context)

        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "mode": mode,
            "result": result,
            "warnings": warnings,
        }

    def _call(self, task_id: str, tool: str, payload: dict[str, Any], step: str | None = None) -> dict[str, Any]:
        step_name = step or tool
        output = run_tool(tool, payload)
        pg.log_step(task_id, step_name, tool, payload, output)
        return output

    def _run_search(self, task_id: str, query: str) -> dict[str, Any]:
        docs = self._call(task_id, "qdrant_search_docs", {"query_vector": [0.0, 0.0, 0.0, 0.0], "query": query, "limit": 5})
        tables = self._call(task_id, "qdrant_search_tables", {"query_vector": [0.0, 0.0, 0.0, 0.0], "query": query, "limit": 5})
        web = self._call(task_id, "yandex_search", {"query": query})
        return {"docs": docs, "tables": tables, "web": web}

    def _run_auto(self, task_id: str, query: str, context: dict[str, Any]) -> dict[str, Any]:
        plan = llm_client.call_json("planner_system.md", {}, query)
        ok, errors = schema_service.validate("plan.schema.json", plan)
        if not ok:
            raise ValueError(f"Planner output schema invalid: {errors}")
        pg.log_step(task_id, "plan", "llm_planner", {"query": query}, plan)

        route = llm_client.call_json("router_system.md", {}, json.dumps({"query": query, "plan": plan}, ensure_ascii=False))
        pg.log_step(task_id, "route", "llm_router", {"query": query, "context": context}, route)

        selected_mode = route.get("mode", "search")
        if selected_mode == "json_object":
            result, _ = self._run_object_generation(task_id, query, context)
            return {"plan": plan, "route": route, "execution": result}
        if selected_mode == "validate_text":
            return {"plan": plan, "route": route, "execution": self._run_text_validation(task_id, query)}
        return {"plan": plan, "route": route, "execution": self._run_search(task_id, query)}

    def _run_object_generation(self, task_id: str, query: str, context: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        warnings: list[str] = []
        object_type = context.get("object_type")
        if not object_type:
            resolved = self._call(task_id, "object_type_resolver", {"query": query, "variables": context})
            object_type = resolved.get("object_type")

        schema_info = self._call(task_id, "object_schema_loader", {"object_type": object_type})
        template_info = self._call(task_id, "object_template_selector", {"object_type": object_type})
        keys = self._call(task_id, "object_key_extractor", {"query": query, "variables": context})
        relations = self._call(task_id, "relations_resolver", {"object_type": object_type})
        entities = self._call(task_id, "entity_resolver", {"query": query, "object_type": object_type})

        fill_payload = {
            "query": query,
            "object_type": object_type,
            "schema": schema_info["schema"],
            "template": template_info["template"],
            "keys": keys,
            "relations": relations,
            "entities": entities,
            "variables": context,
        }
        candidate = self._call(task_id, "object_template_filler", fill_payload)["candidate_json"]

        validation = self._call(task_id, "json_schema_validator", {"schema": schema_info["schema"], "instance": candidate})
        attempts = 0
        while not validation["valid"] and attempts < settings.max_repair_iterations:
            warnings.append(f"repair_iteration_{attempts + 1}")
            repaired = self._call(
                task_id,
                "json_repair",
                {
                    "schema": schema_info["schema"],
                    "candidate_json": candidate,
                    "errors": validation["errors"],
                    "variables": context,
                },
            )
            candidate = repaired["candidate_json"]
            validation = self._call(task_id, "json_schema_validator", {"schema": schema_info["schema"], "instance": candidate})
            attempts += 1

        result = {
            "object_type": object_type,
            "object_json": candidate,
            "provenance": [],
            "warnings": [{"code": "schema_invalid", "path": None, "message": err} for err in validation["errors"]],
            "confidence": 0.7,
        }
        ok, errors = schema_service.validate("object_generation_result.schema.json", result)
        if not ok:
            warnings.append("object_generation_result_schema_validation_failed")
            warnings.extend(errors)
        return result, warnings

    def _run_text_validation(self, task_id: str, text: str) -> dict[str, Any]:
        segmentation = self._call(task_id, "text_segmenter", {"text": text, "variables": {}})
        ok, errors = schema_service.validate("text_segmentation.schema.json", segmentation)
        if not ok:
            raise ValueError(f"Text segmentation schema invalid: {errors}")
        report = self._call(task_id, "text_block_validator", {"segmentation": segmentation, "text": text, "variables": {}})
        valid_report, report_errors = schema_service.validate("validation_report.schema.json", report)
        return {
            "segmentation": segmentation,
            "validation_report": report,
            "report_schema_valid": valid_report,
            "report_schema_errors": report_errors,
        }


orchestrator = Orchestrator()
