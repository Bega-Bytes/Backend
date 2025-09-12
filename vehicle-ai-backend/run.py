#!/usr/bin/env python3
"""
Startup script for Vehicle AI Backend
"""

import uvicorn
from config import settings
import logging
logging.raiseExceptions = False

if __name__ == "__main__":
    print("🚗 Starting Vehicle AI Backend...")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔌 WebSocket: ws://{settings.HOST}:{settings.PORT}/ws")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )