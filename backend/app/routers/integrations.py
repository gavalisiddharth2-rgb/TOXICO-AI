"""
Social Media Integrations Router
Manages connected accounts (Instagram, YouTube, X, Reddit, Facebook),
OAuth configuration, Demo/Mock mode streams, and simulated multi-platform data feeds.
"""

import json
from datetime import datetime
from fastapi import APIRouter, HTTPException

from backend.app.database import get_db_connection
from backend.app.models.schemas import ConnectAccountRequest
from backend.app.ml.pipeline import pipeline

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

# Platform metadata
PLATFORM_INFO = {
    'instagram': {'name': 'Instagram', 'icon': 'instagram', 'color': '#E1306C', 'scopes': 'comments,mentions,insights'},
    'youtube': {'name': 'YouTube', 'icon': 'youtube', 'color': '#FF0000', 'scopes': 'youtube.force-ssl,read'},
    'twitter': {'name': 'X (Twitter)', 'icon': 'twitter', 'color': '#1DA1F2', 'scopes': 'tweet.read,users.read'},
    'reddit': {'name': 'Reddit', 'icon': 'reddit', 'color': '#FF4500', 'scopes': 'read,modposts,modmail'},
    'facebook': {'name': 'Facebook', 'icon': 'facebook', 'color': '#1877F2', 'scopes': 'pages_read_engagement,pages_manage_posts'}
}

# Rich multi-lingual test samples for immediate one-click testing
DEMO_SAMPLES = [
    {
        'id': 'sample-1',
        'language': 'Hindi',
        'script': 'Devanagari',
        'type': 'Toxic / Abusive',
        'platform': 'instagram',
        'text': 'भीड़ में बहुत हब्सी मिलेंगे साले बेवकूफ, अपनी शक्ल देखी है कभी?',
        'author': '@rohit_sharma_9',
        'desc': 'Devanagari hate slur and insult directed at individuals'
    },
    {
        'id': 'sample-2',
        'language': 'Hinglish',
        'script': 'Latin / Transliterated',
        'type': 'Sexual/Explicit Abuse',
        'platform': 'youtube',
        'text': 'teri maa ki chut tu kutta hai saale kamine gaandu',
        'author': '@anon_troll_404',
        'desc': 'Common Romanized Hindi abusive cuss words from social comments'
    },
    {
        'id': 'sample-3',
        'language': 'English',
        'script': 'Latin',
        'type': 'Violent Threat',
        'platform': 'twitter',
        'text': 'You are a disgusting idiot and I will track you down and kill you asshole',
        'author': '@dark_venom_22',
        'desc': 'Direct violent intimidation and cyberbullying'
    },
    {
        'id': 'sample-4',
        'language': 'Kannada',
        'script': 'Kannada',
        'type': 'Severe Slur',
        'platform': 'reddit',
        'text': 'ಸೂಳೆ ಮೂಡೆ ಅವ್ಳು ಕಾಂಗ್ರೆಸ್ ಸೂಪರ್ ಕಾಮಿಡಿ ಪೀಸಗಳು',
        'author': 'u/kannada_critic',
        'desc': 'Gender-based slur in native Kannada script'
    },
    {
        'id': 'sample-5',
        'language': 'Tamil',
        'script': 'Tamil',
        'type': 'Vulgar Abuse',
        'platform': 'youtube',
        'text': 'இப் புண்டா மவனே வீடியோ அளி டி தேவிடியா',
        'author': '@tamil_king_007',
        'desc': 'Extremely profane Tamil abusive comment'
    },
    {
        'id': 'sample-6',
        'language': 'Telugu',
        'script': 'Telugu',
        'type': 'Sexual Abuse',
        'platform': 'facebook',
        'text': 'విడు ఈపాటికి ఎంత మంది అమ్మయిలని దేగిండో వాడిని పట్టుకోండి',
        'author': '@telugu_warrior',
        'desc': 'Derogatory sexualized comment in Telugu script'
    },
    {
        'id': 'sample-7',
        'language': 'Marathi',
        'script': 'Devanagari',
        'type': 'Harassment / Insult',
        'platform': 'instagram',
        'text': 'अरे मूर्खा, तुला काय समजतंय? तोंड बंद ठेव नाहीतर महागात पडेल',
        'author': '@mumbai_bhai_88',
        'desc': 'Aggressive Marathi verbal intimidation'
    },
    {
        'id': 'sample-8',
        'language': 'Malayalam',
        'script': 'Malayalam',
        'type': 'Profanity',
        'platform': 'reddit',
        'text': 'ഈ മൈരേ ഇവിടെ വന്നിരുന്ന് വെറുതെ വർത്തമാനം പറയണ്ട പോടാ',
        'author': 'u/kerala_user_9',
        'desc': 'Malayalam vulgar cuss language'
    },
    {
        'id': 'sample-9',
        'language': 'Hindi',
        'script': 'Devanagari',
        'type': 'Safe / Positive',
        'platform': 'youtube',
        'text': 'नमस्ते सर, आपका वीडियो देखकर बहुत कुछ सीखने को मिला। आपका बहुत बहुत धन्यवाद!',
        'author': '@priya_learns',
        'desc': 'Constructive educational appreciation in Hindi'
    },
    {
        'id': 'sample-10',
        'language': 'Hinglish',
        'script': 'Latin / Transliterated',
        'type': 'Safe / Positive',
        'platform': 'instagram',
        'text': 'bhai thank you so much for this amazing recipe, meri family ko bahut pasand aaya!',
        'author': '@cooking_with_sam',
        'desc': 'Warm cooking feedback in Romanized Hindi'
    },
    {
        'id': 'sample-11',
        'language': 'English',
        'script': 'Latin',
        'type': 'Safe / Constructive',
        'platform': 'twitter',
        'text': 'I disagree with your policy proposal, but appreciate the thoughtful explanation and civil discourse.',
        'author': '@pol_researcher',
        'desc': 'Civil debate within community guidelines'
    }
]

