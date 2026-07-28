# Canan Hemşirelik AI Asistanı - Backend

Canan için 3 modlu RAG tabanlı hemşirelik asistanı.

## Modlar

| Mod | Hitap | RAG | Açıklama |
|-----|-------|-----|----------|
| `gunluk` | Canan Hanım | ❌ | Günlük sohbet asistanı |
| `ders` | Hemşire Hanım | ✅ | Detaylı akademik açıklamalar |
| `hastane` | Hemşire Hanım | ✅ | Kısa, pratik, net bilgiler |

## Kurulum

### 1. Ortam Değişkenleri

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:
- `GOOGLE_API_KEY`: [Google AI Studio](https://aistudio.google.com/app/apikey)'dan al
- `PINECONE_API_KEY`: [Pinecone](https://app.pinecone.io)'dan al

### 2. Python Ortamı

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Belge Yükleme

Ders notlarını kategorilerine göre yükle:

```bash
# Ders notları
python scripts/ingest.py --path data/notes --category ders_notu

# Psikoloji belgeleri
python scripts/ingest.py --path data/psychology --category psikoloji

# Klinik esaslar
python scripts/ingest.py --path data/clinical --category klinik
```

### 4. Sunucuyu Başlat

```bash
# Geliştirme
uvicorn app.main:app --reload

# veya Docker ile
docker-compose up -d
```

## API Kullanımı

### Soru Sor

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hipoglisemi belirtileri nelerdir?", "mode": "ders"}'
```

### Modları Listele

```bash
curl http://localhost:8000/chat/modes
```

## Belge Kategorileri

- `ders_notu`: Ders sunumları ve notları
- `psikoloji`: Hemşirelik psikolojisi
- `klinik`: Klinik esaslar ve prosedürler
- `farmakoloji`: İlaç bilgileri
- `genel`: Diğer kaynaklar

## Dizin Yapısı

```
backend/
├── app/
│   ├── main.py          # FastAPI uygulaması
│   ├── config.py        # Ayarlar
│   ├── prompts.py       # System prompt'lar
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── chain.py
│   └── routes/
│       └── chat.py
├── data/
│   ├── notes/           # Ders notları (PDF, PPTX)
│   ├── psychology/      # Psikoloji belgeleri
│   └── clinical/        # Klinik esaslar
├── scripts/
│   └── ingest.py        # Belge yükleme scripti
├── Dockerfile
└── docker-compose.yml
```
