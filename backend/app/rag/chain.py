"""
RAG Chain modülü - Tüm parçaları birleştirip cevap üretir.
Yeni google-genai SDK kullanır.
"""

from google import genai
from app.config import get_settings
from app.prompts import Mode, get_system_prompt, get_rag_context_template
from app.rag.retriever import search_documents, format_context

_client = None


def get_client():
    """Gemini client'ı döndürür (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


async def generate_response(
    question: str,
    mode: Mode,
    use_rag: bool = True,
    files: list[dict] | None = None,
) -> dict:
    """
    Soruya cevap üretir.
    
    Args:
        question: Kullanıcının sorusu
        mode: Uygulama modu (gunluk, ders, hastane)
        use_rag: RAG kullanılsın mı (günlük modda False)
    
    Returns:
        {"reply": str, "sources": list[str]}
    """
    settings = get_settings()
    client = get_client()
    
    # System prompt'u al
    system_prompt = get_system_prompt(mode)
    
    # RAG kullan (hemşirelik modlarında)
    context = ""
    sources = []
    
    if use_rag and mode != Mode.DAILY:
        try:
            documents = search_documents(
                query=question,
                top_k=settings.top_k_results,
            )
            
            if documents:
                context, sources = format_context(documents)
        except Exception as e:
            print(f"RAG hatası (devam ediliyor): {e}")
    
    # Prompt'u oluştur
    if context:
        rag_template = get_rag_context_template()
        user_message = rag_template.format(
            context=context,
            question=question,
        )
    else:
        user_message = question
    
    # Full prompt
    full_prompt = f"{system_prompt}\n\n{user_message}"
    
    # Multimodal: dosya/resim varsa contents listesi olarak gönder
    try:
        if files:
            from google.genai import types
            
            contents = [full_prompt]
            for f in files:
                if f.get("mime_type", "").startswith("image/"):
                    contents.append(
                        types.Part.from_bytes(
                            data=f["data"],
                            mime_type=f["mime_type"],
                        )
                    )
                else:
                    # PDF veya text dosyası - text olarak ekle
                    if f.get("extracted_text"):
                        contents.append(
                            f"\n\n[Yüklenen dosya: {f.get('filename', 'dosya')}]\n{f['extracted_text']}"
                        )
            
            response = client.models.generate_content(
                model=settings.llm_model,
                contents=contents,
            )
        else:
            response = client.models.generate_content(
                model=settings.llm_model,
                contents=full_prompt,
            )
        reply = response.text
    except Exception as e:
        reply = f"Üzgünüm, bir hata oluştu: {str(e)}"
    
    return {
        "reply": reply,
        "sources": sources,
    }
