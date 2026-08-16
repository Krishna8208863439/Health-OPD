import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease = db.Column(db.String(50), nullable=False, index=True) # e.g. "diabetes", "heart"
    input_data = db.Column(db.JSON, nullable=False) # JSON object of submitted features
    prediction = db.Column(db.Integer, nullable=False) # 0 or 1
    risk_probability = db.Column(db.Float, nullable=False) # 0.0 to 1.0
    risk_level = db.Column(db.String(20), nullable=False) # "Low", "Moderate", "High"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "disease": self.disease,
            "input_data": self.input_data,
            "prediction": self.prediction,
            "risk_probability": round(self.risk_probability, 4),
            "risk_percentage": round(self.risk_probability * 100, 2),
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Prediction id={self.id} disease={self.disease} risk={self.risk_level} prob={self.risk_probability}>"


class ModelMetrics(db.Model):
    __tablename__ = 'model_metrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease = db.Column(db.String(50), nullable=False, index=True) # e.g. "diabetes", "heart"
    model_name = db.Column(db.String(100), nullable=False) # "Logistic Regression", "Random Forest", "Gradient Boosting"
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    roc_auc = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "disease": self.disease,
            "model_name": self.model_name,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "roc_auc": round(self.roc_auc, 4),
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<ModelMetrics id={self.id} disease={self.disease} model={self.model_name} acc={self.accuracy} f1={self.f1_score}>"
