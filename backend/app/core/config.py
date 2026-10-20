from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "orbit-engine"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://orbit:orbit@localhost:5432/orbit",
        validation_alias="DATABASE_URL"
    )

    # Keycloak / OIDC
    oidc_issuer_url: str = Field(default="", validation_alias="OIDC_ISSUER_URL")
    oidc_client_id: str = Field(default="orbit-engine", validation_alias="OIDC_CLIENT_ID")
    oidc_client_secret: str = Field(default="", validation_alias="OIDC_CLIENT_SECRET")
    oidc_redirect_uri: str = Field(default="http://localhost:5173/callback", validation_alias="OIDC_REDIRECT_URI")
    oidc_audience: str = Field(default="orbit-engine", validation_alias="OIDC_AUDIENCE")

    # LLM
    llm_api_key: str = Field(default="", validation_alias="LLM_API_KEY")
    llm_provider: str = Field(default="openai-compatible", validation_alias="LLM_PROVIDER")
    llm_model: str = Field(default="", validation_alias="LLM_MODEL")
    llm_base_url: str = Field(default="", validation_alias="LLM_BASE_URL")

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:5173"], validation_alias="CORS_ORIGINS")

    # Demo mode (local only)
    demo_mode: bool = Field(default=False, validation_alias="DEMO_MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()