"""
Multilingual Toxicity Classifier Engine
Loads trained models for Hindi, Hinglish, Kannada, Malayalam, Tamil, Telugu, and English.
Predicts overall toxicity score, confidence score, and fine-grained categories across all 9 classes.
Supports easily replaceable models and dynamic category extension.
"""

import os
import re
import logging
import joblib
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Core toxicity categories as specified in requirements
STANDARD_CATEGORIES = [
    'Toxic/Abusive',
    'Harassment',
    'Hate Speech',
    'Threat',
    'Insult',
    'Profanity',
    'Discrimination',
    'Sexual/Explicit Abuse',
    'Non-toxic/Safe'
]

# Multilingual keywords and semantic indicators for fine-grained category calibration
CATEGORY_LEXICONS = {
    'Threat': {
        'keywords': [
            'kill', 'murder', 'shoot', 'stab', 'die', 'death', 'destroy', 'beat',
            'maro', 'jaan se mar dunga', 'khatam kar dunga', 'thok dunga', 'pitunga',
            'उदावतो', 'मारून टाकीन', 'ಕೊಲ್ಲುತ್ತೇನೆ', 'ചത്തോളൂ', 'கொல்வேன்', 'చంపేస్తా'
        ],
        'weight': 1.0
    },
    'Sexual/Explicit Abuse': {
        'keywords': [
            'chod', 'chudai', 'chut', 'lund', 'bhosadike', 'randi', 'sexy', 'boobs',
            'blowjob', 'dick', 'pussy', 'vagina', 'rape', 'बुर', 'लंड', 'छिनाल', 'रांड',
            'ಸೂಳೆ', 'തുരുകി', 'തേവിடியா', 'புண்டா', 'దేగిండో', 'గుద్ద'
        ],
        'weight': 0.95
    },
    'Hate Speech': {
        'keywords': [
            'mulle', 'katue', 'bhakt', 'librandu', 'chamar', 'bhangi', 'terrorist',
            'muslim', 'hindu', 'dalit', 'christian', 'jew', 'nazi', 'caste', 'धर्म',
            'हब्सी', 'काफिर', 'जिहादी', 'ಮತ', 'ജാതി', 'சாதி', 'మతం'
        ],
        'weight': 0.90
    },
    'Harassment': {
        'keywords': [
            'stalk', 'harass', 'dox', 'leak', 'chasing', 'target', 'expose',
            'picha karunga', 'berozgar', 'troll', 'घेरेंगे', 'किरुवळ', 'தொல்லை'
        ],
        'weight': 0.85
    },
    'Insult': {
        'keywords': [
            'idiot', 'stupid', 'moron', 'loser', 'dumb', 'clown', 'ugly', 'scum',
            'kutta', 'kamine', 'saale', 'bewakoof', 'gadha', 'ullu', 'gaandu',
            'सूळे ಮೂಡೆ', 'നായേ', 'மவனே', 'పిచ్చోడా', 'దద్దమ్మ'
        ],
        'weight': 0.80
    },
    'Profanity': {
        'keywords': [
            'fuck', 'shit', 'bitch', 'asshole', 'bastard', 'crap', 'damn',
            'bc', 'mc', 'bhenchod', 'madarchod', 'harami', 'kamina', 'bakwas',
            'साले', 'हरामखोर', 'ಮೈರೇ', 'மயிறு'
        ],
        'weight': 0.75
    },
    'Discrimination': {
        'keywords': [
            'racist', 'slur', 'inferior', 'migrant', 'outsider', 'bihari', 'refugee',
            'subhuman', 'dirt', 'अछूत', 'भेदभाव'
        ],
        'weight': 0.85
    }
}

