"""
Configuration settings for TactileCode backend.
"""

import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
FIXTURES_DIR = BASE_DIR / "fixtures"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    api_key: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    fallback_to_mock: bool = os.getenv("FALLBACK_TO_MOCK", "true").lower() in ("true", "1", "yes")
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_content_types: set = {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "image/svg+xml",
    }


settings = Settings()
