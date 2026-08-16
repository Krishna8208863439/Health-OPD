import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, Prediction, ModelMetrics
from services.predictor import prediction_service
from services.pdf_generator import generate_prediction_pdf

api_bp = Blueprint('api_bp', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'ml', 'models')

# =========================================================================
# 1. PREDICTION ENDPOINTS (PHASE 6)
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
# 2. PREDICTIONS HISTORY & MANAGEMENT (PHASE 7)
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
        # Search by ID or disease
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
    # Attach matching feature importance
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
    current_app.logger.info(f"Deleted prediction record ID: {pred_id}")
    return jsonify({"success": True, "message": f"Prediction #{pred_id} deleted successfully"}), 200


# =========================================================================
# 3. DASHBOARD AGGREGATES API (PHASE 7)
# =========================================================================

@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    total_predictions = Prediction.query.count()
    diabetes_count = Prediction.query.filter_by(disease="diabetes").count()
    heart_count = Prediction.query.filter_by(disease="heart").count()

    low_risk = Prediction.query.filter_by(risk_level="Low").count()
    moderate_risk = Prediction.query.filter_by(risk_level="Moderate").count()
    high_risk = Prediction.query.filter_by(risk_level="High").count()

    # Calculate average risk probability
    all_preds = Prediction.query.all()
    avg_risk = round(sum(p.risk_probability for p in all_preds) / max(total_predictions, 1) * 100, 2)

    # Recent 5 predictions
    recent = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()

    # Timeline Trend (last 7 days counts / samples)
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
        "risk_distribution": {
            "Low": low_risk,
            "Moderate": moderate_risk,
            "High": high_risk
        },
        "disease_distribution": {
            "diabetes": diabetes_count,
            "heart": heart_count
        },
        "recent_predictions": [p.to_dict() for p in recent],
        "trend_data": trend_data
    }), 200


# =========================================================================
# 4. MODEL METRICS & EXPLAINABILITY (PHASE 7)
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
        return jsonify({"error": "Bad request", "message": f"Unsupported disease '{disease}'. Choose 'diabetes' or 'heart'."}), 400

    fi_data = prediction_service.feature_importances.get(disease_clean)
    if not fi_data:
        # Fallback to direct file read if not cached
        file_path = os.path.join(MODELS_DIR, f"{disease_clean}_feature_importance.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                fi_data = json.load(f)

    if not fi_data:
        return jsonify({"error": "Not found", "message": f"Feature importance artifact for '{disease_clean}' not available."}), 404

    return jsonify(fi_data), 200


# =========================================================================
# 5. PDF REPORT GENERATION ENDPOINT (PHASE 8)
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
        current_app.logger.info(f"Generated PDF report for prediction #{prediction_id}")
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"HealthPredict_Report_{record.disease.upper()}_{record.id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.exception(f"Error generating PDF report for #{prediction_id}: {str(e)}")
        return jsonify({"error": "PDF Generation Failed", "message": str(e)}), 500
