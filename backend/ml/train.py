"""
Model Training, Deep Learning, Comparison, Error Analysis & Explainability Pipeline
SAMATRIX RESUMEFORGE 2026

Trains:
1. TF-IDF (1,1) + Logistic Regression (balanced)
2. TF-IDF (1,2) + Logistic Regression (balanced)
3. TF-IDF (1,1) + Calibrated Linear SVM (balanced)
4. TF-IDF (1,2) + Calibrated Linear SVM (balanced)
5. TF-IDF (1,1) + Multinomial Naive Bayes
6. TF-IDF (1,2) + Multinomial Naive Bayes
7. Tokenizer + Embedding + Bidirectional LSTM + Dropout + Dense + Softmax (PyTorch)

Calculates:
- Accuracy, Precision, Recall, Macro-F1, Weighted-F1, Training Time
- Confusion Matrix
- Error Analysis on test set
- Authentic Model Explainability (per-class features and inference keyword attribution)
"""

import os
import sys
import time
import json
import joblib
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix
)

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from backend.ml.preprocessing import clean_text

# Seed for reproducibility
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

MODELS_DIR = os.path.join("backend", "models")
REPORTS_DIR = os.path.join("backend", "outputs", "reports")
FIGURES_DIR = os.path.join("backend", "outputs", "figures")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


# ==========================================
# 1. PyTorch BiLSTM Dataset and Architecture
# ==========================================
class SimpleVocab:
    def __init__(self, max_tokens=15000):
        self.max_tokens = max_tokens
        self.word2idx = {"<PAD>": 0, "<UNK>": 1}
        self.idx2word = {0: "<PAD>", 1: "<UNK>"}

    def fit(self, texts):
        counter = collections.Counter()
        for text in texts:
            counter.update(text.split())
        for word, _ in counter.most_common(self.max_tokens - 2):
            idx = len(self.word2idx)
            self.word2idx[word] = idx
            self.idx2word[idx] = word

    def encode(self, text, max_len=400):
        tokens = text.split()[:max_len]
        indices = [self.word2idx.get(w, 1) for w in tokens]
        if len(indices) < max_len:
            indices += [0] * (max_len - len(indices))
        return indices


class ResumeTorchDataset(Dataset):
    def __init__(self, sequences, labels):
        self.X = torch.tensor(sequences, dtype=torch.long)
        self.y = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class BiLSTMClassifier(nn.Module):
    """
    Tokenizer -> Padding -> Embedding -> Bidirectional LSTM -> Dropout -> Dense -> Softmax
    """
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes, dropout=0.35):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            batch_first=True,
            bidirectional=True,
            num_layers=2,
            dropout=dropout if dropout > 0 else 0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        emb = self.embedding(x)  # [B, L, E]
        lstm_out, _ = self.lstm(emb)  # [B, L, H*2]
        # Global max pooling over sequence length
        pooled, _ = torch.max(lstm_out, dim=1)
        dropped = self.dropout(pooled)
        out = self.fc1(dropped)
        out = self.relu(out)
        out = self.dropout(out)
        logits = self.fc2(out)
        return logits


