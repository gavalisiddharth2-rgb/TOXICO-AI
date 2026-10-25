"""
Language Detection Engine
Supports automatic identification of Indic scripts (Hindi, Kannada, Malayalam, Tamil, Telugu, Marathi),
Latin script (English, Hinglish / Romanized Hindi), and Code-Mixed text.
Extensible architecture allows easily registering new languages.
"""

import re
from typing import Dict, Any, Tuple

# Common Hinglish lexical markers (phonetic transliterated Roman script)
HINGLISH_MARKERS = {
    'bhai', 'kya', 'nahi', 'nahin', 'nai', 'teri', 'tere', 'mera', 'meri', 'mere',
    'chutiya', 'saale', 'kutta', 'kamina', 'chod', 'chodate', 'chut', 'gaya', 'gayi',
    'wala', 'wali', 'wale', 'tum', 'tumhara', 'aap', 'aapka', 'hum', 'humara',
    'bhot', 'bahut', 'yaar', 'accha', 'achha', 'kuch', 'kare', 'karega', 'kar',
    'raha', 'rahi', 'rahe', 'bc', 'mc', 'bhenchod', 'behenchod', 'madarchod',
    'bhosadike', 'bhosadi', 'lund', 'gand', 'gaand', 'gaandu', 'chutiye', 'lauda',
    'lawde', 'jhaatu', 'harami', 'sharam', 'bakwas', 'pagal', 'chup', 'maro',
    'kisko', 'isko', 'usko', 'sabko', 'kisi', 'karo', 'bolo', 'sun', 'dekho',
    'dekh', 'thik', 'theek', 'hai', 'hain', 'ho', 'hoga', 'hogi', 'paise', 'dost'
}

# Distinctive Marathi lexical markers (Devanagari script)
MARATHI_MARKERS = {
    'आहे', 'नाही', 'कसा', 'तुला', 'मला', 'काय', 'भावा', 'करणार', 'होते', 'आहेत',
    'करायचे', 'नको', 'बघ', 'गेला', 'गेली', 'दाखव', 'मित्रा', 'साहेब', 'छान'
}

# Language metadata dictionary
SUPPORTED_LANGUAGES = {
    'hi': {'name': 'Hindi', 'script': 'Devanagari', 'family': 'Indo-Aryan'},
    'hinglish': {'name': 'Hinglish (Romanized Hindi)', 'script': 'Latin / Transliterated', 'family': 'Indo-Aryan / Code-Mixed'},
    'en': {'name': 'English', 'script': 'Latin', 'family': 'Germanic'},
    'kn': {'name': 'Kannada', 'script': 'Kannada', 'family': 'Dravidian'},
    'ml': {'name': 'Malayalam', 'script': 'Malayalam', 'family': 'Dravidian'},
    'ta': {'name': 'Tamil', 'script': 'Tamil', 'family': 'Dravidian'},
    'te': {'name': 'Telugu', 'script': 'Telugu', 'family': 'Dravidian'},
    'mr': {'name': 'Marathi', 'script': 'Devanagari', 'family': 'Indo-Aryan'},
    'mixed': {'name': 'Code-Mixed / Multilingual', 'script': 'Mixed Scripts', 'family': 'Multi-family'}
}

