# Local Gemma Vision Setup with Ollama

Complete guide to get Gemma running locally for TactileCode diagram extraction.

## Step 1: Install Ollama

### Windows
1. Download from https://ollama.ai/download
2. Run installer (ollama-windows.exe)
3. Opens in system tray automatically
4. Verify: Open PowerShell and run:
```powershell
ollama --version
```

### macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify installation:**
```bash
ollama --version
ollama serve  # Should run on http://localhost:11434
```

---

## Step 2: Pull a Vision Model

Ollama has several vision options. Pick ONE:

### Option A: LLaVA (Recommended for Architecture Diagrams)
```bash
ollama pull llava:7b-v1.6
```
- **Size:** 4.7 GB
- **Speed:** Moderate (good balance)
- **Accuracy:** Good for diagrams
- **GPU Memory:** 6GB+

### Option B: Gemma 2 Vision (Better accuracy, larger)
```bash
ollama pull gemma2:27b
```
- **Size:** 16 GB
- **Speed:** Slow on CPU
- **Accuracy:** Excellent
- **GPU Memory:** 24GB+

### Option C: Miniconda (Fast, less accurate)
```bash
ollama pull miniconda
```
- **Size:** 1.3 GB
- **Speed:** Fast
- **Accuracy:** Lower
- **GPU Memory:** 2GB+

**Recommendation for MVP:** Start with LLaVA 7B

```bash
ollama pull llava:7b-v1.6
```

---

## Step 3: Verify Ollama is Running

Open new PowerShell:
```powershell
# Check if Ollama is serving
curl http://localhost:11434/api/tags

# Should return available models in JSON
```

If you see models listed, you're good!

If not, explicitly start the server:
```bash
ollama serve
```

---

## Step 4: Test with a Sample Image

```bash
# Test Ollama API
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llava:7b-v1.6",
    "prompt": "Describe this image in one sentence",
    "images": ["<base64-image-here>"],
    "stream": false
  }'
```

---

## Step 5: Install Python Dependencies

Add ollama library to requirements:

```bash
cd backend
pip install ollama
```

---

## Step 6: Update TactileCode Backend

See `OLLAMA_INTEGRATION.md` for the code changes.

---

## Troubleshooting

### "ollama command not found"
- Windows: Restart computer after installation
- macOS/Linux: Add to PATH or restart terminal

### "Connection refused on localhost:11434"
- Run `ollama serve` in a dedicated terminal
- Keep that terminal open while using TactileCode

### "Out of memory" error
- Model too large for your GPU
- Try smaller model (llava:7b instead of gemma2:27b)
- Run on CPU (slower but works)

### "Model pulling stuck"
- Internet connection issue
- Try again: `ollama pull llava:7b-v1.6`

### Slow responses
- Normal on CPU
- LLaVA 7B: ~30-60 seconds per image on CPU
- With GPU: 2-5 seconds

---

## Configuration

Update `.env`:

```bash
# Use Ollama instead of Gemini
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:7b-v1.6

# Disable Gemini
GEMINI_API_KEY=
```

---

## Performance Expectations

| Model | Size | GPU Speed | CPU Speed | Accuracy |
|-------|------|-----------|-----------|----------|
| llava:7b-v1.6 | 4.7GB | 2-5s | 30-60s | Good |
| gemma2:7b | 4.2GB | 2-5s | 30-60s | Better |
| gemma2:27b | 16GB | 5-10s | 2-5min | Excellent |
| miniconda | 1.3GB | <1s | 5-10s | Lower |

---

## Next Steps

1. Install Ollama
2. Pull LLaVA: `ollama pull llava:7b-v1.6`
3. Start server: `ollama serve`
4. Update TactileCode (see OLLAMA_INTEGRATION.md)
5. Restart backend
6. Upload a diagram

Done!
