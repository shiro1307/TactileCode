#!/bin/bash
# TactileCode Ollama Setup Script
# Run this to install and configure Ollama + TactileCode

set -e

echo "================================"
echo "TactileCode Ollama Setup"
echo "================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "[1/4] Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - download from website
        echo "Please download Ollama from https://ollama.ai/download"
        exit 1
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        echo "Please download Ollama from https://ollama.ai/download"
        exit 1
    fi
else
    echo "[1/4] Ollama already installed: $(ollama --version)"
fi

echo ""
echo "[2/4] Pulling LLaVA model (this may take 5-10 minutes)..."
ollama pull llava:7b-v1.6

echo ""
echo "[3/4] Installing TactileCode dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "[4/4] Creating .env configuration..."
cat > .env << 'EOF'
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:7b-v1.6
OLLAMA_TIMEOUT_SECONDS=300
FALLBACK_TO_MOCK=true
EOF

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start Ollama in a dedicated terminal:"
echo "   ollama serve"
echo ""
echo "2. In another terminal, start TactileCode backend:"
echo "   cd backend"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "3. In a third terminal, start frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:5173 and upload a diagram!"
echo ""
echo "================================"
