from utils import compute_role_score, compute_industry_score, compute_completeness_score
from types import SimpleNamespace
def test_role_scores():
    assert compute_role_score("CEO") == 20
    assert compute_role_score("Head of Growth") == 20
    assert compute_role_score("Growth Manager") == 10
    assert compute_role_score("Intern") == 0

def test_industry_scores():
    offer = SimpleNamespace(ideal_industries='["SaaS","MarTech"]')
    assert compute_industry_score("SaaS", offer) == 20
    assert compute_industry_score("SaaS Analytics", offer) == 10
    assert compute_industry_score("Healthcare", offer) == 0

def test_completeness():
    lead = SimpleNamespace(name="A", role="R", company="C", industry="I", location="L", linkedin_bio="B")
    assert compute_completeness_score(lead) == 10
    lead2 = SimpleNamespace(name="", role="R", company="C", industry="I", location="L", linkedin_bio="B")
    assert compute_completeness_score(lead2) == 0
