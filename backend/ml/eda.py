"""
Exploratory Data Analysis (EDA) & Data Quality Module
SAMATRIX RESUMEFORGE 2026

Generates publication-quality charts and structured JSON analytics.
"""

import os
import sys
import json
import collections

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from backend.ml.preprocessing import clean_text

# Style configuration for presentation-ready dark/navy modern visuals
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
PALETTE_PRIMARY = "#3B82F6"
PALETTE_ACCENT = "#8B5CF6"
PALETTE_DARK = "#0F172A"

FIGURES_DIR = os.path.join("backend", "outputs", "figures")
REPORTS_DIR = os.path.join("backend", "outputs", "reports")
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def run_data_quality_check(df: pd.DataFrame) -> dict:
    """Analyze missing values, duplicates, label validity and lengths."""
    total_rows = len(df)
    missing_counts = df.isnull().sum().to_dict()
    id_duplicates = int(df["ID"].duplicated().sum()) if "ID" in df.columns else 0
    text_duplicates = int(df["Resume_str"].duplicated().sum()) if "Resume_str" in df.columns else 0

    # Short / empty resumes check
    df["raw_char_len"] = df["Resume_str"].fillna("").apply(len)
    df["raw_word_len"] = df["Resume_str"].fillna("").apply(lambda x: len(x.split()))
    
    empty_resumes = int((df["raw_word_len"] == 0).sum())
    very_short = int((df["raw_word_len"] < 25).sum())
    very_long = int((df["raw_word_len"] > 2500).sum())

    categories = df["Category"].value_counts().to_dict()

    quality_report = {
        "total_resumes": total_rows,
        "columns": list(df.columns),
        "missing_values": missing_counts,
        "id_duplicates": id_duplicates,
        "exact_text_duplicates": text_duplicates,
        "empty_resumes": empty_resumes,
        "very_short_resumes_lt_25_words": very_short,
        "very_long_resumes_gt_2500_words": very_long,
        "total_categories": len(categories),
        "category_distribution": categories,
        "word_len_stats": {
            "min": int(df["raw_word_len"].min()),
            "max": int(df["raw_word_len"].max()),
            "mean": float(round(df["raw_word_len"].mean(), 2)),
            "median": float(round(df["raw_word_len"].median(), 2)),
            "std": float(round(df["raw_word_len"].std(), 2)),
        },
        "char_len_stats": {
            "min": int(df["raw_char_len"].min()),
            "max": int(df["raw_char_len"].max()),
            "mean": float(round(df["raw_char_len"].mean(), 2)),
            "median": float(round(df["raw_char_len"].median(), 2)),
            "std": float(round(df["raw_char_len"].std(), 2)),
        }
    }

    with open(os.path.join(REPORTS_DIR, "data_quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)

    print("[OK] Data quality check complete. Saved to data_quality_report.json")
    return quality_report


def generate_eda_visualizations(df: pd.DataFrame):
    """Generate all required EDA plots and save to outputs/figures/."""
    print("Running text cleaning for EDA...")
    df["cleaned_text"] = df["Resume_str"].apply(clean_text)
    df["clean_word_len"] = df["cleaned_text"].apply(lambda x: len(x.split()))
    df["clean_char_len"] = df["cleaned_text"].apply(len)

    # 1. Category Distribution Bar Plot
    plt.figure(figsize=(12, 8))
    cat_counts = df["Category"].value_counts().sort_values(ascending=True)
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(cat_counts)))
    bars = plt.barh(cat_counts.index, cat_counts.values, color=colors, edgecolor="black", linewidth=0.5)
    plt.title("ResumeForge — Category Distribution (Total = 2,484)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Resumes", fontsize=11)
    plt.ylabel("Target Category", fontsize=11)
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1.5, bar.get_y() + bar.get_height() / 2, f"{int(width)}",
                 va="center", ha="left", fontsize=9, fontweight="semibold")
    plt.xlim(0, max(cat_counts.values) + 15)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "01_category_distribution.png"), dpi=300)
    plt.close()
    print("[OK] Saved 01_category_distribution.png")

    # 2. Resume Length Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df["clean_word_len"], bins=40, kde=True, ax=axes[0], color="#2563EB", edgecolor="white")
    axes[0].set_title("Resume Word Count Distribution", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Cleaned Word Count")
    axes[0].set_ylabel("Frequency")
    axes[0].axvline(df["clean_word_len"].median(), color="red", linestyle="--", label=f"Median: {int(df['clean_word_len'].median())}")
    axes[0].legend()

    sns.histplot(df["clean_char_len"], bins=40, kde=True, ax=axes[1], color="#7C3AED", edgecolor="white")
    axes[1].set_title("Resume Character Count Distribution", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Cleaned Character Count")
    axes[1].set_ylabel("Frequency")
    axes[1].axvline(df["clean_char_len"].median(), color="red", linestyle="--", label=f"Median: {int(df['clean_char_len'].median())}")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "02_resume_length_distribution.png"), dpi=300)
    plt.close()
    print("[OK] Saved 02_resume_length_distribution.png")

    # 3. Top Unigrams, Bigrams, and Trigrams
    print("Extracting n-grams...")
    # Unigrams (ignoring standard english stop words for informative vocabulary)
    vec_uni = CountVectorizer(stop_words="english", max_features=25)
    X_uni = vec_uni.fit_transform(df["cleaned_text"])
    top_uni = pd.Series(X_uni.toarray().sum(axis=0), index=vec_uni.get_feature_names_out()).sort_values(ascending=False)

    vec_bi = CountVectorizer(stop_words="english", ngram_range=(2, 2), max_features=20)
    X_bi = vec_bi.fit_transform(df["cleaned_text"])
    top_bi = pd.Series(X_bi.toarray().sum(axis=0), index=vec_bi.get_feature_names_out()).sort_values(ascending=False)

    vec_tri = CountVectorizer(stop_words="english", ngram_range=(3, 3), max_features=15)
    X_tri = vec_tri.fit_transform(df["cleaned_text"])
    top_tri = pd.Series(X_tri.toarray().sum(axis=0), index=vec_tri.get_feature_names_out()).sort_values(ascending=False)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].barh(top_uni.index[:15][::-1], top_uni.values[:15][::-1], color=plt.cm.Blues(np.linspace(0.4, 0.9, 15)))
    axes[0].set_title("Top 15 Informative Unigrams", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Frequency")

    axes[1].barh(top_bi.index[:15][::-1], top_bi.values[:15][::-1], color=plt.cm.Purples(np.linspace(0.4, 0.9, 15)))
    axes[1].set_title("Top 15 Informative Bigrams", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Frequency")

    axes[2].barh(top_tri.index[:15][::-1], top_tri.values[:15][::-1], color=plt.cm.teal(np.linspace(0.4, 0.9, 15)) if hasattr(plt.cm, 'teal') else plt.cm.viridis(np.linspace(0.4, 0.8, 15)))
    axes[2].set_title("Top 15 Informative Trigrams", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("Frequency")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "03_top_ngrams.png"), dpi=300)
    plt.close()
    print("[OK] Saved 03_top_ngrams.png")

    # 4. WordCloud Overall
    print("Generating WordCloud...")
    corpus = " ".join(df["cleaned_text"].sample(min(800, len(df)), random_state=42))
    wc = WordCloud(
        width=1200, height=600,
        background_color="#0F172A",
        colormap="cool",
        stopwords={"state", "company", "city", "year", "years", "work", "responsibilities", "new", "time"},
        max_words=150,
        random_state=42
    ).generate(corpus)

    plt.figure(figsize=(14, 7), facecolor="#0F172A")
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("ResumeForge — Overall Vocabulary WordCloud", fontsize=16, color="white", pad=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "04_wordcloud_overall.png"), dpi=300, facecolor="#0F172A")
    plt.close()
    print("[OK] Saved 04_wordcloud_overall.png")

    # 5. Length By Category Boxplot
    plt.figure(figsize=(14, 7))
    order = df.groupby("Category")["clean_word_len"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="Category", y="clean_word_len", order=order, hue="Category", palette="mako", legend=False, showfliers=False)
    plt.title("Cleaned Word Count Across Categories (Median Sorted)", fontsize=13, fontweight="bold")
    plt.xticks(rotation=75, ha="right", fontsize=9)
    plt.ylabel("Cleaned Words")
    plt.xlabel("Category")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "05_length_by_category.png"), dpi=300)
    plt.close()
    print("[OK] Saved 05_length_by_category.png")

    # 6. Class-wise Distinctive TF-IDF Terms
    print("Computing class-wise distinctive TF-IDF vocabulary...")
    tfidf = TfidfVectorizer(stop_words="english", max_features=15000, ngram_range=(1, 2))
    X_tfidf = tfidf.fit_transform(df["cleaned_text"])
    feature_names = np.array(tfidf.get_feature_names_out())

    class_top_terms = {}
    for cat in df["Category"].unique():
        cat_mask = (df["Category"] == cat).values
        cat_mean_tfidf = np.asarray(X_tfidf[cat_mask].mean(axis=0)).ravel()
        top_indices = cat_mean_tfidf.argsort()[::-1][:10]
        class_top_terms[cat] = [
            {"term": feature_names[i], "score": round(float(cat_mean_tfidf[i]), 4)}
            for i in top_indices
        ]

    # Save complete structured EDA metrics to JSON for frontend API consumption
    eda_summary = {
        "total_resumes": len(df),
        "total_categories": int(df["Category"].nunique()),
        "categories": sorted(df["Category"].unique().tolist()),
        "category_counts": df["Category"].value_counts().to_dict(),
        "median_word_length": int(df["clean_word_len"].median()),
        "mean_word_length": round(float(df["clean_word_len"].mean()), 1),
        "top_unigrams": [{"term": k, "count": int(v)} for k, v in top_uni.head(20).items()],
        "top_bigrams": [{"term": k, "count": int(v)} for k, v in top_bi.head(20).items()],
        "top_trigrams": [{"term": k, "count": int(v)} for k, v in top_tri.head(15).items()],
        "class_top_terms": class_top_terms
    }

    with open(os.path.join(REPORTS_DIR, "eda_summary.json"), "w", encoding="utf-8") as f:
        json.dump(eda_summary, f, indent=2)

    print("[OK] EDA complete. Saved eda_summary.json and all figures.")
    return eda_summary


if __name__ == "__main__":
    data_path = os.path.join("data", "Resume.csv")
    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    run_data_quality_check(df)
    generate_eda_visualizations(df)
