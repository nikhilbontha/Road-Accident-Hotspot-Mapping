from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Road Accident Hotspot Mapping"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "insecure-dev-secret-key-change-me-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/road_safety"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "road-safety-imports"
    MINIO_REPORTS_BUCKET: str = "road-safety-reports"
    MINIO_SECURE: bool = False

    # Geospatial Defaults (Hyderabad NH-65 corridor)
    DEMO_CENTER_LAT: float = 17.4200
    DEMO_CENTER_LON: float = 78.5800
    DEFAULT_SEARCH_RADIUS_M: int = 250
    DEFAULT_MIN_ACCIDENTS: int = 5
    DEFAULT_ANALYSIS_PERIOD_MONTHS: int = 12

    # LLM Provider
    LLM_PROVIDER: str = "offline"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
