"""
Backend Test Suite
SAMATRIX RESUMEFORGE 2026

Tests:
1. Health endpoint
2. Model info endpoint
3. Text prediction endpoint (valid, short, empty)
4. File upload endpoint (TXT, PDF, unsupported)
5. Categories and analytics endpoints
6. 5 completely unseen, non-training candidate resumes across distinct verticals
"""

import os
import io
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.ml.predict import predict_resume, ResumePredictor

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "Linear SVM" in data["model_signature"]


def test_model_info_endpoint():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["num_classes"] == 24
    assert data["accuracy"] > 0.65
    assert data["macro_f1"] > 0.60
    assert len(data["categories"]) == 24


def test_predict_text_valid():
    resume_text = (
        "Senior Cloud Architect with 8+ years experience in Python, AWS Lambda, ECS, "
        "Kubernetes, Docker, PostgreSQL, microservices architecture, and CI/CD pipelines. "
        "BS in Computer Science."
    )
    response = client.post("/api/predict", json={"resume_text": resume_text})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "category" in data["prediction"]
    assert data["prediction"]["confidence"] > 0.0
    assert len(data["top_predictions"]) >= 3
    assert len(data["keywords"]) > 0


def test_predict_text_empty():
    response = client.post("/api/predict", json={"resume_text": "   "})
    assert response.status_code in [400, 422]


def test_predict_text_too_short():
    response = client.post("/api/predict", json={"resume_text": "Short"})
    assert response.status_code in [400, 422]


def test_predict_file_txt():
    content = b"Executive Chef with 10+ years culinary leadership in menu planning, kitchen brigade management, food safety HACCP, and fine dining."
    response = client.post(
        "/api/predict/file",
        files={"file": ("chef_resume.txt", io.BytesIO(content), "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prediction"]["category"] == "CHEF"


def test_predict_file_unsupported_type():
    content = b"Fake binary executable content"
    response = client.post(
        "/api/predict/file",
        files={"file": ("malicious.exe", io.BytesIO(content), "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]


def test_categories_endpoint():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 24
    assert "INFORMATION-TECHNOLOGY" in data["categories"]
    assert "CHEF" in data["categories"]
    assert "FINANCE" in data["categories"]


def test_analytics_and_metrics_endpoints():
    res_analytics = client.get("/api/analytics")
    assert res_analytics.status_code == 200
    ana = res_analytics.json()
    assert "eda" in ana
    assert "model_comparison" in ana
    assert len(ana["model_comparison"]) >= 6

    res_metrics = client.get("/api/metrics")
    assert res_metrics.status_code == 200
    met = res_metrics.json()
    assert "classification_report" in met
    assert "feature_importance" in met


def test_unseen_5_diverse_resumes():
    """
    Test ML inference pipeline on 5 realistic, unseen resumes from distinct sectors:
    1. Information Technology / DevOps
    2. Healthcare / Nursing
    3. Legal / Advocate
    4. Culinary / Chef
    5. Human Resources / Talent Acquisition
    """
    unseen_resumes = [
        {
            "sector": "Information Technology",
            "expected_top": ["INFORMATION-TECHNOLOGY", "ENGINEERING"],
            "text": (
                "Lead DevOps Engineer with 9 years automating distributed infrastructure. "
                "Mastery in Python, Golang, Terraform, AWS, Docker containers, Kubernetes clusters, "
                "Ansible, Prometheus monitoring, and zero-downtime deployment pipelines. "
                "BS in Software Engineering."
            )
        },
        {
            "sector": "Healthcare",
            "expected_top": ["HEALTHCARE", "FITNESS"],
            "text": (
                "Registered Nurse (RN) with 6 years experience in ICU critical care, patient assessment, "
                "medication administration, IV therapy, electronic health records (EHR), CPR certified, "
                "vital signs monitoring, and clinical patient care coordination. BSN in Nursing."
            )
        },
        {
            "sector": "Legal",
            "expected_top": ["ADVOCATE"],
            "text": (
                "Trial Attorney and Legal Counsel with 11 years handling civil litigation, court hearings, "
                "legal brief preparation, depositions, case law research, trial defense, settlement negotiation, "
                "and judicial arbitration. Juris Doctor from Law School, State Bar license."
            )
        },
        {
            "sector": "Culinary",
            "expected_top": ["CHEF"],
            "text": (
                "Head Pastry Chef and Kitchen Manager specializing in artisanal bakery, menu engineering, "
                "culinary preparation, food inventory procurement, sanitation HACCP regulations, "
                "and kitchen staff supervision for 4-star boutique restaurants."
            )
        },
        {
            "sector": "Human Resources",
            "expected_top": ["HR"],
            "text": (
                "Human Resources Generalist with 5+ years experience in candidate recruitment, onboarding, "
                "payroll processing, HRIS database management, employee relations, labor compliance, "
                "benefits administration, and conflict resolution. SHRM-CP certified."
            )
        }
    ]

    for item in unseen_resumes:
        res = predict_resume(item["text"])
        assert res["success"] is True, f"Failed for {item['sector']}"
        predicted = res["prediction"]["category"]
        top_cats = [p["category"] for p in res["top_predictions"]]

        # Verify that either the primary prediction or the top-2 matches expected sector categories
        matches = any(exp in top_cats[:2] for exp in item["expected_top"])
        print(f"\n[UNSEEN TEST] {item['sector']}: Predicted '{predicted}' ({res['prediction']['confidence_percentage']}%), Top-3: {top_cats}")
        assert matches, f"Expected {item['expected_top']} in top categories, got {top_cats}"
        assert len(res["keywords"]) > 0
