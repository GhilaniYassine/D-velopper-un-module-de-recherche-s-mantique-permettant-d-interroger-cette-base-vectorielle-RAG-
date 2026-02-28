from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from .config import settings
from .utils import get_logger


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """
    Lazily load and cache the embedding model.
    """
    logger.info("Loading embedding model: %s", settings.embedding_model_name)
    model = SentenceTransformer(settings.embedding_model_name)
    return model


def encode_text(text: str) -> List[float]:
    """
    Generate a 384-dimensional embedding for the given text.
    """
    if not text or not text.strip():
        raise ValueError("Text to embed must be a non-empty string.")

    model = _get_model()
    embedding = model.encode(
        [text],
        convert_to_numpy=True,
    )[0]
    return embedding.tolist()

