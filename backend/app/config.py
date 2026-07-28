from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Google AI (Gemini)
    google_api_key: str
    
    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "canan-nursing"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Model settings - yeni SDK formatı
    embedding_model: str = "text-embedding-004"
    llm_model: str = "gemini-2.5-flash"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
