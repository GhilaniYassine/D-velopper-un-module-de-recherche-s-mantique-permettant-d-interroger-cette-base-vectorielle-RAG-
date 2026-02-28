
## 🚀 Quick Start with Makefile (Recommended)

You can run, set up, and configure the project easily using the provided **Makefile**:

```bash
make setup   # Installs dependencies and prompts for your Gemini API key
make run     # Starts the FastAPI server at http://localhost:8000
```

**Why set the Gemini API key?**

For the best semantic retrieval results, including advanced query rewriting and response reformulation, you should provide your Gemini API key when prompted during `make setup` (or by running `make api-key`). This enables the system to use Google Gemini for smarter, more accurate answers.

If you skip the API key, the system will still work, but without enhanced LLM-powered query rewriting.

# 🧠 Semantic Search Module with ChromaDB - RAG System

**Production-ready semantic search and document ingestion system** using ChromaDB vector store, sentence transformers, and FastAPI.

---

## 🚀 Quick Start - How to Run the Project

### **Prerequisites**
- Python 3.8+ and pip installed
- Virtual environment (recommended)

### **Step 1: Activate Environment**
```bash
source env/bin/activate  # Linux/Mac
# or
env\Scripts\activate     # Windows
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Run the FastAPI Server**
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Open in browser**: 🌐 http://localhost:8000  
**Swagger API Docs**: 📖 http://localhost:8000/docs  

### **Alternative: Run in CLI Mode**
```bash
# Search from command line
python3 -m app.main search -q "Recommended dosages for alpha-amylase?"

# Ingest documents
python3 -m app.main ingest --folder data/enzymes/

