# Lead Scoring Service (Flask) - Ready to run
A simple backend service that implements the assignment:
- POST /offer        -> store offer JSON
- POST /leads/upload -> upload CSV of leads (name,role,company,industry,location,linkedin_bio)
- POST /score        -> run scoring (rule layer + AI layer)
- GET  /results      -> get scored leads (JSON)
- GET  /results/csv  -> download scored leads as CSV
- GET  /health       -> health check

Notes:
- If `OPENAI_API_KEY` environment variable is set, the service will attempt to call OpenAI (deterministic prompt, temperature=0).
- If no API key is provided, the service uses a deterministic internal AI-fallback (simple heuristic) so the project works out-of-the-box.
- SQLite database used: `data.db` inside project folder.

Run locally:
```bash
# create venv (recommended)
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run
export FLASK_APP=app.py
export FLASK_ENV=development
# optional: export OPENAI_API_KEY="sk-..."
flask run --host=0.0.0.0 --port=8080
```

Example usage (replace BASE with http://localhost:8080):
```bash
# create offer
curl -X POST $http://localhost:8080/offer -H "Content-Type: application/json" -d '{
  "name":"AI Outreach Automation",
  "value_props":["24/7 outreach","6x more meetings"],
  "ideal_use_cases":["B2B SaaS mid-market"],
  "ideal_industries":["SaaS","MarTech"]
}'

# upload leads
curl -X POST $http://localhost:8080/leads/upload -F "file=@leads.csv"

# run scoring (scores all leads against the latest offer)
curl -X POST $http://localhost:8080/score

# fetch results
curl $http://localhost:8080/results
```

Project structure included in zip:
```
lead_scoring_service/
├─ app.py
├─ models.py
├─ db.py
├─ scoring.py
├─ ai_client.py
├─ utils.py
├─ requirements.txt
├─ Dockerfile
├─ README.md
├─ run.sh
├─ tests/
│  └─ test_rule_scorer.py
└─ sample_leads.csv
```

