# 🛡️ TOXICO AI — Multilingual AI Content Moderation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Toxico AI** is a production-grade, multilingual AI content moderation safety engine designed to detect toxic comments, hate speech, threats, harassment, and abusive memes across Indic languages (Hindi, Kannada, Malayalam, Tamil, Telugu), Hinglish, and English with Explainable AI (XAI).

---

## 🌟 Key Features

- **🌐 Multilingual & Cross-Lingual Coverage**:
  - Dedicated character and word n-gram ML pipelines for **Hindi**, **Hinglish** (code-mixed), **Kannada**, **Malayalam**, **Tamil**, **Telugu**, and **English**.
  - Script detection & Unicode normalizer capable of handling native Indic scripts as well as Romanized transliterations.
- **🖼️ Multimodal Meme & Image Analysis**:
  - In-browser or server-side OCR engine extracting embedded meme text with contrast & resolution enhancement for downstream toxicity assessment.
- **🔍 Granular 9-Class Toxicity Taxonomy**:
  - `Toxic/Abusive`, `Harassment`, `Hate Speech`, `Threat`, `Insult`, `Profanity`, `Discrimination`, `Sexual/Explicit Abuse`, and `Non-toxic/Safe`.
- **💡 Explainable AI (XAI)**:
  - Transparent feature importance, lexical attribution, and highlighted trigger keywords explaining *why* a piece of content was flagged.
- **⚡ Automated Decision Engine**:
  - Dynamic severity scoring, policy-based confidence thresholds, auto-triage (Allow, Flag for Review, Escalate, Auto-Reject).
- **✨ Liquid Glass Modern Dashboard**:
  - Interactive moderation queue with bulk actions, real-time analytics, social integration simulator, and one-click incident reporting.

---

## 📁 Repository Structure

```text
TOXICO-AI/
├── backend/
│   └── app/
│       ├── data/
│       │   └── trained_models/       # Pretrained TF-IDF & Logistic Regression pipelines (.joblib)
│       ├── ml/
│       │   ├── decision_engine.py    # Policy rules, risk scoring & escalation logic
│       │   ├── explainability.py     # Feature attribution & trigger keyword extractor
│       │   ├── language_detector.py  # Indic & English language detection
│       │   ├── ocr_engine.py         # WinRT / PIL image OCR preprocessing
│       │   ├── pipeline.py           # Unified multi-stage inference pipeline
│       │   ├── text_preprocessor.py  # Script normalization & tokenization
│       │   └── toxicity_classifier.py# Multi-model classification & calibration
│       ├── models/
│       │   └── schemas.py            # Pydantic request/response schemas
│       ├── routers/                  # API endpoints (analyze, moderation, reports, etc.)
│       ├── database.py               # SQLite layer with auto-seeding
│       └── main.py                   # FastAPI server entry point
├── frontend/
│   ├── assets/                       # Sample memes, icons & media
│   ├── css/
│   │   └── styles.css                # Custom Liquid Glass UI styling
│   ├── js/
│   │   ├── views/                    # View controllers (moderation, analyze, analytics...)
│   │   ├── api.js                    # REST client
│   │   ├── app.js                    # SPA router & state management
│   │   └── auth.js                   # Client authentication logic
│   └── index.html                    # Single Page Application
├── dataset/
│   └── language/                     # Indic language train/val/test datasets
├── scripts/
│   ├── inspect_datasets.py           # Dataset verification & stats
│   ├── test_pipeline.py              # ML pipeline test suite
│   └── train_multilingual_models.py  # Automated model retraining script
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.11, 3.12, 3.13 supported)
- Git

### 2. Clone Repository
```bash
git clone https://github.com/gavalisiddharth2-rgb/TOXICO-AI.git
cd TOXICO-AI
```

### 3. Create & Activate Virtual Environment
```bash
# On Windows
py -m venv venv
.\venv\Scripts\activate

# On Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start Application Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at **[http://localhost:8000](http://localhost:8000)** to access the platform.
API Swagger documentation is accessible at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/analyze` | `POST` | Analyzes text or OCR payload for toxicity, language & categories |
| `/api/moderation/queue` | `GET` | Retrieves paginated moderation queue items |
| `/api/moderation/action` | `POST` | Applies moderator action (Approve, Reject, Escalate) |
| `/api/reports/file` | `POST` | Files incident reports to external platforms |
| `/api/analytics/summary` | `GET` | Fetches system stats, violation trends & language breakdown |
| `/api/health` | `GET` | System health check and model loading status |

---

## 🧠 Machine Learning Pipelines

Each language utilizes custom character and word n-gram features (`ngram_range=(2, 5)`, `char_wb` analyzer) coupled with balanced Logistic Regression classifiers optimized for high precision on hate speech and harassment:
- **Hindi Pipeline**: Evaluated on Hindi abusive & toxic datasets.
- **Hinglish Pipeline**: Trained on Romanized Indo-HateSpeech datasets.
- **Dravidian Pipelines**: Kannada, Malayalam, Tamil, Telugu datasets.
- **English Multi-Category Pipeline**: 6 fine-grained classification heads (`toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`).

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).
