import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, Prediction, ModelMetrics, VitalsLog, MedicineReminder, OPDTicket
from services.predictor import prediction_service
from services.pdf_generator import generate_prediction_pdf
from services.healthcare_service import (
    HOSPITALS_DATABASE, calculate_health_score, DIET_PLANS, process_ai_chat
)

api_bp = Blueprint('api_bp', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'ml', 'models')

# =========================================================================
# 1. PREDICTION ENDPOINTS
# =========================================================================

@api_bp.route('/predict/diabetes', methods=['POST'])
def predict_diabetes():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Bad request", "message": "Invalid JSON body provided"}), 400

    try:
        result = prediction_service.validate_and_predict_diabetes(data)
        current_app.logger.info(f"Diabetes prediction computed: ID={result['id']} Prob={result['risk_probability']} Level={result['risk_level']}")
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.warning(f"Validation error in diabetes prediction: {str(e)}")
        return jsonify({"error": "Validation failed", "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"Error computing diabetes prediction: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "Failed to process diabetes prediction"}), 500


@api_bp.route('/predict/heart', methods=['POST'])
def predict_heart():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Bad request", "message": "Invalid JSON body provided"}), 400

    try:
        result = prediction_service.validate_and_predict_heart(data)
        current_app.logger.info(f"Heart disease prediction computed: ID={result['id']} Prob={result['risk_probability']} Level={result['risk_level']}")
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.warning(f"Validation error in heart prediction: {str(e)}")
        return jsonify({"error": "Validation failed", "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"Error computing heart prediction: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "Failed to process heart disease prediction"}), 500


# =========================================================================
# 2. PREDICTIONS HISTORY & MANAGEMENT
# =========================================================================

@api_bp.route('/predictions', methods=['GET'])
def get_predictions():
    disease_filter = request.args.get('disease', '').strip().lower()
    risk_filter = request.args.get('risk_level', '').strip()
    search = request.args.get('search', '').strip()
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    query = Prediction.query

    if disease_filter:
        query = query.filter(Prediction.disease == disease_filter)
    if risk_filter:
        query = query.filter(Prediction.risk_level == risk_filter)
    if search:
        query = query.filter(
            (Prediction.disease.ilike(f"%{search}%")) |
            (Prediction.risk_level.ilike(f"%{search}%"))
        )

    total_count = query.count()
    records = query.order_by(Prediction.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "predictions": [r.to_dict() for r in records]
    }), 200


@api_bp.route('/predictions/<int:pred_id>', methods=['GET'])
def get_prediction_by_id(pred_id: int):
    record = db.session.get(Prediction, pred_id)
    if not record:
        return jsonify({"error": "Not found", "message": f"Prediction record #{pred_id} does not exist"}), 404

    data = record.to_dict()
    fi = prediction_service.feature_importances.get(record.disease, {}).get('features', [])
    data['feature_importance'] = fi
    data['model_name'] = type(prediction_service.models.get(record.disease, None)).__name__
    data['prediction_label'] = "High Risk / Positive" if record.prediction == 1 else "Low Risk / Negative"
    return jsonify(data), 200


@api_bp.route('/predictions/<int:pred_id>', methods=['DELETE'])
def delete_prediction(pred_id: int):
    record = db.session.get(Prediction, pred_id)
    if not record:
        return jsonify({"error": "Not found", "message": f"Prediction record #{pred_id} does not exist"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True, "message": f"Prediction #{pred_id} deleted successfully"}), 200


# =========================================================================
# 3. DASHBOARD AGGREGATES API
# =========================================================================

@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    total_predictions = Prediction.query.count()
    diabetes_count = Prediction.query.filter_by(disease="diabetes").count()
    heart_count = Prediction.query.filter_by(disease="heart").count()

    low_risk = Prediction.query.filter_by(risk_level="Low").count()
    moderate_risk = Prediction.query.filter_by(risk_level="Moderate").count()
    high_risk = Prediction.query.filter_by(risk_level="High").count()

    all_preds = Prediction.query.all()
    avg_risk = round(sum(p.risk_probability for p in all_preds) / max(total_predictions, 1) * 100, 2)
    recent = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()

    trend_data = []
    for i in range(6, -1, -1):
        day_date = datetime.utcnow().date() - timedelta(days=i)
        next_day = day_date + timedelta(days=1)
        day_preds = Prediction.query.filter(
            Prediction.created_at >= datetime.combine(day_date, datetime.min.time()),
            Prediction.created_at < datetime.combine(next_day, datetime.min.time())
        ).all()
        trend_data.append({
            "date": day_date.strftime("%b %d"),
            "total": len(day_preds),
            "diabetes": sum(1 for p in day_preds if p.disease == "diabetes"),
            "heart": sum(1 for p in day_preds if p.disease == "heart")
        })

    return jsonify({
        "total_predictions": total_predictions,
        "diabetes_predictions": diabetes_count,
        "heart_predictions": heart_count,
        "average_risk_percentage": avg_risk,
        "risk_distribution": {"Low": low_risk, "Moderate": moderate_risk, "High": high_risk},
        "disease_distribution": {"diabetes": diabetes_count, "heart": heart_count},
        "recent_predictions": [p.to_dict() for p in recent],
        "trend_data": trend_data
    }), 200


