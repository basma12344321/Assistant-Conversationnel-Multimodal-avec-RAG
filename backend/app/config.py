from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Embeddings
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"  # multilingue FR/EN
    
    # Reranker
    reranker_model: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"  # multilingue FR/EN

    # Qdrant
    qdrant_mode: str = "local"  # "local" (embarqué sur disque, pas besoin de Docker) ou "server" (via Docker)
    qdrant_local_path: str = "../data/qdrant_local"
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

    # Stockage fichiers
    storage_backend: str = "local"
    storage_bucket: str = "documents"

    # Divers
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()