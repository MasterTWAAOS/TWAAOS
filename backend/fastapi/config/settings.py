import os
from functools import lru_cache
from pydantic import BaseModel

# In Pydantic v2, BaseSettings was moved to pydantic-settings package
# For compatibility, we'll use BaseModel instead with similar functionality
class Settings(BaseModel):
    """Application settings."""
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # Note: With BaseModel instead of BaseSettings, env_file loading is not automatic
    # We'll use os.getenv directly instead for environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