# Check system status
python3 -m app.main status
```

---

## ✨ Why This Project is Excellent

### 🎯 **Solves Real Business Problems**
- Enables bakery/pastry professionals to quickly find relevant ingredient information
- Reduces time spent searching through technical documentation
- Improves formulation accuracy with AI-powered semantic understanding
- Supports multilingual queries with embedding models

### 🔐 **Enterprise-Ready Architecture**
- **Modular design**: Clean separation of concerns (database, embeddings, search, API)
- **Type-safe**: Full type hints for better code maintainability
- **Error handling**: Robust exception handling across all components
- **Logging**: Comprehensive logging for debugging and monitoring
- **Configuration management**: Environment-based settings via `.env`

### ⚡ **High Performance**
- **Fast inference**: All-MiniLM-L6-v2 model optimized for speed (~1-2s per query)
- **HNSW indexing**: Efficient vector similarity search via ChromaDB
- **Caching**: Model loaded once, reused for subsequent queries
- **Scalable**: Supports thousands of documents without performance degradation

### 🎨 **User-Friendly**
- **Web interface**: Interactive UI for non-technical users
- **REST API**: Programmatic access for integrations
- **CLI mode**: Command-line interface for automation/scripting
- **Real-time results**: Instant semantic search with similarity scores

### 📊 **Complete RAG Pipeline**
- **Document ingestion**: Automated vectorization of text documents
- **Semantic search**: Cosine similarity-based retrieval
- **Scoring**: Transparent similarity metrics (0-1 scale)
- **Top-K results**: Configurable result ranking (default: top 3)

### 🔍 **Transparent & Auditable**
- Open-source dependencies (no proprietary black boxes)
- All embeddings generated locally
- Search logic is understandable and debuggable
- Full result scoring visible to users

---

## 📋 Project Context: "Automatic Zoom" - Intelligent Bakery Formulation Assistant

### **Business Objective**
Develop an intelligent assistant system for bakery and pastry professionals to query technical documentation about ingredients, additives, and processing parameters using natural language.

### 🎯 Overview

This system implements a complete RAG (Retrieval-Augmented Generation) **retrieval** pipeline supporting:
- **Document Ingestion**: Add documents to the vector store dynamically
- **Semantic Search**: Query documents using natural language similarity
- **REST API**: FastAPI endpoints for search and ingestion
- **Web Interface**: Interactive frontend with real-time results
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

## � Project Requirements & Specifications

### **Provided Resources (Constraints & Prerequisites)**

#### **1. Embedding Model (MANDATORY)**
- **Model**: `all-MiniLM-L6-v2`
- **Source**: Sentence-Transformers
- **Dimensions**: 384
- **Requirement**: Both document embeddings and query embeddings MUST use this model
- **Why**: Ensures consistent vector space between stored and query embeddings

#### **2. Similarity Metric (MANDATORY)**
- **Method**: Cosine Similarity
- **Result Range**: 0 to 1 (where 1 = perfect match)
- **Calculation**: Done by ChromaDB automatically
- **Requirement**: All similarity scores returned to users must be cosine-based

#### **3. Search Results Configuration (MANDATORY)**
- **Top-K Value**: 3 results
- **Ordering**: Results ranked by score (highest to lowest)
- **Requirement**: Always return top 3 most relevant fragments per query
- **Flexibility**: Can be extended to return more, but minimum 3 required

#### **4. Language Requirement**
- **Recommended**: Python 3.8+
- **Rationale**: Ecosystem compatibility (Sentence-Transformers, ChromaDB, FastAPI)
- **Requirement**: Full project implemented in Python

#### **5. Data Structure Requirements**
The vector database must maintain the following structure:

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID | Unique embedding identifier |
| `id_document` | Integer | References source document |
| `texte_fragment` | Text | The actual document chunk/fragment |
| `vecteur` | VECTOR(384) | Embedded representation (384-dim) |
| Metadata | JSON | Document source, chunk index, etc. |

---

## ✅ Requirements Achievement Matrix

### **Requirement 1: Receive User Questions**
- ✅ **Web Interface**: Text input field in `templates/index.html`
- ✅ **REST API**: `/search` POST endpoint accepts `{"question": "..."}`
- ✅ **CLI**: `python3 -m app.main search -q "..."`
- **Implementation**: `app/main.py` + `app/search_service.py`

### **Requirement 2: Generate Query Embeddings**
- ✅ **Model**: Uses `all-MiniLM-L6-v2` exclusively
- ✅ **Dimension**: Produces 384-dimensional vectors
- ✅ **Consistency**: Same model for documents and queries
- **Implementation**: `app/embeddings.py` → `sentence_transformers.SentenceTransformer`

### **Requirement 3: Calculate Cosine Similarity**
- ✅ **Method**: Cosine similarity via ChromaDB
- ✅ **Comparison**: Query embedding vs. all stored embeddings
- ✅ **Efficiency**: HNSW index for fast approximate search
- **Implementation**: `app/database.py` → ChromaDB's `.query()` method

### **Requirement 4: Rank Results by Score**
- ✅ **Ordering**: Automatic (ChromaDB returns results sorted by relevance)
- ✅ **Score Format**: Float (0.0 - 1.0)
- ✅ **Transparency**: Scores displayed to users
- **Implementation**: `app/search_service.py` → `search()` method

### **Requirement 5: Return Top 3 Fragments**
- ✅ **Count**: Exactly 3 results per query
- ✅ **Format**: JSON with text and scores
- ✅ **Flexibility**: Configurable via code (currently hardcoded to 3)
- **Implementation**: `app/database.py` → `top_k = 3`

### **Requirement 6: Display Results**
- ✅ **Fragment Text**: Full text of matched chunk
- ✅ **Similarity Score**: Decimal score (e.g., 0.91)
- ✅ **Format**: Both JSON API and web UI
- **Implementation**: `templates/index.html` for display, `app/main.py` for API

---

## 📊 Example Usage & Expected Output

### **User Query**
```
"Améliorant de panification : quelles sont les quantités recommandées d'alpha-amylase, 
xylanase et d'Acide ascorbique ?"
```

### **Expected Results**
```json
{
  "results": [
    {
      "id": "chunk_1",
      "id_document": 1,
      "texte_fragment": "Dosage recommandé : 0.005% à 0.02% du poids de farine.",
      "score": 0.91
    },
    {
      "id": "chunk_2",
      "id_document": 2,
      "texte_fragment": "Alpha-amylase : utilisation entre 5 et 20 ppm selon la farine.",
      "score": 0.87
    },
    {
      "id": "chunk_3",
      "id_document": 3,
      "texte_fragment": "Xylanase : améliore l'extensibilité de la pâte...",
      "score": 0.82
    }
  ]
}
```

---


## 📦 Setup & Installation (Local Development)

### 1. Create Virtual Environment (Already Done)
The virtual environment is already set up in `env/` folder. Just activate it:

```bash
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 2. Install Dependencies (Already Done)
If needed again:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Pre-configured)
Configuration is already set in `.env` for local development testing.

---

## 🚀 Running the System (Detailed Options)

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
