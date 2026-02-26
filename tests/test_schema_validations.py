from app.services.schema_service import schema_service


def test_plan_schema_validation() -> None:
    payload = {
        "intent": "search",
        "objective": "Find relevant docs",
        "subtasks": [
            {
                "id": "s1",
                "goal": "search docs",
                "deliverable": "evidence_list",
                "tool_candidates": ["qdrant_search_docs"],
            }
        ],
    }
    ok, errors = schema_service.validate("plan.schema.json", payload)
    assert ok, errors


def test_object_generation_result_schema_validation() -> None:
    payload = {
        "object_type": "generic_object",
        "object_json": {"title": "A", "summary": "B"},
        "provenance": [{"path": "$.title", "source": "template", "ref": "object_templates:1"}],
        "warnings": [],
        "confidence": 0.9,
    }
    ok, errors = schema_service.validate("object_generation_result.schema.json", payload)
    assert ok, errors


def test_text_segmentation_schema_validation() -> None:
    payload = {
        "profile": "default",
        "segments": [
            {"id": "seg1", "type": "context", "text": "Контекст"},
            {"id": "seg2", "type": "requirements", "text": "Требования"},
        ],
    }
    ok, errors = schema_service.validate("text_segmentation.schema.json", payload)
    assert ok, errors
