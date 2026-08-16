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

def train_diabetes_models():
    print("=" * 75)
    print("  HealthPredict AI — Phase 2: Diabetes ML Pipeline Training & Evaluation")
    print("=" * 75)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'datasets', 'diabetes.csv')
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Diabetes dataset not found at {data_path}. "
            "Please ensure diabetes.csv is present under ml/datasets/."
        )

    # 1. Load Dataset
    columns = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome'
    ]
    df = pd.read_csv(data_path, header=None, names=columns)
    
    print(f"\n[1] Dataset Loaded Successfully: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"    Class distribution: Non-Diabetic (0): {(df['Outcome'] == 0).sum()}, Diabetic (1): {(df['Outcome'] == 1).sum()}")

    # 2. Data Cleaning & Zero-Value Treatment
    # In Pima Indians dataset, 0 in Glucose, BloodPressure, SkinThickness, Insulin, BMI is physiologically invalid
    zero_as_missing_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    print(f"\n[2] Handling Zero-as-Missing Values in: {zero_as_missing_cols}")
    for col in zero_as_missing_cols:
        zero_count = (df[col] == 0).sum()
        print(f"    - {col}: {zero_count} invalid zero values replaced with median imputation")
        df[col] = df[col].replace(0, np.nan)

    # 3. Train / Test Split (Stratified 80/20)
    X = df.drop(columns=['Outcome'])
    y = df['Outcome']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n[3] Train/Test Split: Train = {X_train.shape[0]} samples, Test = {X_test.shape[0]} samples (Stratified)")

    # 4. Imputation (fit on train only, transform train & test)
    imputer = SimpleImputer(strategy='median')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)
    joblib.dump(imputer, os.path.join(models_dir, 'diabetes_imputer.pkl'))

    # 5. Feature Scaling (fit on train only, transform train & test)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imputed)
    X_test_scaled = scaler.transform(X_test_imputed)
    
    scaler_path = os.path.join(models_dir, 'diabetes_scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"    Saved feature scaler to: {scaler_path}")

    # 6. Train Models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, C=1.0),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, min_samples_leaf=2),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
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
    # Selection justification: In disease risk screening, false negatives (missed cases) carry higher clinical risk.
    # We rank models using a composite score prioritizing Recall and ROC-AUC: Score = (Recall * 0.40) + (ROC-AUC * 0.35) + (F1 * 0.25)
    best_name = max(
        results.keys(),
        key=lambda k: (results[k]['recall'] * 0.40) + (results[k]['roc_auc'] * 0.35) + (results[k]['f1_score'] * 0.25)
    )
    best_model = results[best_name]['model']
    best_model_path = os.path.join(models_dir, 'diabetes_model.pkl')
    joblib.dump(best_model, best_model_path)
    
    print(f"\n[6] Selected Best Model: '{best_name}'")
    print(f"    Justification: Highest clinical diagnostic efficacy (balanced Recall={results[best_name]['recall']:.4f}, ROC-AUC={results[best_name]['roc_auc']:.4f})")
    print(f"    Saved chosen model to: {best_model_path}")

    # 9. Persist all 3 models' metrics into database/healthpredict.db (ModelMetrics table)
    print("\n[7] Persisting Computed Metrics into SQLite 'model_metrics' Table...")
    app = create_app()
    with app.app_context():
        # Clear existing metrics for diabetes to avoid stale duplicate rows
        ModelMetrics.query.filter_by(disease="diabetes").delete()
        
        for name, r in results.items():
            metric_entry = ModelMetrics(
                disease="diabetes",
                model_name=name,
                accuracy=float(r['accuracy']),
                precision=float(r['precision']),
                recall=float(r['recall']),
                f1_score=float(r['f1_score']),
                roc_auc=float(r['roc_auc'])
            )
            db.session.add(metric_entry)
        db.session.commit()
        
        saved_metrics = ModelMetrics.query.filter_by(disease="diabetes").all()
        print(f"    Successfully stored {len(saved_metrics)} model metric records in database.")
        for sm in saved_metrics:
            print(f"      - ID {sm.id}: {sm.model_name} (Acc: {sm.accuracy:.4f}, F1: {sm.f1_score:.4f}, ROC-AUC: {sm.roc_auc:.4f})")

    print("\n[SUCCESS] Phase 2 Diabetes Model Pipeline Completed Successfully!")
    print("=" * 75)

if __name__ == '__main__':
    train_diabetes_models()
