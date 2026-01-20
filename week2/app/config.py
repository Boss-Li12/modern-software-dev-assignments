# ============================================================
# TODO 3: Application Configuration (AI-Generated)
# ============================================================
"""
Centralized configuration management for the application.
Uses environment variables with sensible defaults.

AI-Generated: This file was created with AI assistance for TODO 3.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "Action Item Extractor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_path: Optional[str] = None
    
    # LLM settings
    default_llm_model: str = "llama3.1:8b"
    llm_timeout_seconds: int = 60
    
    # API settings
    api_prefix: str = ""
    
    def __post_init__(self):
        """Load settings from environment variables."""
        self.app_name = os.getenv("APP_NAME", self.app_name)
        self.app_version = os.getenv("APP_VERSION", self.app_version)
        self.debug = os.getenv("APP_DEBUG", "false").lower() in ("true", "1", "yes")
        self.database_path = os.getenv("APP_DATABASE_PATH", self.database_path)
        self.default_llm_model = os.getenv("APP_DEFAULT_LLM_MODEL", self.default_llm_model)
        self.llm_timeout_seconds = int(os.getenv("APP_LLM_TIMEOUT_SECONDS", str(self.llm_timeout_seconds)))
    
    @property
    def db_path(self) -> Path:
        """Get the database path, using default if not set."""
        if self.database_path:
            return Path(self.database_path)
        base_dir = Path(__file__).resolve().parents[1]
        return base_dir / "data" / "app.db"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience access to settings
settings = get_settings()
