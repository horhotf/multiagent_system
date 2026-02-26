CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    trace_id UUID NOT NULL,
    mode TEXT NOT NULL,
    request_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS task_steps (
    id BIGSERIAL PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input_payload JSONB NOT NULL,
    output_payload JSONB NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS artifacts (
    id BIGSERIAL PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,
    path TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS object_schemas (
    id BIGSERIAL PRIMARY KEY,
    object_type TEXT NOT NULL,
    version INT NOT NULL,
    schema_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS object_templates (
    id BIGSERIAL PRIMARY KEY,
    object_type TEXT NOT NULL,
    version INT NOT NULL,
    template_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_catalog (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO object_schemas(object_type, version, schema_json)
VALUES (
    'generic_object',
    1,
    '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":{"title":{"type":"string"},"summary":{"type":"string"}},"required":["title","summary"],"additionalProperties":true}'::jsonb
)
ON CONFLICT DO NOTHING;

INSERT INTO object_templates(object_type, version, template_json)
VALUES (
    'generic_object',
    1,
    '{"title":"","summary":""}'::jsonb
)
ON CONFLICT DO NOTHING;
