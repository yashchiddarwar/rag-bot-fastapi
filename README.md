# RAG Bot with FastAPI and Pinecone

A Retrieval Augmented Generation (RAG) chatbot built with FastAPI, Pinecone vector database, and OpenAI.

## Features

- 📚 Ingest markdown documents from the `data/` folder
- 🔍 Semantic search using Pinecone vector database
- 🤖 AI-powered answers using OpenRouter (access to multiple LLM providers)
- ⚡ Fast API built with FastAPI
- 🔄 RESTful endpoints for querying and searching

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required configuration:
- `OPENROUTER_API_KEY`: Your OpenRouter API key (get it from https://openrouter.ai/keys)
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., `us-east-1`)

Optional configuration:
- `OPENROUTER_MODEL`: The LLM model to use (default: `openai/gpt-4-turbo-preview`)
- `EMBEDDING_MODEL`: The embedding model to use (default: `openai/text-embedding-3-small`)

### 3. Ingest Documents

Run the ingestion script to load your markdown files into Pinecone:

```bash
python ingest.py
```

This will:
- Read all `.md` files from the `data/` folder
- Split them into chunks
- Create embeddings using OpenAI
- Store vectors in Pinecone

### 4. Start the API Server

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /
GET /health
```

### Query with RAG
```
POST /query
```

Request body:
```json
{
  "question": "What are the best practices for caching?",
  "top_k": 5
}
```

Response:
```json
{
  "answer": "Based on the context...",
  "sources": ["caching_strategies_backend.md", "database_connection_pooling.md"]
}
```

### Similarity Search
```
POST /search
```

Request body:
```json
{
  "question": "microservice deployment",
  "top_k": 3
}
```

Returns raw document chunks matching the query.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
rag-bot/
├── data/                  # Markdown knowledge base files
├── main.py               # FastAPI application
├── ingest.py             # Document ingestion script
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## Configuration Options

Edit `.env` to customize:

- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of results to retrieve (default: 5)
- `OPENROUTER_MODEL`: LLM model to use via OpenRouter (default: openai/gpt-4-turbo-preview)
  - Other options: `anthropic/claude-3-opus`, `google/gemini-pro`, `meta-llama/llama-3-70b`, etc.
- `EMBEDDING_MODEL`: Embedding model (default: openai/text-embedding-3-small)

## Example Usage

Using curl:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I handle database connection pooling?"
  }'
```

Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What are SQL indexing best practices?"}
)

print(response.json())
```

## Notes

- Make sure to run `ingest.py` before starting the API to populate the vector database
- Re-run `ingest.py` whenever you add or modify documents in the `data/` folder
- The Pinecone index is created automatically on first run
