# Getting Started: TactileCode with Local Ollama

**Goal:** Get TactileCode working with local Gemma vision model (no API keys, completely offline)

**Time:** 10-15 minutes setup + first image extraction time

---

## Prerequisites

- Windows 10+, macOS, or Linux
- 6GB+ RAM (8GB+ recommended)
- 5GB+ free disk space
- Modern CPU or GPU (any GPU helps)

---

## Step-by-Step Setup

### Step 1: Install Ollama (5 min)

Download and install: **https://ollama.ai/download**

- Windows: Run `.exe` installer
- macOS: Run `.dmg` installer
- Linux: Run installation script

After installation, verify:
```bash
ollama --version
```

### Step 2: Download a Vision Model (10 min)

Open terminal/PowerShell and run:

```bash
ollama pull llava:7b-v1.6
```

This downloads a 4.7 GB vision model. Wait for completion.

**What you'll see:**
```
pulling manifest
pulling 8c...
pulling 8f...
[=================================================] 100%
```

### Step 3: Start Ollama Server

**KEEP THIS TERMINAL OPEN.**

```bash
ollama serve
```

You should see:
```
2024/10/24 10:00:00 Listening on 127.0.0.1:11434
```

If you see this, Ollama is ready!

### Step 4: Configure TactileCode Backend

Create file: `backend/.env`

```bash
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava:7b-v1.6
OLLAMA_TIMEOUT_SECONDS=300
FALLBACK_TO_MOCK=true
```

Save the file.

### Step 5: Start Backend

**NEW TERMINAL** (keep Ollama server running in first one)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Wait for:
```
INFO:     Initializing OllamaClient (model: llava:7b-v1.6)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

If you see "Initializing OllamaClient", you're good!

### Step 6: Start Frontend

**ANOTHER NEW TERMINAL** (Ollama + Backend running)

```bash
cd frontend
npm install  # Only if first time
npm run dev
```

Wait for:
```
VITE v5.4.21 ready in 500 ms
```

### Step 7: Test It!

1. Open **http://localhost:5173** in browser
2. Click "Upload Diagram"
3. Choose a PNG or JPG image
4. **Wait 30-60 seconds** (model is processing)
5. See extracted graph appear!

---

## What Happens Behind the Scenes

```
You upload image.png
         ↓
Browser sends to http://localhost:8000/api/diagrams
         ↓
Backend receives file
         ↓
OllamaClient converts image to base64
         ↓
HTTP POST to http://localhost:11434/api/generate
         ↓
LLaVA vision model analyzes image (30-60 seconds)
         ↓
Model returns JSON: {nodes: [...], edges: [...]}
         ↓
Backend validates and cleans graph
         ↓
Converts to NetworkX graph
         ↓
Stores in memory
         ↓
Returns DiagramResponse
         ↓
Frontend receives and displays
         ↓
You can navigate with arrow keys!
```

---

## Expected Performance

### First Upload (after startup)
- 30-60 seconds on CPU
- 2-5 seconds on GPU
- Model loading into memory

### Subsequent Uploads
- 30-60 seconds on CPU (model stays in memory)
- 2-5 seconds on GPU

### If It's Slow
- Normal on CPU - just wait
- Check Ollama logs for errors
- Try smaller model if needed

---

## Troubleshooting

### "Cannot connect to localhost:11434"

**Problem:** Ollama server not running

**Fix:** 
```bash
ollama serve
```
in first terminal. Keep it open.

### "Model llava:7b-v1.6 not found"

**Problem:** Model didn't download

**Fix:**
```bash
ollama pull llava:7b-v1.6
```

### "Out of memory" or very slow

**Problem:** Model too large or system under load

**Fix:**
- Close other apps
- Try smaller model: `ollama pull miniconda`
- Use GPU if available
- Increase timeout in .env: `OLLAMA_TIMEOUT_SECONDS=600`

### "JSON parse error" in backend logs

**Problem:** Model output malformed

**Fix:**
1. Try different model: `ollama pull gemma2:7b`
2. Check Ollama is responding: `curl http://localhost:11434/api/tags`
3. Look at backend logs for details

### "Upload button doesn't work"

**Problem:** Frontend not connected to backend

**Fix:**
1. Check backend is running (you should see API logs)
2. Check Ollama is running (terminal 1)
3. Refresh browser

---

## Available Models

Try different models by pulling and updating `.env`:

### Fast & Good (Recommended)
```bash
ollama pull llava:7b-v1.6  # ~4.7 GB
```

### Better Accuracy
```bash
ollama pull gemma2:7b  # ~4.2 GB
```

### Fastest (Lower quality)
```bash
ollama pull miniconda  # ~1.3 GB
```

### Best Accuracy (Slow, needs 24GB)
```bash
ollama pull gemma2:27b  # ~16 GB
```

Then update `.env`:
```bash
OLLAMA_MODEL=gemma2:7b
```

Restart backend. That's it!

---

## File Structure

```
TactileCode/
├── backend/
│   ├── .env              ← You create this
│   ├── app/
│   │   ├── services/
│   │   │   ├── ollama_client.py  ← NEW: Ollama integration
│   │   │   └── model_client.py   ← Modified to use Ollama
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── npm run dev
└── OLLAMA_INTEGRATION.md  ← Full reference
```

---

## Next Steps

Now that you have Ollama working:

1. **Test with various diagrams** — Try different image types
2. **Improve prompt** — Edit `backend/app/services/ollama_client.py` line ~14
3. **Benchmark accuracy** — See `backend/benchmark_eval.py`
4. **Deploy** — Use Docker for production

---

## Performance Tips

### For CPU (Mac/Intel)
- Use LLaVA 7B (fastest good option)
- Close browser tabs to free memory
- 30-60 seconds per image is normal

### For GPU (NVIDIA/AMD)
- Ollama auto-detects GPU
- 2-5 seconds per image
- No extra config needed

### For Mac M1/M2
- Auto-optimized with Metal
- Very fast (similar to GPU)

---

## Uninstall / Clean Up

Remove model:
```bash
ollama rm llava:7b-v1.6
```

Uninstall Ollama:
```bash
# Windows: Control Panel → Remove Programs
# macOS: rm -rf /Applications/Ollama.app
# Linux: sudo apt remove ollama
```

---

## Getting Help

Check logs:
1. **Backend logs** — See "Initializing OllamaClient"
2. **Ollama logs** — Check terminal where you ran `ollama serve`
3. **Browser console** — F12 in browser
4. **Detailed debug** — Set `LOG_LEVEL=DEBUG` in `.env`

---

## Success Checklist

- [ ] Ollama installed (`ollama --version` works)
- [ ] Model downloaded (`ollama list` shows llava)
- [ ] Ollama server running (`ollama serve` in terminal 1)
- [ ] `.env` created with Ollama settings
- [ ] Backend running (`http://localhost:8000/docs` loads)
- [ ] Frontend running (`http://localhost:5173` loads)
- [ ] Diagram uploads and extracts

If you can check all boxes, you're good!

---

## Done!

You now have a **fully local, offline diagram extraction system**.

Next: Improve it, benchmark it, deploy it! 🚀
