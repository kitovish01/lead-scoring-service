from db import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import json

class Offer(db.Model):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    value_props = Column(Text)
    ideal_use_cases = Column(Text)
    ideal_industries = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def from_dict(d):
        o = Offer()
        o.name = d.get('name')
        o.value_props = json.dumps(d.get('value_props', []))
        o.ideal_use_cases = json.dumps(d.get('ideal_use_cases', []))
        o.ideal_industries = json.dumps(d.get('ideal_industries', []))
        return o

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value_props": json.loads(self.value_props or "[]"),
            "ideal_use_cases": json.loads(self.ideal_use_cases or "[]"),
            "ideal_industries": json.loads(self.ideal_industries or "[]"),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Lead(db.Model):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    role = Column(String(255))
    company = Column(String(255))
    industry = Column(String(255))
    location = Column(String(255))
    linkedin_bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def from_dict(d):
        l = Lead()
        l.name = d.get('name') or ''
        l.role = d.get('role') or ''
        l.company = d.get('company') or ''
        l.industry = d.get('industry') or ''
        l.location = d.get('location') or ''
        l.linkedin_bio = d.get('linkedin_bio') or ''
        return l

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "company": self.company,
            "industry": self.industry,
            "location": self.location,
            "linkedin_bio": self.linkedin_bio,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ScoreResult(db.Model):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, nullable=False)
    offer_id = Column(Integer, nullable=True)
    rule_score = Column(Integer, default=0)
    ai_label = Column(String(20))
    ai_points = Column(Integer, default=0)
    final_score = Column(Integer, default=0)
    intent = Column(String(20))
    reasoning = Column(Text)
    scored_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "rule_score": self.rule_score,
            "ai_label": self.ai_label,
            "ai_points": self.ai_points,
            "final_score": self.final_score,
            "intent": self.intent,
            "reasoning": self.reasoning,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None
        }

    def to_dict_with_lead(self):
        lead = Lead.query.get(self.lead_id)
        ld = lead.to_dict() if lead else {}
        base = self.to_dict()
        base.update({
            "name": ld.get('name'),
            "role": ld.get('role'),
            "company": ld.get('company'),
            "industry": ld.get('industry'),
        })
        return base
