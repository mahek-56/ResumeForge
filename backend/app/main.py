"""
Main FastAPI Application Entrypoint
SAMATRIX RESUMEFORGE 2026

Mounts:
- CORS middleware
- Centralized router
- Global exception handlers
- Startup lifecycle for preloading ML artifacts
"""

import os
import sys

# Ensure root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.api.endpoints import router as api_router
from backend.ml.predict import ResumePredictor

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load model once on startup to guarantee ultra-fast inference."""
    print("Initiating ResumeForge AI Backend...")
    predictor = ResumePredictor.get_instance()
    if predictor.loaded:
        print(f"Preloaded champion model: {predictor.metadata.get('model_signature', 'Ready')}")
    else:
        print("[WARN] Model artifacts not loaded yet. If training is ongoing, artifacts will load upon completion.")


# Global exception handler to never leak internal stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[UNHANDLED EXCEPTION] {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An internal server error occurred while processing your request."}
    )


# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn
    # Automatically select import string depending on execution directory
    module_target = "app.main:app" if os.path.exists("app") else "backend.app.main:app"
    uvicorn.run(module_target, host="127.0.0.1", port=8000, reload=True)

