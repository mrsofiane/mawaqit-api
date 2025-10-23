from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, ValidationError
from typing import Optional
import sys

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    RATE_LIMIT : str = "60/minute"

    # REDIS
    ENABLE_REDIS: bool = False
    REDIS_URI: str = "redis://localhost:6379"

    # Authentication
    ENABLE_AUTH: bool = False
    BEARER_TOKEN: Optional[str] = None

    @model_validator(mode="after")
    def _check_auth(self):
        if self.ENABLE_AUTH and not self.BEARER_TOKEN:
            raise ValueError(
                "ENABLE_AUTH is set to true but BEARER_TOKEN environment variable is not set. "
                "Please configure BEARER_TOKEN in your .env file."
            )
        return self

try:
    settings = Settings()
except ValidationError as e:
    print(e, file=sys.stderr)
    sys.exit(1)

