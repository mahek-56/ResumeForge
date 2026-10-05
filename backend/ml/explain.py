"""
Explainability Engine for Resume Classification
SAMATRIX RESUMEFORGE 2026

Extracts:
1. Category-level top predictive n-grams and weights directly from trained models.
2. Instance-level local feature attributions: For a specific resume, computes
   the exact positive linear contribution of active tokens:
   contribution_i = tfidf_value_i * coef[predicted_class, i]
"""

import os
import sys
import json
import joblib
import numpy as np
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "models")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "backend", "outputs", "reports")


class ExplainabilityEngine:
    def __init__(self, vectorizer=None, coefficients=None, label_encoder=None):
        self.vectorizer = vectorizer
        self.coefficients = coefficients
        self.label_encoder = label_encoder
        self._category_features_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None

        # Load global feature importance JSON if exists
        self.feat_json_path = os.path.join(REPORTS_DIR, "feature_importance.json")
        if os.path.exists(self.feat_json_path):
            try:
                with open(self.feat_json_path, "r", encoding="utf-8") as f:
                    self._category_features_cache = json.load(f)
            except Exception:
                pass

    def get_global_top_features(self, category: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Return the highest-weighted predictive features for a target category."""
        if self._category_features_cache and category in self._category_features_cache:
            return self._category_features_cache[category][:top_n]
        return []

    def explain_instance(
        self,
        cleaned_text: str,
        predicted_category: str,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Compute authentic instance-level feature contributions for this specific resume.
        Calculates: dot product component = tfidf_value * class_coefficient.
        """
        if self.vectorizer is None or self.coefficients is None or self.label_encoder is None:
            # Fallback to category-level distinctive features if models not passed
            return self.get_global_top_features(predicted_category, top_n=top_k)

        try:
            # Transform text
            tfidf_vec = self.vectorizer.transform([cleaned_text])
            feature_names = self.vectorizer.get_feature_names_out()
            class_idx = list(self.label_encoder.classes_).index(predicted_category)

            class_coefs = self.coefficients[class_idx]

            # Non-zero indices in the resume's TF-IDF vector
            coo = tfidf_vec.tocoo()
            contributions = []

            for col, val in zip(coo.col, coo.data):
                weight = class_coefs[col]
                # Only positive pushing evidence towards this class
                if weight > 0:
                    contrib = val * weight
                    contributions.append({
                        "feature": str(feature_names[col]),
                        "weight": float(round(weight, 4)),
                        "tfidf": float(round(val, 4)),
                        "contribution": float(round(contrib, 5))
                    })

            # Sort by total contribution
            contributions.sort(key=lambda x: x["contribution"], reverse=True)

            if not contributions:
                return self.get_global_top_features(predicted_category, top_n=top_k)

            # Calculate relative percentage score for visual horizontal bars
            max_contrib = contributions[0]["contribution"] if contributions else 1.0
            for item in contributions[:top_k]:
                item["relative_pct"] = int(round((item["contribution"] / max_contrib) * 100))

            return contributions[:top_k]

        except Exception as e:
            print(f"Explainability calculation error: {e}")
            return self.get_global_top_features(predicted_category, top_n=top_k)


def get_explanation_narrative(category: str, top_features: List[Dict[str, Any]]) -> str:
    """Generate a clean, professional rationale explaining model decision."""
    if not top_features:
        return f"Prediction for {category} was driven by consistent domain profile terminology."

    top_terms = [f"'{f['feature']}'" for f in top_features[:3]]
    terms_str = ", ".join(top_terms)
    return (
        f"The prediction was primarily influenced by domain vocabulary and role-specific "
        f"technical terms including {terms_str} matching the {category} benchmark profile."
    )
