# ai_service/src/core/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Components
    DB_USER: str = "myuser"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "laptops_db"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # AI Configuration
    DEFAULT_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1000

    # Vector Database - Point to backend's vector_db
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
    CHROMA_PERSIST_DIRECTORY: Path = PROJECT_ROOT / "backend" / "data" / "vector_db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Collection Names
    REVIEWS_COLLECTION: str = "laptop_reviews"
    QA_COLLECTION: str = "laptop_qa"

    # Search Configuration
    MAX_SEARCH_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # Constructed Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        extra = "ignore"  # This fixes the validation error


settings = Settings()
