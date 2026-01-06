import os
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings


def load_markdown_files(data_dir: str = "data") -> list[Document]:
    """Load all markdown files from the data directory."""
    documents = []
    data_path = Path(data_dir)
    
    for md_file in data_path.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(
                Document(
                    page_content=content,
                    metadata={"source": md_file.name, "file_path": str(md_file)}
                )
            )
    
    print(f"Loaded {len(documents)} documents from {data_dir}")
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def initialize_pinecone():
    """Initialize Pinecone and create index if it doesn't exist."""
    pc = Pinecone(api_key=settings.pinecone_api_key)
    
    # Check if index exists
    existing_indexes = pc.list_indexes()
    index_names = [index.name for index in existing_indexes]
    
    if settings.pinecone_index_name in index_names:
        # Check if dimension matches
        index_info = pc.describe_index(settings.pinecone_index_name)
        if index_info.dimension != 1536:
            print(f"Index {settings.pinecone_index_name} has wrong dimension ({index_info.dimension}). Attempting to delete...")
            pc.delete_index(settings.pinecone_index_name)
            index_names.remove(settings.pinecone_index_name)
            print(f"Index deleted. Creating new one with dimension 1536...")
    
    if settings.pinecone_index_name not in index_names:
        print(f"Creating new index: {settings.pinecone_index_name}")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.pinecone_environment
            )
        )
        print(f"Index {settings.pinecone_index_name} created successfully")
    else:
        print(f"Index {settings.pinecone_index_name} already exists with correct dimensions")
    
    return pc


def ingest_documents():
    """Main ingestion pipeline."""
    print("Starting document ingestion...")
    
    # Load documents
    documents = load_markdown_files()
    
    if not documents:
        print("No documents found to ingest!")
        return
    
    # Split into chunks
    chunks = split_documents(documents)
    
    # Initialize Pinecone
    pc = initialize_pinecone()
    
    # Create embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openrouter_api_key,
        model=settings.embedding_model,
        openai_api_base=settings.openrouter_base_url
    )
    
    # Set API key as environment variable for langchain_pinecone
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
    
    # Create vector store and ingest
    print("Ingesting documents into Pinecone...")
    vectorstore = LangchainPinecone.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=settings.pinecone_index_name
    )
    
    print(f"Successfully ingested {len(chunks)} chunks into Pinecone!")
    return vectorstore


if __name__ == "__main__":
    ingest_documents()
