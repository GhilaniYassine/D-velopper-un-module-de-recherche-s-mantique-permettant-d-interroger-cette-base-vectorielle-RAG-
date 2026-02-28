from dataclasses import dataclass
from typing import List

from .config import settings
from .database import DatabaseError, get_db
from .embeddings import encode_text
from .gemini_service import gemini_service
from .utils import get_logger


logger = get_logger(__name__)


@dataclass
class SearchResult:
    id: int
    id_document: int
    text: str
    score: float


class SemanticSearchService:
    """
    High-level service responsible for semantic search using ChromaDB vector store.
    Integrates Gemini for query enhancement and response reformulation.
    """

    def __init__(self) -> None:
        self._top_k = settings.top_k

    def search(self, question: str, use_gemini: bool = True) -> List[SearchResult]:
        """
        Perform semantic search for the given natural-language question.
        
        Steps:
        1. (Optional) Enhance query using Gemini for better semantic matching
        2. Generate embedding for the (possibly enhanced) query
        3. Search in ChromaDB
        4. Return top-K results
        """
        question = (question or "").strip()
        if not question:
            raise ValueError("Question must be a non-empty string.")

        # Step 1: Enhance query using Gemini if enabled
        search_query = question
        if use_gemini:
            logger.info("Enhancing query with Gemini for better semantic matching")
            search_query = gemini_service.enhance_query(question)
            if search_query != question:
                logger.info("Original query: %s", question)
                logger.info("Enhanced query: %s", search_query)

        logger.info("Starting semantic search with top_k=%d", self._top_k)
        
        try:
            # Step 2: Generate embedding for the (enhanced) query
            embedding = encode_text(search_query)
            logger.info("Generated embedding for question")
            
            # Step 3: Search in ChromaDB
            db = get_db()
            results_data = db.search(embedding, top_k=self._top_k)
            
            # Convert to SearchResult objects
            results: List[SearchResult] = []
            for r in results_data:
                results.append(
                    SearchResult(
                        id=r["id"],
                        id_document=int(r.get("metadata", {}).get("id_document", 0)),
                        text=r["text"],
                        score=float(r["score"]),
                    )
                )
            
            if not results:
                logger.info("Search returned no results")
            else:
                logger.info("Search returned %d results", len(results))

            return results
        except DatabaseError:
            logger.exception("Semantic search failed due to database error")
            raise

    def search_with_reformulation(self, question: str, use_gemini: bool = True) -> tuple:
        """
        Perform semantic search and reformulate the response using Gemini.
        
        Returns:
            Tuple of (results, reformulated_response)
        """
        # Step 1 & 2 & 3: Get search results
        results = self.search(question, use_gemini=use_gemini)
        
        # Step 4: Reformulate response using Gemini if available and we have results
        reformulated_response = None
        if use_gemini and results:
            logger.info("Reformulating response with Gemini")
            fragment_texts = [r.text for r in results]
            reformulated_response = gemini_service.reformulate_response(
                fragment_texts, question
            )
        
        return results, reformulated_response

    def add_document(self, doc_id: str, text: str, id_document: int = 0) -> None:
        """
        Add a document to the vector store.
        The embedding will be generated automatically by ChromaDB.
        """
        try:
            db = get_db()
            db.add_document(
                doc_id=doc_id,
                text=text,
                metadata={"id_document": id_document},
            )
            logger.info("Document %s added to vector store", doc_id)
        except DatabaseError:
            logger.exception("Failed to add document")
            raise

    def get_collection_count(self) -> int:
        """Get the number of documents in the vector store."""
        try:
            db = get_db()
            count = db.get_collection_count()
            logger.info("Vector store contains %d documents", count)
            return count
        except DatabaseError:
            logger.exception("Failed to get collection count")
            raise


search_service = SemanticSearchService()

