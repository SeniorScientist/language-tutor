# LinguaAI - Foreign Language Tutor

An AI-powered language tutoring application with chat, grammar correction, and interactive exercises. Supports **English, Chinese, Russian, and Japanese**.

## Features

### 🗣️ Chat Tutor
- Streaming conversational interface
- Support for 4 languages (English, Chinese, Russian, Japanese)
- Learner level adaptation (beginner/intermediate/advanced)
- RAG-enhanced grammar explanations
- English-to-English explanations for complex concepts

### ✍️ Grammar Correction
- Real-time text analysis
- Error detection and classification (grammar/spelling/punctuation)
- Detailed explanations for each correction
- Language-specific rules (Chinese particles, Russian cases, Japanese keigo)

### 📝 Exercise Generator
- Multiple choice questions
- Fill-in-the-blank exercises
- Translation exercises
- Language-specific topics (HSK, JLPT, etc.)
- Score tracking and hints

### 🎓 Model Training (Admin)
- Training dataset management
- Example approval workflow
- Quality rating system
- Export training data for fine-tuning

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Vector DB**: ChromaDB with sentence-transformers
- **LLM**: Qwen2.5-7B-Instruct (GGUF) or Groq API
- **Deployment**: Docker, Docker Compose, Nginx

## Deployment Modes

| Mode | Use Case | LLM | GPU Required |
|------|----------|-----|--------------|
| Development | Local testing | Groq API | ❌ No |
| Production | Self-hosted server | Qwen2.5-7B | ✅ Yes |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- NVIDIA GPU with 8GB+ VRAM (for production)
- NVIDIA Container Toolkit (for production)

### Option 1: Production Deployment (Local Server with GPU)

1. **Clone and navigate to the project:**
```bash
cd language-tutor
```

2. **Download the model:**
```bash
./scripts/download-model.sh
# Or manually:
mkdir -p backend/models
wget https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf \
  -O backend/models/model.gguf
```

3. **Deploy with Docker:**
```bash
./scripts/deploy.sh
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Development Mode (Groq API)

1. **Get a free Groq API key:** https://console.groq.com/

2. **Create environment file:**
```bash
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

3. **Start with Docker Compose:**
```bash
docker compose up -d
```

### Option 3: Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env
cat > .env << EOF
LLM_PROVIDER=groq
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
EOF

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

---

## Deployment Scripts

| Script | Description |
|--------|-------------|
| `./scripts/deploy.sh` | Build and start production containers |
| `./scripts/deploy.sh --dev` | Start in development mode (Groq) |
| `./scripts/deploy.sh --rebuild` | Force rebuild containers |
| `./scripts/deploy.sh --stop` | Stop all services |
| `./scripts/deploy.sh --logs` | View container logs |
| `./scripts/download-model.sh` | Download Qwen model |

---

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `groq` or `local` | `groq` |
| `GROQ_API_KEY` | Groq API key | - |
| `GROQ_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `LOCAL_MODEL_PATH` | Path to GGUF model | `./models/model.gguf` |
| `GPU_LAYERS` | GPU layers (-1 = all) | `-1` |
| `CONTEXT_LENGTH` | Context window | `8192` |
| `EMBEDDING_MODEL` | Embeddings model | `all-MiniLM-L6-v2` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend URL | `http://localhost:8000` |

---

## API Endpoints

### Chat
- `POST /api/chat/stream` - Streaming chat (SSE)
- `POST /api/chat/` - Non-streaming chat
- `POST /api/chat/explain` - Grammar explanation

### Grammar Correction
- `POST /api/correct/` - Analyze and correct text

### Exercises
- `POST /api/exercises/generate` - Generate exercises
- `POST /api/exercises/check` - Check answer
- `GET /api/exercises/topics` - Available topics
- `GET /api/exercises/types` - Exercise types

### Training (Admin)
- `GET /api/training/datasets` - List datasets
- `POST /api/training/datasets` - Create dataset
- `POST /api/training/datasets/{id}/examples` - Add example
- `POST /api/training/export-data` - Export training data
- `POST /api/training/jobs` - Create training job
- `POST /api/training/jobs/{id}/start` - Start training

### Health
- `GET /api/health` - System health check

---

## Project Structure

```
language-tutor/
├── backend/
│   ├── providers/           # LLM providers (Groq, Local)
│   ├── services/            # Business logic
│   │   ├── rag_service.py   # ChromaDB + embeddings
│   │   ├── tutor_service.py # Core tutoring
│   │   ├── training_data_service.py
│   │   └── training_service.py
│   ├── routers/             # API endpoints
│   ├── models/              # Pydantic schemas
│   ├── Dockerfile           # CPU deployment
│   └── Dockerfile.gpu       # GPU deployment
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   └── lib/                 # API clients
├── docs/                    # Documentation
│   ├── 01-REQUIREMENTS.md
│   ├── 02-ARCHITECTURE.md
│   └── 03-UI-DESIGN.md
├── scripts/
│   ├── deploy.sh            # Deployment script
│   └── download-model.sh    # Model download
├── nginx/                   # Reverse proxy config
├── docker-compose.yml       # Development
├── docker-compose.production.yml  # Production
└── README.md
```

---

## Supported Languages

| Language | Features |
|----------|----------|
| 🇬🇧 English | Phrasal verbs, idioms, complex-to-simple explanations |
| 🇨🇳 Chinese | Tones, measure words, HSK levels, pinyin |
| 🇷🇺 Russian | Cases, verb aspects, Cyrillic support |
| 🇯🇵 Japanese | Particles, keigo, hiragana/katakana/kanji, JLPT levels |

---

## Hardware Requirements

### Minimum (Development)
- CPU: 4 cores
- RAM: 8GB
- GPU: Not required (uses Groq API)

### Recommended (Production)
- CPU: 8 cores
- RAM: 32GB
- GPU: NVIDIA RTX 3070+ (8GB VRAM)
- Storage: 50GB SSD

---

## Troubleshooting

### Model loading issues
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
```

### Out of memory
- Use Q4_K_M quantization (default)
- Reduce context length: `CONTEXT_LENGTH=4096`
- Use smaller model: Qwen2.5-3B instead of 7B

### Slow responses
- Ensure GPU is being used: check logs for "GPU layers"
- Increase GPU layers: `GPU_LAYERS=-1`

---

## Documentation

See the `docs/` folder for detailed documentation:
- [Requirements Specification](docs/01-REQUIREMENTS.md)
- [System Architecture](docs/02-ARCHITECTURE.md)
- [UI/UX Design](docs/03-UI-DESIGN.md)

---

## License

MIT License
