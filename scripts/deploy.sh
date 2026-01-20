#!/bin/bash
# Deployment script for Language Tutor on local PC server or VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo "  --rebuild    Rebuild Docker images"
    echo "  --no-cache   Rebuild with --no-cache (use after changing SERVER_HOST)"
    echo "  --stop       Stop all running services"
    echo "  --logs       Show logs from running services"
    echo "  --set-host   Set/update SERVER_HOST for VPS deployment"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 cpu                    # Run with CPU only (localhost)"
    echo "  $0 cpu --set-host         # Set VPS IP and run CPU mode"
    echo "  $0 gpu                    # Run with GPU"
    echo "  $0 cpu --rebuild          # Rebuild and run CPU mode"
    echo "  $0 cpu --no-cache         # Force full rebuild (after IP change)"
    echo "  $0 --stop                 # Stop all services"
    echo ""
    echo -e "${CYAN}VPS Deployment:${NC}"
    echo "  1. Run: $0 cpu --set-host"
    echo "  2. Enter your VPS public IP or domain when prompted"
    echo "  3. Or manually: echo 'SERVER_HOST=your-ip' > .env && $0 cpu --no-cache"
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

# Set server host for VPS deployment
set_server_host() {
    echo -e "${CYAN}=== VPS/Remote Deployment Setup ===${NC}"
    echo ""
    echo "Enter your VPS public IP address or domain name."
    echo "This will be used by the frontend to connect to the backend API."
    echo ""
    read -p "Server IP/Domain (e.g., 123.45.67.89 or myserver.com): " server_host
    
    if [ -z "$server_host" ]; then
        echo -e "${RED}Error: Server host cannot be empty${NC}"
        exit 1
    fi
    
    # Create or update .env file
    if [ -f ".env" ]; then
        # Update existing SERVER_HOST or add it
        if grep -q "^SERVER_HOST=" .env; then
            sed -i "s/^SERVER_HOST=.*/SERVER_HOST=$server_host/" .env
        else
            echo "SERVER_HOST=$server_host" >> .env
        fi
    else
        echo "SERVER_HOST=$server_host" > .env
    fi
    
    echo -e "${GREEN}SERVER_HOST set to: $server_host${NC}"
    echo -e "${YELLOW}Note: Frontend must be rebuilt with --no-cache to apply changes.${NC}"
    
    # Force rebuild with no-cache
    REBUILD=true
    NO_CACHE=true
}

# Load .env file if exists
load_env() {
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs -d '\n' 2>/dev/null) || true
    fi
}

# Check and warn about SERVER_HOST
check_server_host() {
    load_env
    
    if [ -z "$SERVER_HOST" ] || [ "$SERVER_HOST" = "localhost" ]; then
        echo -e "${YELLOW}================================================${NC}"
        echo -e "${YELLOW}WARNING: SERVER_HOST is not set or is localhost${NC}"
        echo -e "${YELLOW}================================================${NC}"
        echo ""
        echo "The frontend will only work from the same machine (localhost)."
        echo "For VPS/remote deployment, run: $0 $MODE --set-host"
        echo ""
        read -p "Continue with localhost? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    else
        echo -e "${GREEN}SERVER_HOST: $SERVER_HOST${NC}"
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
    local no_cache="$4"
    
    # Load environment
    load_env
    local api_url="http://${SERVER_HOST:-localhost}:8000"
    
    echo -e "${BLUE}Deploying in ${mode_name} mode...${NC}"
    echo -e "${YELLOW}Using: $compose_file${NC}"
    echo -e "${CYAN}API URL (baked into frontend): $api_url${NC}"
    
    if [ "$rebuild" = true ]; then
        if [ "$no_cache" = true ]; then
            echo -e "${YELLOW}Rebuilding images with --no-cache (this may take a while)...${NC}"
            docker compose -f "$compose_file" build --no-cache
        else
            echo -e "${YELLOW}Rebuilding images (this may take a while)...${NC}"
            docker compose -f "$compose_file" build
        fi
    fi
    
    echo -e "${YELLOW}Starting services...${NC}"
    docker compose -f "$compose_file" up -d --build
    
    # Wait longer for CPU mode
    local wait_time=12
    if [ "$mode_name" = "CPU" ]; then
        wait_time=18
    fi
    
    sleep 5
    wait_for_health "$compose_file" "$wait_time"
    
    # Get the server host for display
    load_env
    local display_host="${SERVER_HOST:-localhost}"
    
    echo ""
    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    echo -e "Frontend: ${GREEN}http://${display_host}:3000${NC}"
    echo -e "Backend API: ${GREEN}http://${display_host}:8000${NC}"
    echo -e "API Docs: ${GREEN}http://${display_host}:8000/docs${NC}"
    echo ""
    if [ "$display_host" != "localhost" ]; then
        echo -e "${CYAN}Remote Access: Open http://${display_host}:3000 from any browser${NC}"
        echo ""
    fi
    echo "Commands:"
    echo "  View logs:     $0 --logs"
    echo "  Stop services: $0 --stop"
    echo "  Rebuild:       $0 $MODE --rebuild"
    echo "  Change host:   $0 $MODE --set-host"
}

# Parse arguments
MODE=""
REBUILD=false
SET_HOST=false
NO_CACHE=false

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
        --no-cache)
            REBUILD=true
            NO_CACHE=true
            shift
            ;;
        --set-host)
            SET_HOST=true
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

# Handle --set-host option
if [ "$SET_HOST" = true ]; then
    set_server_host
fi

# Check SERVER_HOST for non-dev modes
if [ "$MODE" != "dev" ]; then
    check_server_host
fi

# Select compose file based on mode
case $MODE in
    cpu)
        COMPOSE_FILE="docker-compose.cpu.yml"
        check_model "./backend/models/model.gguf"
        echo -e "${YELLOW}Note: CPU mode is slower. Consider GPU for better performance.${NC}"
        deploy "$COMPOSE_FILE" "CPU" "$REBUILD" "$NO_CACHE"
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
        deploy "$COMPOSE_FILE" "GPU" "$REBUILD" "$NO_CACHE"
        ;;
    production)
        COMPOSE_FILE="docker-compose.production.yml"
        if ! check_gpu; then
            echo -e "${RED}Error: Production mode requires NVIDIA Docker runtime${NC}"
            echo -e "${YELLOW}Or use: $0 cpu${NC}"
            exit 1
        fi
        check_model "./backend/models/model.gguf"
        deploy "$COMPOSE_FILE" "PRODUCTION" "$REBUILD" "$NO_CACHE"
        ;;
    dev)
        COMPOSE_FILE="docker-compose.yml"
        echo -e "${YELLOW}Development mode uses Groq API (requires GROQ_API_KEY)${NC}"
        deploy "$COMPOSE_FILE" "DEVELOPMENT" "$REBUILD" "$NO_CACHE"
        ;;
esac
