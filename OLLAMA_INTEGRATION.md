# Ollama Integration for TactileCode

Complete setup guide for using local Gemma vision models with TactileCode.

## Quick Start (5 minutes)

### 1. Install Ollama
Download and install: https://ollama.ai/download

### 2. Pull a Vision Model
Choose ONE:

**LLaVA 7B (Recommended - Good balance)**
```bash
ollama pull llava:7b-v1.6
```

**Or Gemma 2 7B (Better accuracy)**
```bash
ollama pull gemma2:7b
```

Wait for download (2-10 minutes depending on internet).

### 3. Start Ollama Server
Open dedicated terminal/PowerShell:
```bash
ollama serve
```

Keep this terminal open while using TactileCode.

### 4. Configure TactileCode
Create `backend/.env`:

```bash
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:7b-v1.6
OLLAMA_TIMEOUT_SECONDS=300
```

### 5. Restart Backend

Stop current backend (Ctrl+C).

```bash
cd backend
pip install -r requirements.txt  # Install aiohttp if needed
python -m uvicorn app.main:app --reload
```

Watch for log message:
```
INFO:     Initializing OllamaClient (model: llava:7b-v1.6)
```

### 6. Test Upload

1. Go to http://localhost:5173
2. Upload a diagram image (PNG or JPG)
3. Wait 30-60 seconds (model is working)
4. See extracted graph appear

**That's it!**

---

## What's Happening Behind the Scenes

```
Your Image
    ↓
[Frontend Upload]
    ↓
[FastAPI /api/diagrams POST]
    ↓
[OllamaClient.extract_graph()]
    ↓
[HTTP POST to Ollama]
    ↓
[llava:7b-v1.6 Vision Model]
    ↓
[Returns JSON with nodes/edges/confidence]
    ↓
[Validator sanitizes graph]
    ↓
[NetworkX builds graph]
    ↓
[Returns DiagramResponse]
    ↓
[Frontend displays with queries]
```

---

## Performance Expectations

### CPU Only (No GPU)
- First run: 2-3 minutes (model loads into memory)
- Subsequent runs: 30-60 seconds per image
- Memory usage: 4-8 GB
- **Good for testing/demo, bearable for small batch**

### With GPU (NVIDIA/AMD/Intel)
- First run: 30 seconds (model loads to VRAM)
- Subsequent runs: 2-5 seconds per image
- Memory usage: 2-4 GB VRAM + 2-4 GB RAM
- **Usable for production**

### By Model Size

| Model | Size | CPU | GPU | Quality |
|-------|------|-----|-----|---------|
| llava:7b-v1.6 | 4.7GB | 30-60s | 2-5s | Good |
| gemma2:7b | 4.2GB | 30-60s | 2-5s | Better |
| gemma2:27b | 16GB | 2-5min | 5-10s | Excellent |
| miniconda | 1.3GB | 5-15s | <1s | Lower |

**Recommendation:** Start with `llava:7b-v1.6` for MVP. Upgrade if needed.

---

## Troubleshooting

### "Connection refused" or "Cannot connect to localhost:11434"

**Problem:** Ollama server not running

**Solution:**
```bash
ollama serve
```

Keep this terminal open in background.

### "Model not found"

**Problem:** Model not downloaded

**Solution:**
```bash
ollama pull llava:7b-v1.6
```

Wait for completion.

### "Out of memory"

**Problem:** Model too large for your system

**Solution:**
1. Use smaller model: `ollama pull miniconda`
2. Close other applications
3. Add swap/pagefile (Windows: Settings → System → Storage)

### "Timeout after 300s"

**Problem:** Model is too slow or stuck

**Solution:**
1. Increase timeout in `.env`:
   ```bash
   OLLAMA_TIMEOUT_SECONDS=600
   ```
2. Use smaller model
3. Check Ollama server logs for errors

### "Invalid JSON from model"

**Problem:** Model output malformed

**Solution:**
1. Try different model: `ollama pull gemma2:7b`
2. Check model is installed: `ollama list`
3. See detailed logs: Set `LOG_LEVEL=DEBUG`

