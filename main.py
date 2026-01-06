from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import Pinecone as LangchainPinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import settings

# Set Pinecone API key as environment variable
os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key

app = FastAPI(title="RAG Bot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class HealthResponse(BaseModel):
    status: str
    message: str


class DocumentListResponse(BaseModel):
    documents: list[dict]


class DocumentContentResponse(BaseModel):
    filename: str
    content: str


# Initialize components
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.openrouter_api_key,
    model=settings.embedding_model,
    openai_api_base=settings.openrouter_base_url
)

vectorstore = LangchainPinecone(
    index_name=settings.pinecone_index_name,
    embedding=embeddings
)

llm = ChatOpenAI(
    openai_api_key=settings.openrouter_api_key,
    model_name=settings.openrouter_model,
    temperature=0,
    openai_api_base=settings.openrouter_base_url,
    max_tokens=1000
)

# Custom prompt template
prompt_template = """You are a helpful assistant that answers questions based on the provided context.
Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": settings.top_k_results}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)


@app.get("/")
async def root():
    """Serve the chat interface."""
    return FileResponse("static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="RAG Bot API is running"
    )


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    Get list of all knowledge base documents.
    """
    try:
        data_path = Path("data")
        documents = []
        
        for md_file in data_path.glob("*.md"):
            # Read first few lines for preview
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                preview = content[:200] + "..." if len(content) > 200 else content
            
            documents.append({
                "filename": md_file.name,
                "title": md_file.stem.replace("_", " ").title(),
                "preview": preview
            })
        
        return DocumentListResponse(documents=documents)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.get("/documents/{filename}", response_model=DocumentContentResponse)
async def get_document(filename: str):
    """
    Get the full content of a specific document.
    """
    try:
        # Security: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = Path("data") / filename
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Document not found")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return DocumentContentResponse(
            filename=filename,
            content=content
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG bot with a question.
    
    Args:
        request: QueryRequest containing the question and optional top_k parameter
        
    Returns:
        QueryResponse with the answer and source documents
    """
    try:
        # Update retriever if custom top_k is provided
        if request.top_k != settings.top_k_results:
            qa_chain.retriever.search_kwargs["k"] = request.top_k
        
        # Run the query
        result = qa_chain.invoke({"query": request.question})
        
        # Extract sources
        sources = []
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)
        
        return QueryResponse(
            answer=result["result"],
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/search")
async def similarity_search(request: QueryRequest):
    """
    Perform similarity search without LLM generation.
    Returns raw documents matching the query.
    """
    try:
        docs = vectorstore.similarity_search(
            request.question,
            k=request.top_k
        )
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "metadata": doc.metadata
            })
        
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
