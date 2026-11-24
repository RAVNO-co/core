from pydantic import PostgresDsn, SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class OpenRouterSettings(Base):
    model_config = SettingsConfigDict(env_prefix="OPENROUTER_")
    API_KEY: SecretStr


class AgentSettings(Base):
    model_config = SettingsConfigDict(env_prefix="AGENT_")
    # None creates in-memory checkpointer
    CHECKPOINTER_DSN: PostgresDsn | None = None

    MODEL: str
    TEMPERATURE: float = 0
    MAX_TOKENS: int = 4000
    REASONING: dict[str, str]
