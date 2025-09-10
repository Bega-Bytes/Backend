import os
from typing import List


class Settings:
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",  # Alternative frontend port
    ]

    # Add environment-specific origins
    if os.getenv("FRONTEND_URL"):
        ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL"))

    # ML Service configuration
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ML_SERVICE_TIMEOUT: int = int(os.getenv("ML_SERVICE_TIMEOUT", "30"))

    # WebSocket configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))

    # Vehicle state configuration
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "22.0"))
    DEFAULT_FAN_SPEED: int = int(os.getenv("DEFAULT_FAN_SPEED", "3"))
    DEFAULT_VOLUME: int = int(os.getenv("DEFAULT_VOLUME", "50"))

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "vehicle_backend.log")

    # API Keys (if needed for external services)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Database configuration (if needed later)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vehicle.db")

    # Feature flags
    ENABLE_VOICE_PROCESSING: bool = os.getenv("ENABLE_VOICE_PROCESSING", "true").lower() == "true"
    ENABLE_WEBSOCKET: bool = os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"
    ENABLE_ML_FALLBACK: bool = os.getenv("ENABLE_ML_FALLBACK", "true").lower() == "true"


# Create settings instance
settings = Settings()

# Validation
if settings.DEBUG:
    print("🔧 Running in DEBUG mode")
    print(f"🌐 Allowed origins: {settings.ALLOWED_ORIGINS}")
    print(f"🤖 ML Service URL: {settings.ML_SERVICE_URL}")