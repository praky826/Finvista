"""
FINVISTA Configuration Module
Loads environment variables and validates required settings.
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Database
    database_url: str = "postgresql://postgres:Blackdog@localhost:5432/finvista"

    # Security
    secret_key: str = "finvista-super-secret-key-change-in-production-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"

    # CORS
    cors_origins: str = '["http://localhost:5173","http://localhost:3000"]'

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"
    rate_limit_api: str = "100/minute"

    # Logging
    log_level: str = "INFO"

    # Features
    enable_business_mode: bool = True
    enable_reports: bool = True
    enable_exports: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string to list."""
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
