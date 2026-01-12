# Language Tutor - System Architecture

**Version:** 1.0  
**Date:** January 2026  

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
│                    (Desktop / Mobile / Tablet)                       │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ HTTPS (Port 80/443)
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     NGINX REVERSE PROXY                              │
│              (Rate Limiting, SSL, Load Balancing)                    │
└─────────────┬─────────────────────────────────────┬─────────────────┘
              │ /                                   │ /api
              ▼                                     ▼
┌──────────────────────────┐         ┌──────────────────────────────────┐
│     FRONTEND (Next.js)   │         │      BACKEND (FastAPI)           │
│     Port 3000            │         │      Port 8000                   │
│                          │         │                                  │
│  ┌────────────────────┐  │         │  ┌────────────────────────────┐  │
│  │    React App       │  │         │  │     API Routers            │  │
│  │    TypeScript      │  │         │  │  - /chat (streaming)       │  │
│  │    Tailwind CSS    │  │         │  │  - /correction             │  │
│  │    shadcn/ui       │  │         │  │  - /exercises              │  │
│  └────────────────────┘  │         │  │  - /training               │  │
│                          │         │  └────────────┬───────────────┘  │
│  Pages:                  │         │               │                  │
│  - / (Chat Tutor)        │         │  ┌────────────▼───────────────┐  │
│  - /grammar              │         │  │     Services Layer         │  │
│  - /exercises            │         │  │  - TutorService            │  │
│  - /training             │         │  │  - RAGService              │  │
└──────────────────────────┘         │  │  - TrainingDataService     │  │
                                     │  │  - TrainingService         │  │
                                     │  └────────────┬───────────────┘  │
                                     │               │                  │
                                     │  ┌────────────▼───────────────┐  │
                                     │  │   LLM Provider Factory     │  │
                                     │  │  - GroqProvider (dev)      │  │
                                     │  │  - LocalProvider (prod)    │  │
                                     │  └────────────┬───────────────┘  │
                                     └───────────────┼──────────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────┐
                    │                                │                    │
                    ▼                                ▼                    ▼
        ┌──────────────────┐           ┌──────────────────┐    ┌─────────────────┐
        │   ChromaDB       │           │   Qwen2.5-7B     │    │   File Storage  │
        │   (Vector DB)    │           │   (GGUF Model)   │    │   (Training)    │
        │                  │           │                  │    │                 │
        │  - Grammar Rules │           │   GPU Inference  │    │  - datasets.json│
        │  - Vocabulary    │           │   CUDA/ROCm      │    │  - jobs.json    │
        │  - Examples      │           │                  │    │  - exports/     │
        └──────────────────┘           └──────────────────┘    └─────────────────┘
```

---

## 2. Component Details

### 2.1 Frontend Architecture

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Home (Chat Tutor)
│   ├── grammar/           # Grammar Check page
│   ├── exercises/         # Exercises page
│   ├── training/          # Training Management page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── ChatInterface.tsx  # Main chat component
│   ├── CorrectionTool.tsx # Grammar correction UI
│   ├── ExercisePanel.tsx  # Exercise generation/display
│   ├── TrainingPanel.tsx  # Training management UI
│   ├── Sidebar.tsx        # Navigation
│   ├── Header.tsx         # Top bar
│   └── ui/                # shadcn/ui components
└── lib/
    ├── api.ts             # Backend API client
    ├── training-api.ts    # Training API client
    └── utils.ts           # Utility functions
```

**Key Technologies:**
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS
- **shadcn/ui**: Accessible component library

### 2.2 Backend Architecture

```
backend/
├── main.py                 # FastAPI application entry
├── config.py               # Settings management
├── routers/
│   ├── chat.py            # Chat endpoints (SSE streaming)
│   ├── correction.py      # Grammar correction endpoints
│   ├── exercises.py       # Exercise generation endpoints
│   └── training.py        # Training management endpoints
├── services/
│   ├── tutor_service.py   # Core tutoring logic
│   ├── rag_service.py     # ChromaDB operations
│   ├── training_data_service.py  # Dataset management
│   └── training_service.py       # Fine-tuning operations
├── providers/
│   ├── base.py            # Abstract LLM provider
│   ├── factory.py         # Provider factory
│   ├── groq_provider.py   # Groq API provider
│   └── local_provider.py  # Local GGUF provider
└── models/
    └── schemas.py         # Pydantic models
```

