"""
Settings Router
Manages detection sensitivity thresholds, active languages, and platform configs.
"""

import json
from fastapi import APIRouter
from backend.app.database import get_db_connection
from backend.app.models.schemas import SettingsUpdateRequest
from backend.app.ml.decision_engine import decision_engine
from backend.app.ml.toxicity_classifier import toxicity_classifier

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("")
def get_settings():
    """Retrieves current platform settings and active AI models info."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM system_settings")
    settings_dict = {}
    for r in cursor.fetchall():
        key, val = r['key'], r['value']
        try:
            settings_dict[key] = json.loads(val)
        except Exception:
            settings_dict[key] = val

    conn.close()

    # Loaded models metadata
    loaded_models = []
    for lang_code, model in toxicity_classifier.models.items():
        loaded_models.append({
            'language_code': lang_code,
            'name': f"{lang_code.upper()} Classifier",
            'type': type(model).__name__,
            'status': 'Active & Loaded'
        })

    return {
        'settings': settings_dict,
        'loaded_models': loaded_models,
        'available_categories': toxicity_classifier.categories
    }

@router.post("")
def update_settings(payload: SettingsUpdateRequest):
    """Updates system thresholds and active language preferences."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if payload.safe_threshold is not None:
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", ('safe_threshold', str(payload.safe_threshold)))
        decision_engine.safe_threshold = payload.safe_threshold

    if payload.review_threshold is not None:
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", ('review_threshold', str(payload.review_threshold)))
        decision_engine.review_threshold = payload.review_threshold

    if payload.flag_threshold is not None:
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", ('flag_threshold', str(payload.flag_threshold)))
        decision_engine.flag_threshold = payload.flag_threshold

    if payload.auto_flag_enabled is not None:
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", ('auto_flag_enabled', str(payload.auto_flag_enabled).lower()))

    if payload.active_languages is not None:
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", ('active_languages', json.dumps(payload.active_languages)))

    conn.commit()
    conn.close()

    return {'success': True, 'message': 'Platform settings successfully updated.'}
