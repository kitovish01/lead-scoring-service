import re, json
def compute_role_score(role):
    if not role: return 0
    r = role.lower()
    decision = ['ceo','founder','co-founder','cofounder','head of','vp','vice president','director','chief','cto','cmo','president','owner','managing director']
    influencer = ['manager','lead','principal','senior','staff','growth','product','bd','business development','account executive','sales']
    for d in decision:
        if d in r:
            return 20
    for inf in influencer:
        if inf in r:
            return 10
    return 0

def _norm(s):
    return (s or '').lower().strip()

def compute_industry_score(lead_industry, offer):
    try:
        ideal = json.loads(offer.ideal_industries or "[]")
    except Exception:
        ideal = []
    li = _norm(lead_industry)
    if not li:
        return 0
    for ind in ideal:
        if _norm(ind) == li:
            return 20
    # token overlap
    lset = set(li.split())
    for ind in ideal:
        if lset & set(_norm(ind).split()):
            return 10
    return 0

def compute_completeness_score(lead):
    fields = [lead.name, lead.role, lead.company, lead.industry, lead.location, lead.linkedin_bio]
    return 10 if all((f and str(f).strip()!='') for f in fields) else 0
