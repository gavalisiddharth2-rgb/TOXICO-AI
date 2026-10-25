"""
Database Layer for Multilingual AI Content Moderation Platform
Uses SQLite with robust schema, connection pooling, and realistic seed data.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'moderation.db')

def get_db_connection():
    """Returns an active SQLite connection with row factory configured."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Simple SHA-256 password hash for standard user auth."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initializes schema tables and seeds initial data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Connected Accounts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS connected_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        platform_display_name TEXT NOT NULL,
        account_name TEXT NOT NULL,
        handle TEXT NOT NULL,
        avatar_url TEXT,
        status TEXT NOT NULL,
        is_demo BOOLEAN DEFAULT 1,
        access_token TEXT,
        scopes TEXT,
        posts_monitored_count INTEGER DEFAULT 0,
        toxic_detected_count INTEGER DEFAULT 0,
        last_sync_at TIMESTAMP
    )
    ''')

    # 3. Content Items Table (Moderation Queue Items)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        source_url TEXT,
        author_name TEXT NOT NULL,
        author_handle TEXT NOT NULL,
        author_avatar TEXT,
        content_type TEXT DEFAULT 'text',
        original_text TEXT NOT NULL,
        media_url TEXT,
        ocr_extracted_text TEXT,
        detected_language_code TEXT NOT NULL,
        detected_language_name TEXT NOT NULL,
        toxicity_score REAL NOT NULL,
        is_toxic BOOLEAN NOT NULL,
        confidence_score REAL NOT NULL,
        flagged_categories TEXT NOT NULL,
        category_scores TEXT NOT NULL,
        explanation TEXT NOT NULL,
        flagged_keywords TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        urgency_level TEXT NOT NULL,
        moderation_status TEXT NOT NULL,
        moderator_override BOOLEAN DEFAULT 0,
        moderator_notes TEXT,
        reviewed_by TEXT,
        reviewed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Moderation Actions Audit Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS moderation_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_item_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        moderator_name TEXT NOT NULL,
        reason TEXT,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 5. Platform Reports Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS platform_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_item_id INTEGER NOT NULL,
        report_ticket_id TEXT UNIQUE NOT NULL,
        platform TEXT NOT NULL,
        violation_category TEXT NOT NULL,
        severity TEXT NOT NULL,
        evidence_payload TEXT NOT NULL,
        platform_report_status TEXT NOT NULL,
        filed_by TEXT NOT NULL,
        filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 6. System Settings Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    ''')

    conn.commit()

    # Check if seed data is needed
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_database(conn)

    conn.close()

