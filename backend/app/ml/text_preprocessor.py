"""
Multilingual Text Preprocessing Pipeline
Preserves the raw content while cleaning, normalizing obfuscations,
extracting social media artifacts, and detecting emoji abuse cues.
"""

import re
import unicodedata
from typing import Dict, Any, List

# Emojis often associated with harassment, hate, vulgarity, or threats
HIGH_RISK_EMOJIS = {
    '🖕': {'name': 'middle_finger', 'category': 'Profanity', 'weight': 0.8},
    '🤬': {'name': 'cursing_face', 'category': 'Toxic/Abusive', 'weight': 0.7},
    '💩': {'name': 'poop', 'category': 'Insult', 'weight': 0.5},
    '🤡': {'name': 'clown', 'category': 'Harassment', 'weight': 0.4},
    '🤮': {'name': 'vomiting', 'category': 'Insult', 'weight': 0.5},
    '🔪': {'name': 'knife', 'category': 'Threat', 'weight': 0.8},
    '🔫': {'name': 'gun', 'category': 'Threat', 'weight': 0.8},
    '💣': {'name': 'bomb', 'category': 'Threat', 'weight': 0.8},
    '☠️': {'name': 'skull', 'category': 'Threat', 'weight': 0.6},
    '💀': {'name': 'skull', 'category': 'Threat', 'weight': 0.5},
    '🐷': {'name': 'pig', 'category': 'Insult', 'weight': 0.6},
    '🐕': {'name': 'dog', 'category': 'Insult', 'weight': 0.4},
    '🐒': {'name': 'monkey', 'category': 'Discrimination', 'weight': 0.7},
}

class TextPreprocessor:
    def __init__(self):
        # Common obfuscation patterns (e.g., f*ck -> fuck, b**ch -> bitch)
        self.obfuscation_map = {
            r'\bf+[\*@#!]+c*k\b': 'fuck',
            r'\bb+[\*@#!]+t*c*h\b': 'bitch',
            r'\bs+[\*@#!]+t\b': 'shit',
            r'\ba+[\*@#!]+h*o*l*e\b': 'asshole',
            r'\bk+[\*@#!]+t*t*a\b': 'kutta',
            r'\bc+h+[\*@#!]+t\b': 'chut',
            r'\bb+[\*@#!]+c+\b': 'bc',
            r'\bm+[\*@#!]+c+\b': 'mc',
        }

    def clean(self, raw_text: str) -> Dict[str, Any]:
        """
        Processes raw text without mutating the original representation.
        Returns cleaned text, tokens, extracted entities, and emoji context.
        """
        if not raw_text:
            return {
                'original': '',
                'cleaned': '',
                'tokens': [],
                'mentions': [],
                'hashtags': [],
                'urls': [],
                'emojis': [],
                'emoji_risk_score': 0.0,
                'char_count': 0,
                'word_count': 0
            }

        original = raw_text
        # Normalize Unicode (NFC)
        normalized = unicodedata.normalize('NFC', original)
        
        # Remove zero-width spaces and control characters
        normalized = re.sub(r'[\u200B-\u200D\uFEFF]', '', normalized)

        # Extract mentions, hashtags, URLs
        mentions = re.findall(r'@\w+', normalized)
        hashtags = re.findall(r'#\w+', normalized)
        urls = re.findall(r'https?://\S+|www\.\S+', normalized)

        # Extract flagged emojis
        detected_emojis = []
        emoji_score = 0.0
        for char in normalized:
            if char in HIGH_RISK_EMOJIS:
                meta = HIGH_RISK_EMOJIS[char]
                detected_emojis.append({'emoji': char, **meta})
                emoji_score = max(emoji_score, meta['weight'])

        # Create cleaned text for NLP models
        cleaned = normalized

        # Replace URLs
        cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', cleaned)
        # Remove excessive repeated characters (e.g., "noooooo" -> "noo", "bheeeen" -> "bheen")
        cleaned = re.sub(r'(.)\1{3,}', r'\1\1', cleaned)

        # De-obfuscate common profanity asterisks
        for pattern, replacement in self.obfuscation_map.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        # Tokenize (supporting Indic letters, alphanumeric)
        tokens = re.findall(r'[\w]+', cleaned.lower(), flags=re.UNICODE)

        return {
            'original': original,
            'cleaned': cleaned.strip(),
            'tokens': tokens,
            'mentions': mentions,
            'hashtags': hashtags,
            'urls': urls,
            'emojis': detected_emojis,
            'emoji_risk_score': emoji_score,
            'char_count': len(original),
            'word_count': len(tokens)
        }

text_preprocessor = TextPreprocessor()
