import os
from pathlib import Path


class AIConfig:
    # ChromaDB Configuration
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    CHROMA_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "vector_db"

    # Embedding Configuration
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # FastEmbed model
    EMBEDDING_DIMENSION = 384  # Dimension for the chosen model

    # Collection Names
    REVIEWS_COLLECTION = "laptop_reviews"
    QA_COLLECTION = "laptop_qa"

    # Search Configuration
    MAX_SEARCH_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7

    # LLM Configuration (for Phase 3)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = "gpt-4"
    FALLBACK_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        Path(cls.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
