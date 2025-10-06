from flask import Flask, request, jsonify, send_file, Response
from db import db, init_db
from models import Offer, Lead, ScoreResult
from scoring import ScoringService
from io import StringIO
import csv, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
scorer = ScoringService()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status":"ok"})

@app.route('/offer', methods=['POST'])
def create_offer():
    data = request.get_json(force=True)
    if not data or 'name' not in data:
        return jsonify({"error":"name is required"}), 400
    offer = Offer.from_dict(data)
    db.session.add(offer)
    db.session.commit()
    return jsonify(offer.to_dict()), 201

@app.route('/leads/upload', methods=['POST'])
def upload_leads():
    if 'file' not in request.files:
        return jsonify({"error":"file is required"}), 400
    f = request.files['file']
    text = f.stream.read().decode('utf-8')
    reader = csv.DictReader(StringIO(text))
    required = ['name','role','company','industry','location','linkedin_bio']
    ingested = 0
    errors = []
    for i,row in enumerate(reader, start=1):
        # normalize keys (lower)
        row = {k.strip().lower(): (v.strip() if v is not None else '') for k,v in row.items()}
        if not all(k in row for k in required):
            errors.append({"row":i,"error":"missing required columns"})
            continue
        lead = Lead.from_dict(row)
        db.session.add(lead)
        ingested += 1
    db.session.commit()
    return jsonify({"ingested":ingested,"errors":errors})

@app.route('/score', methods=['POST'])
def run_score():
    # score all leads against latest offer
    offer = Offer.query.order_by(Offer.created_at.desc()).first()
    if not offer:
        return jsonify({"error":"no offer found; create an offer first"}), 400
    leads = Lead.query.all()
    results = scorer.score_leads(leads, offer)
    # return first 25 results
    return jsonify({"scored": len(results), "results": [r.to_dict() for r in results[:25]]})

@app.route('/results', methods=['GET'])
def get_results():
    offer_id = request.args.get('offerId', None)
    q = ScoreResult.query.join(Lead).order_by(ScoreResult.final_score.desc())
    rows = q.all()
    return jsonify([r.to_dict_with_lead() for r in rows])

@app.route('/results/csv', methods=['GET'])
def results_csv():
    rows = ScoreResult.query.join(Lead).order_by(ScoreResult.final_score.desc()).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['id','name','role','company','industry','intent','score','reasoning'])
    for r in rows:
        lead = Lead.query.get(r.lead_id)
        writer.writerow([r.id, lead.name, lead.role, lead.company, lead.industry, r.intent, r.final_score, r.reasoning])
    si.seek(0)
    return Response(si.getvalue(), mimetype='text/csv', headers={ 'Content-Disposition': 'attachment; filename=results.csv' })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
