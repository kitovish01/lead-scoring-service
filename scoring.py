from models import Lead, ScoreResult
from db import db
from ai_client import AIClient
from utils import compute_role_score, compute_industry_score, compute_completeness_score
import math, time, os

class ScoringService:
    def __init__(self):
        self.ai = AIClient()

    def score_leads(self, leads, offer):
        results = []
        for lead in leads:
            # compute rule score (0-50)
            role_score = compute_role_score(lead.role)
            industry_score = compute_industry_score(lead.industry, offer)
            completeness = compute_completeness_score(lead)
            rule_score = role_score + industry_score + completeness
            # AI layer
            ai_resp = self.ai.classify_intent(lead, offer)
            ai_label = ai_resp.get('intent', 'Medium')
            ai_expl = ai_resp.get('explanation', 'No explanation from AI')
            ai_points = 50 if ai_label=='High' else 30 if ai_label=='Medium' else 10
            final_score = rule_score + ai_points
            if final_score > 100:
                final_score = 100
            sr = ScoreResult(
                lead_id = lead.id,
                offer_id = offer.id if hasattr(offer,'id') else None,
                rule_score = int(rule_score),
                ai_label = ai_label,
                ai_points = ai_points,
                final_score = int(final_score),
                intent = ai_label,
                reasoning = f"Rule: role_score={role_score}, industry_score={industry_score}, completeness={completeness}. AI: {ai_expl}"
            )
            db.session.add(sr)
            db.session.commit()
            results.append(sr)
        return results
