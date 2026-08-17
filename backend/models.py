import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), default="")
    role = db.Column(db.String(50), default="patient")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }


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


class VitalsLog(db.Model):
    __tablename__ = 'vitals_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    systolic = db.Column(db.Integer, nullable=False) # e.g. 120
    diastolic = db.Column(db.Integer, nullable=False) # e.g. 80
    heart_rate = db.Column(db.Integer, nullable=False) # e.g. 72
    glucose = db.Column(db.Float, nullable=False) # e.g. 95
    spo2 = db.Column(db.Integer, default=98, nullable=False) # e.g. 98%
    temperature = db.Column(db.Float, default=98.6, nullable=False) # e.g. 98.6 F
    health_score = db.Column(db.Integer, default=85, nullable=False)
    notes = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "heart_rate": self.heart_rate,
            "glucose": self.glucose,
            "spo2": self.spo2,
            "temperature": self.temperature,
            "health_score": self.health_score,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }


class MedicineReminder(db.Model):
    __tablename__ = 'medicine_reminders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100), nullable=False) # e.g. "500 mg"
    timing = db.Column(db.String(100), nullable=False) # e.g. "Morning & Night"
    meal_instruction = db.Column(db.String(50), default="After Meal") # "Before Meal", "After Meal"
    stock_count = db.Column(db.Integer, default=30)
    taken_today = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dosage": self.dosage,
            "timing": self.timing,
            "meal_instruction": self.meal_instruction,
            "stock_count": self.stock_count,
            "taken_today": self.taken_today,
            "created_at": self.created_at.isoformat()
        }


class OPDTicket(db.Model):
    __tablename__ = 'opd_tickets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_name = db.Column(db.String(120), default="Patient")
    department = db.Column(db.String(80), nullable=False) # e.g. "Cardiology", "General Medicine"
    token_number = db.Column(db.Integer, nullable=False)
    triage_level = db.Column(db.String(50), default="ROUTINE") # "CRITICAL", "URGENT", "ROUTINE"
    chief_complaint = db.Column(db.String(255), default="")
    status = db.Column(db.String(50), default="waiting") # "waiting", "in_consultation", "completed"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_name": self.patient_name,
            "department": self.department,
            "token_number": self.token_number,
            "triage_level": self.triage_level,
            "chief_complaint": self.chief_complaint,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
