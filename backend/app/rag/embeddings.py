"""
Embedding modülü - Metinleri vektörlere dönüştürür.
Yeni google-genai SDK kullanır.
"""

from google import genai
from app.config import get_settings

_client = None


def get_client():
    """Gemini client'ı döndürür (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


def get_embedding(text: str) -> list[float]:
    """Tek bir metin için embedding oluştur."""
    client = get_client()
    settings = get_settings()
    result = client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
    )
    return result.embeddings[0].values


def get_query_embedding(text: str) -> list[float]:
    """Sorgu için embedding oluştur."""
    return get_embedding(text)


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Birden fazla metin için embedding oluştur."""
    embeddings = []
    for text in texts:
        emb = get_embedding(text)
        embeddings.append(emb)
    return embeddings
