"""Application settings using Pydantic Settings.

Dual-Engine LLM Strategy:
- Classifier: Always Gemini 1.5 Pro (complex routing)
- Agents: Configurable - Gemini Flash (default) or Vultr/Llama 3.3
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    app_name: str = "nexus"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ==========================================================================
    # Database (MongoDB Atlas)
    # ==========================================================================
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "nexus-core"

    # ==========================================================================
    # Gemini (Google AI) - Used for Classifier
    # ==========================================================================
    gemini_api_key: SecretStr = SecretStr("")
    classifier_model: str = "gemini-1.5-pro"
    gemini_agent_model: str = "gemini-1.5-flash"

    # ==========================================================================
    # Vultr Serverless Inference (Llama 3.3) - Alternative Agent Provider
    # ==========================================================================
    vultr_api_key: SecretStr = SecretStr("")
    vultr_inference_url: str = "https://api.vultrinference.com/v1"
    vultr_agent_model: str = "llama-3.3-70b-instruct"

    # ==========================================================================
    # LLM Provider Switch
    # ==========================================================================
    # Master switch for agent LLM provider
    # "gemini" = Use Gemini Flash for agents (default)
    # "vultr" = Use Vultr/Llama 3.3 for agents (cost savings)
    active_agent_provider: Literal["gemini", "vultr"] = "gemini"

    # ==========================================================================
    # Redis (for caching/sessions)
    # ==========================================================================
    redis_url: str = "redis://localhost:6379/0"

    # ==========================================================================
    # External Services (Backend Dev 2 tools)
    # ==========================================================================
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    google_service_account_json: str = ""
    github_token: str = ""
    figma_access_token: str = ""
    calendly_api_key: str = ""

    # ==========================================================================
    # Server
    # ==========================================================================
    host: str = "0.0.0.0"
    port: int = 8000

    # ==========================================================================
    # Computed Properties
    # ==========================================================================
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def agent_model(self) -> str:
        """Get the active agent model based on provider switch."""
        if self.active_agent_provider == "vultr":
            return self.vultr_agent_model
        return self.gemini_agent_model

    @property
    def agent_api_key(self) -> SecretStr:
        """Get the API key for the active agent provider."""
        if self.active_agent_provider == "vultr":
            return self.vultr_api_key
        return self.gemini_api_key


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
