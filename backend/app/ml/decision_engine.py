"""
Decision & Moderation Recommendation Engine
Translates toxicity scores, category severity, and risk levels into
actionable moderation suggestions for human review.
"""

from typing import Dict, Any, List

class DecisionEngine:
    def __init__(self, safe_thresh: float = 0.25, review_thresh: float = 0.60, flag_thresh: float = 0.85):
        self.safe_threshold = safe_thresh
        self.review_threshold = review_thresh
        self.flag_threshold = flag_thresh

    def update_thresholds(self, safe_thresh: float = None, review_thresh: float = None, flag_thresh: float = None):
        if safe_thresh is not None: self.safe_threshold = safe_thresh
        if review_thresh is not None: self.review_threshold = review_thresh
        if flag_thresh is not None: self.flag_threshold = flag_thresh

    def recommend(
        self,
        overall_score: float,
        is_toxic: bool,
        flagged_categories: List[str],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Determines the appropriate moderation workflow action based on AI assessment.
        Workflow: Safe / Allow -> Queue for Review -> Flag & Restrict -> Escalate & Report
        """
        has_threat = 'Threat' in flagged_categories
        has_sexual = 'Sexual/Explicit Abuse' in flagged_categories
        has_hate = 'Hate Speech' in flagged_categories

        # 1. Critical Urgency: Threats, severe sexual abuse, or > 85% toxicity
        if has_threat or (overall_score >= self.flag_threshold and (has_sexual or has_hate)):
            return {
                'recommended_action': 'Escalate & Submit Platform Report',
                'recommended_status': 'Flagged',
                'urgency_level': 'Critical',
                'severity_badge': 'danger',
                'requires_human_override': True,
                'next_steps': [
                    'Prioritize in moderation queue immediately',
                    'Initiate official platform abuse report',
                    'Consider user account temporary shadow-ban or warning',
                    'Log incident into audit log for compliance'
                ]
            }

        # 2. High Urgency: Toxicity between 60% and 85%
        if overall_score >= self.review_threshold:
            return {
                'recommended_action': 'Flag & Restrict Visibility',
                'recommended_status': 'Flagged',
                'urgency_level': 'High',
                'severity_badge': 'warning',
                'requires_human_override': True,
                'next_steps': [
                    'Apply sensitive content filter / reduce post reach',
                    'Assign to human moderator for validation',
                    'If confirmed, dispatch platform moderation report'
                ]
            }

        # 3. Medium Urgency: Toxicity between 25% and 60% (Ambiguous / Borderline)
        if overall_score >= self.safe_threshold or (is_toxic and confidence < 0.80):
            return {
                'recommended_action': 'Queue for Moderator Review',
                'recommended_status': 'Under Review',
                'urgency_level': 'Medium',
                'severity_badge': 'info',
                'requires_human_override': True,
                'next_steps': [
                    'Leave content visible under active observation',
                    'Allow community moderator to review contextual nuances',
                    'Approve as safe or escalate to flagged'
                ]
            }

        # 4. Low Urgency: Safe content
        return {
            'recommended_action': 'Allow / Approved (Safe)',
            'recommended_status': 'Safe',
            'urgency_level': 'Low',
            'severity_badge': 'success',
            'requires_human_override': False,
            'next_steps': [
                'No action required',
                'Content cleared by automated safety filter'
            ]
        }

decision_engine = DecisionEngine()
