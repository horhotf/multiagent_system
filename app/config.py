from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "multiagent-orchestrator"
    host: str = "0.0.0.0"
    port: int = 8000

    postgres_dsn: str = "postgresql://postgres:postgres@postgres:5432/multiagent"
    qdrant_url: str = "http://qdrant:6333"

    llm_base_url: str = "http://host.docker.internal:11434/v1"
    llm_api_key: str = "dummy"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 60

    max_repair_iterations: int = 2
    default_tool_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