class ToxicityClassifier:
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, 'data', 'trained_models')

        self.models_dir = models_dir
        self.models: Dict[str, Any] = {}
        self.categories = STANDARD_CATEGORIES.copy()
        self.load_models()

    def load_models(self):
        """Loads all serialized joblib pipelines from disk."""
        model_files = {
            'hi': 'hindi_model.joblib',
            'hinglish': 'hinglish_model.joblib',
            'kn': 'kannada_model.joblib',
            'ml': 'malyalam_model.joblib',
            'ta': 'tamil_model.joblib',
            'te': 'telugu_model.joblib',
            'en': 'english_multicat_model.joblib',
        }

        for lang, fname in model_files.items():
            path = os.path.join(self.models_dir, fname)
            if os.path.exists(path):
                try:
                    self.models[lang] = joblib.load(path)
                    logger.info(f"Loaded {lang} model from {path}")
                except Exception as e:
                    logger.error(f"Failed to load {lang} model: {e}")
            else:
                logger.warning(f"Model file not found: {path}")

    def register_category(self, category_name: str, keywords: List[str] = None, weight: float = 0.8):
        """Dynamically add or extend a moderation category."""
        if category_name not in self.categories:
            self.categories.insert(-1, category_name)
        if keywords:
            CATEGORY_LEXICONS[category_name] = {'keywords': keywords, 'weight': weight}

    def predict(self, text: str, detected_lang: str = 'en', emoji_risk: float = 0.0) -> Dict[str, Any]:
        """
        Predicts toxicity, confidence score, and fine-grained categories.
        Uses language-appropriate model with multi-category mapping.
        """
        if not text or not text.strip():
            return self._empty_result()

        clean_lower = text.lower().strip()
        lang = detected_lang.lower()

        # 1. Base Toxicity Prediction from Language Model
        raw_prob = 0.0
        used_model = 'default_heuristic'

        if lang == 'en' and 'en' in self.models:
            en_bundle = self.models['en']
            vec = en_bundle['vectorizer'].transform([clean_lower])
            raw_prob = float(en_bundle['models']['toxic'].predict_proba(vec)[0, 1])
            used_model = 'Jigsaw English Multi-Category Classifier'
        elif lang in self.models:
            pipe = self.models[lang]
            raw_prob = float(pipe.predict_proba([clean_lower])[0, 1])
            used_model = f'{lang.upper()} Specialized Indic Classifier'
        elif lang == 'mr' and 'hi' in self.models:
            # Marathi shares Devanagari script; use Devanagari Hindi model
            pipe = self.models['hi']
            raw_prob = float(pipe.predict_proba([clean_lower])[0, 1])
            used_model = 'Devanagari Indic Classifier (Marathi mode)'
        elif 'hinglish' in self.models:
            # Fallback to Hinglish/Multilingual pipeline
            pipe = self.models['hinglish']
            raw_prob = float(pipe.predict_proba([clean_lower])[0, 1])
            used_model = 'Hinglish Multilingual Classifier (Fallback)'
        else:
            raw_prob = 0.1

        # Incorporate emoji risk modifier
        if emoji_risk > 0.0:
            raw_prob = max(raw_prob, min(0.99, raw_prob * 0.7 + emoji_risk * 0.35))

        # Check for explicit severe keywords in any language
        has_severe_kw = False
        for severe_cat in ['Threat', 'Sexual/Explicit Abuse', 'Hate Speech', 'Profanity']:
            if any(kw in clean_lower for kw in CATEGORY_LEXICONS.get(severe_cat, {}).get('keywords', [])):
                has_severe_kw = True
                break

        if has_severe_kw:
            raw_prob = max(raw_prob, 0.85)

        # 2. Category Probability Breakdown
        category_scores: Dict[str, float] = {}

        # If English, leverage Jigsaw multi-label outputs directly
        if lang == 'en' and 'en' in self.models:
            en_bundle = self.models['en']
            vec = en_bundle['vectorizer'].transform([clean_lower])
            jig_map = {
                'Toxic/Abusive': 'toxic',
                'Harassment': 'insult',
                'Hate Speech': 'identity_hate',
                'Threat': 'threat',
                'Insult': 'insult',
                'Profanity': 'obscene',
                'Discrimination': 'identity_hate',
                'Sexual/Explicit Abuse': 'obscene',
            }
            for cat, jig_key in jig_map.items():
                if jig_key in en_bundle['models']:
                    prob = float(en_bundle['models'][jig_key].predict_proba(vec)[0, 1])
                    category_scores[cat] = round(prob, 4)
                else:
                    category_scores[cat] = round(raw_prob * 0.5, 4)
        else:
            # For Indic & Hinglish languages, derive fine-grained categories via semantic calibration
            for cat, meta in CATEGORY_LEXICONS.items():
                kw_hits = sum(1 for kw in meta['keywords'] if kw in clean_lower)
                if kw_hits > 0:
                    # Explicit category match
                    cat_prob = min(0.98, raw_prob * 0.8 + (kw_hits * 0.15) * meta['weight'])
                else:
                    # General category distribution based on base toxicity
                    if cat in ['Toxic/Abusive', 'Profanity', 'Insult']:
                        cat_prob = raw_prob * 0.85
                    elif cat in ['Harassment', 'Hate Speech']:
                        cat_prob = raw_prob * 0.60
                    elif cat in ['Threat', 'Sexual/Explicit Abuse', 'Discrimination']:
                        cat_prob = raw_prob * 0.35
                    else:
                        cat_prob = raw_prob * 0.40
                category_scores[cat] = round(min(0.99, cat_prob), 4)

        # Baseline Toxic/Abusive matches overall toxicity
        category_scores['Toxic/Abusive'] = round(max(category_scores.get('Toxic/Abusive', 0.0), raw_prob), 4)

        # Non-toxic / Safe is complementary
        safe_prob = round(max(0.01, 1.0 - raw_prob), 4)
        category_scores['Non-toxic/Safe'] = safe_prob

        # Overall Toxicity Score
        overall_score = round(raw_prob, 4)
        is_toxic = overall_score >= 0.50

        # Confidence Score: distance from uncertain threshold (0.50) scaled to [0.70, 0.99]
        uncertainty_dist = abs(overall_score - 0.50) * 2 # 0.0 to 1.0
        confidence = round(min(0.99, max(0.72, 0.70 + (uncertainty_dist * 0.28))), 2)

        # Detected Categories (threshold >= 0.45, excluding Non-toxic if toxic)
        flagged_categories = []
        if is_toxic:
            for cat, score in category_scores.items():
                if cat != 'Non-toxic/Safe' and score >= 0.45:
                    flagged_categories.append(cat)
            if not flagged_categories:
                flagged_categories = ['Toxic/Abusive']
        else:
            flagged_categories = ['Non-toxic/Safe']

        return {
            'overall_score': overall_score,
            'is_toxic': is_toxic,
            'confidence': confidence,
            'flagged_categories': flagged_categories,
            'category_scores': category_scores,
            'model_name': used_model,
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            'overall_score': 0.0,
            'is_toxic': False,
            'confidence': 0.95,
            'flagged_categories': ['Non-toxic/Safe'],
            'category_scores': {cat: (1.0 if cat == 'Non-toxic/Safe' else 0.0) for cat in self.categories},
            'model_name': 'None (Empty Input)',
        }

toxicity_classifier = ToxicityClassifier()
