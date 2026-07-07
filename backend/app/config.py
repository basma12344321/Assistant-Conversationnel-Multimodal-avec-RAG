import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"

    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "ragdb"
    postgres_user: str = "raguser"
    postgres_password: str = "changeme"

    # Auth
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Divers
    environment: str = "development"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @classmethod
    def parse_env_var(cls, field_name, raw_val):
        if field_name == "cors_origins":
            if raw_val is None:
                return ["http://localhost:3000"]
            if isinstance(raw_val, str):
                value = raw_val.strip()
                if not value:
                    return []
                if value.startswith("[") and value.endswith("]"):
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list):
                            return parsed
                    except json.JSONDecodeError:
                        pass
                return [item.strip() for item in value.split(",") if item.strip()]
            if isinstance(raw_val, list):
                return raw_val
            return [str(raw_val)]
        return super().parse_env_var(field_name, raw_val)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
