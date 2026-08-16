import os
import json
import joblib
import numpy as np

def generate_feature_importance_artifacts():
    print("=" * 75)
    print("  HealthPredict AI — Phase 4: Feature Importance Artifact Generation")
    print("=" * 75)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, 'models')

    # -------------------------------------------------------------
    # 1. Diabetes Feature Importance
    # -------------------------------------------------------------
    diabetes_model_path = os.path.join(models_dir, 'diabetes_model.pkl')
    if not os.path.exists(diabetes_model_path):
        raise FileNotFoundError(f"Trained diabetes model not found at {diabetes_model_path}.")

    diabetes_model = joblib.load(diabetes_model_path)
    diabetes_feature_names = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ]
    diabetes_descriptions = {
        'Glucose': 'Plasma glucose concentration (2h post oral glucose tolerance test)',
        'BMI': 'Body Mass Index (weight in kg / height in m^2)',
        'Age': 'Patient age in years',
        'DiabetesPedigreeFunction': 'Genetic predisposition score based on family pedigree',
        'Pregnancies': 'Number of gestational events / pregnancies',
        'BloodPressure': 'Diastolic blood pressure in mm Hg',
        'Insulin': '2-Hour serum insulin (mu U/ml)',
        'SkinThickness': 'Triceps skin fold thickness in mm'
    }

    if hasattr(diabetes_model, 'feature_importances_'):
        raw_importances = diabetes_model.feature_importances_
    else:
        raw_importances = np.abs(diabetes_model.coef_[0])

    total_imp = np.sum(raw_importances)
    percentages = (raw_importances / total_imp) * 100.0

    diabetes_features_list = []
    for feat, raw, pct in zip(diabetes_feature_names, raw_importances, percentages):
        diabetes_features_list.append({
            "feature": feat,
            "raw_importance": round(float(raw), 6),
            "percentage": round(float(pct), 2),
            "description": diabetes_descriptions.get(feat, '')
        })

    # Sort descending by importance
    diabetes_features_list.sort(key=lambda x: x["percentage"], reverse=True)

    diabetes_artifact = {
        "disease": "diabetes",
        "model_name": type(diabetes_model).__name__,
        "total_features": len(diabetes_features_list),
        "features": diabetes_features_list,
        "total_percentage": round(sum(f["percentage"] for f in diabetes_features_list), 2)
    }

    diabetes_json_path = os.path.join(models_dir, 'diabetes_feature_importance.json')
    with open(diabetes_json_path, 'w', encoding='utf-8') as f:
        json.dump(diabetes_artifact, f, indent=2)
    print(f"\n[1] Saved Diabetes Feature Importance to: {diabetes_json_path}")

    # -------------------------------------------------------------
    # 2. Heart Disease Feature Importance
    # -------------------------------------------------------------
    heart_model_path = os.path.join(models_dir, 'heart_model.pkl')
    if not os.path.exists(heart_model_path):
        raise FileNotFoundError(f"Trained heart model not found at {heart_model_path}.")

    heart_model = joblib.load(heart_model_path)
    heart_feature_names = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ]
    heart_descriptions = {
        'thal': 'Thalassemia defect severity (Normal, Fixed, Reversible)',
        'ca': 'Number of major vessels (0-3) colored by fluoroscopy',
        'cp': 'Chest pain type (Typical, Atypical, Non-Anginal, Asymptomatic)',
        'oldpeak': 'ST depression induced by exercise relative to rest',
        'thalach': 'Maximum heart rate achieved during stress test',
        'age': 'Patient age in years',
        'chol': 'Serum cholesterol in mg/dl',
        'trestbps': 'Resting blood pressure in mm Hg',
        'exang': 'Exercise induced angina presence',
        'slope': 'Slope of peak exercise ST segment',
        'sex': 'Patient sex (0: Female, 1: Male)',
        'restecg': 'Resting electrocardiographic findings',
        'fbs': 'Fasting blood sugar > 120 mg/dl indicator'
    }

    if hasattr(heart_model, 'feature_importances_'):
        raw_importances_heart = heart_model.feature_importances_
    else:
        raw_importances_heart = np.abs(heart_model.coef_[0])

    total_imp_heart = np.sum(raw_importances_heart)
    percentages_heart = (raw_importances_heart / total_imp_heart) * 100.0

    heart_features_list = []
    for feat, raw, pct in zip(heart_feature_names, raw_importances_heart, percentages_heart):
        heart_features_list.append({
            "feature": feat,
            "raw_importance": round(float(raw), 6),
            "percentage": round(float(pct), 2),
            "description": heart_descriptions.get(feat, '')
        })

    # Sort descending by importance
    heart_features_list.sort(key=lambda x: x["percentage"], reverse=True)

    heart_artifact = {
        "disease": "heart",
        "model_name": type(heart_model).__name__,
        "total_features": len(heart_features_list),
        "features": heart_features_list,
        "total_percentage": round(sum(f["percentage"] for f in heart_features_list), 2)
    }

    heart_json_path = os.path.join(models_dir, 'heart_feature_importance.json')
    with open(heart_json_path, 'w', encoding='utf-8') as f:
        json.dump(heart_artifact, f, indent=2)
    print(f"[2] Saved Heart Disease Feature Importance to: {heart_json_path}")

    print("\n[SUCCESS] Phase 4 Feature Importance Artifacts Generated Successfully!")
    print("=" * 75)

if __name__ == '__main__':
    generate_feature_importance_artifacts()
