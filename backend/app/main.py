"""
TactileCode Backend FastAPI Application.
Accessible architecture and flowchart graph extraction for blind and low-vision developers.
"""

import logging
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.diagrams import router as diagrams_router
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("tactilecode")

app = FastAPI(
    title="TactileCode API",
    description="Accessible Diagram-to-Graph Extraction Pipeline",
    version="1.0.0"
)

# CORS configuration for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagrams_router)

# Serve frontend static files (if built)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve React SPA - fallback to index.html for client-side routing."""
        # Ignore API routes
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)
        
        # Try exact file first
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Fallback to index.html for SPA routing
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        return JSONResponse({"error": "Not found"}, status_code=404)
    
    @app.get("/", include_in_schema=False)
    async def serve_root():
        """Serve root index.html"""
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({
            "message": "TactileCode API running",
            "docs": "/docs",
            "frontend": "Not built. Run: cd frontend && npm run build"
        })


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    from app.services.model_client import get_model_client
    
    model_client = get_model_client()
    
    # Check if it's Ollama and verify connection
    ollama_status = None
    if settings.ollama_enabled:
        from app.services.ollama_client import OllamaClient
        if isinstance(model_client, OllamaClient):
            ollama_status = await model_client.health_check()
    
    return {
        "status": "healthy",
        "service": "TactileCode API",
        "model_type": type(model_client).__name__,
        "model_configured": bool(settings.api_key) or settings.ollama_enabled,
        "ollama_enabled": settings.ollama_enabled,
        "ollama_status": ollama_status,
        "fallback_enabled": settings.fallback_to_mock,
    }


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error handling {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal server error occurred. Please verify graph input."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
