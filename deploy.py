#!/usr/bin/env python3
"""
TactileCode Unified Deployment Script
Runs both backend API and serves frontend static build from one process.
Perfect for Replit, Railway, Render, etc.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def build_frontend():
    """Build React frontend to static files."""
    print("\n🔨 Building frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    result = subprocess.run(
        ["npm", "install"],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ npm install failed: {result.stderr}")
        return False
    print("✓ npm dependencies installed")
    
    # Build
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ npm build failed: {result.stderr}")
        return False
    print("✓ Frontend built to dist/")
    
    return True

def main():
    """Start the unified server."""
    # Build frontend first
    if not build_frontend():
        print("\n❌ Frontend build failed. Exiting.")
        sys.exit(1)
    
    print("\n🚀 Starting TactileCode server...\n")
    
    # Start backend (which now serves frontend)
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Set environment
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("FALLBACK_TO_MOCK", "true")
    
    # Run backend with frontend static files
    try:
        subprocess.run([
            "python", "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=False)
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
