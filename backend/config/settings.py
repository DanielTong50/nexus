"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),  # Look in parent (project root) first, then current
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "nexus"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "nexus"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Google AI (Gemini)
    google_api_key: str = ""

    # LLM Models
    classifier_model: str = "gemini-3.0-pro"
    agent_model: str = "gemini-3.0-flash"

    # External Services
    mcp_enabled: bool = True
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    google_service_account_json: str = ""
    google_sheets_spreadsheet_id: str = ""
    github_token: str = ""
    figma_access_token: str = ""
    calendly_api_key: str = ""
    notion_token: str = ""

    # OAuth Credentials (for user-based OAuth flows)
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    slack_oauth_client_id: str = ""
    slack_oauth_client_secret: str = ""
    notion_oauth_client_id: str = ""
    notion_oauth_client_secret: str = ""
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    calendly_oauth_client_id: str = ""
    calendly_oauth_client_secret: str = ""
    
    # OAuth Security
    oauth_redirect_base_url: str = "http://localhost:8000"
    token_encryption_key: str = ""  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    oauth_state_secret: str = ""  # Auto-generated if not set

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
