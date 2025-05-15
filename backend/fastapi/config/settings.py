import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
base_dir = Path(__file__).resolve().parent.parent.parent  # Navigate to backend directory
dotenv_path = base_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

# In Pydantic v2, BaseSettings was moved to pydantic-settings package
# For compatibility, we'll use BaseModel instead with similar functionality
class Settings(BaseModel):
    """Application settings."""
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # Note: With BaseModel instead of BaseSettings, env_file loading is not automatic
    # We'll use os.getenv directly instead for environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
