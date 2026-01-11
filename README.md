# LinguaAI - Foreign Language Tutor

An AI-powered language tutoring application with chat, grammar correction, and interactive exercises. Supports multiple deployment modes for flexibility.

## Features

### Chat Tutor

- Streaming conversational interface
- Multiple language support (Spanish, French, German, etc.)
- Learner level adaptation (beginner/intermediate/advanced)
- RAG-enhanced grammar explanations

### Grammar Correction

- Real-time text analysis
- Error detection and classification (grammar/spelling/punctuation)
- Detailed explanations for each correction
- Side-by-side comparison view

### Exercise Generator

- Multiple choice questions
- Fill-in-the-blank exercises
- Translation exercises
- Score tracking and hints
- Instant feedback with explanations

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Vector DB**: ChromaDB with sentence-transformers
- **LLM**: OpenAI-compatible API (Groq or local GGUF models)

## Deployment Modes

### Local Development (Groq API)

Uses Groq's free API for LLM inference. No GPU required.

### Cloud Production (Local LLM)

Uses llama-cpp-python with GGUF models. Requires NVIDIA GPU.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. Clone the repository and navigate to the project directory:

```bash
cd language-tutor
```

2. Create environment file:

```bash
# Create .env file with your Groq API key
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

3. Start with Docker Compose:

```bash
# For local development (uses Groq API)
docker-compose up -d

# For GPU deployment (uses local LLM)
# First, place your GGUF model in ./models/model.gguf
docker-compose -f docker-compose.gpu.yml up -d
```

4. Access the application:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```bash
# LLM Provider: "groq" or "local"
LLM_PROVIDER=groq

# Groq API (get free key at https://console.groq.com/)
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Local LLM (for GPU deployment)
LOCAL_MODEL_PATH=./models/model.gguf
GPU_LAYERS=-1
CONTEXT_LENGTH=4096

# Embeddings (works on CPU)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

5. Start the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:

```bash
npm run dev
```

5. Open http://localhost:3000

## Environment Variables

### Backend

| Variable                   | Description                               | Default                          |
| -------------------------- | ----------------------------------------- | -------------------------------- |
| `LLM_PROVIDER`             | LLM provider to use: `groq` or `local`    | `groq`                           |
| `GROQ_API_KEY`             | Groq API key (required for groq provider) | -                                |
| `GROQ_MODEL`               | Groq model name                           | `llama-3.1-70b-versatile`        |
| `GROQ_BASE_URL`            | Groq API base URL                         | `https://api.groq.com/openai/v1` |
| `LOCAL_MODEL_PATH`         | Path to GGUF model file                   | `./models/model.gguf`            |
| `GPU_LAYERS`               | Number of GPU layers (-1 for all)         | `-1`                             |
| `CONTEXT_LENGTH`           | Context window size                       | `4096`                           |
| `EMBEDDING_MODEL`          | Sentence-transformer model                | `all-MiniLM-L6-v2`               |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path                     | `./chroma_db`                    |
| `CORS_ORIGINS`             | Allowed CORS origins                      | `["http://localhost:3000"]`      |

### Frontend

| Variable              | Description     | Default                 |
| --------------------- | --------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## API Endpoints

### Chat

- `POST /api/chat/` - Send message (non-streaming)
- `POST /api/chat/stream` - Send message (SSE streaming)
- `POST /api/chat/explain` - Get grammar explanation

### Grammar Correction

- `POST /api/correct/` - Correct text

### Exercises

- `POST /api/exercises/generate` - Generate exercises
- `POST /api/exercises/check` - Check answer
- `GET /api/exercises/topics` - List available topics
- `GET /api/exercises/types` - List exercise types
- `GET /api/exercises/levels` - List learner levels

### Health

- `GET /api/health` - Health check

## Project Structure

```
language-tutor/
├── backend/
│   ├── providers/          # LLM provider implementations
│   │   ├── base.py         # Abstract base class
│   │   ├── groq_provider.py
│   │   ├── local_provider.py
│   │   └── factory.py      # Provider factory
│   ├── services/           # Business logic
│   │   ├── rag_service.py  # ChromaDB + embeddings
│   │   └── tutor_service.py
│   ├── routers/            # API routes
│   │   ├── chat.py
│   │   ├── correction.py
│   │   └── exercises.py
│   ├── models/             # Pydantic schemas
│   ├── config.py           # Settings
│   ├── main.py             # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Dockerfile.gpu
├── frontend/
│   ├── app/                # Next.js App Router
│   │   ├── page.tsx        # Chat page
│   │   ├── grammar/        # Grammar page
│   │   ├── exercises/      # Exercises page
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/         # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── CorrectionTool.tsx
│   │   └── ExercisePanel.tsx
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   └── utils.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Local development
├── docker-compose.gpu.yml  # GPU deployment
└── README.md
```

## Using Local LLM (GPU Deployment)

1. Download a GGUF model (e.g., Llama 3.1):

```bash
mkdir -p models
# Download your preferred GGUF model to ./models/model.gguf
```

2. Set environment variable:

```bash
export LLM_PROVIDER=local
export LOCAL_MODEL_PATH=./models/model.gguf
```

3. Install llama-cpp-python with GPU support:

```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

4. Start the application or use `docker-compose.gpu.yml`

## Getting a Groq API Key

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Add to your `.env` file

Groq offers free API access with generous rate limits, making it ideal for development and personal use.

## Customization

### Adding Languages

Edit the language lists in:

- `frontend/components/ChatInterface.tsx`
- `frontend/components/CorrectionTool.tsx`
- `frontend/components/ExercisePanel.tsx`
- `backend/routers/exercises.py` (EXERCISE_TOPICS)

### Adding Grammar Rules

The RAG system seeds initial data on first run. To add more:

```python
from services.rag_service import get_rag_service

rag = get_rag_service()
rag.add_grammar_rule(
    rule_id="custom_rule_1",
    content="Your grammar rule explanation...",
    language="Spanish"
)
```

## License

MIT License
