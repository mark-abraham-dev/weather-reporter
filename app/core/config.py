from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Union
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Weather Monitoring Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False, description="Debug mode")

    # Server settings
    HOST: str = Field("0.0.0.0", description="Server host")
    PORT: int = Field(8000, description="Server port")

    # CORS settings
    CORS_ORIGINS: List[str] = Field(["*"], description="CORS allowed origins")

    # MongoDB settings
    MONGODB_URI: str = Field("mongodb://localhost:27017/", description="MongoDB connection URI")
    MONGODB_DB_NAME: str = Field("weather_db", description="MongoDB database name")
    MONGODB_WEATHER_COLLECTION: str = Field("weather_data", description="MongoDB weather collection")

    # Weather API settings
    WEATHER_API_KEY: str = Field("your_api_key_here", description="Weather API key")
    WEATHER_API_URL: str = Field("https://api.openweathermap.org/data/2.5/weather", description="Weather API URL")
    WEATHER_LOCATION: str = Field("Austin,TX", description="Location to fetch weather for")

    # Scheduler settings
    WEATHER_UPDATE_INTERVAL_SECONDS: int = Field(10, description="Weather update interval in seconds")

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings to avoid reading .env file on each request"""
    return Settings()
