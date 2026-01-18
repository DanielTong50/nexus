"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # Application
    app_name: str = "nexus"
    app_env: Literal["development", "staging", "production", "dev", "prod"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = True
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
        ],
        alias="CORS_ORIGINS"
    )

    # MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_database: str = Field(default="nexus", alias="MONGODB_DATABASE")

    # Aliases for backward compatibility
    @property
    def MONGO_URI(self) -> str:
        return self.mongodb_uri

    @property
    def DB_NAME(self) -> str:
        return self.mongodb_database

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Google AI (Gemini)
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    # LLM Models
    classifier_model: str = Field(default="gemini-2.0-flash", alias="CLASSIFIER_MODEL")
    agent_model: str = Field(default="gemini-2.0-flash", alias="AGENT_MODEL")

    # Vultr (Alternative LLM Provider)
    vultr_api_key: Optional[str] = Field(default=None, alias="VULTR_API_KEY")
    vultr_inference_url: str = "https://api.vultrinference.com/v1"
    vultr_agent_model: str = Field(default="llama-3.3-70b-instruct-fp8", alias="VULTR_AGENT_MODEL")
    active_agent_provider: Literal["gemini", "vultr"] = "gemini"

    # MCP Settings
    mcp_enabled: bool = True

    # External Services
    slack_bot_token: str = Field(default="", alias="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(default="", alias="SLACK_SIGNING_SECRET")
    slack_allowed_channels: str = ""
    google_service_account_json: str = Field(default="", alias="GOOGLE_SERVICE_ACCOUNT_JSON")
    google_sheets_spreadsheet_id: str = Field(default="", alias="GOOGLE_SHEETS_SPREADSHEET_ID")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    figma_access_token: str = Field(default="", alias="FIGMA_ACCESS_TOKEN")
    calendly_api_key: str = Field(default="", alias="CALENDLY_API_KEY")
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
    token_encryption_key: str = ""  
    oauth_state_secret: str = ""  

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env in ("production", "prod")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
