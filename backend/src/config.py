from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, Union


import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Bali Travel Planner"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Travel Planning for Bali, Indonesia"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Application Constraints
    DESTINATION_SCOPE: str = "bali"  # Application is limited to Bali only
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # JWT Configuration
    # IMPORTANT: These defaults are for LOCAL DEV ONLY.
    # In staging/production, set these via environment variables.
    SECRET_KEY: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    JWT_REFRESH_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    def validate_secrets(self) -> None:
        """
        Validate that required secrets are set in non-development environments.
        Call this during app startup.
        """
        if self.ENVIRONMENT in ("staging", "production"):
            missing = []
            if not self.SECRET_KEY:
                missing.append("SECRET_KEY")
            if not self.JWT_SECRET_KEY:
                missing.append("JWT_SECRET_KEY")
            if not self.JWT_REFRESH_SECRET_KEY:
                missing.append("JWT_REFRESH_SECRET_KEY")
            if missing:
                raise ValueError(
                    f"Missing required secrets for {self.ENVIRONMENT}: {', '.join(missing)}. "
                    "See .env.example for required environment variables."
                )
        else:
            # Development defaults (insecure, local only)
            if not self.SECRET_KEY:
                self.SECRET_KEY = "dev-secret-key-not-for-production"
            if not self.JWT_SECRET_KEY:
                self.JWT_SECRET_KEY = "dev-jwt-secret-not-for-production"
            if not self.JWT_REFRESH_SECRET_KEY:
                self.JWT_REFRESH_SECRET_KEY = "dev-refresh-secret-not-for-production"
    
    # CORS Configuration
    # Include frontend development server (Vite default port is 5173)
    CORS_ORIGINS: Union[list[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins string into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Redis (Caching & Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SHORT: int = 300      # 5 minutes
    CACHE_TTL_MEDIUM: int = 3600    # 1 hour
    CACHE_TTL_LONG: int = 86400     # 24 hours
    
    # External APIs - Bali-Specific
    # Visual Crossing Weather API (https://www.visualcrossing.com/)
    VISUAL_CROSSING_API_KEY: Optional[str] = None
    VISUAL_CROSSING_API_URL: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    
    # OpenStreetMap Settings
    OSM_API_URL: str = "https://api.openstreetmap.org/api/0.6"
    OSM_NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    OSM_OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    OSM_USER_AGENT: str = "BaliTravelPlanner/1.0"
    
    # Bali Geographic Boundaries (for filtering OSM data)
    BALI_MIN_LAT: float = -8.85
    BALI_MAX_LAT: float = -8.05
    BALI_MIN_LON: float = 114.4
    BALI_MAX_LON: float = 115.7
    
    # AI/ML Services
    OPENAI_API_KEY: Optional[str] = None
    LANGBASE_API_KEY: Optional[str] = None
    LANGBASE_PIPE_NAME: str = "bali-travel-planner"
    COHERE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Amadeus API (Flight & Hotel Search)
    AMADEUS_API_KEY: Optional[str] = None
    AMADEUS_API_SECRET: Optional[str] = None
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"  # Use "https://api.amadeus.com" for production
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Singleton instance
settings = Settings()

