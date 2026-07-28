"""
Canan Hemşirelik AI Asistanı - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import chat


# FastAPI uygulaması
app = FastAPI(
    title="Canan Hemşirelik Asistanı",
    description="""
    Canan için 3 modlu AI asistanı:
    - **Günlük**: Samimi sohbet asistanı (Canan Hanım)
    - **Ders Çalışma**: Akademik hemşirelik asistanı (Hemşire Hanım)
    - **Hastane/Staj**: Pratik klinik asistanı (Hemşire Hanım)
    """,
    version="1.0.0",
)

# CORS ayarları (mobil app için gerekli)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtlanmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(chat.router)


@app.get("/")
async def root():
    """Ana sayfa - API bilgisi."""
    return {
        "name": "Canan Hemşirelik Asistanı",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "chat": "/chat/",
            "modes": "/chat/modes",
            "docs": "/docs",
            "health": "/health",
        }
    }


@app.get("/health")
async def health_check():
    """Sunucu sağlık kontrolü."""
    settings = get_settings()
    return {
        "status": "healthy",
        "pinecone_index": settings.pinecone_index_name,
        "llm_model": settings.llm_model,
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
