from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    """
    Configurações da aplicação
    Carrega valores de variáveis de ambiente ou .env
    """

    # Application
    APP_NAME: str = "Mobistory Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://mobistory:mobistory_dev_password@localhost:5432/mobistory_db"

    # JWT
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias

    # OpenAI
    OPENAI_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8081",
        "http://localhost:19006",
        "exp://192.168.1.100:8081",
    ]

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
