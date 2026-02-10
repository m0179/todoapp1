"""
Configuration settings for the application.
Loads environment variables and provides configuration constants.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        DATABASE_URL: PostgreSQL database connection string
        APP_NAME: Name of the application
        DEBUG: Debug mode flag
    """
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/todoapp"
    APP_NAME: str = "Todo API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()


# Create a global settings instance
settings = get_settings()
