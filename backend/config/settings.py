from typing import List, Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    # App Config
    ENVIRONMENT: Literal["dev", "development", "prod", "production"] = Field(default="dev", alias="APP_ENV")
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database (MongoDB Atlas)
    MONGO_URI: str = Field(alias="MONGODB_URI")
    DB_NAME: str = Field(default="nexus-core", alias="MONGODB_DATABASE")

    # LLM Provider 1: Google Gemini (Classifier & Agents)
    GEMINI_API_KEY: SecretStr = Field(alias="GOOGLE_API_KEY")
    CLASSIFIER_MODEL: str = "gemini-1.5-pro"
    AGENT_MODEL_GEMINI: str = Field(default="gemini-1.5-flash", alias="AGENT_MODEL")

    # LLM Provider 2: Vultr / OpenAI Compatible (Agents Only)
    VULTR_API_KEY: Optional[SecretStr] = None
    VULTR_INFERENCE_URL: str = "https://api.vultrinference.com/v1"
    AGENT_MODEL_VULTR: str = Field(default="zephyr-7b-beta-Q5_K_M", alias="VULTR_AGENT_MODEL")

    # Master Switch: Selects which provider runs the Agents
    ACTIVE_AGENT_PROVIDER: Literal["gemini", "vultr"] = "gemini"

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),  # Look in parent (project root) first, then current
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True  # Allow both alias and field name
    )

settings = Settings()
