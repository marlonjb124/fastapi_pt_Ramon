from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI PT"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    OAUTH2_SCHEME: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl=f"{API_V1_STR}/auth/login")
    # Database configuration
    DB_USER: str = os.getenv("DB_USER", "fastapi")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "fastapi-password")
    DB_HOST: str = os.getenv("DB_HOST", "fastapi-postgresql:5432")
    DB_NAME: str = os.getenv("DB_NAME", "fastapi")
    DATABASE_URL: Optional[str] = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    # JWT configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cambiarsecreto")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Instancia global de configuración
settings = Settings()