**Key Technologies:**
- **FastAPI**: Async Python web framework
- **Pydantic**: Data validation
- **llama-cpp-python**: Local LLM inference
- **ChromaDB**: Vector database
- **sentence-transformers**: Text embeddings

### 2.3 LLM Provider Factory Pattern

```python
# Provider selection based on environment
class LLMProviderFactory:
    @staticmethod
    def create_provider(settings: Settings) -> BaseLLMProvider:
        if settings.llm_provider == "groq":
            return GroqProvider(settings)
        elif settings.llm_provider == "local":
            return LocalProvider(settings)
```

**Benefits:**
- Easy switching between development (Groq) and production (local)
- Consistent interface for all providers
- No code changes needed for deployment

### 2.4 RAG (Retrieval Augmented Generation)

```
Query Flow:
1. User asks about grammar
2. Query embedded using sentence-transformers (CPU)
3. ChromaDB finds relevant grammar rules/examples
4. Context injected into LLM prompt
5. LLM generates response with accurate information
```

**Collections:**
- `grammar_rules`: Language-specific grammar explanations
- `vocabulary`: Word definitions and usage
- `examples`: Example sentences for each language

---

## 3. Data Flow

### 3.1 Chat Flow (Streaming)

```
User Input → Frontend → POST /api/chat/stream
                              │
                              ▼
                    [TutorService.chat_stream()]
                              │
                    ┌─────────▼─────────┐
                    │  RAGService       │
                    │  - Search grammar │
                    │  - Get examples   │
                    └─────────┬─────────┘
                              │ context
                              ▼
                    ┌─────────────────────┐
                    │  LLM Provider       │
                    │  - Format messages  │
                    │  - Generate stream  │
                    └─────────┬───────────┘
                              │ SSE chunks
                              ▼
                    Frontend (real-time display)
```

### 3.2 Correction Flow

```
User Text → POST /api/correction/check
                     │
                     ▼
           [TutorService.correct_text()]
                     │
                     ▼
           LLM generates JSON:
           {
             "original": "...",
             "corrected": "...",
             "errors": [...]
           }
                     │
                     ▼
           Frontend displays diff
```

### 3.3 Exercise Flow

```
Topic/Type/Level → POST /api/exercises/generate
                          │
                          ▼
              [TutorService.generate_exercise()]
                          │
                          ▼
              LLM generates exercises JSON:
              {
                "question": "...",
                "options": [...],
                "correct_answer": "...",
                "explanation": "..."
              }
                          │
                          ▼
              Frontend renders exercise
```

---

## 4. Deployment Architecture

### 4.1 Docker Containers

```
┌────────────────────────────────────────────────────────────┐
│                    Docker Host (Local PC)                   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    nginx        │  │    frontend     │  │   backend   │ │
│  │    (optional)   │  │    (Next.js)    │  │   (FastAPI) │ │
│  │    Port 80      │  │    Port 3000    │  │   Port 8000 │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           │                    │                   │        │
│           └────────────────────┼───────────────────┘        │
│                                │                            │
│  ┌─────────────────────────────▼───────────────────────────┐│
│  │              Docker Network (language-tutor-network)     ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  Volumes:                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ chroma_db/   │  │ models/      │  │ training_*/  │       │
│  │ (persistent) │  │ (read-only)  │  │ (persistent) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Production Deployment Commands

```bash
# Initial setup
./scripts/download-model.sh   # Download Qwen model

# Start production
./scripts/deploy.sh           # Build and start containers

# With nginx (optional)
docker compose -f docker-compose.production.yml --profile production up -d

# View logs
./scripts/deploy.sh --logs

