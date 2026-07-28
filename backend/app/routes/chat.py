"""
Chat API endpoint'leri.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List
from io import BytesIO

from app.prompts import Mode
from app.rag.chain import generate_response


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat isteği şeması."""
    message: str = Field(..., min_length=1, max_length=2000, description="Kullanıcının sorusu")
    mode: Mode = Field(default=Mode.STUDY, description="Uygulama modu: gunluk, ders, hastane")


class ChatResponse(BaseModel):
    """Chat cevabı şeması."""
    reply: str = Field(..., description="Asistanın cevabı")
    sources: list[str] = Field(default=[], description="Kullanılan kaynaklar")
    mode: str = Field(..., description="Kullanılan mod")


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Soru sor, cevap al.
    
    - **message**: Sormak istediğin soru
    - **mode**: 
        - `gunluk`: Günlük asistan (Canan)
        - `ders`: Ders çalışma modu (Hemşire Hanım, detaylı)
        - `hastane`: Hastane/staj modu (Hemşire Hanım, kısa ve net)
    """
    try:
        use_rag = request.mode not in (Mode.DAILY, Mode.FAL)
        
        result = await generate_response(
            question=request.message,
            mode=request.mode,
            use_rag=use_rag,
        )
        
        return ChatResponse(
            reply=result["reply"],
            sources=result["sources"],
            mode=request.mode.value,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cevap üretilirken bir hata oluştu: {str(e)}"
        )


def _extract_text_from_file(filename: str, content: bytes) -> str:
    """Dosyadan metin çıkar (PDF, DOCX, TXT)."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    
    try:
        if ext == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == "docx":
            from docx import Document
            doc = Document(BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext in ("txt", "md"):
            return content.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[Dosya okunamadı: {e}]"
    return ""


@router.post("/multimodal", response_model=ChatResponse)
async def chat_multimodal(
    message: str = Form(...),
    mode: str = Form(...),
    files: List[UploadFile] = File(default=[]),
) -> ChatResponse:
    """
    Resim ve dosya destekli chat endpoint'i.
    """
    try:
        mode_enum = Mode(mode)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Geçersiz mod: {mode}")
    
    processed_files = []
    
    for upload in files:
        content = await upload.read()
        mime_type = upload.content_type or "application/octet-stream"
        filename = upload.filename or "dosya"
        
        file_data = {
            "filename": filename,
            "mime_type": mime_type,
        }
        
        if mime_type.startswith("image/"):
            file_data["data"] = content
        else:
            file_data["extracted_text"] = _extract_text_from_file(filename, content)
        
        processed_files.append(file_data)
    
    try:
        use_rag = mode_enum not in (Mode.DAILY, Mode.FAL)
        
        result = await generate_response(
            question=message,
            mode=mode_enum,
            use_rag=use_rag,
            files=processed_files if processed_files else None,
        )
        
        return ChatResponse(
            reply=result["reply"],
            sources=result["sources"],
            mode=mode_enum.value,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cevap üretilirken bir hata oluştu: {str(e)}"
        )


@router.get("/modes")
async def get_modes():
    """Kullanılabilir modları listeler."""
    return {
        "modes": [
            {
                "id": "gunluk",
                "name": "Günlük Asistan",
                "description": "Samimi sohbet, günlük sorular",
                "hitap": "Canan",
            },
            {
                "id": "ders",
                "name": "Ders Çalışma",
                "description": "Detaylı akademik açıklamalar",
                "hitap": "Hemşire Hanım",
            },
            {
                "id": "hastane",
                "name": "Hastane / Staj",
                "description": "Kısa, net, pratik bilgiler",
                "hitap": "Hemşire Hanım",
            },
            {
                "id": "fal",
                "name": "Falcı",
                "description": "Gizemli Kahve Falı Yorumcusu",
                "hitap": "Canan",
            },
        ]
    }
