"""
Analytics and Metrics Service
SAMATRIX RESUMEFORGE 2026

Loads and serves real calculated EDA figures, model comparisons,
per-class reports, and error analysis summaries to API callers.
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../../backend/outputs/reports")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../../backend/models")


def get_analytics_data() -> Dict[str, Any]:
    """Retrieve full exploratory and performance analytics."""
    eda_path = os.path.join(REPORTS_DIR, "eda_summary.json")
    comp_path = os.path.join(REPORTS_DIR, "model_comparison.csv")
    err_path = os.path.join(REPORTS_DIR, "error_summary.json")
    meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

    eda_data = {}
    if os.path.exists(eda_path):
        with open(eda_path, "r", encoding="utf-8") as f:
            eda_data = json.load(f)

    model_comp = []
    if os.path.exists(comp_path):
        df_comp = pd.read_csv(comp_path)
        model_comp = df_comp.to_dict(orient="records")

    error_summary = {}
    if os.path.exists(err_path):
        with open(err_path, "r", encoding="utf-8") as f:
            error_summary = json.load(f)

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    return {
        "eda": eda_data,
        "model_comparison": model_comp,
        "error_summary": error_summary,
        "champion_metadata": meta
    }


def get_metrics_data() -> Dict[str, Any]:
    """Retrieve per-class classification report and top features."""
    per_class_path = os.path.join(REPORTS_DIR, "per_class_metrics.json")
    feat_path = os.path.join(REPORTS_DIR, "feature_importance.json")

    per_class = {}
    if os.path.exists(per_class_path):
        with open(per_class_path, "r", encoding="utf-8") as f:
            per_class = json.load(f)

    feature_map = {}
    if os.path.exists(feat_path):
        with open(feat_path, "r", encoding="utf-8") as f:
            feature_map = json.load(f)

    return {
        "classification_report": per_class,
        "feature_importance": feature_map
    }


def get_features_for_category(category: str) -> List[Dict[str, Any]]:
    """Retrieve top weighted n-grams for a specific category."""
    feat_path = os.path.join(REPORTS_DIR, "feature_importance.json")
    if os.path.exists(feat_path):
        with open(feat_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(category, [])
    return []