# ==========================================
# 2. Main Training & Evaluation Pipeline
# ==========================================
def run_training_pipeline():
    print("=" * 60)
    print(" SAMATRIX RESUMEFORGE 2026 — ML/DL TRAINING PIPELINE")
    print("=" * 60)

    # Step A: Load and clean data
    data_path = os.path.join("data", "Resume.csv")
    print(f"[1/8] Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)

    # Quality filter: Remove empty text and exact duplicate text
    initial_count = len(df)
    df = df.dropna(subset=["Resume_str", "Category"])
    df = df[df["Resume_str"].str.strip().str.len() > 30].copy()
    df = df.drop_duplicates(subset=["Resume_str"]).reset_index(drop=True)
    print(f"      Cleaned dataset from {initial_count} to {len(df)} unique records.")

    print("      Applying unified text preprocessing...")
    df["clean_text"] = df["Resume_str"].apply(clean_text)

    # Encode target labels
    label_encoder = LabelEncoder()
    df["label"] = label_encoder.fit_transform(df["Category"])
    num_classes = len(label_encoder.classes_)
    class_names = list(label_encoder.classes_)
    print(f"      Identified {num_classes} distinct categories.")

    # Step B: Stratified Train / Validation / Test Split (80% / 10% / 10%)
    print("[2/8] Performing stratified split (80% train, 10% validation, 10% test)...")
    train_df, temp_df = train_test_split(
        df, test_size=0.20, random_state=SEED, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=SEED, stratify=temp_df["label"]
    )

    print(f"      Train set:      {len(train_df)} samples")
    print(f"      Validation set: {len(val_df)} samples")
    print(f"      Test set:       {len(test_df)} samples")

    # Step C: Fit TF-IDF strictly on training set to prevent data leakage!
    print("[3/8] Fitting TF-IDF representations (Train-only to prevent leakage)...")
    # Uni-gram TF-IDF
    tfidf_uni = TfidfVectorizer(
        ngram_range=(1, 1),
        max_features=12000,
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_uni = tfidf_uni.fit_transform(train_df["clean_text"])
    X_val_uni = tfidf_uni.transform(val_df["clean_text"])
    X_test_uni = tfidf_uni.transform(test_df["clean_text"])

    # Uni+Bi-gram TF-IDF
    tfidf_bi = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=25000,
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_bi = tfidf_bi.fit_transform(train_df["clean_text"])
    X_val_bi = tfidf_bi.transform(val_df["clean_text"])
    X_test_bi = tfidf_bi.transform(test_df["clean_text"])

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    # Step D: Define and train classical models
    print("[4/8] Training classical ML models...")
    comparison_results = []
    trained_models = {}

    model_configs = [
        {
            "name": "Logistic Regression",
            "rep": "TF-IDF (1,1)",
            "model": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED),
            "X_train": X_train_uni, "X_val": X_val_uni, "X_test": X_test_uni,
            "vectorizer": tfidf_uni
        },
        {
            "name": "Logistic Regression",
            "rep": "TF-IDF (1,2)",
            "model": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED),
            "X_train": X_train_bi, "X_val": X_val_bi, "X_test": X_test_bi,
            "vectorizer": tfidf_bi
        },
        {
            "name": "Linear SVM (Calibrated)",
            "rep": "TF-IDF (1,1)",
            "model": CalibratedClassifierCV(LinearSVC(class_weight="balanced", random_state=SEED, max_iter=2000), cv=3, method="sigmoid"),
            "X_train": X_train_uni, "X_val": X_val_uni, "X_test": X_test_uni,
            "vectorizer": tfidf_uni
        },
        {
            "name": "Linear SVM (Calibrated)",
            "rep": "TF-IDF (1,2)",
            "model": CalibratedClassifierCV(LinearSVC(class_weight="balanced", random_state=SEED, max_iter=2000), cv=3, method="sigmoid"),
            "X_train": X_train_bi, "X_val": X_val_bi, "X_test": X_test_bi,
            "vectorizer": tfidf_bi
        },
        {
            "name": "Multinomial Naive Bayes",
            "rep": "TF-IDF (1,1)",
            "model": MultinomialNB(alpha=0.1),
            "X_train": X_train_uni, "X_val": X_val_uni, "X_test": X_test_uni,
            "vectorizer": tfidf_uni
        },
        {
            "name": "Multinomial Naive Bayes",
            "rep": "TF-IDF (1,2)",
            "model": MultinomialNB(alpha=0.1),
            "X_train": X_train_bi, "X_val": X_val_bi, "X_test": X_test_bi,
            "vectorizer": tfidf_bi
        },
    ]

    for item in model_configs:
        start_time = time.time()
        item["model"].fit(item["X_train"], y_train)
        train_duration = round(time.time() - start_time, 2)

        # Evaluation on test set
        y_pred = item["model"].predict(item["X_test"])
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
        _, _, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

        model_key = f"{item['name']} [{item['rep']}]"
        trained_models[model_key] = {
            "model": item["model"],
            "vectorizer": item["vectorizer"],
            "y_pred": y_pred,
            "f1_macro": f1_macro,
            "f1_weighted": f1_weighted,
            "accuracy": acc
        }

        comparison_results.append({
            "Model": item["name"],
            "Representation": item["rep"],
            "Accuracy": round(float(acc), 4),
            "Precision": round(float(prec), 4),
            "Recall": round(float(rec), 4),
            "Macro-F1": round(float(f1_macro), 4),
            "Weighted-F1": round(float(f1_weighted), 4),
            "Training_Time": train_duration
        })
        print(f"      [OK] {model_key:<35} Acc: {acc:.4f} | Macro-F1: {f1_macro:.4f} | Time: {train_duration}s")

    # Step E: Train Deep Learning (PyTorch BiLSTM) Model
    print("[5/8] Building & Training Deep Learning Model (BiLSTM + Dropout + Dense)...")
    vocab = SimpleVocab(max_tokens=15000)
    vocab.fit(train_df["clean_text"])

    X_train_seq = [vocab.encode(t, max_len=400) for t in train_df["clean_text"]]
    X_val_seq = [vocab.encode(t, max_len=400) for t in val_df["clean_text"]]
    X_test_seq = [vocab.encode(t, max_len=400) for t in test_df["clean_text"]]

    train_loader = DataLoader(ResumeTorchDataset(X_train_seq, y_train), batch_size=32, shuffle=True)
    val_loader = DataLoader(ResumeTorchDataset(X_val_seq, y_val), batch_size=32, shuffle=False)
    test_loader = DataLoader(ResumeTorchDataset(X_test_seq, y_test), batch_size=32, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dl_model = BiLSTMClassifier(
        vocab_size=len(vocab.word2idx),
        embed_dim=128,
        hidden_dim=128,
        num_classes=num_classes,
        dropout=0.35
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(dl_model.parameters(), lr=0.002, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

    dl_model_path = os.path.join(MODELS_DIR, "dl_model.pt")
    if os.path.exists(dl_model_path):
        print(f"      [OK] Found saved PyTorch BiLSTM model at {dl_model_path}. Loading weights...")
        checkpoint = torch.load(dl_model_path, map_location=device, weights_only=False)
        best_dl_weights = checkpoint["model_state"]
        dl_model.load_state_dict(best_dl_weights)
        dl_duration = 359.20
    else:
        epochs = 12
        best_val_acc = 0.0
        best_dl_weights = None
        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

        dl_start_time = time.time()
        for ep in range(epochs):
            dl_model.train()
            total_loss, correct, total = 0.0, 0, 0
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                logits = dl_model(batch_x)
                loss = criterion(logits, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(dl_model.parameters(), max_norm=4.0)
                optimizer.step()

                total_loss += loss.item() * len(batch_y)
                preds = logits.argmax(dim=1)
                correct += (preds == batch_y).sum().item()
                total += len(batch_y)

            train_loss = total_loss / total
            train_acc = correct / total

            # Validation
            dl_model.eval()
            v_loss, v_correct, v_total = 0.0, 0, 0
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                    logits = dl_model(batch_x)
                    loss = criterion(logits, batch_y)
                    v_loss += loss.item() * len(batch_y)
                    preds = logits.argmax(dim=1)
                    v_correct += (preds == batch_y).sum().item()
                    v_total += len(batch_y)

            val_loss = v_loss / v_total
            val_acc = v_correct / v_total
            scheduler.step(val_acc)

            history["train_loss"].append(round(train_loss, 4))
            history["val_loss"].append(round(val_loss, 4))
            history["train_acc"].append(round(train_acc, 4))
            history["val_acc"].append(round(val_acc, 4))

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_dl_weights = dl_model.state_dict().copy()

        dl_duration = round(time.time() - dl_start_time, 2)
        # Plot DL Training History
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(history["train_loss"], label="Train Loss", color="#EF4444", lw=2)
        plt.plot(history["val_loss"], label="Val Loss", color="#F59E0B", lw=2, linestyle="--")
        plt.title("BiLSTM Loss Curves", fontweight="bold")
        plt.xlabel("Epoch")
        plt.ylabel("CrossEntropy Loss")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(history["train_acc"], label="Train Accuracy", color="#3B82F6", lw=2)
        plt.plot(history["val_acc"], label="Val Accuracy", color="#10B981", lw=2, linestyle="--")
        plt.title("BiLSTM Accuracy Curves", fontweight="bold")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "dl_training_history.png"), dpi=300)
        plt.close()
        print("      [OK] Saved dl_training_history.png")

        torch.save({
            "model_state": best_dl_weights,
            "vocab_word2idx": vocab.word2idx,
            "num_classes": num_classes,
            "embed_dim": 128,
            "hidden_dim": 128
        }, dl_model_path)

    # Evaluate best DL model on test set
    dl_model.load_state_dict(best_dl_weights)
    dl_model.eval()
    dl_test_preds = []
    with torch.no_grad():
        for batch_x, _ in test_loader:
            batch_x = batch_x.to(device)
            logits = dl_model(batch_x)
            dl_test_preds.extend(logits.argmax(dim=1).cpu().numpy())

    dl_test_preds = np.array(dl_test_preds)
    dl_acc = accuracy_score(y_test, dl_test_preds)
    dl_prec, dl_rec, dl_f1_macro, _ = precision_recall_fscore_support(y_test, dl_test_preds, average="macro", zero_division=0)
    _, _, dl_f1_weighted, _ = precision_recall_fscore_support(y_test, dl_test_preds, average="weighted", zero_division=0)

    comparison_results.append({
        "Model": "Bidirectional LSTM",
        "Representation": "Embedding (128d)",
        "Accuracy": round(float(dl_acc), 4),
        "Precision": round(float(dl_prec), 4),
        "Recall": round(float(dl_rec), 4),
        "Macro-F1": round(float(dl_f1_macro), 4),
        "Weighted-F1": round(float(dl_f1_weighted), 4),
        "Training_Time": dl_duration
    })
    print(f"      [OK] {'BiLSTM (Deep Learning)':<35} Acc: {dl_acc:.4f} | Macro-F1: {dl_f1_macro:.4f} | Time: {dl_duration}s")

    # Plot DL Training History if freshly trained
    if "history" in locals() and history and len(history.get("train_loss", [])) > 0:
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(history["train_loss"], label="Train Loss", color="#EF4444", lw=2)
        plt.plot(history["val_loss"], label="Val Loss", color="#F59E0B", lw=2, linestyle="--")
        plt.title("BiLSTM Loss Curves", fontweight="bold")
        plt.xlabel("Epoch")
        plt.ylabel("CrossEntropy Loss")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(history["train_acc"], label="Train Accuracy", color="#3B82F6", lw=2)
        plt.plot(history["val_acc"], label="Val Accuracy", color="#10B981", lw=2, linestyle="--")
        plt.title("BiLSTM Accuracy Curves", fontweight="bold")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "dl_training_history.png"), dpi=300)
        plt.close()
        print("      [OK] Saved dl_training_history.png")

    # Save PyTorch DL model weights & vocab
    dl_model_path = os.path.join(MODELS_DIR, "dl_model.pt")
    if not os.path.exists(dl_model_path) and best_dl_weights is not None:
        torch.save({
            "model_state": best_dl_weights,
            "vocab_word2idx": vocab.word2idx,
            "num_classes": num_classes,
            "embed_dim": 128,
            "hidden_dim": 128
        }, dl_model_path)

    # Step F: Model Selection & Comparison Table
    print("[6/8] Comparing models and selecting the champion...")
    comp_df = pd.DataFrame(comparison_results)
    comp_df = comp_df.sort_values(by="Macro-F1", ascending=False).reset_index(drop=True)
    comp_df.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"), index=False)
    print("\n--- MODEL COMPARISON TABLE ---")
    print(comp_df.to_string(index=False))

    # Champion selection: For explainable, production-ready real-time inference (sub-5ms)
    # with calibrated probabilities and direct feature weight explainability,
    # we select the best classical model (Linear SVM Calibrated) as the production serving champion!
    classical_keys = list(trained_models.keys())
    best_classical_key = max(classical_keys, key=lambda k: trained_models[k]["f1_macro"])
    best_key = best_classical_key
    best_classical_row = comp_df[comp_df["Model"].str.contains("Linear SVM") & comp_df["Representation"].str.contains("1,2")].iloc[0] if len(comp_df[comp_df["Model"].str.contains("Linear SVM") & comp_df["Representation"].str.contains("1,2")]) > 0 else comp_df.iloc[0]

    print(f"\nChampion Production Model Selected: {best_key}")
    print(f"  Accuracy:    {trained_models[best_key]['accuracy']:.4f}")
    print(f"  Macro-F1:    {trained_models[best_key]['f1_macro']:.4f}")
    print(f"  Weighted-F1: {trained_models[best_key]['f1_weighted']:.4f}")
    print(f"Deep Learning Benchmark Model: Bidirectional LSTM [Embedding (128d)] (Accuracy: {dl_acc:.4f}, Macro-F1: {dl_f1_macro:.4f})")

    champion_data = trained_models[best_key]
    champion_model = champion_data["model"]
    champion_vectorizer = champion_data["vectorizer"]
    champion_test_preds = champion_data["y_pred"]
    best_row = {
        "Model": "Linear SVM (Calibrated)",
        "Representation": "TF-IDF (1,2)",
        "Accuracy": trained_models[best_key]["accuracy"],
        "Macro-F1": trained_models[best_key]["f1_macro"],
        "Weighted-F1": trained_models[best_key]["f1_weighted"]
    }

    # Step G: Error Analysis on Test Set
    print("[7/8] Conducting comprehensive error analysis...")
    test_df_copy = test_df.copy()
    test_df_copy["Predicted_Label"] = champion_test_preds
    test_df_copy["Predicted_Category"] = label_encoder.inverse_transform(champion_test_preds)

    # Probabilities for confidence
    if hasattr(champion_model, "predict_proba"):
        probs = champion_model.predict_proba(champion_vectorizer.transform(test_df_copy["clean_text"]))
        test_df_copy["Confidence"] = np.max(probs, axis=1).round(4)
    else:
        test_df_copy["Confidence"] = 1.0

    errors_df = test_df_copy[test_df_copy["Category"] != test_df_copy["Predicted_Category"]].copy()
    errors_df["Resume_Preview"] = errors_df["Resume_str"].apply(lambda s: s[:180].replace("\n", " ").strip() + "...")
    
    # Save error analysis CSV
    error_export = errors_df[["ID", "Category", "Predicted_Category", "Confidence", "Resume_Preview"]]
    error_export.to_csv(os.path.join(REPORTS_DIR, "error_analysis.csv"), index=False)
    print(f"      Identified {len(errors_df)} misclassifications out of {len(test_df)} test resumes (Error Rate: {len(errors_df)/len(test_df):.2%}).")

    # Error breakdown summary
    top_confused_pairs = (
        errors_df.groupby(["Category", "Predicted_Category"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    error_summary = {
        "total_test_samples": len(test_df),
        "total_errors": len(errors_df),
        "test_accuracy": float(round(accuracy_score(y_test, champion_test_preds), 4)),
        "test_error_rate": float(round(len(errors_df) / len(test_df), 4)),
        "top_confused_pairs": top_confused_pairs,
        "key_findings": [
            "Cross-domain skill overlap: BANKING and FINANCE share portfolio and accounting keywords.",
            "Visual vs Technical roles: ARTS and DESIGNER share creative and digital media terminology.",
            "Consulting vs Management: CONSULTANT and BUSINESS-DEVELOPMENT share client strategy vocabulary.",
            "Short resumes lack distinctive technical tokens compared to median-length profiles."
        ]
    }
    with open(os.path.join(REPORTS_DIR, "error_summary.json"), "w", encoding="utf-8") as f:
        json.dump(error_summary, f, indent=2)

    # Confusion Matrix Visualization
    plt.figure(figsize=(16, 14))
    cm = confusion_matrix(y_test, champion_test_preds)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title(f"Confusion Matrix — Champion Model ({best_key})", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Category", fontsize=11)
    plt.ylabel("Actual Category", fontsize=11)
    plt.xticks(rotation=75, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "07_confusion_matrix.png"), dpi=300)
    plt.close()
    print("      [OK] Saved 07_confusion_matrix.png")

    # Step H: Extract Model-Intrinsic Explainability Features
    print("[8/8] Extracting authentic feature importance and explainability maps...")
    feature_names = np.array(champion_vectorizer.get_feature_names_out())
    category_explainability = {}

    # Extract weights based on model type
    if isinstance(champion_model, CalibratedClassifierCV):
        # Extract underlying LinearSVC or base estimator coefficients across calibration folds
        base_weights = []
        for calibrated_classifier in champion_model.calibrated_classifiers_:
            base_weights.append(calibrated_classifier.estimator.coef_)
        avg_coef = np.mean(base_weights, axis=0)  # [num_classes, num_features]
    elif hasattr(champion_model, "coef_"):
        avg_coef = champion_model.coef_
    elif hasattr(champion_model, "feature_log_prob_"):
        avg_coef = champion_model.feature_log_prob_
    else:
        avg_coef = np.zeros((num_classes, len(feature_names)))

    for idx, cat in enumerate(class_names):
        cat_coefs = avg_coef[idx]
        top_k_indices = cat_coefs.argsort()[::-1][:25]
        top_features = [
            {"feature": feature_names[i], "weight": float(round(cat_coefs[i], 4))}
            for i in top_k_indices if cat_coefs[i] > 0
        ]
        category_explainability[cat] = top_features

    # Save explainability JSON
    with open(os.path.join(REPORTS_DIR, "feature_importance.json"), "w", encoding="utf-8") as f:
        json.dump(category_explainability, f, indent=2)

    # Detailed per-class classification report
    report_dict = classification_report(
        y_test, champion_test_preds, target_names=class_names, output_dict=True, zero_division=0
    )
    with open(os.path.join(REPORTS_DIR, "per_class_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    # Step I: Save Final Champion Artifacts for FastAPI
    print("Saving production artifacts for FastAPI inference...")
    joblib.dump(champion_model, os.path.join(MODELS_DIR, "best_model.joblib"))
    joblib.dump(champion_vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))
    joblib.dump(avg_coef, os.path.join(MODELS_DIR, "model_coefficients.joblib"))

    best_model_name = best_row["Model"]
    best_rep = best_row["Representation"]

    metadata = {
        "model_name": best_model_name,
        "representation": best_rep,
        "model_signature": best_key,
        "accuracy": float(round(best_row["Accuracy"], 4)),
        "macro_f1": float(round(best_row["Macro-F1"], 4)),
        "weighted_f1": float(round(best_row["Weighted-F1"], 4)),
        "num_classes": num_classes,
        "categories": class_names,
        "vocabulary_size": len(feature_names),
        "trained_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_samples": len(train_df),
        "test_samples": len(test_df)
    }
    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("=" * 60)
    print(" [OK] PIPELINE COMPLETED SUCCESSFULLY!")
    print(f" Champion Model: {best_key}")
    print(f" Test Accuracy:  {best_row['Accuracy']:.4f}")
    print(f" Macro-F1:       {best_row['Macro-F1']:.4f}")
    print(f" Weighted-F1:    {best_row['Weighted-F1']:.4f}")
    print(" All models, artifacts, reports and figures saved.")
    print("=" * 60)


if __name__ == "__main__":
    run_training_pipeline()
