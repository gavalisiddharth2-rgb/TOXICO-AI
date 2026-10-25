"""
Explainability & Attribution Engine
Provides clear, human-understandable explanations for AI moderation decisions.
Highlights offending keywords/phrases, computes token-level contributions,
and generates structured rationale with human-in-the-loop disclaimers.
"""

import re
from typing import Dict, Any, List

AI_DISCLAIMER = (
    "AI-generated prediction. This assessment assists human moderators and should be "
    "verified by a human moderator before taking punitive or legal enforcement actions."
)

class ExplainabilityEngine:
    def __init__(self):
        pass

    def explain(
        self,
        original_text: str,
        cleaned_text: str,
        detected_lang: str,
        overall_score: float,
        is_toxic: bool,
        confidence: float,
        flagged_categories: List[str],
        category_scores: Dict[str, float],
        tokens: List[str]
    ) -> Dict[str, Any]:
        """
        Generates human-readable reasoning, highlights offending tokens,
        and constructs transparency metadata.
        """
        if not original_text or not original_text.strip():
            return {
                'explanation': 'No content provided for analysis.',
                'flagged_keywords': [],
                'highlighted_text': '',
                'disclaimer': AI_DISCLAIMER
            }

        # 1. Identify offending keywords/tokens
        from backend.app.ml.toxicity_classifier import CATEGORY_LEXICONS
        
        found_keywords = set()
        clean_lower = original_text.lower()

        # Scan for category-specific keywords
        for cat, meta in CATEGORY_LEXICONS.items():
            for kw in meta['keywords']:
                # Word boundary match
                pattern = r'(?<!\w)' + re.escape(kw) + r'(?!\w)'
                if re.search(pattern, clean_lower):
                    found_keywords.add(kw)

        # Also check high-frequency abusive tokens in our tokens list
        abusive_stems = {
            'fuck', 'shit', 'bitch', 'asshole', 'kill', 'die', 'murder', 'idiot',
            'moron', 'kutta', 'kamina', 'saale', 'bewakoof', 'chutiya', 'chod',
            'bhenchod', 'madarchod', 'lund', 'chut', 'randi', 'gaandu', 'harami',
            'terrorist', 'சூಳೆ', 'ಮೈರೇ', 'പുണ്ട', 'தேவிடியா', 'దేగిండో'
        }
        for token in tokens:
            if token in abusive_stems:
                found_keywords.add(token)

        flagged_list = sorted(list(found_keywords))

        # 2. Build plain-English explanation
        explanation = self._build_narrative(
            is_toxic=is_toxic,
            overall_score=overall_score,
            confidence=confidence,
            categories=flagged_categories,
            flagged_list=flagged_list,
            lang=detected_lang
        )

        # 3. Create highlighted HTML preview for UI
        highlighted_text = self._highlight_text(original_text, flagged_list)

        return {
            'explanation': explanation,
            'flagged_keywords': flagged_list,
            'highlighted_text': highlighted_text,
            'disclaimer': AI_DISCLAIMER,
            'audit_summary': f"AI evaluated {len(tokens)} tokens in {detected_lang.upper()}. Severity: {int(overall_score * 100)}%."
        }

    def _build_narrative(
        self,
        is_toxic: bool,
        overall_score: float,
        confidence: float,
        categories: List[str],
        flagged_list: List[str],
        lang: str
    ) -> str:
        """Constructs concise, natural explanation."""
        if not is_toxic:
            return (
                f"Content is classified as Safe / Non-toxic ({int(confidence * 100)}% confidence). "
                "The text adheres to platform community standards with no abusive or threatening markers detected."
            )

        cat_names = [c for c in categories if c != 'Non-toxic/Safe']
        cat_str = ", ".join(cat_names[:3]) if cat_names else "Toxic/Abusive"
        
        kw_snippet = ""
        if flagged_list:
            display_kws = [f"'{kw}'" for kw in flagged_list[:3]]
            kw_snippet = f" Flagged linguistic markers include {', '.join(display_kws)}."

        # Specific category guidance
        specific_note = ""
        if 'Threat' in cat_names:
            specific_note = " Direct violent intent or physical intimidation was identified."
        elif 'Sexual/Explicit Abuse' in cat_names:
            specific_note = " Explicit sexual vulgarity or non-consensual abusive terms were detected."
        elif 'Hate Speech' in cat_names:
            specific_note = " Targeted hostility or identity/community slurs were identified."
        elif 'Harassment' in cat_names:
            specific_note = " Targeted bullying, demeaning remarks, or harassment patterns detected."

        return (
            f"Flagged for {cat_str} with {int(overall_score * 100)}% severity ({int(confidence * 100)}% AI confidence).{kw_snippet}{specific_note} "
            "Requires human review before moderation action."
        )

    def _highlight_text(self, text: str, flagged_list: List[str]) -> str:
        """Surrounds detected keywords with <mark class='flagged-token'> tags for UI."""
        if not flagged_list:
            return text

        escaped_text = text
        for kw in flagged_list:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            escaped_text = pattern.sub(f"<mark class='flagged-token' title='Flagged token'>{kw}</mark>", escaped_text)
        return escaped_text

explainability_engine = ExplainabilityEngine()
