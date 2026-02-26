from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT_DIR / "schemas"


class SchemaService:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, schema_name: str) -> dict[str, Any]:
        if schema_name in self._cache:
            return self._cache[schema_name]
        path = SCHEMAS_DIR / schema_name
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self._cache[schema_name] = schema
        return schema


    def validate_inline(self, schema: dict[str, Any], payload: Any) -> tuple[bool, list[str]]:
        Draft202012Validator.check_schema(schema)
        try:
            validator = Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
            messages = [f"{'/'.join([str(x) for x in err.absolute_path]) or '$'}: {err.message}" for err in errors]
            return len(messages) == 0, messages
        except Exception as exc:  # noqa: BLE001
            return False, [str(exc)]

    def validate(self, schema_name: str, payload: Any) -> tuple[bool, list[str]]:
        schema = self.load(schema_name)
        try:
            validator = Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
            messages = [f"{'/'.join([str(x) for x in err.absolute_path]) or '$'}: {err.message}" for err in errors]
            return len(messages) == 0, messages
        except Exception as exc:  # noqa: BLE001
            return False, [str(exc)]


schema_service = SchemaService()
