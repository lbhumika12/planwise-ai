"""
PlanWise AI - Configuration Module
Reads all settings from environment variables with sensible defaults.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # Database
    database_url: str = "sqlite:///./planwise.db"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:4173"

    # AI Provider
    ai_provider: Optional[str] = None  # "openai", "anthropic", "gemini"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # AI Model names
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-haiku-20241022"
    gemini_model: str = "gemini-2.5-flash"

    # Defaults
    default_timezone: str = "Asia/Kolkata"
    default_start_time: str = "09:00"
    default_end_time: str = "21:00"
    default_break_duration: int = 30

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_available(self) -> bool:
        """Returns True if any AI provider is configured."""
        if self.ai_provider == "openai" and self.openai_api_key:
            return True
        if self.ai_provider == "anthropic" and self.anthropic_api_key:
            return True
        if self.ai_provider == "gemini" and self.gemini_api_key:
            return True
        # Auto-detect
        if self.openai_api_key:
            return True
        if self.anthropic_api_key:
            return True
        if self.gemini_api_key:
            return True
        return False

    @property
    def active_ai_provider(self) -> Optional[str]:
        """Returns the active AI provider name."""
        if self.ai_provider:
            return self.ai_provider
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"
        if self.gemini_api_key:
            return "gemini"
        return None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

