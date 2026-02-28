#!/usr/bin/env python3
"""
Ingestion script to load documents from data/enzymes/ into the vector store.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.search_service import search_service
from app.utils import get_logger

logger = get_logger(__name__)

def ingest_documents_from_folder(folder_path: str) -> int:
    """
    Load all .txt files from a folder and ingest them into the vector store.
    """
    folder = Path(folder_path)
    if not folder.exists():
        logger.error("Folder does not exist: %s", folder_path)
        return 1
    
    if not folder.is_dir():
        logger.error("Path is not a directory: %s", folder_path)
        return 1
    
    # Find all .txt files
    txt_files = sorted(folder.glob("*.txt"))
    if not txt_files:
        logger.warning("No .txt files found in %s", folder_path)
        return 0
    
    logger.info("Found %d documents to ingest", len(txt_files))
    
    ingested_count = 0
    for idx, file_path in enumerate(txt_files, start=1):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            doc_id = file_path.stem
            search_service.add_document(
                doc_id=doc_id,
                text=text,
                id_document=idx,
            )
            logger.info("[%d/%d] Ingested: %s (%d chars)", idx, len(txt_files), doc_id, len(text))
            ingested_count += 1
        except Exception as exc:
            logger.error("[%d/%d] Failed to ingest %s: %s", idx, len(txt_files), file_path.stem, exc)
    
    logger.info("Successfully ingested %d/%d documents", ingested_count, len(txt_files))
    
    # Check total count
    try:
        total_count = search_service.get_collection_count()
        logger.info("Vector store now contains %d total documents", total_count)
    except Exception as exc:
        logger.error("Failed to get collection count: %s", exc)
    
    return 0 if ingested_count == len(txt_files) else 1

if __name__ == "__main__":
    folder = "data/enzymes"
    logger.info("Starting ingestion from %s...", folder)
    sys.exit(ingest_documents_from_folder(folder))
