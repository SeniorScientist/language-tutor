#!/bin/bash
# Deployment script for Language Tutor on local PC server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Language Tutor Deployment Script ===${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Check NVIDIA Docker runtime (optional for GPU)
if docker info 2>/dev/null | grep -q "nvidia"; then
    echo -e "${GREEN}NVIDIA Docker runtime detected${NC}"
    GPU_AVAILABLE=true
else
    echo -e "${YELLOW}NVIDIA Docker runtime not found - will use CPU mode${NC}"
    GPU_AVAILABLE=false
fi

# Check if model exists
MODEL_PATH="./backend/models/model.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${YELLOW}Warning: Model file not found at $MODEL_PATH${NC}"
    echo -e "${YELLOW}Please download the model:${NC}"
    echo -e "  wget https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf -O backend/models/model.gguf"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Parse arguments
MODE="production"
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            MODE="development"
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --stop)
            echo -e "${YELLOW}Stopping services...${NC}"
            docker compose -f docker-compose.production.yml down
            echo -e "${GREEN}Services stopped${NC}"
            exit 0
            ;;
        --logs)
            docker compose -f docker-compose.production.yml logs -f
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dev] [--rebuild] [--stop] [--logs]"
            exit 1
            ;;
    esac
done

# Select compose file
if [ "$MODE" = "development" ]; then
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${YELLOW}Running in DEVELOPMENT mode (using Groq API)${NC}"
else
    COMPOSE_FILE="docker-compose.production.yml"
    echo -e "${GREEN}Running in PRODUCTION mode (using local LLM)${NC}"
fi

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"

if [ "$REBUILD" = true ]; then
    docker compose -f "$COMPOSE_FILE" build --no-cache
fi

docker compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check health
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null || echo "failed")

if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}Backend is healthy${NC}"
else
    echo -e "${RED}Backend health check failed${NC}"
    echo "Check logs with: docker compose -f $COMPOSE_FILE logs backend"
fi

# Print status
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "Commands:"
echo "  View logs: $0 --logs"
echo "  Stop services: $0 --stop"
echo "  Rebuild: $0 --rebuild"
