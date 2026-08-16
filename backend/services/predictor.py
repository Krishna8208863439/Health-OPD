import os
import json
import joblib
import numpy as np
from datetime import datetime
from models import db, Prediction

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'ml', 'models')

class MLPredictionService:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.imputers = {}
        self.feature_importances = {}
        self._load_artifacts()

    def _load_artifacts(self):
        # 1. Diabetes Artifacts
        diabetes_model_path = os.path.join(MODELS_DIR, 'diabetes_model.pkl')
        diabetes_scaler_path = os.path.join(MODELS_DIR, 'diabetes_scaler.pkl')
        diabetes_imputer_path = os.path.join(MODELS_DIR, 'diabetes_imputer.pkl')
        diabetes_fi_path = os.path.join(MODELS_DIR, 'diabetes_feature_importance.json')

        if os.path.exists(diabetes_model_path):
            self.models['diabetes'] = joblib.load(diabetes_model_path)
        if os.path.exists(diabetes_scaler_path):
            self.scalers['diabetes'] = joblib.load(diabetes_scaler_path)
        if os.path.exists(diabetes_imputer_path):
            self.imputers['diabetes'] = joblib.load(diabetes_imputer_path)
        if os.path.exists(diabetes_fi_path):
            with open(diabetes_fi_path, 'r', encoding='utf-8') as f:
                self.feature_importances['diabetes'] = json.load(f)

        # 2. Heart Disease Artifacts
        heart_model_path = os.path.join(MODELS_DIR, 'heart_model.pkl')
        heart_scaler_path = os.path.join(MODELS_DIR, 'heart_scaler.pkl')
        heart_imputer_path = os.path.join(MODELS_DIR, 'heart_imputer.pkl')
        heart_fi_path = os.path.join(MODELS_DIR, 'heart_feature_importance.json')

        if os.path.exists(heart_model_path):
            self.models['heart'] = joblib.load(heart_model_path)
        if os.path.exists(heart_scaler_path):
            self.scalers['heart'] = joblib.load(heart_scaler_path)
        if os.path.exists(heart_imputer_path):
            self.imputers['heart'] = joblib.load(heart_imputer_path)
        if os.path.exists(heart_fi_path):
            with open(heart_fi_path, 'r', encoding='utf-8') as f:
                self.feature_importances['heart'] = json.load(f)

    @staticmethod
    def derive_risk_level(probability: float) -> str:
        # Standard clinical risk stratification thresholds
        if probability < 0.35:
            return "Low"
        elif probability <= 0.70:
            return "Moderate"
        else:
            return "High"

    def validate_and_predict_diabetes(self, data: dict) -> dict:
        required = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
        ]
        # Check required fields
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: '{field}'")
            if data[field] is None:
                raise ValueError(f"Field '{field}' cannot be null")

        try:
            pregnancies = int(data['Pregnancies'])
            glucose = float(data['Glucose'])
            bp = float(data['BloodPressure'])
            skin = float(data['SkinThickness'])
            insulin = float(data['Insulin'])
            bmi = float(data['BMI'])
            dpf = float(data['DiabetesPedigreeFunction'])
            age = int(data['Age'])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numerical format in submitted features: {str(e)}")

        # Range Validations
        if not (0 <= pregnancies <= 25):
            raise ValueError("Pregnancies must be between 0 and 25")
        if not (30 <= glucose <= 300):
            raise ValueError("Glucose must be between 30 and 300 mg/dL")
        if not (30 <= bp <= 250):
            raise ValueError("BloodPressure must be between 30 and 250 mm Hg")
        if not (0 <= skin <= 100):
            raise ValueError("SkinThickness must be between 0 and 100 mm")
        if not (0 <= insulin <= 900):
            raise ValueError("Insulin must be between 0 and 900 mu U/ml")
        if not (10.0 <= bmi <= 75.0):
            raise ValueError("BMI must be between 10.0 and 75.0 kg/m^2")
        if not (0.01 <= dpf <= 3.0):
            raise ValueError("DiabetesPedigreeFunction must be between 0.01 and 3.0")
        if not (1 <= age <= 125):
            raise ValueError("Age must be between 1 and 125 years")

        # Feature Vector Preparation
        raw_features = np.array([[
            pregnancies,
            np.nan if glucose == 0 else glucose,
            np.nan if bp == 0 else bp,
            np.nan if skin == 0 else skin,
            np.nan if insulin == 0 else insulin,
            np.nan if bmi == 0 else bmi,
            dpf,
            age
        ]], dtype=float)

        # Impute & Scale
        imputed = self.imputers['diabetes'].transform(raw_features)
        scaled = self.scalers['diabetes'].transform(imputed)

        # Real Model Prediction
        model = self.models['diabetes']
        prediction = int(model.predict(scaled)[0])
        probabilities = model.predict_proba(scaled)[0]
        risk_probability = float(probabilities[1])
        risk_level = self.derive_risk_level(risk_probability)

        # Clean sanitized input dict for DB storage
        input_record = {
            "Pregnancies": pregnancies,
            "Glucose": glucose,
            "BloodPressure": bp,
            "SkinThickness": skin,
            "Insulin": insulin,
            "BMI": bmi,
            "DiabetesPedigreeFunction": dpf,
            "Age": age
        }

        # Persist to database
        record = Prediction(
            disease="diabetes",
            input_data=input_record,
            prediction=prediction,
            risk_probability=risk_probability,
            risk_level=risk_level
        )
        db.session.add(record)
        db.session.commit()

        fi = self.feature_importances.get('diabetes', {}).get('features', [])

        return {
            "id": record.id,
            "disease": "diabetes",
            "prediction": prediction,
            "prediction_label": "High Risk / Positive" if prediction == 1 else "Low Risk / Negative",
            "risk_probability": round(risk_probability, 4),
            "risk_percentage": round(risk_probability * 100, 2),
            "risk_level": risk_level,
            "model_name": type(model).__name__,
            "feature_importance": fi,
            "input_data": input_record,
            "created_at": record.created_at.isoformat()
        }

    def validate_and_predict_heart(self, data: dict) -> dict:
        required = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
            'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
        ]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: '{field}'")
            if data[field] is None:
                raise ValueError(f"Field '{field}' cannot be null")

        try:
            age = int(data['age'])
            sex = int(data['sex'])
            cp = int(data['cp'])
            trestbps = float(data['trestbps'])
            chol = float(data['chol'])
            fbs = int(data['fbs'])
            restecg = int(data['restecg'])
            thalach = float(data['thalach'])
            exang = int(data['exang'])
            oldpeak = float(data['oldpeak'])
            slope = int(data['slope'])
            ca = int(data['ca'])
            thal = int(data['thal'])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numerical format in submitted features: {str(e)}")

        # Range Validations
        if not (1 <= age <= 125):
            raise ValueError("Age must be between 1 and 125")
        if sex not in (0, 1):
            raise ValueError("Sex must be 0 (Female) or 1 (Male)")
        if cp not in (1, 2, 3, 4):
            raise ValueError("Chest pain type (cp) must be 1, 2, 3, or 4")
        if not (50 <= trestbps <= 260):
            raise ValueError("Resting blood pressure must be between 50 and 260 mm Hg")
        if not (80 <= chol <= 650):
            raise ValueError("Serum cholesterol must be between 80 and 650 mg/dl")
        if fbs not in (0, 1):
            raise ValueError("Fasting blood sugar indicator (fbs) must be 0 or 1")
        if restecg not in (0, 1, 2):
            raise ValueError("Resting ECG (restecg) must be 0, 1, or 2")
        if not (50 <= thalach <= 250):
            raise ValueError("Maximum heart rate (thalach) must be between 50 and 250 bpm")
        if exang not in (0, 1):
            raise ValueError("Exercise-induced angina (exang) must be 0 or 1")
        if not (0.0 <= oldpeak <= 10.0):
            raise ValueError("ST depression (oldpeak) must be between 0.0 and 10.0")
        if slope not in (1, 2, 3):
            raise ValueError("ST slope must be 1, 2, or 3")
        if ca not in (0, 1, 2, 3):
            raise ValueError("Major vessels colored (ca) must be 0, 1, 2, or 3")
        if thal not in (3, 6, 7):
            raise ValueError("Thalassemia (thal) must be 3 (Normal), 6 (Fixed defect), or 7 (Reversible defect)")

        # Feature Vector Preparation
        raw_features = np.array([[
            age, sex, cp, trestbps, chol, fbs, restecg,
            thalach, exang, oldpeak, slope, ca, thal
        ]], dtype=float)

        # Impute & Scale
        imputed = self.imputers['heart'].transform(raw_features)
        scaled = self.scalers['heart'].transform(imputed)

        # Real Model Prediction
        model = self.models['heart']
        prediction = int(model.predict(scaled)[0])
        probabilities = model.predict_proba(scaled)[0]
        risk_probability = float(probabilities[1])
        risk_level = self.derive_risk_level(risk_probability)

        input_record = {
            "age": age, "sex": sex, "cp": cp, "trestbps": trestbps,
            "chol": chol, "fbs": fbs, "restecg": restecg, "thalach": thalach,
            "exang": exang, "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
        }

        # Persist to database
        record = Prediction(
            disease="heart",
            input_data=input_record,
            prediction=prediction,
            risk_probability=risk_probability,
            risk_level=risk_level
        )
        db.session.add(record)
        db.session.commit()

        fi = self.feature_importances.get('heart', {}).get('features', [])

        return {
            "id": record.id,
            "disease": "heart",
            "prediction": prediction,
            "prediction_label": "High Risk / Disease Likely" if prediction == 1 else "Low Risk / Normal",
            "risk_probability": round(risk_probability, 4),
            "risk_percentage": round(risk_probability * 100, 2),
            "risk_level": risk_level,
            "model_name": type(model).__name__,
            "feature_importance": fi,
            "input_data": input_record,
            "created_at": record.created_at.isoformat()
        }

prediction_service = MLPredictionService()
