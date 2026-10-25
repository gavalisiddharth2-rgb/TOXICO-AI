"""
Unified Multilingual Content Moderation Pipeline
End-to-End Orchestrator:
Input -> Language Detection -> Preprocessing -> Multilingual NLP / OCR -> Toxicity Classification ->
Explainability -> Recommendation -> Moderation Workflow
"""

import logging
from typing import Dict, Any, Optional
from PIL import Image

from backend.app.ml.language_detector import language_detector
from backend.app.ml.text_preprocessor import text_preprocessor
from backend.app.ml.ocr_engine import ocr_engine
from backend.app.ml.toxicity_classifier import toxicity_classifier
from backend.app.ml.explainability import explainability_engine
from backend.app.ml.decision_engine import decision_engine

logger = logging.getLogger(__name__)

class ModerationPipeline:
    def __init__(self):
        self.lang_detector = language_detector
        self.preprocessor = text_preprocessor
        self.ocr = ocr_engine
        self.classifier = toxicity_classifier
        self.explainer = explainability_engine
        self.decision = decision_engine

    async def analyze_text(self, text: str, manual_language: Optional[str] = None) -> Dict[str, Any]:
        """Runs the complete NLP toxicity analysis pipeline on raw text input."""
        # 1. Text Preprocessing
        prep = self.preprocessor.clean(text)
        cleaned_text = prep['cleaned']
        original_text = prep['original']

        # 2. Language Detection (Auto-detect or user override)
        if manual_language and manual_language != 'auto':
            lang_meta = self.lang_detector.languages.get(
                manual_language,
                {'name': manual_language.capitalize(), 'script': 'Selected', 'family': 'Custom'}
            )
            lang_result = {
                'language_code': manual_language,
                'language_name': lang_meta['name'],
                'script': lang_meta['script'],
                'confidence': 1.0,
                'is_code_mixed': False,
                'details': f"Manually selected {lang_meta['name']}"
            }
        else:
            lang_result = self.lang_detector.detect(cleaned_text or original_text)

        detected_lang = lang_result['language_code']

        # 3. Toxicity Classification
        cls_result = self.classifier.predict(
            text=cleaned_text or original_text,
            detected_lang=detected_lang,
            emoji_risk=prep['emoji_risk_score']
        )

        overall_score = cls_result['overall_score']
        is_toxic = cls_result['is_toxic']
        confidence = cls_result['confidence']
        flagged_categories = cls_result['flagged_categories']
        category_scores = cls_result['category_scores']
        model_used = cls_result['model_name']

        # 4. Explainability & Attribution
        explanation_result = self.explainer.explain(
            original_text=original_text,
            cleaned_text=cleaned_text,
            detected_lang=detected_lang,
            overall_score=overall_score,
            is_toxic=is_toxic,
            confidence=confidence,
            flagged_categories=flagged_categories,
            category_scores=category_scores,
            tokens=prep['tokens']
        )

        # 5. Recommended Action
        rec_result = self.decision.recommend(
            overall_score=overall_score,
            is_toxic=is_toxic,
            flagged_categories=flagged_categories,
            confidence=confidence
        )

        return {
            'content_type': 'text',
            'original_text': original_text,
            'cleaned_text': cleaned_text,
            'language': lang_result,
            'toxicity': {
                'overall_score': overall_score,
                'percentage': int(round(overall_score * 100)),
                'is_toxic': is_toxic,
                'confidence': confidence,
                'confidence_percentage': int(round(confidence * 100)),
                'flagged_categories': flagged_categories,
                'category_scores': category_scores,
                'model_name': model_used
            },
            'explainability': explanation_result,
            'decision': rec_result,
            'preprocessing_metadata': {
                'word_count': prep['word_count'],
                'char_count': prep['char_count'],
                'mentions': prep['mentions'],
                'hashtags': prep['hashtags'],
                'emojis_detected': prep['emojis']
            }
        }

    async def analyze_image(self, pil_image: Image.Image, manual_language: Optional[str] = None) -> Dict[str, Any]:
        """Runs OCR followed by multilingual NLP toxicity analysis on image/meme."""
        # 1. OCR Text Extraction
        ocr_res = await self.ocr.extract_text_from_pil(pil_image)
        extracted_text = ocr_res.get('extracted_text', '').strip()

        # 2. Feed extracted text into text pipeline
        if not extracted_text:
            return {
                'content_type': 'image',
                'ocr': {
                    'extracted_text': '',
                    'word_count': 0,
                    'engine': ocr_res.get('engine', 'Unknown'),
                    'success': False,
                    'error': 'No readable text was detected in the uploaded image.'
                },
                'original_text': '',
                'language': {
                    'language_code': 'unknown',
                    'language_name': 'Unknown',
                    'script': 'None',
                    'confidence': 0.0,
                    'is_code_mixed': False,
                    'details': 'No text extracted'
                },
                'toxicity': {
                    'overall_score': 0.0,
                    'percentage': 0,
                    'is_toxic': False,
                    'confidence': 0.90,
                    'confidence_percentage': 90,
                    'flagged_categories': ['Non-toxic/Safe'],
                    'category_scores': {cat: 0.0 for cat in self.classifier.categories},
                    'model_name': 'None'
                },
                'explainability': {
                    'explanation': 'No text could be extracted from this image. Image does not contain detectable toxic text.',
                    'flagged_keywords': [],
                    'highlighted_text': '',
                    'disclaimer': self.explainer.AI_DISCLAIMER if hasattr(self.explainer, 'AI_DISCLAIMER') else "AI-generated prediction for human review."
                },
                'decision': {
                    'recommended_action': 'Allow / Approved (No Text Detected)',
                    'recommended_status': 'Safe',
                    'urgency_level': 'Low',
                    'severity_badge': 'success',
                    'requires_human_override': False,
                    'next_steps': ['No toxic text extracted from image']
                }
            }

        # Run text analysis on extracted OCR text
        analysis = await self.analyze_text(extracted_text, manual_language)
        analysis['content_type'] = 'image'
        analysis['ocr'] = ocr_res

        return analysis

pipeline = ModerationPipeline()
