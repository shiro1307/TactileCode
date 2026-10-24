"""
Configuration settings for TactileCode backend.
"""

import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
FIXTURES_DIR = BASE_DIR / "fixtures"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    # Gemma 4 API (via Google AI Studio - Primary)
    gemma_api_key: str = os.getenv("GEMMA_API_KEY", "")
    
    # Fallback options
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "false").lower() in ("true", "1", "yes")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llava:7b-v1.6")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))
    
    # Legacy Gemini API (fallback)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    
    # General settings
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


settings = Settings()
