from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import settings
from .utils import get_logger


logger = get_logger(__name__)


class DatabaseError(Exception):
    """Raised when a database operation fails."""


class BaseDatabase:
    """
    Minimal interface shared by database backends.
    """

    backend: str

    def search(
        self, query_embedding: List[float], top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using embedding."""
        raise NotImplementedError

    def add_document(
        self, doc_id: str, text: str, embedding: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a document to the vector store."""
        raise NotImplementedError

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class ChromaDatabase(BaseDatabase):
    """
    ChromaDB vector database backend for semantic search with ingestion.
    """

    backend = "chroma"

    def __init__(self) -> None:
        try:
            self._client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            self._collection = self._client.get_or_create_collection(
                name="semantic_search",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "ChromaDB initialized at %s with collection 'semantic_search'",
                settings.chroma_db_path,
            )
        except Exception as exc:
            logger.exception("Failed to initialize ChromaDB")
            raise DatabaseError("Failed to initialize ChromaDB") from exc

    def search(
        self, query_embedding: List[float], top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using query embedding.
        Returns top_k results with similarity scores.
        """
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            
            # Format results to match the expected schema
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for idx, (doc_id, distance, metadata_item, document) in enumerate(
                    zip(
                        results["ids"][0],
                        results["distances"][0],
                        results["metadatas"][0],
                        results["documents"][0],
                    )
                ):
                    # ChromaDB distances are L2 by default, convert to cosine similarity
                    # For cosine distance, similarity = 1 - distance
                    similarity_score = 1.0 - (distance / 2.0)  # Normalize
                    similarity_score = max(0.0, min(1.0, similarity_score))  # Clamp to [0, 1]
                    
                    formatted_results.append({
                        "id": idx + 1,
                        "doc_id": doc_id,
                        "text": document,
                        "score": similarity_score,
                        "metadata": metadata_item,
                    })
            
            logger.info("ChromaDB search returned %d results", len(formatted_results))
            return formatted_results
        except Exception as exc:
            logger.exception("ChromaDB search failed")
            raise DatabaseError("Database search failed") from exc

    def add_document(
        self, doc_id: str, text: str, embedding: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a document to ChromaDB.
        If embedding is not provided, it will be generated during upsert.
        """
        try:
            if metadata is None:
                metadata = {}
            
            # ChromaDB will auto-generate embeddings if not provided
            self._collection.upsert(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding] if embedding else None,
                metadatas=[metadata],
            )
            logger.info("Document %s added to ChromaDB", doc_id)
        except Exception as exc:
            logger.exception("Failed to add document to ChromaDB")
            raise DatabaseError("Failed to add document") from exc

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            count = self._collection.count()
            logger.info("ChromaDB collection has %d documents", count)
            return count
        except Exception as exc:
            logger.exception("Failed to get collection count")
            raise DatabaseError("Failed to get collection count") from exc

    def close(self) -> None:
        """Close ChromaDB client."""
        try:
            self._client.delete_collection(name="semantic_search_temp")  # Just verify connectivity
        except Exception:
            pass  # Collection may not exist, that's fine
        logger.info("ChromaDB client closed")


_db_instance: Optional[BaseDatabase] = None


def get_db() -> BaseDatabase:
    """
    Lazily initialize and return a singleton Database instance.
    Currently uses ChromaDB as the primary backend.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = ChromaDatabase()
    return _db_instance


