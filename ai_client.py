import os, json, re, textwrap
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

def _normalize_text(s):
    return (s or '').lower().strip()

class AIClient:
    def __init__(self):
        self.key = OPENAI_KEY

    def classify_intent(self, lead, offer):
        # Build context
        offer_json = {
            "name": getattr(offer,'name',None),
            "value_props": getattr(offer,'value_props', "[]"),
            "ideal_use_cases": getattr(offer,'ideal_use_cases', "[]"),
            "ideal_industries": getattr(offer,'ideal_industries', "[]")
        }
        lead_json = {
            "name": lead.name,
            "role": lead.role,
            "company": lead.company,
            "industry": lead.industry,
            "location": lead.location,
            "linkedin_bio": lead.linkedin_bio[:1000]
        }
        # If OpenAI key present, call OpenAI ChatCompletion (deterministic, temp=0)
        if self.key:
            try:
                import openai
                openai.api_key = self.key
                system = "You are a strict lead qualification assistant. Return ONLY JSON: {\"intent\":\"High|Medium|Low\",\"explanation\":\"1-2 sentences\"}"
                user = f"Offer: {json.dumps(offer_json)}\\nProspect: {json.dumps(lead_json)}\\nDecide intent."
                resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=[{"role":"system","content":system},{"role":"user","content":user}], temperature=0, max_tokens=120)
                txt = resp.choices[0].message.content.strip()
                # Extract JSON
                m = re.search(r'\\{.*\\}', txt, re.S)
                if m:
                    data = json.loads(m.group(0))
                    # ensure intent normalized
                    data['intent'] = data.get('intent','Medium').title()
                    return {"intent": data['intent'], "explanation": data.get('explanation','')}
            except Exception as e:
                # fallback to internal heuristic
                pass
        # Fallback deterministic heuristic (works offline)
        role = _normalize_text(lead.role)
        industry = _normalize_text(lead.industry)
        bio = _normalize_text(lead.linkedin_bio)
        score = 0
        if any(x in role for x in ['ceo','founder','head of','vp','vice president','director','chief','cto','cmo','president','owner']):
            score += 2
        elif any(x in role for x in ['manager','lead','principal','senior','growth','product','bd','business development','account executive']):
            score += 1
        # industry match with offer's ideal_industries text
        ideal = ''.join(getattr(offer,'ideal_industries') or '')
        ideal = _normalize_text(ideal)
        if industry and industry in ideal:
            score += 2
        elif industry and any(tok in ideal for tok in industry.split()[:2]):
            score += 1
        if 'hiring' in bio or 'outreach' in bio or 'sales' in bio:
            score += 1
        # Map to label
        if score >=3:
            return {"intent":"High","explanation":"Heuristic: strong role/industry/bio signals."}
        elif score==2:
            return {"intent":"Medium","explanation":"Heuristic: some fit but not strong."}
        else:
            return {"intent":"Low","explanation":"Heuristic: limited signals in role/industry/bio."}