@router.get("/accounts")
def list_connected_accounts():
    """Returns all configured social media accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM connected_accounts ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {'accounts': rows}

@router.post("/connect")
def connect_account(payload: ConnectAccountRequest):
    """Simulates connecting a new social platform via OAuth/Demo Mode."""
    conn = get_db_connection()
    cursor = conn.cursor()

    info = PLATFORM_INFO.get(payload.platform.lower(), {
        'name': payload.platform.capitalize(),
        'scopes': 'read,write'
    })

    now_iso = datetime.utcnow().isoformat()
    token = f"{payload.platform[:2]}_live_oauth_token_{int(datetime.utcnow().timestamp())}"

    cursor.execute('''
    INSERT INTO connected_accounts (
        platform, platform_display_name, account_name, handle, avatar_url,
        status, is_demo, access_token, scopes, posts_monitored_count, toxic_detected_count, last_sync_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
    ''', (
        payload.platform.lower(), info['name'], payload.account_name, payload.handle,
        'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop',
        'Connected', 1 if payload.is_demo else 0, token, info['scopes'], now_iso
    ))

    acc_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        'success': True,
        'account_id': acc_id,
        'message': f"Successfully connected {info['name']} account {payload.handle}."
    }

@router.post("/disconnect/{account_id}")
def disconnect_account(account_id: int):
    """Disconnects or removes a social account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM connected_accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()
    return {'success': True, 'message': 'Account disconnected successfully.'}

@router.get("/demo-samples")
def get_demo_samples():
    """Provides ready-to-test multilingual sample posts and comments."""
    return {'samples': DEMO_SAMPLES}

@router.post("/sync-stream")
async def sync_stream():
    """
    Simulates fetching a fresh stream of 4 multilingual comments from connected social accounts,
    automatically running them through the pipeline, updating metrics, and queuing flagged items.
    """
    stream_candidates = [
        ('instagram', '@user_rohit45', 'Rude Troll', 'kutta saala besharam, teri aukat nahi hai idhar aane ki', 'hinglish'),
        ('youtube', '@vikas_tech', 'Vikas Rao', 'Super explanation sir, thank you very much for this video!', 'en'),
        ('twitter', '@angry_bot9', 'Anonymous Bot', 'I swear I will find your address and finish you off asshole', 'en'),
        ('reddit', 'u/desi_memer', 'Desi Memer', 'சூಪರ್ ಕಾಮಿಡಿ ಭ್ರಷ್ಟ ಕಾಂಗ್ರೆಸ್ ಸೂಳೆ ಮೂಡೆ', 'kn')
    ]

    added_items = []
    conn = get_db_connection()
    cursor = conn.cursor()

    for platform_id, handle, name, text, expected_lang in stream_candidates:
        analysis = await pipeline.analyze_text(text)
        tox = analysis['toxicity']
        decision = analysis['decision']
        lang = analysis['language']
        explain = analysis['explainability']

        cursor.execute('''
        INSERT INTO content_items (
            platform, author_name, author_handle, author_avatar, content_type,
            original_text, detected_language_code, detected_language_name,
            toxicity_score, is_toxic, confidence_score, flagged_categories,
            category_scores, explanation, flagged_keywords, recommended_action,
            urgency_level, moderation_status
        ) VALUES (?, ?, ?, ?, 'text', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            platform_id, name, handle,
            'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop',
            text, lang['language_code'], lang['language_name'],
            tox['overall_score'], 1 if tox['is_toxic'] else 0, tox['confidence'],
            json.dumps(tox['flagged_categories']), json.dumps(tox['category_scores']),
            explain['explanation'], json.dumps(explain['flagged_keywords']),
            decision['recommended_action'], decision['urgency_level'],
            decision['recommended_status']
        ))

        added_items.append({
            'id': cursor.lastrowid,
            'platform': platform_id,
            'text': text,
            'toxicity': tox['percentage'],
            'is_toxic': tox['is_toxic'],
            'language': lang['language_name']
        })

    # Update account monitor counts
    cursor.execute("UPDATE connected_accounts SET posts_monitored_count = posts_monitored_count + 4, last_sync_at = ?", (datetime.utcnow().isoformat(),))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'synced_count': len(added_items),
        'items': added_items,
        'message': f"Fetched and processed {len(added_items)} new social items across connected platforms."
    }
