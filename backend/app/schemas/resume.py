"""
Pydantic Schemas for API Request and Response Models
SAMATRIX RESUMEFORGE 2026
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Raw text of the candidate resume")


class PredictionResult(BaseModel):
    category: str
    confidence: float
    confidence_percentage: float


class TopPrediction(BaseModel):
    category: str
    score: float
    percentage: float


class KeywordAttribution(BaseModel):
    feature: str
    weight: float
    contribution: Optional[float] = None
    relative_pct: Optional[int] = 100


class SkillCategory(BaseModel):
    category: str
    skills: List[str]


class ProfileMetrics(BaseModel):
    word_count: int
    char_count: int
    education_signals: List[str]
    experience_signals: List[str]
    has_certifications: bool
    certifications_count: int


class PredictResponse(BaseModel):
    success: bool
    prediction: PredictionResult
    top_predictions: List[TopPrediction]
    keywords: List[KeywordAttribution]
    explanation: Optional[str] = None
    skills: Optional[List[SkillCategory]] = None
    metrics: Optional[ProfileMetrics] = None
    model: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    model_signature: Optional[str] = None


class ModelInfoResponse(BaseModel):
    model_name: str
    representation: str
    model_signature: str
    accuracy: float
    macro_f1: float
    weighted_f1: float
    num_classes: int
    categories: List[str]
    vocabulary_size: int
    trained_timestamp: str
    training_samples: int
    test_samples: int
