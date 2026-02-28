"""
Gemini LLM service for query enhancement and response reformulation.
"""

from typing import List, Dict, Any

import google.generativeai as genai

from .config import settings
from .utils import get_logger


logger = get_logger(__name__)


class GeminiService:
    """
    Service for LLM-based query enhancement and response reformulation using Google Gemini.
    """

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured; LLM features will be disabled")
            self._client = None
        else:
            genai.configure(api_key=settings.gemini_api_key)
            self._client = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                ),
            )
            logger.info("Gemini service initialized successfully with model: gemini-1.5-flash")

    def _is_available(self) -> bool:
        """Check if Gemini client is available."""
        return self._client is not None

    def enhance_query(self, original_query: str) -> str:
        """
        Rewrite and enhance the user's query to be more suitable for semantic search.
        
        System Message: Optimized for query reformulation with focus on bakery/pastry domain.
        """
        if not self._is_available():
            logger.warning("Gemini not available; returning original query")
            return original_query

        system_prompt = """You are a specialized query optimizer for bakery and pastry ingredient formulation systems.

Your task is to take a user's natural language question and rewrite it to be more suitable for semantic search 
over technical bakery documentation. The rewritten query should:

1. Include specific technical terminologies used in bakery science (enzymes, improvers, ppm dosages, etc.)
2. Expand abbreviations and implicit references
3. Emphasize key technical aspects that would match technical documents
4. Remove casual language and focus on precise, technical phrasing
5. Include relevant domain context around enzyme names, compounds, and formulation parameters

Guidelines:
- If the user asks about "enzyme", specify which enzyme (amylase, xylanase, etc.) if detectable from context
- Always mention dosage units (ppm, percentage, g/kg) if relevant to the query
- Expand functions like "improve" to technical outcomes (crumb structure, fermentation, extensibility, etc.)
- Keep the query concise but technically precise
- Maintain the user's original intent while enhancing technical clarity

Return ONLY the rewritten query. Do not include explanations or additional text."""

        try:
            response = self._client.generate_content(
                f"{system_prompt}\n\nUser's original query: {original_query}",
                stream=False,
            )
            
            enhanced_query = response.text.strip()
            logger.info("Query enhanced: '%s' -> '%s'", original_query[:50], enhanced_query[:50])
            return enhanced_query
        except Exception as exc:
            logger.error("Failed to enhance query with Gemini: %s", exc)
            return original_query

    def reformulate_response(self, retrieved_fragments: List[str], original_query: str) -> str:
        """
        Reformat the retrieved search results into a well-structured, user-friendly response.
        
        System Message: Optimized for response formatting with focus on clarity and presentation.
        """
        if not self._is_available():
            logger.warning("Gemini not available; returning raw fragments")
            return self._format_fragments_plain(retrieved_fragments)

        # Prepare the fragments with ranking
        formatted_fragments = "\n\n---\n\n".join(
            [f"**Result {idx + 1}:**\n{fragment}" 
             for idx, fragment in enumerate(retrieved_fragments)]
        )

        system_prompt = """You are a professional technical documentation formatter specializing in bakery science.

Your task is to take raw retrieved technical documents about bakery ingredients and reformulate them into 
a clear, well-structured response that directly answers the user's question.

Instructions:
1. Synthesize information from the retrieved fragments to create a cohesive answer
2. Organize the response with clear sections (Dosage, Functions, Applications, etc.)
3. Highlight key numerical values (ppm, percentages, temperatures) in bold
4. Use bullet points for lists of benefits, functions, or applications
5. Extract and emphasize information most relevant to the user's original question
6. Maintain technical accuracy while improving readability
7. Avoid redundant information across fragments
8. End with a brief practical summary if appropriate

Format the response in clean Markdown with:
- Clear headers for each section
- Bold for important values and technical terms
- Bullet points for lists
- Proper spacing and structure

Return ONLY the reformatted response in Markdown. Do not include metadata or fragments source information."""

        try:
            response = self._client.generate_content(
                f"{system_prompt}\n\n"
                f"User's question: {original_query}\n\n"
                f"Retrieved technical documents:\n\n{formatted_fragments}",
                stream=False,
            )
            
            reformulated = response.text.strip()
            logger.info("Response reformulated successfully (%d chars)", len(reformulated))
            return reformulated
        except Exception as exc:
            logger.error("Failed to reformulate response with Gemini: %s", exc)
            return self._format_fragments_plain(retrieved_fragments)

    @staticmethod
    def _format_fragments_plain(fragments: List[str]) -> str:
        """Fallback plain text formatting if Gemini is unavailable."""
        lines = []
        for idx, fragment in enumerate(fragments, start=1):
            lines.append(f"## Result {idx}\n")
            lines.append(fragment)
            lines.append("\n")
        return "\n".join(lines)


# Global instance
gemini_service = GeminiService()
