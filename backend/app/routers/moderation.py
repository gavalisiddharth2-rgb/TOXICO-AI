"""
Moderation Queue Router
Supports viewing, searching, filtering, overriding, and auditing moderation decisions.
"""

import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from backend.app.database import get_db_connection
from backend.app.models.schemas import ModerationActionRequest

router = APIRouter(prefix="/api/moderation", tags=["Moderation"])

@router.get("/queue")
def get_moderation_queue(
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100)
):
    """Retrieves paginated moderation items matching search and filter parameters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if status and status != 'all':
        conditions.append("moderation_status = ?")
        params.append(status)

    if platform and platform != 'all':
        conditions.append("platform = ?")
        params.append(platform)

    if language and language != 'all':
        conditions.append("detected_language_code = ?")
        params.append(language)

    if search and search.strip():
        conditions.append("(original_text LIKE ? OR author_name LIKE ? OR author_handle LIKE ?)")
        search_param = f"%{search.strip()}%"
        params.extend([search_param, search_param, search_param])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Total count
    cursor.execute(f"SELECT COUNT(*) FROM content_items{where_clause}", params)
    total_count = cursor.fetchone()[0]

    # Query items with pagination
    offset = (page - 1) * limit
    cursor.execute(f'''
    SELECT * FROM content_items
    {where_clause}
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    ''', (*params, limit, offset))

    rows = cursor.fetchall()
    items = []
    for r in rows:
        d = dict(r)
        d['flagged_categories'] = json.loads(d['flagged_categories']) if d['flagged_categories'] else []
        d['category_scores'] = json.loads(d['category_scores']) if d['category_scores'] else {}
        d['flagged_keywords'] = json.loads(d['flagged_keywords']) if d['flagged_keywords'] else []
        items.append(d)

    conn.close()

    return {
        'items': items,
        'total': total_count,
        'page': page,
        'limit': limit,
        'pages': max(1, (total_count + limit - 1) // limit)
    }

@router.get("/item/{item_id}")
def get_content_item(item_id: int):
    """Retrieves full details and audit history for a single item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Content item not found")

    item = dict(row)
    item['flagged_categories'] = json.loads(item['flagged_categories']) if item['flagged_categories'] else []
    item['category_scores'] = json.loads(item['category_scores']) if item['category_scores'] else {}
    item['flagged_keywords'] = json.loads(item['flagged_keywords']) if item['flagged_keywords'] else []

    # Get associated actions
    cursor.execute("SELECT * FROM moderation_actions WHERE content_item_id = ? ORDER BY id DESC", (item_id,))
    actions = [dict(a) for a in cursor.fetchall()]

    # Get associated platform reports
    cursor.execute("SELECT * FROM platform_reports WHERE content_item_id = ?", (item_id,))
    reports = [dict(p) for p in cursor.fetchall()]

    conn.close()
    return {
        'item': item,
        'actions': actions,
        'reports': reports
    }

@router.post("/action")
def perform_moderation_action(payload: ModerationActionRequest):
    """
    Applies a human moderator decision (Flag, Approve, Report, Resolve, False Positive).
    Overrides AI decision where applicable and writes to audit log.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (payload.content_item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Content item not found")

    old_status = item['moderation_status']
    action_map = {
        'approve': 'Safe',
        'flag': 'Flagged',
        'report': 'Reported',
        'resolve': 'Resolved',
        'mark_false_positive': 'False Positive',
        'review': 'Under Review'
    }

    new_status = action_map.get(payload.action.lower(), old_status)
    override = 1 if (new_status != item['moderation_status']) else 0

    now_iso = datetime.utcnow().isoformat()

    cursor.execute('''
    UPDATE content_items
    SET moderation_status = ?,
        moderator_override = ?,
        moderator_notes = ?,
        reviewed_by = ?,
        reviewed_at = ?
    WHERE id = ?
    ''', (new_status, override, payload.notes, payload.moderator_name, now_iso, payload.content_item_id))

    # Log action
    cursor.execute('''
    INSERT INTO moderation_actions (content_item_id, action_type, previous_status, new_status, moderator_name, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (payload.content_item_id, payload.action, old_status, new_status, payload.moderator_name, payload.notes))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'content_item_id': payload.content_item_id,
        'previous_status': old_status,
        'new_status': new_status,
        'action': payload.action
    }

@router.get("/audit-log")
def get_audit_log(limit: int = 50):
    """Retrieves chronological audit trail of human moderator actions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT a.*, c.author_handle, c.platform, c.detected_language_name
    FROM moderation_actions a
    JOIN content_items c ON a.content_item_id = c.id
    ORDER BY a.id DESC
    LIMIT ?
    ''', (limit,))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {'audit_log': rows}
