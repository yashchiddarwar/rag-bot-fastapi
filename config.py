from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_model: str = "google/gemma-3-12b-it:free"
    embedding_model: str = "openai/text-embedding-3-small"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "rag-bot-index"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
