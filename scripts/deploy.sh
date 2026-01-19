#!/bin/bash
# Deployment script for Language Tutor on local PC server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Language Tutor Deployment Script ===${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Show usage
show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "Modes:"
    echo "  cpu          Run with CPU only (slower, no GPU needed)"
    echo "  gpu          Run with GPU support (requires NVIDIA Docker)"
    echo "  production   Full production setup with GPU + Nginx"
    echo "  dev          Development mode (uses Groq API)"
    echo ""
    echo "Options:"
    echo "  --rebuild    Rebuild Docker images from scratch"
    echo "  --stop       Stop all running services"
    echo "  --logs       Show logs from running services"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 cpu              # Run with CPU only"
    echo "  $0 gpu              # Run with GPU"
    echo "  $0 production       # Full production with Nginx"
    echo "  $0 cpu --rebuild    # Rebuild and run CPU mode"
    echo "  $0 --stop           # Stop all services"
}

# Check prerequisites
check_prerequisites() {
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
}

# Check GPU availability
check_gpu() {
    if docker info 2>/dev/null | grep -q "nvidia"; then
        echo -e "${GREEN}NVIDIA Docker runtime detected${NC}"
        return 0
    else
        echo -e "${YELLOW}NVIDIA Docker runtime not found${NC}"
        return 1
    fi
}

# Check model file
check_model() {
    local model_path="$1"
    if [ ! -f "$model_path" ]; then
        echo -e "${YELLOW}Warning: Model file not found at $model_path${NC}"
        echo -e "${YELLOW}Please download the model:${NC}"
        echo -e "  wget https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf -O backend/models/model.gguf"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}Model file found${NC}"
    fi
}

# Stop all services
stop_services() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    docker compose -f docker-compose.production.yml down 2>/dev/null || true
    docker compose -f docker-compose.gpu.yml down 2>/dev/null || true
    docker compose -f docker-compose.cpu.yml down 2>/dev/null || true
    docker compose -f docker-compose.yml down 2>/dev/null || true
    echo -e "${GREEN}All services stopped${NC}"
}

# Show logs
show_logs() {
    echo -e "${YELLOW}Checking for running services...${NC}"
    if docker ps | grep -q "language-tutor"; then
        # Find which compose file is running
        for file in docker-compose.production.yml docker-compose.gpu.yml docker-compose.cpu.yml docker-compose.yml; do
            if [ -f "$file" ] && docker compose -f "$file" ps 2>/dev/null | grep -q "running"; then
                echo -e "${GREEN}Showing logs from $file${NC}"
                docker compose -f "$file" logs -f
                exit 0
            fi
        done
        # Fallback: just show any language-tutor logs
        docker logs -f $(docker ps -q --filter "name=language-tutor" | head -1)
    else
        echo -e "${RED}No running services found${NC}"
    fi
    exit 0
}

# Wait for backend health
wait_for_health() {
    local compose_file="$1"
    local max_retries="${2:-12}"
    
    echo -e "${YELLOW}Waiting for backend to be healthy...${NC}"
    
    for i in $(seq 1 $max_retries); do
        if curl -s http://localhost:8000/api/health 2>/dev/null | grep -q "healthy"; then
            echo -e "${GREEN}Backend is healthy!${NC}"
            return 0
        fi
        echo -e "${YELLOW}  Attempt $i/$max_retries - waiting...${NC}"
        sleep 10
    done
    
    echo -e "${RED}Backend health check failed${NC}"
    echo "Check logs with: docker compose -f $compose_file logs backend"
    return 1
}

# Main deployment function
deploy() {
    local compose_file="$1"
    local mode_name="$2"
    local rebuild="$3"
    
    echo -e "${BLUE}Deploying in ${mode_name} mode...${NC}"
    echo -e "${YELLOW}Using: $compose_file${NC}"
    
    if [ "$rebuild" = true ]; then
        echo -e "${YELLOW}Rebuilding images (this may take a while)...${NC}"
        docker compose -f "$compose_file" build --no-cache
    fi
    
    echo -e "${YELLOW}Starting services...${NC}"
    docker compose -f "$compose_file" up -d
    
    # Wait longer for CPU mode
    local wait_time=12
    if [ "$mode_name" = "CPU" ]; then
        wait_time=18
    fi
    
    sleep 5
    wait_for_health "$compose_file" "$wait_time"
    
    echo ""
    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
    echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo "Commands:"
    echo "  View logs:     $0 --logs"
    echo "  Stop services: $0 --stop"
    echo "  Rebuild:       $0 $MODE --rebuild"
}

# Parse arguments
MODE=""
REBUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        cpu|CPU)
            MODE="cpu"
            shift
            ;;
        gpu|GPU)
            MODE="gpu"
            shift
            ;;
        production|prod|PRODUCTION)
            MODE="production"
            shift
            ;;
        dev|DEV|development)
            MODE="dev"
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        --logs)
            show_logs
            exit 0
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# If no mode specified, show usage
if [ -z "$MODE" ]; then
    echo -e "${RED}Error: No deployment mode specified${NC}"
    echo ""
    show_usage
    exit 1
fi

# Check prerequisites
check_prerequisites

# Select compose file based on mode
case $MODE in
    cpu)
        COMPOSE_FILE="docker-compose.cpu.yml"
        check_model "./backend/models/model.gguf"
        echo -e "${YELLOW}Note: CPU mode is slower. Consider GPU for better performance.${NC}"
        deploy "$COMPOSE_FILE" "CPU" "$REBUILD"
        ;;
    gpu)
        COMPOSE_FILE="docker-compose.gpu.yml"
        if ! check_gpu; then
            echo -e "${RED}Error: GPU mode requires NVIDIA Docker runtime${NC}"
            echo -e "${YELLOW}Install with: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html${NC}"
            echo -e "${YELLOW}Or use: $0 cpu${NC}"
            exit 1
        fi
        check_model "./backend/models/model.gguf"
        deploy "$COMPOSE_FILE" "GPU" "$REBUILD"
        ;;
    production)
        COMPOSE_FILE="docker-compose.production.yml"
        if ! check_gpu; then
            echo -e "${RED}Error: Production mode requires NVIDIA Docker runtime${NC}"
            echo -e "${YELLOW}Or use: $0 cpu${NC}"
            exit 1
        fi
        check_model "./backend/models/model.gguf"
        deploy "$COMPOSE_FILE" "PRODUCTION" "$REBUILD"
        ;;
    dev)
        COMPOSE_FILE="docker-compose.yml"
        echo -e "${YELLOW}Development mode uses Groq API (requires GROQ_API_KEY)${NC}"
        deploy "$COMPOSE_FILE" "DEVELOPMENT" "$REBUILD"
        ;;
esac
