import os
import sys
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.pipeline import Pipeline

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.makedirs(os.path.join("backend", "app", "data", "trained_models"), exist_ok=True)
models_dir = os.path.join("backend", "app", "data", "trained_models")

print("==================================================")
print("  TRAINING MULTILINGUAL TOXICITY MODELS")
print("==================================================")

# 1. Indic Languages (Hindi, Kannada, Malayalam, Tamil, Telugu)
indic_langs = {
    'hindi': 'hindi_train.csv',
    'kannada': 'kannada_train.csv',
    'malyalam': 'malyalam_train.csv',
    'tamil': 'tamil_train.csv',
    'telugu': 'telugu_train.csv'
}

for lang, filename in indic_langs.items():
    path = filename if os.path.exists(filename) else os.path.join("dataset", "language", filename)
    if not os.path.exists(path):
        print(f"Skipping {lang}: {path} not found")
        continue

    print(f"\n--> Training {lang.upper()} model from {path}...")
    t0 = time.time()
    df = pd.read_csv(path)
    df = df.dropna(subset=['text', 'label'])
    
    # In the Indic dataset:
    # label 0 = Toxic / Abusive / Hate
    # label 1 = Safe / Non-toxic
    # We will standardize our target: 1 = Toxic, 0 = Safe
    # so y = (df['label'] == 0).astype(int)
    X = df['text'].astype(str)
    y = (df['label'] == 0).astype(int)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

    # Use char_wb + word n-grams for robust Indic morphological coverage
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(2, 5), analyzer='char_wb', min_df=2, max_features=30000)),
        ('clf', LogisticRegression(C=3.0, max_iter=500, class_weight='balanced'))
    ])

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_val)
    acc = accuracy_score(y_val, preds)
    f1 = f1_score(y_val, preds)
    print(f"    Done in {time.time()-t0:.2f}s | Val Accuracy: {acc*100:.2f}% | F1: {f1:.4f}")

    model_path = os.path.join(models_dir, f"{lang}_model.joblib")
    joblib.dump(pipe, model_path)
    print(f"    Saved to {model_path}")

# 2. Hinglish / Romanized Hindi (Indo-HateSpeech_Dataset.xlsx)
indo_path = os.path.join("dataset", "Indo-HateSpeech_Dataset.xlsx")
if os.path.exists(indo_path):
    print(f"\n--> Training HINGLISH model from {indo_path}...")
    t0 = time.time()
    df_indo = pd.read_excel(indo_path)
    df_indo = df_indo.dropna(subset=['Comment', 'Label'])
    df_indo['Comment'] = df_indo['Comment'].astype(str)
    # Filter labels
    df_indo = df_indo[df_indo['Label'].astype(str).str.contains("HS0|HS1")]
    # HS1 = 1 (Toxic), HS0 = 0 (Safe)
    y_indo = df_indo['Label'].astype(str).str.contains("HS1").astype(int)
    X_indo = df_indo['Comment']

    X_train, X_val, y_train, y_val = train_test_split(X_indo, y_indo, test_size=0.15, random_state=42, stratify=y_indo)

    pipe_hinglish = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(2, 5), analyzer='char_wb', min_df=2, max_features=35000)),
        ('clf', LogisticRegression(C=2.5, max_iter=500, class_weight='balanced'))
    ])
    pipe_hinglish.fit(X_train, y_train)
    preds = pipe_hinglish.predict(X_val)
    acc = accuracy_score(y_val, preds)
    f1 = f1_score(y_val, preds)
    print(f"    Done in {time.time()-t0:.2f}s | Val Accuracy: {acc*100:.2f}% | F1: {f1:.4f}")

    model_path = os.path.join(models_dir, "hinglish_model.joblib")
    joblib.dump(pipe_hinglish, model_path)
    print(f"    Saved to {model_path}")

# 3. English Multi-Category Model (Jigsaw Dataset)
jigsaw_path = os.path.join("dataset", "jigsaw-toxic-comment-train-processed-seqlen128.csv")
if os.path.exists(jigsaw_path):
    print(f"\n--> Training ENGLISH MULTI-CATEGORY model from {jigsaw_path}...")
    t0 = time.time()
    categories = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    df_jig = pd.read_csv(jigsaw_path, nrows=75000) # Sample 75k rows for fast, balanced training
    df_jig = df_jig.dropna(subset=['comment_text'])

    tfidf_en = TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_features=30000, sublinear_tf=True)
    X_mat = tfidf_en.fit_transform(df_jig['comment_text'].astype(str))

    cat_models = {}
    for cat in categories:
        y_cat = df_jig[cat].values
        clf = LogisticRegression(C=2.0, max_iter=400, class_weight='balanced')
        clf.fit(X_mat, y_cat)
        cat_models[cat] = clf
        print(f"    Trained category '{cat}' (positives: {int(y_cat.sum())})")

    jig_bundle = {
        'vectorizer': tfidf_en,
        'categories': categories,
        'models': cat_models
    }
    model_path = os.path.join(models_dir, "english_multicat_model.joblib")
    joblib.dump(jig_bundle, model_path)
    print(f"    Done in {time.time()-t0:.2f}s | Saved to {model_path}")

print("\n==================================================")
print("  ALL MULTILINGUAL MODELS SUCCESSFULLY TRAINED!")
print("==================================================")