def seed_database(conn: sqlite3.Connection):
    """Populates realistic seed data including multilingual comments and demo accounts."""
    cursor = conn.cursor()
    now = datetime.utcnow()

    # 1. Seed Users
    cursor.execute('''
    INSERT INTO users (username, email, full_name, role, password_hash)
    VALUES (?, ?, ?, ?, ?)
    ''', ('moderator', 'moderator@toxico.ai', 'Senior AI Safety Moderator', 'Moderator', hash_password('demo123')))

    cursor.execute('''
    INSERT INTO users (username, email, full_name, role, password_hash)
    VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@toxico.ai', 'Platform Administrator', 'Admin', hash_password('admin123')))

    # 2. Seed Connected Accounts
    demo_accounts = [
        ('instagram', 'Instagram', 'Tech Trends India', '@techtrends_in', 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=100&auto=format&fit=crop', 'Connected', 1, 'ig_token_demo_98234', 'comments,mentions,insights', 1420, 84, now.isoformat()),
        ('youtube', 'YouTube', 'Global Desi Creator Hub', '@GlobalDesiHQ', 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=100&auto=format&fit=crop', 'Connected', 1, 'yt_token_demo_55122', 'youtube.force-ssl,read', 3200, 192, now.isoformat()),
        ('twitter', 'X (Twitter)', 'Digital Voices Live', '@digital_voices', 'https://images.unsplash.com/photo-1611605698335-8b1569810432?w=100&auto=format&fit=crop', 'Connected', 1, 'x_token_demo_77301', 'tweet.read,users.read,dm.read', 2150, 143, now.isoformat()),
        ('reddit', 'Reddit', 'r/IndiaDiscussion Mod Team', 'u/safety_bot', 'https://images.unsplash.com/photo-1543269865-cbf427effbad?w=100&auto=format&fit=crop', 'Connected', 1, 'rd_token_demo_44199', 'read,modposts,modmail', 890, 67, now.isoformat()),
        ('facebook', 'Facebook', 'Community Support Page', '@community_help', 'https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=100&auto=format&fit=crop', 'Connected', 1, 'fb_token_demo_11203', 'pages_read_engagement,pages_manage_posts', 620, 29, now.isoformat()),
    ]

    for acc in demo_accounts:
        cursor.execute('''
        INSERT INTO connected_accounts (platform, platform_display_name, account_name, handle, avatar_url, status, is_demo, access_token, scopes, posts_monitored_count, toxic_detected_count, last_sync_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', acc)

    # 3. Seed Realistic Multilingual Content Items
    sample_items = [
        {
            'platform': 'instagram',
            'author_name': 'Aarav Sharma',
            'author_handle': '@aarav_s99',
            'author_avatar': 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'teri maa ki chut tu kutta hai saale kamine, video delete kar',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'hinglish',
            'detected_language_name': 'Hinglish (Romanized Hindi)',
            'toxicity_score': 0.98,
            'is_toxic': 1,
            'confidence_score': 0.98,
            'flagged_categories': json.dumps(['Sexual/Explicit Abuse', 'Hate Speech', 'Harassment', 'Insult', 'Profanity']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.98, 'Sexual/Explicit Abuse': 0.95, 'Harassment': 0.88, 'Hate Speech': 0.85, 'Insult': 0.92, 'Profanity': 0.94, 'Threat': 0.40, 'Discrimination': 0.35, 'Non-toxic/Safe': 0.02}),
            'explanation': "Flagged for Sexual/Explicit Abuse, Hate Speech, and Harassment with 98% severity (98% AI confidence). Flagged linguistic markers include 'chut', 'kutta', 'kamine', 'saale'. Explicit sexual vulgarity and abusive terms detected.",
            'flagged_keywords': json.dumps(['chut', 'kutta', 'kamine', 'saale']),
            'recommended_action': 'Escalate & Submit Platform Report',
            'urgency_level': 'Critical',
            'moderation_status': 'Flagged',
            'days_ago': 0.2
        },
        {
            'platform': 'youtube',
            'author_name': 'Vikram Rathore',
            'author_handle': '@vikram_rathore',
            'author_avatar': 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'भीड़ में बहुत हब्सी मिलेंगे साले, इन सबको सबक सिखाना पड़ेगा',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'hi',
            'detected_language_name': 'Hindi',
            'toxicity_score': 0.94,
            'is_toxic': 1,
            'confidence_score': 0.95,
            'flagged_categories': json.dumps(['Hate Speech', 'Harassment', 'Insult', 'Profanity']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.94, 'Hate Speech': 0.91, 'Harassment': 0.85, 'Insult': 0.88, 'Profanity': 0.80, 'Threat': 0.55, 'Discrimination': 0.72, 'Sexual/Explicit Abuse': 0.20, 'Non-toxic/Safe': 0.06}),
            'explanation': "Flagged for Hate Speech, Harassment, and Insult with 94% severity (95% AI confidence). Flagged linguistic markers include 'हब्सी', 'साले'. Identity-based derogatory slurs identified.",
            'flagged_keywords': json.dumps(['हब्सी', 'साले']),
            'recommended_action': 'Escalate & Submit Platform Report',
            'urgency_level': 'Critical',
            'moderation_status': 'Under Review',
            'days_ago': 0.5
        },
        {
            'platform': 'twitter',
            'author_name': 'Mark Peterson',
            'author_handle': '@markp_2026',
            'author_avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'You are a filthy idiot and I will kill you, piece of shit',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'en',
            'detected_language_name': 'English',
            'toxicity_score': 0.99,
            'is_toxic': 1,
            'confidence_score': 0.99,
            'flagged_categories': json.dumps(['Threat', 'Toxic/Abusive', 'Harassment', 'Insult', 'Profanity']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.99, 'Threat': 0.98, 'Insult': 0.96, 'Profanity': 0.95, 'Harassment': 0.92, 'Hate Speech': 0.35, 'Discrimination': 0.20, 'Sexual/Explicit Abuse': 0.30, 'Non-toxic/Safe': 0.01}),
            'explanation': "Flagged for Threat, Insult, and Profanity with 99% severity (99% AI confidence). Flagged linguistic markers include 'kill', 'idiot', 'shit'. Direct violent threat detected.",
            'flagged_keywords': json.dumps(['kill', 'idiot', 'shit']),
            'recommended_action': 'Escalate & Submit Platform Report',
            'urgency_level': 'Critical',
            'moderation_status': 'Reported',
            'days_ago': 1.1
        },
        {
            'platform': 'instagram',
            'author_name': 'Karthik Raja',
            'author_handle': '@karthik_raja_chennai',
            'author_avatar': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'இப் புண்டா மவனே வீடியோ அளி டி தேவிடியா',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'ta',
            'detected_language_name': 'Tamil',
            'toxicity_score': 0.96,
            'is_toxic': 1,
            'confidence_score': 0.97,
            'flagged_categories': json.dumps(['Sexual/Explicit Abuse', 'Insult', 'Profanity', 'Toxic/Abusive']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.96, 'Sexual/Explicit Abuse': 0.94, 'Insult': 0.90, 'Profanity': 0.88, 'Harassment': 0.75, 'Hate Speech': 0.40, 'Threat': 0.30, 'Discrimination': 0.25, 'Non-toxic/Safe': 0.04}),
            'explanation': "Flagged for Sexual/Explicit Abuse, Insult, and Profanity with 96% severity (97% AI confidence). Flagged markers include 'புண்டா', 'மவனே'. Highly derogatory profanity detected.",
            'flagged_keywords': json.dumps(['புண்டா', 'மவனே']),
            'recommended_action': 'Flag & Restrict Visibility',
            'urgency_level': 'High',
            'moderation_status': 'Flagged',
            'days_ago': 1.4
        },
        {
            'platform': 'reddit',
            'author_name': 'CyberBangalore',
            'author_handle': 'u/blr_mod_watcher',
            'author_avatar': 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'ಸೂಳೆ ಮೂಡೆ ಅವ್ಳು ಕಾಂಗ್ರೆಸ್ ಸೂಪರ್ ಕಾಮಿಡಿ ಪೀಸಗಳು',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'kn',
            'detected_language_name': 'Kannada',
            'toxicity_score': 0.95,
            'is_toxic': 1,
            'confidence_score': 0.96,
            'flagged_categories': json.dumps(['Sexual/Explicit Abuse', 'Insult', 'Harassment']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.95, 'Sexual/Explicit Abuse': 0.92, 'Insult': 0.89, 'Harassment': 0.84, 'Profanity': 0.80, 'Hate Speech': 0.50, 'Threat': 0.25, 'Discrimination': 0.20, 'Non-toxic/Safe': 0.05}),
            'explanation': "Flagged for Sexual/Explicit Abuse and Insult with 95% severity (96% AI confidence). Offending Kannada slur 'ಸೂಳೆ' detected.",
            'flagged_keywords': json.dumps(['ಸೂಳೆ']),
            'recommended_action': 'Flag & Restrict Visibility',
            'urgency_level': 'High',
            'moderation_status': 'Under Review',
            'days_ago': 1.8
        },
        {
            'platform': 'youtube',
            'author_name': 'Sunita Deshmukh',
            'author_handle': '@sunita_d',
            'author_avatar': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'अरे मूर्खा, तुला काय समजतंय? तोंड बंद ठेव नाहीतर महागात पडेल',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'mr',
            'detected_language_name': 'Marathi',
            'toxicity_score': 0.78,
            'is_toxic': 1,
            'confidence_score': 0.86,
            'flagged_categories': json.dumps(['Insult', 'Harassment']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.78, 'Insult': 0.82, 'Harassment': 0.74, 'Profanity': 0.65, 'Threat': 0.45, 'Hate Speech': 0.25, 'Discrimination': 0.20, 'Sexual/Explicit Abuse': 0.15, 'Non-toxic/Safe': 0.22}),
            'explanation': "Flagged for Insult and Harassment with 78% severity (86% AI confidence). Contains aggressive verbal intimidation in Marathi.",
            'flagged_keywords': json.dumps(['मूर्खा']),
            'recommended_action': 'Flag & Restrict Visibility',
            'urgency_level': 'High',
            'moderation_status': 'Flagged',
            'days_ago': 2.1
        },
        {
            'platform': 'facebook',
            'author_name': 'Ramesh Kumar',
            'author_handle': '@ramesh_hyd',
            'author_avatar': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'విడు ఈపాటికి ఎంత మంది అమ్మయిలని దేగిండో వాడిని పట్టుకోండి',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'te',
            'detected_language_name': 'Telugu',
            'toxicity_score': 0.89,
            'is_toxic': 1,
            'confidence_score': 0.91,
            'flagged_categories': json.dumps(['Sexual/Explicit Abuse', 'Insult']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.89, 'Sexual/Explicit Abuse': 0.88, 'Insult': 0.82, 'Profanity': 0.78, 'Harassment': 0.70, 'Hate Speech': 0.30, 'Threat': 0.35, 'Discrimination': 0.15, 'Non-toxic/Safe': 0.11}),
            'explanation': "Flagged for Sexual/Explicit Abuse with 89% severity (91% AI confidence). Explicit vulgarity detected in Telugu.",
            'flagged_keywords': json.dumps(['దేగిండో']),
            'recommended_action': 'Escalate & Submit Platform Report',
            'urgency_level': 'Critical',
            'moderation_status': 'Reported',
            'days_ago': 2.3
        },
        {
            'platform': 'youtube',
            'author_name': 'Kochi Techies',
            'author_handle': '@kochi_tech',
            'author_avatar': 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'ഈ മൈരേ ഇവിടെ വന്നിരുന്ന് വെറുതെ വർത്തമാനം പറയണ്ട പോടാ',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'ml',
            'detected_language_name': 'Malayalam',
            'toxicity_score': 0.87,
            'is_toxic': 1,
            'confidence_score': 0.90,
            'flagged_categories': json.dumps(['Profanity', 'Insult', 'Harassment']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.87, 'Profanity': 0.86, 'Insult': 0.84, 'Harassment': 0.72, 'Sexual/Explicit Abuse': 0.35, 'Hate Speech': 0.25, 'Threat': 0.20, 'Discrimination': 0.15, 'Non-toxic/Safe': 0.13}),
            'explanation': "Flagged for Profanity and Insult with 87% severity (90% AI confidence). Malayalam vulgar cuss term 'മൈരേ' detected.",
            'flagged_keywords': json.dumps(['മൈരേ']),
            'recommended_action': 'Flag & Restrict Visibility',
            'urgency_level': 'High',
            'moderation_status': 'Flagged',
            'days_ago': 2.5
        },
        {
            'platform': 'instagram',
            'author_name': 'Ananya Verma',
            'author_handle': '@ananya_v',
            'author_avatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'Love this initiative! Such positive energy and wonderful content.',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'en',
            'detected_language_name': 'English',
            'toxicity_score': 0.02,
            'is_toxic': 0,
            'confidence_score': 0.98,
            'flagged_categories': json.dumps(['Non-toxic/Safe']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.02, 'Non-toxic/Safe': 0.98, 'Insult': 0.01, 'Profanity': 0.01, 'Threat': 0.01, 'Harassment': 0.01, 'Hate Speech': 0.01, 'Discrimination': 0.01, 'Sexual/Explicit Abuse': 0.01}),
            'explanation': "Content is classified as Safe / Non-toxic (98% confidence). The text adheres to platform community standards with no abusive or threatening markers detected.",
            'flagged_keywords': json.dumps([]),
            'recommended_action': 'Allow / Approved (Safe)',
            'urgency_level': 'Low',
            'moderation_status': 'Safe',
            'days_ago': 3.0
        },
        {
            'platform': 'youtube',
            'author_name': 'Devendra Joshi',
            'author_handle': '@joshi_dev',
            'author_avatar': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'नमस्ते सर, बहुत ज्ञानवर्धक वीडियो था। धन्यवाद मार्गदर्शन के लिए।',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'hi',
            'detected_language_name': 'Hindi',
            'toxicity_score': 0.01,
            'is_toxic': 0,
            'confidence_score': 0.99,
            'flagged_categories': json.dumps(['Non-toxic/Safe']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.01, 'Non-toxic/Safe': 0.99, 'Insult': 0.01, 'Profanity': 0.01, 'Threat': 0.01, 'Harassment': 0.01, 'Hate Speech': 0.01, 'Discrimination': 0.01, 'Sexual/Explicit Abuse': 0.01}),
            'explanation': "Content is classified as Safe / Non-toxic (99% confidence). The text adheres to platform community standards with no abusive or threatening markers detected.",
            'flagged_keywords': json.dumps([]),
            'recommended_action': 'Allow / Approved (Safe)',
            'urgency_level': 'Low',
            'moderation_status': 'Safe',
            'days_ago': 3.2
        },
        {
            'platform': 'twitter',
            'author_name': 'Simran Kaur',
            'author_handle': '@simran_k',
            'author_avatar': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'Stop attacking women in the tech industry. We demand respect!',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'en',
            'detected_language_name': 'English',
            'toxicity_score': 0.42,
            'is_toxic': 0,
            'confidence_score': 0.78,
            'flagged_categories': json.dumps(['Non-toxic/Safe']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.42, 'Harassment': 0.38, 'Insult': 0.20, 'Threat': 0.15, 'Profanity': 0.10, 'Hate Speech': 0.12, 'Discrimination': 0.18, 'Sexual/Explicit Abuse': 0.05, 'Non-toxic/Safe': 0.58}),
            'explanation': "Borderline sensitivity detected around advocacy phrases. Content represents advocacy and is within acceptable discourse guidelines.",
            'flagged_keywords': json.dumps([]),
            'recommended_action': 'Queue for Moderator Review',
            'urgency_level': 'Medium',
            'moderation_status': 'False Positive',
            'days_ago': 3.5,
            'override': 1,
            'notes': 'Reviewed by moderator: Context is anti-harassment advocacy, marked False Positive.'
        },
        {
            'platform': 'reddit',
            'author_name': 'Rahul Nair',
            'author_handle': 'u/rahul_chem',
            'author_avatar': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop',
            'content_type': 'text',
            'original_text': 'bhai thank you so much for this tutorial, saved my exam preparation completely',
            'media_url': None,
            'ocr_extracted_text': None,
            'detected_language_code': 'hinglish',
            'detected_language_name': 'Hinglish (Romanized Hindi)',
            'toxicity_score': 0.03,
            'is_toxic': 0,
            'confidence_score': 0.97,
            'flagged_categories': json.dumps(['Non-toxic/Safe']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.03, 'Non-toxic/Safe': 0.97, 'Insult': 0.01, 'Profanity': 0.01, 'Threat': 0.01, 'Harassment': 0.01, 'Hate Speech': 0.01, 'Discrimination': 0.01, 'Sexual/Explicit Abuse': 0.01}),
            'explanation': "Content is classified as Safe / Non-toxic (97% confidence). Grateful academic feedback with no toxicity.",
            'flagged_keywords': json.dumps([]),
            'recommended_action': 'Allow / Approved (Safe)',
            'urgency_level': 'Low',
            'moderation_status': 'Safe',
            'days_ago': 4.0
        },
        {
            'platform': 'instagram',
            'author_name': 'MemeFactory India',
            'author_handle': '@memefactory_desi',
            'author_avatar': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=100&auto=format&fit=crop',
            'content_type': 'image',
            'original_text': '[IMAGE MEME] OCR Extracted Text: You are completely worthless and everyone hates you idiot',
            'media_url': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500&auto=format&fit=crop',
            'ocr_extracted_text': 'You are completely worthless and everyone hates you idiot',
            'detected_language_code': 'en',
            'detected_language_name': 'English',
            'toxicity_score': 0.92,
            'is_toxic': 1,
            'confidence_score': 0.94,
            'flagged_categories': json.dumps(['Harassment', 'Insult', 'Toxic/Abusive']),
            'category_scores': json.dumps({'Toxic/Abusive': 0.92, 'Harassment': 0.90, 'Insult': 0.93, 'Profanity': 0.40, 'Hate Speech': 0.30, 'Threat': 0.20, 'Discrimination': 0.15, 'Sexual/Explicit Abuse': 0.10, 'Non-toxic/Safe': 0.08}),
            'explanation': "Image OCR text extracted successfully. Flagged for Harassment and Insult with 92% severity (94% AI confidence). Flagged linguistic markers include 'worthless', 'hates', 'idiot'. Targeted cyberbullying meme.",
            'flagged_keywords': json.dumps(['worthless', 'idiot']),
            'recommended_action': 'Flag & Restrict Visibility',
            'urgency_level': 'High',
            'moderation_status': 'Flagged',
            'days_ago': 4.5
        }
    ]

    for item in sample_items:
        created_time = (now - timedelta(days=item.get('days_ago', 1.0))).isoformat()
        cursor.execute('''
        INSERT INTO content_items (
            platform, author_name, author_handle, author_avatar, content_type,
            original_text, media_url, ocr_extracted_text, detected_language_code,
            detected_language_name, toxicity_score, is_toxic, confidence_score,
            flagged_categories, category_scores, explanation, flagged_keywords,
            recommended_action, urgency_level, moderation_status, moderator_override,
            moderator_notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['platform'], item['author_name'], item['author_handle'], item['author_avatar'],
            item['content_type'], item['original_text'], item['media_url'], item['ocr_extracted_text'],
            item['detected_language_code'], item['detected_language_name'], item['toxicity_score'],
            item['is_toxic'], item['confidence_score'], item['flagged_categories'],
            item['category_scores'], item['explanation'], item['flagged_keywords'],
            item['recommended_action'], item['urgency_level'], item['moderation_status'],
            item.get('override', 0), item.get('notes', None), created_time
        ))

    # 4. Seed Sample Platform Reports
    reports = [
        (3, 'TKT-X-2026-0912', 'twitter', 'Threat / Violent Intimidation', 'Critical', json.dumps({'evidence': 'You are a filthy idiot and I will kill you', 'user': '@markp_2026'}), 'Content Removed', 'Senior AI Safety Moderator'),
        (7, 'TKT-FB-2026-0844', 'facebook', 'Sexual/Explicit Abuse', 'Critical', json.dumps({'evidence': 'విడు ఈపాటికి ఎంత మంది అమ్మయిలని దేగిండో వాడిని పట్టుకోండి', 'user': '@ramesh_hyd'}), 'In Review by Platform', 'Senior AI Safety Moderator'),
        (1, 'TKT-IG-2026-0731', 'instagram', 'Harassment & Abuse', 'High', json.dumps({'evidence': 'teri maa ki chut tu kutta hai saale kamine', 'user': '@aarav_s99'}), 'Submitted', 'Senior AI Safety Moderator'),
    ]

    for rep in reports:
        cursor.execute('''
        INSERT INTO platform_reports (content_item_id, report_ticket_id, platform, violation_category, severity, evidence_payload, platform_report_status, filed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rep)

    # 5. Seed System Settings
    settings = [
        ('safe_threshold', '0.25'),
        ('review_threshold', '0.60'),
        ('flag_threshold', '0.85'),
        ('auto_flag_enabled', 'true'),
        ('active_languages', json.dumps(['en', 'hi', 'hinglish', 'kn', 'ml', 'ta', 'te', 'mr'])),
        ('ocr_engine_enabled', 'true'),
        ('audit_logging', 'true'),
        ('demo_mode', 'true')
    ]

    for key, val in settings:
        cursor.execute('''
        INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)
        ''', (key, val))

    conn.commit()

# Initialize upon module import
init_db()
