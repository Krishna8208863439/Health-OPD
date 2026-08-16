import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

# Add backend directory to sys.path so we can persist metrics to ModelMetrics table
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app import create_app
from models import db, ModelMetrics

def train_heart_models():
    print("=" * 75)
    print("  HealthPredict AI — Phase 3: Heart Disease ML Pipeline Training & Evaluation")
    print("=" * 75)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'datasets', 'heart.csv')
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Heart disease dataset not found at {data_path}. "
            "Please ensure heart.csv is present under ml/datasets/."
        )

    # 1. Load Dataset & Define Attributes
    # Attribute Encoding Scheme (Documented for Backend API):
    # - age: Patient age (years)
    # - sex: 0 = Female, 1 = Male
    # - cp: Chest Pain Type (1: Typical Angina, 2: Atypical Angina, 3: Non-Anginal, 4: Asymptomatic)
    # - trestbps: Resting Blood Pressure (mm Hg)
    # - chol: Serum Cholesterol (mg/dl)
    # - fbs: Fasting Blood Sugar > 120 mg/dl (0 = False, 1 = True)
    # - restecg: Resting ECG (0: Normal, 1: ST-T wave abnormality, 2: Left ventricular hypertrophy)
    # - thalach: Maximum Heart Rate Achieved (bpm)
    # - exang: Exercise Induced Angina (0 = No, 1 = Yes)
    # - oldpeak: ST depression induced by exercise relative to rest
    # - slope: Peak exercise ST slope (1: Upsloping, 2: Flat, 3: Downsloping)
    # - ca: Major vessels colored by fluoroscopy (0, 1, 2, 3)
    # - thal: Thalassemia (3: Normal, 6: Fixed defect, 7: Reversible defect)
    # - target: 0 = Normal / Healthy, >0 = Heart Disease Present
    columns = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
    ]
    df = pd.read_csv(data_path, header=None, names=columns, na_values='?')
    
    print(f"\n[1] Dataset Loaded: {df.shape[0]} patient records, {df.shape[1]} attributes")

    # 2. Binarize Target and Handle Missing Values
    # Target: 0 = Absence of heart disease, 1-4 = Presence of heart disease
    df['target'] = (df['target'] > 0).astype(int)
    print(f"    Class distribution: Healthy (0): {(df['target'] == 0).sum()}, Disease Present (1): {(df['target'] == 1).sum()}")

    # Check for missing values in 'ca' and 'thal'
    print(f"\n[2] Handling Missing Data in 'ca' and 'thal':")
    print(f"    - 'ca' missing values: {df['ca'].isna().sum()}")
    print(f"    - 'thal' missing values: {df['thal'].isna().sum()}")

    # 3. Train/Test Split (Stratified 80/20)
    X = df.drop(columns=['target'])
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n[3] Stratified Train/Test Split: Train = {X_train.shape[0]}, Test = {X_test.shape[0]} samples")

    # 4. Imputation
    imputer = SimpleImputer(strategy='median')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)
    joblib.dump(imputer, os.path.join(models_dir, 'heart_imputer.pkl'))

    # 5. Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imputed)
    X_test_scaled = scaler.transform(X_test_imputed)

    scaler_path = os.path.join(models_dir, 'heart_scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"    Saved feature scaler to: {scaler_path}")

    # 6. Train Models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, C=0.8),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, min_samples_leaf=2),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.06, max_depth=3, random_state=42)
    }

    results = {}
    print("\n[4] Training and Evaluating 3 Classifier Models on Held-Out Test Set:\n")
    print(f"{'Model Name':<22} | {'Accuracy':<9} | {'Precision':<10} | {'Recall':<8} | {'F1-Score':<9} | {'ROC-AUC':<8}")
    print("-" * 75)

    for name, clf in models.items():
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)
        y_prob = clf.predict_proba(X_test_scaled)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "model": clf,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
            "confusion_matrix": cm
        }

        print(f"{name:<22} | {acc:.4f}    | {prec:.4f}     | {rec:.4f}   | {f1:.4f}    | {auc:.4f}")

    # 7. Detailed Evaluation Breakdowns
    print("\n[5] Confusion Matrix & Detailed Metrics:")
    for name, r in results.items():
        cm = r['confusion_matrix']
        print(f"\n  -- {name} --")
        print(f"     Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        print(f"     Accuracy={r['accuracy']:.4f}, Precision={r['precision']:.4f}, Recall={r['recall']:.4f}, F1={r['f1_score']:.4f}, ROC-AUC={r['roc_auc']:.4f}")

    # 8. Best Model Selection
    # Selection justification: Highest composite diagnostic score prioritizing Recall and ROC-AUC
    best_name = max(
        results.keys(),
        key=lambda k: (results[k]['recall'] * 0.40) + (results[k]['roc_auc'] * 0.35) + (results[k]['f1_score'] * 0.25)
    )
    best_model = results[best_name]['model']
    best_model_path = os.path.join(models_dir, 'heart_model.pkl')
    joblib.dump(best_model, best_model_path)

    print(f"\n[6] Selected Best Model: '{best_name}'")
    print(f"    Justification: Superior clinical screening performance (Accuracy={results[best_name]['accuracy']:.4f}, Recall={results[best_name]['recall']:.4f}, ROC-AUC={results[best_name]['roc_auc']:.4f})")
    print(f"    Saved chosen model to: {best_model_path}")

    # 9. Persist all 3 models' metrics into database/healthpredict.db (ModelMetrics table)
    print("\n[7] Persisting Computed Metrics into SQLite 'model_metrics' Table...")
    app = create_app()
    with app.app_context():
        # Clear existing metrics for heart disease to avoid stale duplicate rows
        ModelMetrics.query.filter_by(disease="heart").delete()

        for name, r in results.items():
            metric_entry = ModelMetrics(
                disease="heart",
                model_name=name,
                accuracy=float(r['accuracy']),
                precision=float(r['precision']),
                recall=float(r['recall']),
                f1_score=float(r['f1_score']),
                roc_auc=float(r['roc_auc'])
            )
            db.session.add(metric_entry)
        db.session.commit()

        saved_metrics = ModelMetrics.query.filter_by(disease="heart").all()
        print(f"    Successfully stored {len(saved_metrics)} heart model metric records in database.")
        for sm in saved_metrics:
            print(f"      - ID {sm.id}: {sm.model_name} (Acc: {sm.accuracy:.4f}, Recall: {sm.recall:.4f}, ROC-AUC: {sm.roc_auc:.4f})")

    print("\n[SUCCESS] Phase 3 Heart Disease Model Pipeline Completed Successfully!")
    print("=" * 75)

if __name__ == '__main__':
    train_heart_models()