---

## Model Comparison

### LLaVA 7B (Recommended for Architecture Diagrams)
```bash
ollama pull llava:7b-v1.6
```
- ✓ Good at diagrams
- ✓ Reasonable speed
- ✓ Balanced memory
- ✓ Well-tested

### Gemma 2 7B (Better Accuracy)
```bash
ollama pull gemma2:7b
```
- ✓ Better accuracy
- ✓ Reasonable speed
- ✓ Balanced memory
- ✓ Newer model

### Gemma 2 27B (Best Accuracy, Slow)
```bash
ollama pull gemma2:27b
```
- ✗ Requires 16GB+
- ✗ Very slow on CPU
- ✓ Excellent accuracy
- ✓ Good for GPU

### MiniCPM (Fast, Lower Quality)
```bash
ollama pull miniconda
```
- ✓ Very fast
- ✓ Low memory
- ✗ Lower accuracy
- ✓ Good for testing

**For MVP:** Stick with LLaVA 7B.

---

## Testing Ollama Directly

Before using with TactileCode, test Ollama API:

```bash
# 1. Check models
curl http://localhost:11434/api/tags

# 2. Simple text generation
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llava:7b-v1.6",
    "prompt": "Say hello",
    "stream": false
  }'

# 3. Expected response
{"model":"llava:7b-v1.6","created_at":"...","response":"Hello!..."}
```

If you see responses, Ollama is working!

---

## Configuration Reference

### .env Options

```bash
# Enable Ollama
OLLAMA_ENABLED=true

# Ollama server URL (default: localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# Model to use (see models below)
OLLAMA_MODEL=llava:7b-v1.6

# How long to wait for model response (seconds)
OLLAMA_TIMEOUT_SECONDS=300

# Fallback to mock data if Ollama fails
FALLBACK_TO_MOCK=true
```

### Logging

To see detailed Ollama logs, set environment variable:
```bash
LOG_LEVEL=DEBUG
```

Then restart backend.

---

## Adding New Models

To use a different model, just pull it:

```bash
ollama pull neural-chat:7b
ollama pull llama2:7b
ollama pull mistral:7b
```

Then update `.env`:
```bash
OLLAMA_MODEL=neural-chat:7b
```

Restart backend. Done!

---

## GPU Acceleration

### NVIDIA (CUDA)
- Ollama auto-detects
- Just needs NVIDIA drivers
- Works out of the box

### AMD (ROCm)
- Windows: Use CPU or WSL2 with ROCm
- Linux: `ollama serve` with ROCm driver

### Intel (OneAPI)
- Limited support
- Usually CPU fallback

### Apple Silicon
- Auto-optimized for Metal
- Excellent performance

---

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Ollama client dependencies
RUN pip install aiohttp

# Copy TactileCode
COPY backend /app/backend

WORKDIR /app/backend

RUN pip install -r requirements.txt

ENV OLLAMA_ENABLED=true
ENV OLLAMA_BASE_URL=http://ollama:11434

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3'

services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

  tactilecode:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      OLLAMA_ENABLED: "true"
      OLLAMA_BASE_URL: "http://ollama:11434"
      OLLAMA_MODEL: "llava:7b-v1.6"
    depends_on:
      - ollama

volumes:
  ollama_data:
```

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Pull a model
3. ✅ Start server
4. ✅ Configure TactileCode
5. ✅ Restart backend
6. ✅ Upload diagram
7. Monitor performance and adjust as needed

---

## Support

### Check Model Status
```bash
ollama list
```

### See Ollama Logs
```bash
ollama serve  # Logs in console
```

### Kill Stuck Process
```bash
# Windows: Task Manager → End "Ollama Service"
# macOS: killall ollama
# Linux: pkill ollama
```

### Reset Everything
```bash
# Remove all models (careful!)
rm -rf ~/.ollama/models

# Start fresh
ollama pull llava:7b-v1.6
ollama serve
```

---

Enjoy local, offline diagram extraction!