# =========================================================================
# 4. MODEL METRICS & EXPLAINABILITY
# =========================================================================

@api_bp.route('/model-metrics', methods=['GET'])
def get_model_metrics():
    disease_filter = request.args.get('disease', '').strip().lower()
    query = ModelMetrics.query
    if disease_filter:
        query = query.filter_by(disease=disease_filter)

    records = query.order_by(ModelMetrics.id.asc()).all()
    return jsonify({
        "total": len(records),
        "metrics": [r.to_dict() for r in records]
    }), 200


@api_bp.route('/feature-importance/<disease>', methods=['GET'])
def get_feature_importance(disease: str):
    disease_clean = disease.strip().lower()
    if disease_clean not in ('diabetes', 'heart'):
        return jsonify({"error": "Bad request", "message": f"Unsupported disease '{disease}'."}), 400

    fi_data = prediction_service.feature_importances.get(disease_clean)
    if not fi_data:
        file_path = os.path.join(MODELS_DIR, f"{disease_clean}_feature_importance.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                fi_data = json.load(f)

    if not fi_data:
        return jsonify({"error": "Not found", "message": f"Feature importance artifact for '{disease_clean}' not available."}), 404

    return jsonify(fi_data), 200


# =========================================================================
# 5. PDF REPORT GENERATION ENDPOINT
# =========================================================================

@api_bp.route('/report/<int:prediction_id>', methods=['GET'])
def download_prediction_report(prediction_id: int):
    record = db.session.get(Prediction, prediction_id)
    if not record:
        return jsonify({"error": "Not found", "message": f"Prediction record #{prediction_id} not found"}), 404

    data = record.to_dict()
    data['feature_importance'] = prediction_service.feature_importances.get(record.disease, {}).get('features', [])
    data['model_name'] = type(prediction_service.models.get(record.disease, None)).__name__

    try:
        pdf_buffer = generate_prediction_pdf(data)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"HealthPredict_Report_{record.disease.upper()}_{record.id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.exception(f"Error generating PDF report: {str(e)}")
        return jsonify({"error": "PDF Generation Failed", "message": str(e)}), 500


# =========================================================================
# 6. UNIFIED HEALTHCARE+ ENDPOINTS (HOSPITALS, VITALS, MEDS, CHAT, OPD, DIET, SOS)
# =========================================================================

@api_bp.route('/hospitals', methods=['GET'])
def get_hospitals():
    city = request.args.get('city', '').strip()
    search = request.args.get('search', '').strip().lower()
    
    hospitals = HOSPITALS_DATABASE
    if city:
        hospitals = [h for h in hospitals if h['city'].lower() == city.lower()]
    if search:
        hospitals = [
            h for h in hospitals 
            if search in h['name'].lower() 
            or search in h['city'].lower() 
            or any(search in s.lower() for s in h['specialty'])
        ]
    return jsonify({"total": len(hospitals), "hospitals": hospitals}), 200


@api_bp.route('/vitals', methods=['GET', 'POST'])
def handle_vitals():
    if request.method == 'POST':
        data = request.get_json() or {}
        systolic = int(data.get('systolic', 120))
        diastolic = int(data.get('diastolic', 80))
        heart_rate = int(data.get('heart_rate', 72))
        glucose = float(data.get('glucose', 95))
        spo2 = int(data.get('spo2', 98))
        temp = float(data.get('temperature', 98.6))
        notes = data.get('notes', '')

        score = calculate_health_score(systolic, diastolic, heart_rate, glucose, spo2, temp)
        
        vital = VitalsLog(
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate,
            glucose=glucose,
            spo2=spo2,
            temperature=temp,
            health_score=score,
            notes=notes
        )
        db.session.add(vital)
        db.session.commit()
        return jsonify({"status": "success", "vital": vital.to_dict(), "health_score": score}), 201

    # GET vitals history
    logs = VitalsLog.query.order_by(VitalsLog.created_at.desc()).limit(20).all()
    latest_score = logs[0].health_score if logs else 85
    return jsonify({
        "current_score": latest_score,
        "logs": [l.to_dict() for l in logs]
    }), 200


@api_bp.route('/medicines', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_medicines():
    if request.method == 'GET':
        # Default sample medicines if none in db
        if MedicineReminder.query.count() == 0:
            sample_meds = [
                MedicineReminder(name="Metformin", dosage="500 mg", timing="Morning & Night", meal_instruction="After Meal", stock_count=24, taken_today=True),
                MedicineReminder(name="Atorvastatin", dosage="10 mg", timing="Night", meal_instruction="After Meal", stock_count=18, taken_today=False),
                MedicineReminder(name="Telmisartan", dosage="40 mg", timing="Morning", meal_instruction="Before Meal", stock_count=30, taken_today=True)
            ]
            db.session.add_all(sample_meds)
            db.session.commit()

        meds = MedicineReminder.query.order_by(MedicineReminder.id.asc()).all()
        return jsonify({"medicines": [m.to_dict() for m in meds]}), 200

    elif request.method == 'POST':
        data = request.get_json() or {}
        med = MedicineReminder(
            name=data.get('name', 'Medicine'),
            dosage=data.get('dosage', '500 mg'),
            timing=data.get('timing', 'Morning'),
            meal_instruction=data.get('meal_instruction', 'After Meal'),
            stock_count=int(data.get('stock_count', 30)),
            taken_today=False
        )
        db.session.add(med)
        db.session.commit()
        return jsonify({"status": "success", "medicine": med.to_dict()}), 201

    elif request.method == 'PUT':
        data = request.get_json() or {}
        med_id = data.get('id')
        med = db.session.get(MedicineReminder, med_id)
        if not med:
            return jsonify({"error": "Medicine not found"}), 404

        if 'taken_today' in data:
            med.taken_today = bool(data['taken_today'])
            if med.taken_today and med.stock_count > 0:
                med.stock_count -= 1
        db.session.commit()
        return jsonify({"status": "success", "medicine": med.to_dict()}), 200

    elif request.method == 'DELETE':
        med_id = request.args.get('id', type=int)
        med = db.session.get(MedicineReminder, med_id)
        if med:
            db.session.delete(med)
            db.session.commit()
        return jsonify({"status": "success", "message": "Medicine deleted"}), 200


@api_bp.route('/chat', methods=['POST'])
def handle_chat():
    data = request.get_json() or {}
    user_msg = data.get('message', '')
    if not user_msg:
        return jsonify({"error": "Message required"}), 400
    res = process_ai_chat(user_msg)
    return jsonify(res), 200


@api_bp.route('/opd/tickets', methods=['GET', 'POST'])
def handle_opd():
    if request.method == 'POST':
        data = request.get_json() or {}
        dept = data.get('department', 'General Medicine')
        patient = data.get('patient_name', 'Patient')
        complaint = data.get('chief_complaint', 'General Consultation')
        triage = data.get('triage_level', 'ROUTINE')

        # Compute next token
        last_ticket = OPDTicket.query.filter_by(department=dept).order_by(OPDTicket.id.desc()).first()
        next_tok = (last_ticket.token_number + 1) if last_ticket else 101

        ticket = OPDTicket(
            patient_name=patient,
            department=dept,
            token_number=next_tok,
            triage_level=triage,
            chief_complaint=complaint,
            status="waiting"
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify({"status": "success", "ticket": ticket.to_dict()}), 201

    # GET tickets
    tickets = OPDTicket.query.order_by(OPDTicket.id.desc()).limit(15).all()
    return jsonify({"tickets": [t.to_dict() for t in tickets]}), 200


@api_bp.route('/diet/plans', methods=['GET'])
def get_diet():
    return jsonify({"plans": DIET_PLANS}), 200


@api_bp.route('/sos/trigger', methods=['POST'])
def handle_sos():
    data = request.get_json() or {}
    lat = data.get('lat', '16.7050')
    lng = data.get('lng', '74.2433')
    current_app.logger.warning(f"EMERGENCY SOS TRIGGERED at Lat: {lat}, Lng: {lng}")
    return jsonify({
        "status": "triggered",
        "emergency_contacts": [
            {"service": "National Emergency", "number": "112"},
            {"service": "Ambulance", "number": "108"},
            {"service": "Police", "number": "100"},
            {"service": "Women / Senior Citizen Helpline", "number": "1091"}
        ],
        "coordinates": {"lat": lat, "lng": lng}
    }), 200
