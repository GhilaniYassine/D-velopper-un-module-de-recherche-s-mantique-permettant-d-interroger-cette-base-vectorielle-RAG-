import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    """
    Application configuration loaded from environment variables or .env file.
    """

    # Vector store backend: "chroma" for ChromaDB (default)
    db_backend: str = os.getenv("DB_BACKEND", "chroma").lower()

    # ChromaDB settings
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "data/chroma_db")

    # Embedding model (must be all-MiniLM-L6-v2 per spec)
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"
    )

    # Search parameters (Top K = 3 per spec)
    top_k: int = 3

    # Gemini API Configuration for LLM-based query and response reformulation
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()

