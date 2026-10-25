"""
Reports Router
Generates official platform escalation reports, compliance bundles, and exports.
"""

import io
import csv
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Response

from backend.app.database import get_db_connection
from backend.app.models.schemas import SubmitReportRequest

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("")
def list_reports():
    """Retrieves all official platform abuse reports."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT r.*, c.original_text, c.author_handle, c.author_name, c.detected_language_name, c.toxicity_score
    FROM platform_reports r
    JOIN content_items c ON r.content_item_id = c.id
    ORDER BY r.id DESC
    ''')

    rows = cursor.fetchall()
    reports = []
    for r in rows:
        d = dict(r)
        d['evidence_payload'] = json.loads(d['evidence_payload']) if d['evidence_payload'] else {}
        reports.append(d)

    conn.close()
    return {'reports': reports}

@router.post("/submit")
def submit_platform_report(payload: SubmitReportRequest):
    """
    Submits an official report packet for platform abuse dispatch.
    Updates the content item status to 'Reported' and generates unique ticket ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM content_items WHERE id = ?", (payload.content_item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Content item not found")

    platform = item['platform']
    short_uuid = str(uuid.uuid4())[:8].upper()
    ticket_id = f"TKT-{platform[:2].upper()}-2026-{short_uuid}"

    evidence = {
        'original_text': item['original_text'],
        'author': item['author_handle'],
        'detected_language': item['detected_language_name'],
        'ai_toxicity_score': f"{int(item['toxicity_score'] * 100)}%",
        'explanation': item['explanation'],
        'custom_notes': payload.custom_notes or "Violates platform community standards on abusive behavior."
    }

    cursor.execute('''
    INSERT INTO platform_reports (
        content_item_id, report_ticket_id, platform, violation_category,
        severity, evidence_payload, platform_report_status, filed_by
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        payload.content_item_id, ticket_id, platform, payload.violation_category,
        item['urgency_level'], json.dumps(evidence), 'Submitted', payload.moderator_name
    ))

    # Update item status to 'Reported'
    cursor.execute('''
    UPDATE content_items
    SET moderation_status = 'Reported',
        reviewed_by = ?,
        reviewed_at = ?
    WHERE id = ?
    ''', (payload.moderator_name, datetime.utcnow().isoformat(), payload.content_item_id))

    # Audit log
    cursor.execute('''
    INSERT INTO moderation_actions (content_item_id, action_type, previous_status, new_status, moderator_name, notes)
    VALUES (?, 'report', ?, 'Reported', ?, ?)
    ''', (payload.content_item_id, item['moderation_status'], payload.moderator_name, f"Submitted official platform ticket: {ticket_id}"))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'report_ticket_id': ticket_id,
        'platform': platform,
        'status': 'Submitted',
        'message': f"Official report ticket {ticket_id} generated for {platform.capitalize()}."
    }

@router.get("/export")
def export_reports(format: str = "csv"):
    """Exports compliance reports into CSV or JSON format."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT r.report_ticket_id, r.platform, r.violation_category, r.severity,
           r.platform_report_status, r.filed_by, r.filed_at,
           c.author_handle, c.detected_language_name, c.toxicity_score, c.original_text
    FROM platform_reports r
    JOIN content_items c ON r.content_item_id = c.id
    ORDER BY r.id DESC
    ''')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if format.lower() == "json":
        return Response(
            content=json.dumps(rows, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=moderation_reports.json"}
        )

    # Default CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Platform", "Violation Category", "Severity",
        "Status", "Filed By", "Filed At", "Author Handle", "Language",
        "Toxicity Score", "Original Content"
    ])

    for r in rows:
        writer.writerow([
            r['report_ticket_id'],
            r['platform'],
            r['violation_category'],
            r['severity'],
            r['platform_report_status'],
            r['filed_by'],
            r['filed_at'],
            r['author_handle'],
            r['detected_language_name'],
            f"{int(r['toxicity_score']*100)}%",
            r['original_text']
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=moderation_reports.csv"}
    )
