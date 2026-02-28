# 🧠 Semantic Search Module with ChromaDB

**Production-ready semantic search and document ingestion system** using ChromaDB vector store, sentence transformers, and FastAPI.

## 🎯 Overview

This system implements a complete RAG (Retrieval-Augmented Generation) **retrieval** pipeline supporting:
- **Document Ingestion**: Add documents to the vector store dynamically
- **Semantic Search**: Query documents using natural language similarity
- **REST API**: FastAPI endpoints for search and ingestion
- **Web Interface**: Interactive frontend with real-time results

## 🏗 Architecture (per agent.md specifications)

### Technology Stack
- **Vector Store**: ChromaDB (persistent, easy to use)
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions, Sentence-Transformers)
- **Similarity**: Cosine similarity (in ChromaDB)
- **API**: FastAPI + Uvicorn
- **Database**: Persistent ChromaDB at `data/chroma_db/`

### Key Features
✅ **Dynamic document ingestion** via REST API or CLI  
✅ **Semantic search** with top-3 results  
✅ **Web interface** for interactive queries  
✅ **CLI support** for batch operations  
✅ **Status monitoring** (`/status` endpoint)  
✅ **Health checks** (`/healthz` endpoint)  

---

## 📦 Setup & Installation

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# .env defaults are already configured for local development
```

---

## 🚀 Running the System

### Option A: Start FastAPI Server (Full System)

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ **Open in browser**: http://localhost:8000  
✅ **API documentation**: http://localhost:8000/docs (Swagger UI)  
✅ **Alternative docs**: http://localhost:8000/redoc (ReDoc)  

### Option B: CLI Mode

#### Search
```bash
python3 -m app.main search -q "What are the recommended dosages for alpha-amylase?"
```

JSON output:
```bash
python3 -m app.main search -q "..." --json
```

#### Ingest from Folder
```bash
python3 -m app.main ingest --folder data/enzymes/
```

#### Check Status
```bash
python3 -m app.main status
```

#### Standalone Ingestion Script
```bash
python3 ingest_documents.py
```

---

## 🔌 API Endpoints

### Search (Semantic Retrieval)
**POST** `/search`

Request:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"question":"What is alpha-amylase used for?"}'
```

Response:
```json
{
  "results": [
    {
      "id": 1,
      "id_document": 1,
      "texte_fragment": "Alpha-Amylase (AMY1) - Baking Enzyme...",
      "score": 0.8601
    }
  ]
}
```

### Ingest Documents
**POST** `/ingest`

Request:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc_1",
        "text": "Your document text here..."
      }
    ]
  }'
```

Response:
```json
{
  "status": "success",
  "documents_ingested": 1
}
```

### Status Check
**GET** `/status`

```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "status": "healthy",
  "total_documents": 4,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### Health Check
**GET** `/healthz`

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{"status": "ok"}
```

---

## 📁 Project Structure

```
challenge/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + CLI
│   ├── config.py            # Settings & environment
│   ├── database.py          # ChromaDB wrapper
│   ├── embeddings.py        # Sentence-Transformers integration
│   ├── search_service.py    # Business logic for search/ingest
│   └── utils.py             # Helper utilities
├── data/
│   ├── enzymes/             # Document folder (4 sample documents)
│   │   ├── alpha_amylase.txt
│   │   ├── xylanase.txt
│   │   ├── ascorbic_acid.txt
│   │   └── benzoyl_peroxide.txt
│   └── chroma_db/           # Vector store (auto-created)
├── templates/
│   └── index.html           # Web frontend
├── static/                  # (Empty, for future static assets)
├── ingest_documents.py      # Standalone ingestion script
├── .env                     # Local configuration
├── .env.example             # Configuration template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🧪 How It Works

### 1. **Document Ingestion Flow**

```
.txt files in data/enzymes/
    ↓
ingest_documents.py (reads files)
    ↓
sentence-transformers (generates 384-dim embeddings)
    ↓
ChromaDB (stores embeddings + text)
    ↓
Vector store ready for search
```

### 2. **Semantic Search Flow**

```
User query in web interface (or API call)
    ↓
FastAPI /search endpoint
    ↓
sentence-transformers (generates query embedding)
    ↓
ChromaDB cosine similarity search
    ↓
Top 3 results with scores
    ↓
JSON response to frontend
    ↓
Display in web interface
```

---

## 📊 Sample Documents

The system includes 4 pre-configured sample bakery/enzyme documents:

1. **alpha_amylase.txt** - Enzyme dosing (50-300 ppm) and functions
2. **xylanase.txt** - Hemicellulase enzyme for bread quality
3. **ascorbic_acid.txt** - Oxidizing agent for dough conditioning
4. **benzoyl_peroxide.txt** - Flour bleaching and dough improver

These are automatically ingested on first run via `ingest_documents.py`.

---

## 🔧 Configuration

Edit `.env` to customize:

```bash
# Vector store backend
DB_BACKEND=chroma

# ChromaDB storage path (relative or absolute)
CHROMA_DB_PATH=data/chroma_db

# Embedding model (MANDATORY - do not change per spec)
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

---

## ⚡ Performance Notes

- **First search**: ~12 seconds (model loading, caching afterwards)
- **Subsequent searches**: ~1-2 seconds
- **Embedding generation**: All-MiniLM-L6-v2 handles 384D embeddings efficiently
- **Vector store**: ChromaDB uses HNSW for fast similarity search

---

## 🧪 Testing

### Test Search Functionality
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"question":"Recommended dosages for enzyme improvers?"}'
```

### Test Ingestion
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents":[{"id":"test","text":"New enzyme document..."}]}'
```

### Verify Results
```bash
curl http://localhost:8000/status
```

---

## 📝 Agent.md Requirements Met

✅ Embedding model: `all-MiniLM-L6-v2` (384 dimensions)  
✅ Similarity: Cosine similarity  
✅ Top K: 3 results  
✅ Clean modular architecture  
✅ Production-ready code  
✅ Error handling + logging  
✅ CLI interface + REST API  
✅ Config management with .env  
✅ Document ingestion pipeline  

---

## 🐛 Troubleshooting

### Server won't start
```bash
lsof -i :8000  # Check if port is in use
```

### Embedding model not downloading
- First run automatically downloads the model (~100MB)
- Ensure internet connectivity

### ChromaDB directory error
```bash
mkdir -p data/chroma_db
```

### Search returns no results
```bash
# Ensure documents are ingested
curl http://localhost:8000/status

# If needed, ingest documents
python3 ingest_documents.py
```

---

## 📚 Resources

- [ChromaDB](https://docs.trychroma.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

---

**Built for bakery & pastry formulation RAG assistance** ✨
