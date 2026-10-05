"""
Inference Pipeline for Resume Classification
SAMATRIX RESUMEFORGE 2026

Loads trained champion model artifacts and exposes `predict_resume(text)`.
Zero retraining at inference; sub-50ms latency.
"""

import os
import sys
import json
import joblib
import numpy as np
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.ml.preprocessing import clean_text, extract_skills, extract_sections_and_metrics
from backend.ml.explain import ExplainabilityEngine, get_explanation_narrative

MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "models")


class ResumePredictor:
    _instance = None

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.coefficients = None
        self.metadata = {}
        self.explainer = None
        self.loaded = False
        self._load_artifacts()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ResumePredictor()
        return cls._instance

    def _load_artifacts(self):
        try:
            model_path = os.path.join(MODELS_DIR, "best_model.joblib")
            vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
            le_path = os.path.join(MODELS_DIR, "label_encoder.joblib")
            coef_path = os.path.join(MODELS_DIR, "model_coefficients.joblib")
            meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

            if not os.path.exists(model_path):
                print(f"[WARN] Artifacts not yet available at {model_path}. Run train.py first.")
                return

            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vec_path)
            self.label_encoder = joblib.load(le_path)

            if os.path.exists(coef_path):
                self.coefficients = joblib.load(coef_path)

            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            self.explainer = ExplainabilityEngine(
                vectorizer=self.vectorizer,
                coefficients=self.coefficients,
                label_encoder=self.label_encoder
            )
            self.loaded = True
            print(f"[OK] ResumePredictor loaded successfully: {self.metadata.get('model_signature', 'Champion Model')}")
        except Exception as e:
            print(f"[ERROR] Failed to load model artifacts: {e}")
            self.loaded = False

    def predict(self, raw_text: str) -> Dict[str, Any]:
        """
        End-to-end inference on a single resume text string.
        """
        if not self.loaded:
            self._load_artifacts()
            if not self.loaded:
                return {
                    "success": False,
                    "error": "Model artifacts not loaded. Ensure train.py has been executed."
                }

        if not raw_text or not raw_text.strip():
            return {
                "success": False,
                "error": "Input resume text is empty."
            }

        cleaned = clean_text(raw_text)
        if len(cleaned.split()) < 3:
            return {
                "success": False,
                "error": "Resume text is too brief to extract meaningful classification features."
            }

        # Vectorize
        X = self.vectorizer.transform([cleaned])

        # Get calibrated probabilities
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
        else:
            # Fallback if raw SVM
            df_vals = self.model.decision_function(X)[0]
            exp_vals = np.exp(df_vals - np.max(df_vals))
            probs = exp_vals / exp_vals.sum()

        top_indices = np.argsort(probs)[::-1]
        classes = self.label_encoder.classes_

        # Predicted class and confidence
        top_idx = top_indices[0]
        predicted_category = str(classes[top_idx])
        confidence = float(round(probs[top_idx], 4))

        # Top 3 or Top 5 predictions
        top_predictions = []
        for i in top_indices[:5]:
            cat_name = str(classes[i])
            score = float(round(probs[i], 4))
            top_predictions.append({
                "category": cat_name,
                "score": score,
                "percentage": round(score * 100, 1)
            })

        # Explainability
        top_features = self.explainer.explain_instance(
            cleaned_text=cleaned,
            predicted_category=predicted_category,
            top_k=8
        )
        explanation_narrative = get_explanation_narrative(predicted_category, top_features)

        # Profile intelligence extraction
        skills_detected = extract_skills(raw_text)
        structural_metrics = extract_sections_and_metrics(raw_text)

        return {
            "success": True,
            "prediction": {
                "category": predicted_category,
                "confidence": confidence,
                "confidence_percentage": round(confidence * 100, 1)
            },
            "top_predictions": top_predictions[:3],
            "all_top_predictions": top_predictions,
            "keywords": top_features,
            "explanation": explanation_narrative,
            "skills": skills_detected,
            "metrics": structural_metrics,
            "model": self.metadata.get("model_name", "Linear SVM (Calibrated)"),
            "model_metadata": self.metadata
        }


def predict_resume(text: str) -> Dict[str, Any]:
    """Convenience functional interface."""
    predictor = ResumePredictor.get_instance()
    return predictor.predict(text)
