# TactileCode Ollama Setup Script for Windows
# Run: powershell -ExecutionPolicy Bypass -File setup_ollama.ps1

Write-Host "================================"
Write-Host "TactileCode Ollama Setup for Windows"
Write-Host "================================"
Write-Host ""

# Step 1: Check/Install Ollama
Write-Host "[1/5] Checking Ollama installation..."
try {
    $ollamaVersion = ollama --version
    Write-Host "✓ Ollama already installed: $ollamaVersion"
} catch {
    Write-Host "✗ Ollama not found. Please install from https://ollama.ai/download"
    Write-Host ""
    Write-Host "After installation, run this script again."
    exit 1
}

# Step 2: Pull model
Write-Host ""
Write-Host "[2/5] Pulling LLaVA 7B model (this may take 5-10 minutes)..."
Write-Host "Downloading ~4.7 GB model..."
ollama pull llava:7b-v1.6

# Step 3: Verify model
Write-Host ""
Write-Host "[3/5] Verifying model..."
$models = ollama list
if ($models -like "*llava*") {
    Write-Host "✓ Model successfully installed"
} else {
    Write-Host "✗ Model installation may have failed"
}

# Step 4: Install Python dependencies
Write-Host ""
Write-Host "[4/5] Installing Python dependencies..."
Set-Location backend
pip install -r requirements.txt
Set-Location ..

# Step 5: Create .env file
Write-Host ""
Write-Host "[5/5] Creating .env configuration..."
$envContent = @"
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:7b-v1.6
OLLAMA_TIMEOUT_SECONDS=300
FALLBACK_TO_MOCK=true
"@

Set-Content -Path "backend\.env" -Value $envContent
Write-Host "✓ Configuration saved to backend\.env"

# Summary
Write-Host ""
Write-Host "================================"
Write-Host "Setup Complete!"
Write-Host "================================"
Write-Host ""
Write-Host "Next steps (open 3 terminals):"
Write-Host ""
Write-Host "Terminal 1 - Start Ollama:"
Write-Host "  ollama serve"
Write-Host ""
Write-Host "Terminal 2 - Start Backend:"
Write-Host "  cd backend"
Write-Host "  python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "Terminal 3 - Start Frontend:"
Write-Host "  cd frontend"
Write-Host "  npm run dev"
Write-Host ""
Write-Host "Then open: http://localhost:5173"
Write-Host ""
Write-Host "================================"
