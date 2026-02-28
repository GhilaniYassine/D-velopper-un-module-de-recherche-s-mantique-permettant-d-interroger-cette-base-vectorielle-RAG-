import logging
import math
from typing import Iterable, Sequence


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with a consistent configuration.
    """
    logger = logging.getLogger(name)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logger


def to_pgvector(embedding: Sequence[float]) -> str:
    """
    Convert a sequence of floats to a PostgreSQL pgvector literal.
    """
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"


def parse_embedding(text: str) -> Sequence[float]:
    """
    Parse a comma-separated embedding representation from SQLite.
    """
    return [float(x) for x in text.split(",") if x]


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    a_list = list(a)
    b_list = list(b)
    if len(a_list) != len(b_list):
        raise ValueError("Vectors must have the same dimension for cosine similarity.")

    dot = sum(x * y for x, y in zip(a_list, b_list))
    norm_a = math.sqrt(sum(x * x for x in a_list))
    norm_b = math.sqrt(sum(y * y for y in b_list))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


