#!/bin/bash
# Download Qwen2.5-7B model for Language Tutor

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Language Tutor Model Download ===${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="$PROJECT_DIR/backend/models"

# Create models directory
mkdir -p "$MODEL_DIR"

cd "$MODEL_DIR"

# Model options
echo ""
echo "Select model to download:"
echo "1) Qwen2.5-7B-Instruct-Q4_K_M (4.4GB) - Recommended for 8GB+ VRAM"
echo "2) Qwen2.5-3B-Instruct-Q4_K_M (2.0GB) - For lower VRAM"
echo "3) Qwen2.5-7B-Instruct-Q8_0 (7.7GB) - Higher quality, needs 12GB+ VRAM"
echo "4) Custom URL"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
        MODEL_NAME="Qwen2.5-7B-Instruct-Q4_K_M"
        ;;
    2)
        MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
        MODEL_NAME="Qwen2.5-3B-Instruct-Q4_K_M"
        ;;
    3)
        MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q8_0.gguf"
        MODEL_NAME="Qwen2.5-7B-Instruct-Q8_0"
        ;;
    4)
        read -p "Enter model URL: " MODEL_URL
        MODEL_NAME="custom_model"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Downloading $MODEL_NAME...${NC}"
echo "URL: $MODEL_URL"
echo "Destination: $MODEL_DIR/model.gguf"
echo ""

# Download with progress
if command -v wget &> /dev/null; then
    wget --show-progress -O model.gguf "$MODEL_URL"
elif command -v curl &> /dev/null; then
    curl -L --progress-bar -o model.gguf "$MODEL_URL"
else
    echo "Error: wget or curl is required"
    exit 1
fi

# Verify download
if [ -f "model.gguf" ]; then
    SIZE=$(du -h model.gguf | cut -f1)
    echo ""
    echo -e "${GREEN}Download complete!${NC}"
    echo "Model: model.gguf ($SIZE)"
    echo ""
    echo "You can now start the application with:"
    echo "  cd $PROJECT_DIR && ./scripts/deploy.sh"
else
    echo "Download failed!"
    exit 1
fi
