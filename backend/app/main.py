"""
TactileCode Backend FastAPI Application.
Accessible architecture and flowchart graph extraction for blind and low-vision developers.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "TactileCode API",
        "model_configured": bool(settings.api_key),
        "model_name": settings.model_name,
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
