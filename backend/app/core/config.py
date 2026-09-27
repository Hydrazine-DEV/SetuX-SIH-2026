"""
SetuX / VeriX — Core Configuration & Environment Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    PROJECT_NAME: str = "SetuX / VeriX — Infrastructure Monitoring & Intelligence Platform"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "verix-setux-sih2026-authentication-secret-key-32bytes")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/setux.db")
    
    # Storage / Uploads
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]
    
    DEMO_MODE: bool = True

    class Config:
        case_sensitive = True
        extra = "allow"


settings = Settings()
