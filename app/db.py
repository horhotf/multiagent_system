from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row

from app.config import settings


class PostgresClient:
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or settings.postgres_dsn

    @contextmanager
    def conn(self):
        with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                yield conn, cur

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> None:
        with self.conn() as (conn, cur):
            cur.execute(sql, params)
            conn.commit()

    def fetch_all(self, sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
        with self.conn() as (_, cur):
            cur.execute(sql, params)
            return list(cur.fetchall())

    def fetch_one(self, sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
        with self.conn() as (_, cur):
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def log_task(self, task_id: str, trace_id: str, mode: str, request_payload: dict[str, Any]) -> None:
        self.execute(
            """
            INSERT INTO tasks (id, trace_id, mode, request_payload)
            VALUES (%s, %s, %s, %s::jsonb)
            """,
            (task_id, trace_id, mode, json.dumps(request_payload, ensure_ascii=False)),
        )

    def log_step(
        self,
        task_id: str,
        step_name: str,
        tool_name: str,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any],
        status: str = "ok",
        error_message: str | None = None,
    ) -> None:
        self.execute(
            """
            INSERT INTO task_steps (task_id, step_name, tool_name, input_payload, output_payload, status, error_message)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
            """,
            (
                task_id,
                step_name,
                tool_name,
                json.dumps(input_payload, ensure_ascii=False),
                json.dumps(output_payload, ensure_ascii=False),
                status,
                error_message,
            ),
        )


pg = PostgresClient()