# Stop
./scripts/deploy.sh --stop
```

### 4.3 Environment Configuration

| Variable | Development | Production |
|----------|-------------|------------|
| `LLM_PROVIDER` | `groq` | `local` |
| `GROQ_API_KEY` | Required | Not used |
| `LOCAL_MODEL_PATH` | Not used | `/app/models/model.gguf` |
| `GPU_LAYERS` | Not used | `-1` (all) |
| `CONTEXT_LENGTH` | 4096 | 8192 |

---

## 5. Security Architecture

### 5.1 Network Security

```
Internet
    │
    ▼ (Port 80/443 only)
┌──────────────┐
│    Nginx     │ ← Rate limiting (10 req/s API, 30 req/s general)
│              │ ← Security headers (X-Frame-Options, etc.)
└──────┬───────┘
       │ (Internal network only)
       ▼
┌──────────────────────────────────┐
│     Docker Internal Network      │
│  (Not exposed to internet)       │
└──────────────────────────────────┘
```

### 5.2 Input Validation

- All API inputs validated with Pydantic models
- Maximum text length limits
- HTML/script injection prevention
- Rate limiting per IP

---

## 6. Scalability Considerations

### 6.1 Current Design (Single Server)

```
Capacity: ~50 concurrent users
Bottleneck: GPU inference (one request at a time per worker)
```

### 6.2 Future Scaling Options

```
Option 1: Multiple GPU workers
┌──────────────┐
│   Backend    │──┬── Worker 1 (GPU 0)
│   Load       │  ├── Worker 2 (GPU 1)
│   Balancer   │  └── Worker 3 (GPU 2)
└──────────────┘

Option 2: Request queuing
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Backend │───▶│  Queue  │───▶│  Worker │
└─────────┘    └─────────┘    └─────────┘

Option 3: Batch inference
- Group similar requests
- Process in batches
- Distribute results
```

---

## 7. Monitoring & Logging

### 7.1 Health Checks

```
GET /api/health
Response: {
  "status": "healthy",
  "llm_provider": "local",
  "rag_status": true,
  "model_loaded": true
}
```

### 7.2 Logging

```python
# JSON structured logging
{
  "timestamp": "2026-01-12T10:30:00Z",
  "level": "INFO",
  "service": "tutor_service",
  "action": "chat_request",
  "language": "Japanese",
  "duration_ms": 1234
}
```

### 7.3 Docker Logs

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f backend

# Log rotation configured in docker-compose.production.yml
```

---

## 8. Backup & Recovery

### 8.1 Data to Backup

| Data | Location | Frequency | Method |
|------|----------|-----------|--------|
| ChromaDB | `./backend/chroma_db/` | Daily | rsync/tar |
| Training Data | `./backend/training_data/` | After changes | git/rsync |
| Training Jobs | `./backend/training_jobs/` | After changes | git/rsync |
| Model Files | `./backend/models/` | After updates | Copy |

### 8.2 Recovery Procedure

```bash
# Stop services
./scripts/deploy.sh --stop

# Restore data
rsync -av backup/chroma_db/ ./backend/chroma_db/
rsync -av backup/training_data/ ./backend/training_data/

# Restart
./scripts/deploy.sh
```

---

## 9. Technology Decisions

### 9.1 Why Qwen2.5-7B?

| Factor | Decision |
|--------|----------|
| Multilingual | Excellent Chinese/Japanese/English support |
| Size | Fits in 8GB VRAM (Q4 quantization) |
| Quality | Strong instruction following |
| License | Apache 2.0 (commercial use OK) |

### 9.2 Why ChromaDB?

| Factor | Decision |
|--------|----------|
| Simplicity | Embedded, no separate server |
| Python | Native Python API |
| Persistence | Built-in disk storage |
| Embeddings | Works with sentence-transformers |

### 9.3 Why Next.js?

| Factor | Decision |
|--------|----------|
| SSR/SSG | Better SEO if needed |
| React | Large ecosystem |
| App Router | Modern routing |
| TypeScript | Type safety |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial architecture |
