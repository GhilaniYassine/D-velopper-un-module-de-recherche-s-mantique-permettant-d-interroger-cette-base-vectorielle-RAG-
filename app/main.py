import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .database import DatabaseError, get_db
from .search_service import SearchResult, search_service
from .utils import get_logger


logger = get_logger(__name__)

app = FastAPI(
    title="Semantic Search Module with Gemini Enhancement",
    description="Semantic search with document ingestion and Gemini-powered query optimization and response reformulation.",
    version="2.0.0",
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural language question")
    use_gemini: bool = Field(True, description="Use Gemini for query enhancement and response reformulation")


class IngestRequest(BaseModel):
    documents: List[Dict[str, str]] = Field(
        ..., description="List of documents with 'id' and 'text' keys"
    )


class SearchResponseItem(BaseModel):
    id: int
    id_document: int
    texte_fragment: str
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResponseItem]
    reformulated_response: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    total_documents: int
    embedding_model: str


class IngestResponse(BaseModel):
    status: str
    documents_ingested: int


def _format_cli_results(results: List[SearchResult]) -> str:
    if not results:
        return "No results found.\n"

    lines: List[str] = []
    for idx, r in enumerate(results, start=1):
        lines.append(f"Result {idx}")
        lines.append(f"Text: {r.text}")
        lines.append(f"Score: {r.score:.4f}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """
    Simple HTML frontend to query the semantic search service.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_model=SearchResponse)
def search_endpoint(payload: SearchRequest) -> SearchResponse:
    """
    Search for semantically similar documents with optional Gemini enhancement.
    
    When use_gemini=true:
    1. Enhance query using Gemini for better semantic matching
    2. Perform semantic search
    3. Reformulate response using Gemini for better presentation
    """
    try:
        if payload.use_gemini:
            # Get results and reformulated response
            results, reformulated = search_service.search_with_reformulation(
                payload.question, use_gemini=True
            )
        else:
            # Get only results without Gemini
            results = search_service.search(payload.question, use_gemini=False)
            reformulated = None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Vector store unavailable")

    items = [
        SearchResponseItem(
            id=r.id,
            id_document=r.id_document,
            texte_fragment=r.text,
            score=r.score,
        )
        for r in results
    ]
    return SearchResponse(results=items, reformulated_response=reformulated)


@app.post("/ingest", response_model=IngestResponse)
def ingest_endpoint(payload: IngestRequest) -> IngestResponse:
    """
    Ingest documents into the vector store.
    Expects a list of documents with 'id' and 'text' keys.
    """
    if not payload.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    try:
        count = 0
        for doc in payload.documents:
            if "id" not in doc or "text" not in doc:
                raise ValueError("Each document must have 'id' and 'text' keys")
            
            search_service.add_document(
                doc_id=doc["id"],
                text=doc["text"],
                id_document=int(doc.get("id_document", 0)),
            )
            count += 1
        
        return IngestResponse(
            status="success",
            documents_ingested=count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Vector store unavailable")


@app.get("/status", response_model=StatusResponse)
def status_endpoint() -> StatusResponse:
    """
    Get the status of the semantic search service.
    """
    try:
        from .config import settings
        count = search_service.get_collection_count()
        return StatusResponse(
            status="healthy",
            total_documents=count,
            embedding_model=settings.embedding_model_name,
        )
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Vector store unavailable")


@app.get("/healthz")
def healthcheck() -> Dict[str, Any]:
    """
    Lightweight health endpoint.
    """
    try:
        _ = get_db()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover
        logger.warning("Healthcheck failed: %s", exc)
        return {"status": "degraded", "error": str(exc)}


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="semantic-search",
        description="Semantic search CLI with document ingestion and Gemini enhancement.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument(
        "-q",
        "--question",
        required=True,
        help="Natural language question to search for",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    search_parser.add_argument(
        "--no-gemini",
        action="store_true",
        help="Disable Gemini query enhancement and response reformulation",
    )
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument(
        "--folder",
        required=True,
        help="Folder containing documents to ingest",
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get service status")
    
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point for the semantic search system.
    """
    args = _parse_args(argv)
    
    if args.command == "search":
        try:
            use_gemini = not args.no_gemini
            results, reformulated = search_service.search_with_reformulation(
                args.question, use_gemini=use_gemini
            )
        except ValueError as exc:
            logger.error("%s", exc)
            return 2
        except DatabaseError as exc:
            logger.error("%s", exc)
            return 3

        if args.json:
            payload = {
                "results": [
                    {
                        "id": r.id,
                        "id_document": r.id_document,
                        "texte_fragment": r.text,
                        "score": r.score,
                    }
                    for r in results
                ]
            }
            if reformulated:
                payload["reformulated_response"] = reformulated
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if reformulated:
                print("\n" + "="*60)
                print("REFORMULATED RESPONSE:")
                print("="*60 + "\n")
                print(reformulated)
                print("\n" + "="*60)
                print("RAW SEARCH RESULTS:")
                print("="*60 + "\n")
            print(_format_cli_results(results), end="")
        return 0
    
    elif args.command == "ingest":
        try:
            folder_path = Path(args.folder)
            if not folder_path.exists():
                logger.error("Folder %s does not exist", args.folder)
                return 1
            
            doc_count = 0
            for file_path in folder_path.glob("*.txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                
                doc_id = file_path.stem
                search_service.add_document(
                    doc_id=doc_id,
                    text=text,
                    id_document=doc_count + 1,
                )
                doc_count += 1
                logger.info("Ingested document: %s", doc_id)
            
            logger.info("Successfully ingested %d documents", doc_count)
            return 0
        except DatabaseError as exc:
            logger.error("%s", exc)
            return 3
    
    elif args.command == "status":
        try:
            count = search_service.get_collection_count()
            print(f"Vector store contains {count} documents")
            return 0
        except DatabaseError as exc:
            logger.error("%s", exc)
            return 3
    
    else:
        print("Please specify a command: search, ingest, or status")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

