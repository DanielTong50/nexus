"""Application settings using Pydantic Settings.

Dual-Engine LLM Strategy:
- Classifier: Always Gemini (complex routing)
- Agents: Configurable - Gemini (default) or Vultr/Llama 3.3
"""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, SecretStr
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
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ==========================================================================
    # Database (MongoDB Atlas)
    # ==========================================================================
    # Maps to MONGODB_URI in .env
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    # Maps to MONGODB_DATABASE in .env
    mongodb_database: str = Field(default="nexus", alias="MONGODB_DATABASE")

    # ==========================================================================
    # Gemini (Google AI) - Used for Classifier
    # ==========================================================================
    # Maps to GOOGLE_API_KEY in .env
    google_api_key: SecretStr = Field(default=SecretStr(""), alias="GOOGLE_API_KEY")
    # Maps to CLASSIFIER_MODEL in .env
    classifier_model: str = Field(default="gemini-2.0-flash", alias="CLASSIFIER_MODEL")
    # Maps to AGENT_MODEL in .env (for Gemini agents)
    agent_model: str = Field(default="gemini-2.0-flash", alias="AGENT_MODEL")

    # ==========================================================================
    # Vultr Serverless Inference (Llama 3.3) - Alternative Agent Provider
    # ==========================================================================
    vultr_api_key: SecretStr = Field(default=SecretStr(""), alias="VULTR_API_KEY")
    vultr_inference_url: str = Field(
        default="https://api.vultrinference.com/v1", alias="VULTR_INFERENCE_URL"
    )
    vultr_agent_model: str = Field(
        default="llama-3.3-70b-instruct-fp8", alias="VULTR_AGENT_MODEL"
    )

    # ==========================================================================
    # LLM Provider Switch
    # ==========================================================================
    # "gemini" = Use Gemini for agents (default)
    # "vultr" = Use Vultr/Llama 3.3 for agents
    active_agent_provider: Literal["gemini", "vultr"] = Field(
        default="gemini", alias="ACTIVE_AGENT_PROVIDER"
    )

    # ==========================================================================
    # Redis (for caching/sessions)
    # ==========================================================================
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

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
        return self.app_env == "production"

    @property
    def current_agent_model(self) -> str:
        """Get the active agent model based on provider switch."""
        if self.active_agent_provider == "vultr":
            return self.vultr_agent_model
        return self.agent_model

    @property
    def current_agent_api_key(self) -> SecretStr:
        """Get the API key for the active agent provider."""
        if self.active_agent_provider == "vultr":
            return self.vultr_api_key
        return self.google_api_key


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
