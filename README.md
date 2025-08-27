# 📦 Data Pipeline with Traceability

A FastAPI-based prototype ingestion and traceability pipeline to create and manage a **document vector store** from multiple document types. Built for traceability with metadata and supports vector similarity search.

---

## 🚀 Tech Stack

- **FastAPI** – API framework
- **ChromaDB** – Vector store backend
- **LangChain** – Document loaders, splitters, and retrieval logic
- **Hugging Face & OpenAI** – Embedding model support
- **uv** – Python package & virtual environment manager

---

## 📚 Current Features

- 🔄 **Document ingestion pipeline**
  - Supports: `.csv`, `.txt`, `.pdf`
  - Chunking with `RecursiveCharacterTextSplitter` for text/PDF, row-based splitter for CSV
- 🔖 **Traceability metadata**
  - Stores source file name and timestamp with each indexed chunk
- 🧠 **Vector indexing & search**
  - Deduplicates chunks using hash-based IDs
  - `/retrieve/docs` API returns top 3 matches from vector DB with metadata (source file name, datetimestamp & relevance score)
- ✏️ **Quality score support**
  - Return quality/confidence score for search results
- 🔐 **Embedding support**
  - Hugging Face models (default)
  - OpenAI models (with API key)
- 🧪 **Basic test coverage**
  - Upload, retrieval, and indexing logic


---

## 🔮 Upcoming Features

- 🔄 **Chunk-level updates**
  - Update modified chunks and remove outdated ones
- 🧪 **Expanded test coverage**
  - End-to-end tests and embedding mocks
- 📁 **Additional file format support**

---

## 📈 Usage

- Access Swagger UI:
  `http://localhost:8000/docs`
- Ready for frontend integration for document upload & search workflows

---

## ⚙️ Setup (using [`uv`](https://github.com/astral-sh/uv))

```bash
# 1. Install uv if not installed
curl -Ls https://astral.sh/uv/install.sh | sh

# 2. Create venv & install dependencies
uv sync --all-packages

# 3. Before running the application, update the environment variables with your own subscription details.
The provided example .env.example file can be used as template for a standard test suite setup and for running the retrieval API.

# 4. Run the test suite to create a ready-made vector index for testing the application via Swagger:
pytest test_main.py

# 5. Run the FastAPI app - have fun!!
uvicorn main:app --reload