class LanguageDetector:
    def __init__(self):
        self.languages = SUPPORTED_LANGUAGES.copy()

    def register_language(self, code: str, name: str, script: str, family: str = "Unknown"):
        """Extensible method to dynamically add new language support."""
        self.languages[code] = {'name': name, 'script': script, 'family': family}

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detects language, script, confidence, and code-mixing indicators.
        Preserves original text without mandatory translation.
        """
        if not text or not text.strip():
            return {
                'language_code': 'en',
                'language_name': 'English',
                'script': 'Latin',
                'confidence': 0.5,
                'is_code_mixed': False,
                'details': 'Empty text default'
            }

        text_clean = text.strip()
        words = re.findall(r'\b\w+\b', text_clean.lower())
        total_chars = len(re.sub(r'\s+', '', text_clean))

        # Count character distributions by Unicode blocks
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text_clean))
        kannada_count = len(re.findall(r'[\u0C80-\u0CFF]', text_clean))
        malayalam_count = len(re.findall(r'[\u0D00-\u0D7F]', text_clean))
        tamil_count = len(re.findall(r'[\u0B80-\u0BFF]', text_clean))
        telugu_count = len(re.findall(r'[\u0C00-\u0C7F]', text_clean))
        latin_count = len(re.findall(r'[a-zA-Z]', text_clean))

        script_counts = {
            'devanagari': devanagari_count,
            'kannada': kannada_count,
            'malayalam': malayalam_count,
            'tamil': tamil_count,
            'telugu': telugu_count,
            'latin': latin_count
        }

        # Check for significant Code-Mixing (both Indic script and Latin present)
        indic_total = devanagari_count + kannada_count + malayalam_count + tamil_count + telugu_count
        is_code_mixed = False
        if indic_total > 5 and latin_count > 5:
            is_code_mixed = True

        # 1. Kannada
        if kannada_count > 0 and kannada_count >= (indic_total * 0.7):
            conf = min(0.99, max(0.80, kannada_count / max(1, total_chars)))
            return {
                'language_code': 'kn',
                'language_name': 'Kannada',
                'script': 'Kannada',
                'confidence': round(conf, 2),
                'is_code_mixed': is_code_mixed,
                'details': f'Kannada script detected ({kannada_count} glyphs)'
            }

        # 2. Malayalam
        if malayalam_count > 0 and malayalam_count >= (indic_total * 0.7):
            conf = min(0.99, max(0.80, malayalam_count / max(1, total_chars)))
            return {
                'language_code': 'ml',
                'language_name': 'Malayalam',
                'script': 'Malayalam',
                'confidence': round(conf, 2),
                'is_code_mixed': is_code_mixed,
                'details': f'Malayalam script detected ({malayalam_count} glyphs)'
            }

        # 3. Tamil
        if tamil_count > 0 and tamil_count >= (indic_total * 0.7):
            conf = min(0.99, max(0.80, tamil_count / max(1, total_chars)))
            return {
                'language_code': 'ta',
                'language_name': 'Tamil',
                'script': 'Tamil',
                'confidence': round(conf, 2),
                'is_code_mixed': is_code_mixed,
                'details': f'Tamil script detected ({tamil_count} glyphs)'
            }

        # 4. Telugu
        if telugu_count > 0 and telugu_count >= (indic_total * 0.7):
            conf = min(0.99, max(0.80, telugu_count / max(1, total_chars)))
            return {
                'language_code': 'te',
                'language_name': 'Telugu',
                'script': 'Telugu',
                'confidence': round(conf, 2),
                'is_code_mixed': is_code_mixed,
                'details': f'Telugu script detected ({telugu_count} glyphs)'
            }

        # 5. Devanagari (Hindi vs Marathi)
        if devanagari_count > 0 and devanagari_count >= (indic_total * 0.6):
            # Check for distinctive Marathi character 'ळ' (\u0933) or Marathi vocabulary
            has_marathi_char = '\u0933' in text_clean
            marathi_matches = sum(1 for w in words if w in MARATHI_MARKERS)
            
            if has_marathi_char or marathi_matches >= 2:
                conf = 0.92 if has_marathi_char else 0.86
                return {
                    'language_code': 'mr',
                    'language_name': 'Marathi',
                    'script': 'Devanagari',
                    'confidence': round(conf, 2),
                    'is_code_mixed': is_code_mixed,
                    'details': 'Devanagari script with Marathi lexical markers'
                }
            else:
                conf = min(0.99, max(0.85, devanagari_count / max(1, total_chars)))
                return {
                    'language_code': 'hi',
                    'language_name': 'Hindi',
                    'script': 'Devanagari',
                    'confidence': round(conf, 2),
                    'is_code_mixed': is_code_mixed,
                    'details': f'Devanagari script detected ({devanagari_count} glyphs)'
                }

        # 6. Latin Script -> English vs Hinglish (Transliterated Hindi)
        if latin_count > 0:
            hinglish_matches = [w for w in words if w in HINGLISH_MARKERS]
            hinglish_ratio = len(hinglish_matches) / max(1, len(words))

            if len(hinglish_matches) >= 2 or hinglish_ratio >= 0.20:
                conf = min(0.98, max(0.82, 0.70 + (len(hinglish_matches) * 0.08)))
                return {
                    'language_code': 'hinglish',
                    'language_name': 'Hinglish (Romanized Hindi)',
                    'script': 'Latin / Transliterated',
                    'confidence': round(conf, 2),
                    'is_code_mixed': True,
                    'details': f'Transliterated Hindi words identified ({", ".join(hinglish_matches[:4])})'
                }

            # Otherwise Standard English
            conf = min(0.98, max(0.85, latin_count / max(1, total_chars)))
            return {
                'language_code': 'en',
                'language_name': 'English',
                'script': 'Latin',
                'confidence': round(conf, 2),
                'is_code_mixed': is_code_mixed,
                'details': 'Latin script / English lexicon match'
            }

        # Fallback
        return {
            'language_code': 'en',
            'language_name': 'English',
            'script': 'General',
            'confidence': 0.70,
            'is_code_mixed': False,
            'details': 'Default multilingual analyzer routing'
        }

# Global singleton
language_detector = LanguageDetector()
