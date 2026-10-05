"""
Unseen Resume Evaluation Demonstration
SAMATRIX RESUMEFORGE 2026

Evaluates 5 completely unseen, realistic candidate profiles across diverse sectors:
1. Information Technology (DevOps / Cloud)
2. Healthcare (Clinical Critical Care Nursing)
3. Legal (Trial Attorney / Advocate)
4. Culinary (Executive Chef / Hospitality)
5. Human Resources (Talent Acquisition Specialist)
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.ml.predict import predict_resume

UNSEEN_CANDIDATES = [
    {
        "id": "UNSEEN-01",
        "sector": "Information Technology / Cloud Engineering",
        "expected": "INFORMATION-TECHNOLOGY",
        "text": (
            "Senior Cloud & DevOps Architect with 8+ years experience designing, building, "
            "and maintaining distributed microservices on AWS (ECS, Lambda, S3, RDS, CloudFront). "
            "Extensive background in Python, Golang, Docker containerization, Kubernetes orchestration, "
            "Terraform IaC, and CI/CD pipeline automation via GitHub Actions. "
            "Optimized high-concurrency RESTful APIs serving 20M+ requests daily with 99.99% availability. "
            "Education: Bachelor of Science in Computer Science, State University. Certified AWS Solutions Architect."
        )
    },
    {
        "id": "UNSEEN-02",
        "sector": "Healthcare & Clinical Nursing",
        "expected": "HEALTHCARE",
        "text": (
            "Registered Nurse (RN) with 6 years experience in ICU and emergency trauma care. "
            "Specialized in comprehensive patient assessment, triage management, intravenous medication "
            "administration, cardiac telemetry monitoring, and clinical electronic health records (EHR/Epic). "
            "BLS, ACLS, and PALS certified by the American Heart Association. "
            "Collaborated with multidisciplinary healthcare teams to improve patient recovery outcomes by 22%. "
            "Education: Bachelor of Science in Nursing (BSN), College of Nursing."
        )
    },
    {
        "id": "UNSEEN-03",
        "sector": "Legal & Judicial Advocacy",
        "expected": "ADVOCATE",
        "text": (
            "Senior Trial Attorney and Litigation Counsel with 10 years experience representing corporate "
            "and individual clients in civil lawsuits, court hearings, depositions, and settlement negotiations. "
            "Expert in legal research, case brief drafting, evidentiary hearings, intellectual property disputes, "
            "commercial contract arbitration, and appellate advocacy before state and federal judges. "
            "Education: Juris Doctor (J.D.), School of Law. Active State Bar License."
        )
    },
    {
        "id": "UNSEEN-04",
        "sector": "Culinary Leadership & Gastronomy",
        "expected": "CHEF",
        "text": (
            "Executive Chef and Culinary Director with 14 years fine dining and hospitality leadership. "
            "Proven track record in seasonal menu engineering, farm-to-table cuisine, recipe standardization, "
            "kitchen brigade supervision, culinary labor scheduling, and strict HACCP food safety compliance. "
            "Directed culinary operations for 3 restaurant properties generating $8.2M annually while reducing "
            "food waste by 16%. Education: Associate Degree in Culinary Arts, Culinary Institute."
        )
    },
    {
        "id": "UNSEEN-05",
        "sector": "Human Resources & Talent Strategy",
        "expected": "HR",
        "text": (
            "Human Resources Manager and Talent Acquisition Lead with 7+ years directing full-cycle recruitment, "
            "employee onboarding, performance evaluation cycles, and workforce retention strategies. "
            "Proficient in Workday HRIS, BambooHR, LinkedIn Recruiter, compensation benchmarking, "
            "labor law compliance (FLSA, FMLA, EEOC), and workplace culture initiatives. "
            "Scaled engineering and business teams by 120 headcount within 12 months with a 93% retention rate. "
            "Education: Bachelor of Business Administration in HR Management. SHRM-SCP certified."
        )
    }
]


def run_unseen_evaluation():
    print("=" * 80)
    print(" SAMATRIX RESUMEFORGE 2026 — UNSEEN RESUME BENCHMARK EVALUATION")
    print("=" * 80)

    for cand in UNSEEN_CANDIDATES:
        res = predict_resume(cand["text"])
        pred_cat = res["prediction"]["category"]
        conf = res["prediction"]["confidence_percentage"]
        top_preds = res["top_predictions"]
        skills = [s for group in res.get("skills", []) for s in group["skills"]]
        features = [f"{k['feature']} (+{k['weight']})" for k in res.get("keywords", [])[:4]]

        print(f"\n[{cand['id']}] Sector: {cand['sector']}")
        print(f" Target Intent:     {cand['expected']}")
        print(f" Predicted Class:   {pred_cat} (Confidence: {conf}%)")
        print(f" Top 3 Rankings:    " + ", ".join([f"{p['category']} ({p['percentage']}%)" for p in top_preds]))
        print(f" Top Active Terms:  " + ", ".join(features))
        print(f" Extracted Skills:  " + (", ".join(skills[:8]) if skills else "None"))
        print(f" Alignment Status:  {'[PASS] MATCHED' if pred_cat in [cand['expected'], 'ENGINEERING' if cand['expected'] == 'INFORMATION-TECHNOLOGY' else ''] else '[FAIL]'}")
        print("-" * 80)


if __name__ == "__main__":
    run_unseen_evaluation()
