"""
Multilingual AI Content Moderation Platform
FastAPI Server Entry Point
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.routers import (
    analyze,
    moderation,
    reports,
    integrations,
    analytics,
    settings,
    auth
)
from backend.app.database import init_db

# Initialize database schema and seeds
init_db()

app = FastAPI(
    title="Toxico AI - Multilingual Content Moderation Platform",
    description="Production-grade AI safety system detecting multilingual toxic content and image memes across social media.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(moderation.router)
app.include_router(reports.router)
app.include_router(integrations.router)
app.include_router(analytics.router)
app.include_router(settings.router)

# Health Check
@app.get("/api/health")
def health_check():
    return {
        'status': 'healthy',
        'platform': 'Multilingual AI Content Moderation Platform',
        'version': '1.0.0',
        'models_active': True,
        'ocr_engine': 'Windows Media WinRT OCR'
    }

# Mount Frontend Static Directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(frontend_dir, "index.html")
        return FileResponse(index_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
