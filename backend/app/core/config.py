import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "NEXUS FORENSIC API"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./nexus.db"
    STORAGE_PATH: str = "../storage"
    MAX_UPLOAD_SIZE_MB: int = 100

    CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000"]'

    @property
    def parsed_cors_origins(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except Exception:
            return ["*"]


settings = Settings()
