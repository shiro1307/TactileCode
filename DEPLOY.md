# TactileCode Live Deployment Guide

Get TactileCode live with a public link in **5 minutes**.

---

## Option 1: Replit (Easiest, Fastest) ⚡

### Steps:

1. **Push to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Add deployment config"
   git push
   ```

2. **Go to [replit.com](https://replit.com)**
   - Click "Import from GitHub"
   - Select your TactileCode repo
   - Click "Import"

3. **Replit auto-detects `.replit` file**
   - Automatically runs `python deploy.py`
   - Builds frontend + starts backend
   - Generates live link automatically

4. **Your live URL appears at top** 
   - Example: `https://tacticl-code.replit.dev`
   - Share this link!

**Total time: 3–5 minutes**

---

## Option 2: Railway (Also Very Easy) 🚂

### Steps:

1. **Go to [railway.app](https://railway.app)**
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Connect your repo

2. **Railway auto-detects Python + Node**
   - Creates `Procfile` automatically (or uses existing)
   - Builds frontend
   - Starts backend

3. **Add environment variables**
   - Go to "Variables"
   - Paste your `.env` contents:
     ```
     GEMMA_API_KEY=your_key_here
     FALLBACK_TO_MOCK=true
     PORT=8000
     HOST=0.0.0.0
     ```

4. **Deploy runs automatically**
   - Live URL appears in "Deployments"
   - Example: `https://tacticl-code-production.up.railway.app`

**Total time: 5–7 minutes**

---

## Option 3: Render (Free Tier) 🎨

### Steps:

1. **Go to [render.com](https://render.com)**
   - Click "New +" → "Web Service"
   - Connect GitHub repo

2. **Configure:**
   - Name: `tacticl-code`
   - Environment: `Python 3`
   - Build command: `python deploy.py`
   - Start command: (leave empty, handled by deploy.py)

3. **Add environment variables**
   - Paste `.env` contents

4. **Click "Deploy"**
   - Takes ~2–3 minutes
   - Live URL: `https://tacticl-code.onrender.com`

**Total time: 5–8 minutes**

---

## What Gets Deployed

`deploy.py` handles everything:

1. **Installs Python dependencies** from `requirements.txt`
2. **Installs Node dependencies** with `npm install`
3. **Builds React frontend** to static files
4. **Starts FastAPI backend** on port 8000
5. **Serves both** from same URL (no CORS issues)

---

## Configuration

### Environment Variables

The backend reads from `.env`. For deployments, add these to your platform:

```bash
# Required
GEMMA_API_KEY=your_api_key_here  # Get free key from ai.google.dev
FALLBACK_TO_MOCK=true             # Use mock data if API fails (recommended)

# Optional
PORT=8000
HOST=0.0.0.0
MAX_UPLOAD_SIZE_MB=10
OLLAMA_ENABLED=false
```

### API Key Options (Free)

1. **Google Gemma 4** (Recommended)
   - Go to [ai.google.dev](https://ai.google.dev)
   - Click "Get API Key"
   - Copy key to deployment platform's environment variables
   - Free tier: 60 requests/minute

2. **Fallback Mode** (No API Needed)
   - Set `FALLBACK_TO_MOCK=true`
   - Demo works with cached responses
   - Perfect for testing/showcasing

---

## Testing Your Live Deployment

Once deployed, test with:

```bash
# Health check
curl https://your-live-url.com/api/health

# Should return:
{
  "status": "healthy",
  "service": "TactileCode API",
  "model_configured": true,
  "fallback_enabled": true
}
```

---

## Troubleshooting

### "Build failed"
- Check `deploy.py` logs
- Ensure `requirements.txt` and `package.json` exist
- Frontend build may take 60+ seconds

### "Module not found"
- Deployment platform must have Python 3.10+
- Check `replit.nix` or platform's Python version setting

### "Upload fails" / "API returns 500"
- Verify `GEMMA_API_KEY` is set correctly
- Check backend logs for errors
- Try with `FALLBACK_TO_MOCK=true`

### "Frontend shows blank page"
- Check browser console (F12)
- Verify API requests go to `/api/*` endpoints
- Frontend auto-detects backend at same domain

---

## Recommended: Replit + GitHub Link

**Fastest way to share:**

1. Deploy on Replit (5 min)
2. Replit auto-generates shareable link
3. Works with no backend setup on recipient's end

**Link looks like:**
```
https://replit.com/@yourusername/tacticl-code
```

Share this URL — anyone can click "Run" to see it live.

---

## Local Development (Alternative)

If you want to deploy locally first:

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend dev server
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## Deployment Comparison

| Platform | Time | Free Tier | Uptime | Link Share |
|----------|------|-----------|--------|-----------|
| **Replit** | 3–5 min | ✓ Yes | 99% | Instant |
| **Railway** | 5–7 min | ✓ $5/mo after | 99.9% | Instant |
| **Render** | 5–8 min | ✓ Yes (sleeps) | 99.5% | Instant |
| Local (ngrok) | 10 min | ✓ Yes | Your PC | ngrok URL |

---

## Next Steps After Deployment

1. **Test the live link**
   - Upload a test diagram
   - Try keyboard navigation (↑↓ arrows, Tab)
   - Test screen reader (if available)

2. **Share your live URL**
   - Perfect for hackathon demos
   - Works on any device with a browser

3. **Scale if needed**
   - Upgrade Replit plan for more resources
   - Switch to Railway/Render for production

---

## Get Live URL

**Pick one:**

- **Replit**: 5 min ⚡ (Easiest)
- **Railway**: 7 min 🚂
- **Render**: 8 min 🎨

Then reply with your live URL!

