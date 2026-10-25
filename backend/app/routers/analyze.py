"""
Analyze Router
Handles real-time text analysis, image/meme OCR analysis, and queue persistence.
"""

import io
import json
import logging
from typing import Optional
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.ml.pipeline import pipeline
from backend.app.models.schemas import AnalyzeTextRequest
from backend.app.database import get_db_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analyze", tags=["Analyze"])

@router.post("/text")
async def analyze_text_endpoint(payload: AnalyzeTextRequest):
    """Analyzes raw text for language, toxicity, categories, explanation, and recommendation."""
    try:
        result = await pipeline.analyze_text(
            text=payload.text,
            manual_language=payload.language
        )
        return result
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    language: Optional[str] = Form("auto")
):
    """
    Uploads image/meme, performs OCR text extraction, displays extracted text,
    and runs multilingual NLP toxicity analysis.
    """
    try:
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        result = await pipeline.analyze_image(
            pil_image=pil_image,
            manual_language=language
        )
        # Include original filename
        result['filename'] = file.filename
        return result
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@router.post("/save-to-queue")
async def save_to_queue(payload: dict):
    """Saves an analyzed item into the moderation queue for human review."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        original_text = payload.get('original_text', '')
        toxicity = payload.get('toxicity', {})
        lang = payload.get('language', {})
        explain = payload.get('explainability', {})
        decision = payload.get('decision', {})
        platform = payload.get('platform', 'manual')
        author_name = payload.get('author_name', 'Manual Submission')
        author_handle = payload.get('author_handle', '@anonymous')
        content_type = payload.get('content_type', 'text')
        ocr_text = payload.get('ocr', {}).get('extracted_text') if payload.get('ocr') else None

        cursor.execute('''
        INSERT INTO content_items (
            platform, author_name, author_handle, author_avatar, content_type,
            original_text, ocr_extracted_text, detected_language_code,
            detected_language_name, toxicity_score, is_toxic, confidence_score,
            flagged_categories, category_scores, explanation, flagged_keywords,
            recommended_action, urgency_level, moderation_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            platform, author_name, author_handle,
            'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop',
            content_type, original_text, ocr_text,
            lang.get('language_code', 'en'), lang.get('language_name', 'English'),
            toxicity.get('overall_score', 0.0),
            1 if toxicity.get('is_toxic') else 0,
            toxicity.get('confidence', 0.9),
            json.dumps(toxicity.get('flagged_categories', ['Non-toxic/Safe'])),
            json.dumps(toxicity.get('category_scores', {})),
            explain.get('explanation', ''),
            json.dumps(explain.get('flagged_keywords', [])),
            decision.get('recommended_action', 'Queue for Review'),
            decision.get('urgency_level', 'Medium'),
            decision.get('recommended_status', 'Under Review')
        ))

        item_id = cursor.lastrowid
        conn.commit()
        return {'success': True, 'content_item_id': item_id, 'message': 'Item added to moderation queue.'}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
