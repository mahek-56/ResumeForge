"""
FastAPI Route Endpoints
SAMATRIX RESUMEFORGE 2026

Exposes:
- GET  /api/health
- GET  /api/model-info
- POST /api/predict
- POST /api/predict/file
- POST /api/analyze
- GET  /api/categories
- GET  /api/analytics
- GET  /api/metrics
- GET  /api/features/{category}
"""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List

from backend.app.schemas.resume import (
    PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
)
from backend.ml.predict import ResumePredictor
from backend.app.services.document_parser import parse_resume_document
from backend.app.services.analytics_service import (
    get_analytics_data, get_metrics_data, get_features_for_category
)
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check and model loading verification."""
    predictor = ResumePredictor.get_instance()
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        model_loaded=predictor.loaded,
        model_signature=predictor.metadata.get("model_signature", "Not loaded")
    )


@router.get("/model-info")
async def get_model_info():
    """Retrieve champion model metadata and training parameters."""
    predictor = ResumePredictor.get_instance()
    if not predictor.metadata:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metadata is unavailable. Please run training pipeline first."
        )
    return predictor.metadata


@router.post("/predict")
async def predict_text(request: PredictRequest):
    """
    Classify resume raw text and extract calibrated confidence and keywords.
    """
    if not request.resume_text or len(request.resume_text.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text must contain at least 10 characters."
        )

    predictor = ResumePredictor.get_instance()
    result = predictor.predict(request.resume_text)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.get("error", "Classification failed.")
        )

    return result


@router.post("/predict/file")
async def predict_file(file: UploadFile = File(...)):
    """
    Accept PDF, DOCX, or TXT file, extract text, and return classification insights.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Accepted formats: PDF, DOCX, TXT."
        )

    file_bytes = await file.read()

    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    success, extracted_text, error_msg = parse_resume_document(file_bytes, file.filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_msg
        )

    predictor = ResumePredictor.get_instance()
    result = predictor.predict(extracted_text)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.get("error", "Failed to analyze extracted document text.")
        )

    result["filename"] = file.filename
    result["file_size_kb"] = round(len(file_bytes) / 1024, 1)
    result["extracted_preview"] = extracted_text[:300].strip() + "..."
    return result


@router.post("/analyze")
async def analyze_comprehensive(request: PredictRequest):
    """
    Alias / extended endpoint for full resume profile intelligence.
    """
    return await predict_text(request)


@router.get("/categories")
async def get_all_categories():
    """Retrieve list of all 24 resume classification target categories."""
    predictor = ResumePredictor.get_instance()
    if predictor.label_encoder is not None:
        categories = list(predictor.label_encoder.classes_)
    else:
        categories = predictor.metadata.get("categories", [])
    return {"total": len(categories), "categories": categories}


@router.get("/analytics")
async def get_analytics():
    """Retrieve aggregate dataset distribution, model comparison, and error metrics."""
    return get_analytics_data()


@router.get("/metrics")
async def get_metrics():
    """Retrieve per-class Precision/Recall/F1 and feature maps."""
    return get_metrics_data()


@router.get("/features/{category}")
async def get_category_features(category: str):
    """Retrieve top weighted predictive n-grams for an individual category."""
    features = get_features_for_category(category)
    if not features:
        # Check case-insensitive match
        all_cats = ResumePredictor.get_instance().metadata.get("categories", [])
        matched = next((c for c in all_cats if c.lower() == category.lower()), None)
        if matched:
            features = get_features_for_category(matched)

    return {
        "category": category,
        "features": features
    }
