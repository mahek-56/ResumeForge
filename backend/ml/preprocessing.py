"""
Text Preprocessing Pipeline for Resume Classification
SAMATRIX RESUMEFORGE 2026

Ensures identical text normalization across:
- Data quality checking
- Exploratory data analysis (EDA)
- Model training & cross-validation
- Model testing
- Production FastAPI real-time inference
"""

import re
import html
from typing import List, Dict, Any, Set, Tuple

# Technical terms and compound tokens to preserve and normalize
SPECIAL_TOKEN_MAP = {
    r"(?i)\bc\+\+(?!\w)": "cplusplus",
    r"(?i)\bc\#(?!\w)": "csharp",
    r"(?i)(?<!\w)\.net(?!\w)": "dotnet",
    r"(?i)\bnode\.js\b": "nodejs",
    r"(?i)\breact\.js\b": "reactjs",
    r"(?i)\bvue\.js\b": "vuejs",
    r"(?i)\bci/cd\b": "cicd",
    r"(?i)\btcp/ip\b": "tcpip",
    r"(?i)\bpl/sql\b": "plsql",
    r"(?i)\bscikit-learn\b": "scikitlearn",
    r"(?i)\bpower\s*bi\b": "powerbi",
    r"(?i)\bms\s*office\b": "msoffice",
    r"(?i)\bms\s*excel\b": "msexcel",
    r"(?i)\bms\s*word\b": "msword",
    r"(?i)\bui/ux\b": "uiux",
    r"(?i)\br&d\b": "randd",
    r"(?i)\bp&l\b": "pandl",
}

# Regex for stripping contact and non-informative markers
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
BULLET_PATTERN = re.compile(r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u25CF\x96\x95\*\-\•]")
EXTRA_PUNCT_PATTERN = re.compile(r"[^\w\s\+\#]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")

# Comprehensive domain skill vocabulary for automated insight extraction
KNOWN_SKILLS: Dict[str, List[str]] = {
    "Programming & Core Tech": [
        "python", "java", "c++", "c#", ".net", "javascript", "typescript", "php", "ruby", "go", "rust",
        "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "plsql", "sqlite"
    ],
    "Web & Frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi", "spring boot", "express", "node.js",
        "html", "css", "tailwind", "bootstrap", "graphql", "rest api", "microservices"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi",
        "data analysis", "data science", "llm", "transformers", "xgboost", "random forest"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ci/cd",
        "git", "linux", "ansible", "cloud computing"
    ],
    "Business, Finance & HR": [
        "financial analysis", "accounting", "auditing", "budgeting", "financial modeling",
        "taxation", "recruitment", "talent acquisition", "human resources", "payroll",
        "employee relations", "performance management", "p&l management", "business development"
    ],
    "Engineering & Design": [
        "autocad", "solidworks", "catia", "matlab", "embedded systems", "circuit design",
        "ui/ux", "figma", "adobe photoshop", "illustrator", "graphic design", "revit"
    ],
    "Management & Methodologies": [
        "agile", "scrum", "project management", "pmp", "six sigma", "stakeholder management",
        "strategic planning", "risk management", "operations management"
    ]
}


def normalize_special_tokens(text: str) -> str:
    """Normalize domain-critical compound terms before token punctuation stripping."""
    lowered = text.lower()
    for pattern, replacement in SPECIAL_TOKEN_MAP.items():
        lowered = re.sub(pattern, replacement, lowered)
    return lowered


def clean_text(text: str, preserve_special_tokens: bool = True) -> str:
    """
    Standardize raw resume text into clean, tokenizable NLP string.
    Identical across training, evaluation, and production API inference.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Unescape HTML entities
    cleaned = html.unescape(text)

    # 2. Strip HTML tags
    cleaned = HTML_TAG_PATTERN.sub(" ", cleaned)

    # 3. Strip URLs, emails, phone numbers
    cleaned = URL_PATTERN.sub(" ", cleaned)
    cleaned = EMAIL_PATTERN.sub(" ", cleaned)
    cleaned = PHONE_PATTERN.sub(" ", cleaned)

    # 4. Normalize special technical tokens before general cleaning
    if preserve_special_tokens:
        cleaned = normalize_special_tokens(cleaned)
    else:
        cleaned = cleaned.lower()

    # 5. Remove bullets and excessive punctuation, retaining letters, digits, and underscores
    cleaned = BULLET_PATTERN.sub(" ", cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", cleaned)

    # 6. Normalize whitespace
    cleaned = MULTI_SPACE_PATTERN.sub(" ", cleaned).strip()

    return cleaned


def extract_skills(text: str) -> List[Dict[str, Any]]:
    """
    Extract verified technical and professional skills present in resume text.
    Returns matched skills grouped by domain with count.
    """
    if not text:
        return []

    text_lower = " " + text.lower() + " "
    detected: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for category, skills in KNOWN_SKILLS.items():
        matched_in_cat: List[str] = []
        for skill in skills:
            # Word boundary regex matching
            escaped = re.escape(skill)
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, text_lower):
                if skill not in seen:
                    matched_in_cat.append(skill.title() if len(skill) > 3 else skill.upper())
                    seen.add(skill)
        if matched_in_cat:
            detected.append({
                "category": category,
                "skills": matched_in_cat
            })

    return detected


def extract_sections_and_metrics(text: str) -> Dict[str, Any]:
    """
    Extract structural signals: education markers, years of experience indicators,
    word count, and reading statistics.
    """
    if not text:
        return {
            "word_count": 0,
            "char_count": 0,
            "education_signals": [],
            "experience_signals": [],
            "has_certifications": False
        }

    words = text.split()
    word_count = len(words)
    char_count = len(text)

    # Education markers
    edu_patterns = [
        r"\b(?:bachelor|b\.s|b\.a|b\.tech|b\.e|master|m\.s|m\.a|m\.tech|m\.b\.a|ph\.d|doctorate|degree|diploma|university|college|institute)\b"
    ]
    edu_found: Set[str] = set()
    for pat in edu_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            edu_found.add(m.title())

    # Experience indicators (e.g. "5+ years", "10 years experience")
    exp_matches = re.findall(r"\b(\d{1,2}\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)\b", text, re.IGNORECASE)
    exp_signals = list(set([m.strip() for m in exp_matches]))

    # Certifications indicator
    cert_matches = re.findall(r"\b(?:certified|certification|license|pmp|aws certified|cpa|cfa|cissp)\b", text, re.IGNORECASE)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "education_signals": list(edu_found)[:6],
        "experience_signals": exp_signals[:4],
        "has_certifications": len(cert_matches) > 0,
        "certifications_count": len(cert_matches)
    }
