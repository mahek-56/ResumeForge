"""
Application Configuration
SAMATRIX RESUMEFORGE 2026
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResumeForge AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DESCRIPTION: str = "AI-powered resume classification and profile intelligence platform"
    
    # CORS settings - allows frontend dev server
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # File limits
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}

settings = Settings()
