from pydantic import PostgresDsn, SecretStr
from pydantic_settings import (
    BaseSettings as PydanticSettingsBase,
)
from pydantic_settings import (
    SettingsConfigDict,
)


class BaseSettings(PydanticSettingsBase):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    OPENROUTER_API_KEY: SecretStr


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_")
    # No DSN creates in-memory checkpointer
    CHECKPOINTER_DSN: PostgresDsn | None = None

    AGENT_MODEL: str
    TEMPERATURE: float = 0
    MAX_TOKENS: int = 4000
    REASONING: dict[str, str]
