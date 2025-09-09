import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # WebSocket Settings
    WEBSOCKET_TIMEOUT: int = int(os.getenv("WEBSOCKET_TIMEOUT", "60"))
    
    # Vehicle Default Settings
    DEFAULT_TEMPERATURE: int = int(os.getenv("DEFAULT_TEMPERATURE", "22"))
    DEFAULT_VOLUME: int = int(os.getenv("DEFAULT_VOLUME", "50"))
    DEFAULT_BRIGHTNESS: int = int(os.getenv("DEFAULT_BRIGHTNESS", "50"))
    
    # NLP Settings
    NLP_CONFIDENCE_THRESHOLD: float = float(os.getenv("NLP_CONFIDENCE_THRESHOLD", "0.7"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Create global settings instance
settings = Settings()