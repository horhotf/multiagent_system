# Multi-agent System Spec Pack

This archive contains:
- `schemas/` JSON Schemas for plans, tool calls, evidence, object generation, text segmentation & validation.
- `prompts/` System prompts for Planner/Router/Object generation/Repair/Text segmentation & validation.

Intended use:
1) Wire schemas into your orchestrator (Pydantic models + jsonschema validation).
2) Store prompts in your codebase and call LLM via aider chat / OpenAI-compatible endpoint.
3) Build tools: Qdrant (docs/tables spaces), Postgres queries, Yandex search, image & pptx generators.

Note: `_warnings` / `_repair_note` fields require schema allowance if you set additionalProperties=false.
A common approach is to keep warnings in the pipeline result envelope, not inside the object JSON.
