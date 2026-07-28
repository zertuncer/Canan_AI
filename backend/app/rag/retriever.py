"""
Retriever modülü - Pinecone'dan ilgili belgeleri getirir.
Pinecone SDK v3+ kullanır (LangChain olmadan).
"""

from pinecone import Pinecone
from app.config import get_settings
from app.rag.embeddings import get_query_embedding

_index = None


def get_pinecone_index():
    """Pinecone index'ini döndürür (singleton)."""
    global _index
    
    if _index is None:
        settings = get_settings()
        pc = Pinecone(api_key=settings.pinecone_api_key)
        _index = pc.Index(settings.pinecone_index_name)
    
    return _index


def search_documents(query: str, top_k: int = 5, category: str = None) -> list[dict]:
    """
    Sorguya en uygun belgeleri getirir.
    
    Args:
        query: Arama sorgusu
        top_k: Döndürülecek belge sayısı
        category: Belge kategorisi filtresi (opsiyonel)
    
    Returns:
        İlgili belge parçalarının listesi
    """
    settings = get_settings()
    index = get_pinecone_index()
    
    # Sorguyu embedding'e çevir
    query_embedding = get_query_embedding(query)
    
    # Kategori filtresi
    filter_dict = None
    if category:
        filter_dict = {"category": category}
    
    # Pinecone'da ara
    results = index.query(
        vector=query_embedding,
        top_k=top_k or settings.top_k_results,
        include_metadata=True,
        filter=filter_dict,
    )
    
    # Sonuçları düzenle
    documents = []
    for match in results.matches:
        doc = {
            "id": match.id,
            "score": match.score,
            "content": match.metadata.get("text", ""),
            "source": match.metadata.get("source", "Bilinmeyen"),
            "page": match.metadata.get("page", ""),
            "category": match.metadata.get("category", ""),
        }
        documents.append(doc)
    
    return documents


def format_context(documents: list[dict]) -> tuple[str, list[str]]:
    """
    Belgeleri context string'e ve kaynak listesine dönüştürür.
    
    Returns:
        (context_string, sources_list)
    """
    if not documents:
        return "", []
    
    context_parts = []
    sources = []
    
    for i, doc in enumerate(documents, 1):
        content = doc.get("content", "")
        source = doc.get("source", "Bilinmeyen kaynak")
        page = doc.get("page", "")
        category = doc.get("category", "")
        
        context_parts.append(f"[Belge {i}]\n{content}")
        
        source_info = source
        if page:
            source_info += f" - Sayfa {page}"
        if category:
            source_info += f" ({category})"
        sources.append(source_info)
    
    return "\n\n".join(context_parts), sources
