import os
import sys
from app import create_app
from models import db, Prediction, ModelMetrics

def run_db_seed_and_verification():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("  HealthPredict AI — Phase 1 Database Schema Verification")
        print("=" * 60)

        # Ensure tables exist
        db.create_all()
        print("\n[1] Auto-created database tables: 'predictions', 'model_metrics'")

        # 1. Test Prediction Table: INSERT
        print("\n[2] Testing 'predictions' Table: INSERT")
        sample_input = {
            "Pregnancies": 2,
            "Glucose": 138,
            "BloodPressure": 72,
            "SkinThickness": 35,
            "Insulin": 0,
            "BMI": 33.6,
            "DiabetesPedigreeFunction": 0.627,
            "Age": 47
        }
        test_pred = Prediction(
            disease="diabetes",
            input_data=sample_input,
            prediction=1,
            risk_probability=0.7425,
            risk_level="High"
        )
        db.session.add(test_pred)

        # 2. Test ModelMetrics Table: INSERT
        print("[3] Testing 'model_metrics' Table: INSERT")
        test_metric = ModelMetrics(
            disease="diabetes",
            model_name="Random Forest Classifier",
            accuracy=0.8247,
            precision=0.7826,
            recall=0.7500,
            f1_score=0.7660,
            roc_auc=0.8841
        )
        db.session.add(test_metric)
        db.session.commit()
        print(f"  --> Inserted Prediction row ID: {test_pred.id}")
        print(f"  --> Inserted ModelMetrics row ID: {test_metric.id}")

        # 3. Test SELECT & verify exact fields
        print("\n[4] Testing SELECT Queries & Schema Fields")
        fetched_pred = db.session.get(Prediction, test_pred.id)
        print(f"  [Prediction Fetched]")
        print(f"    - ID: {fetched_pred.id}")
        print(f"    - Disease: {fetched_pred.disease}")
        print(f"    - Input Data: {fetched_pred.input_data}")
        print(f"    - Prediction: {fetched_pred.prediction}")
        print(f"    - Risk Probability: {fetched_pred.risk_probability}")
        print(f"    - Risk Percentage: {fetched_pred.to_dict()['risk_percentage']}%")
        print(f"    - Risk Level: {fetched_pred.risk_level}")
        print(f"    - Created At: {fetched_pred.created_at}")

        fetched_metric = db.session.get(ModelMetrics, test_metric.id)
        print(f"\n  [ModelMetrics Fetched]")
        print(f"    - ID: {fetched_metric.id}")
        print(f"    - Disease: {fetched_metric.disease}")
        print(f"    - Model Name: {fetched_metric.model_name}")
        print(f"    - Accuracy: {fetched_metric.accuracy}")
        print(f"    - Precision: {fetched_metric.precision}")
        print(f"    - Recall: {fetched_metric.recall}")
        print(f"    - F1 Score: {fetched_metric.f1_score}")
        print(f"    - ROC AUC: {fetched_metric.roc_auc}")
        print(f"    - Created At: {fetched_metric.created_at}")

        # Assertions to ensure zero fabrication
        assert fetched_pred is not None, "Failed to retrieve inserted Prediction row"
        assert fetched_metric is not None, "Failed to retrieve inserted ModelMetrics row"
        assert fetched_pred.disease == "diabetes"
        assert fetched_pred.risk_level == "High"
        assert fetched_metric.model_name == "Random Forest Classifier"

        # 4. Test DELETE
        print("\n[5] Testing DELETE")
        db.session.delete(fetched_pred)
        db.session.delete(fetched_metric)
        db.session.commit()

        # Confirm deleted
        check_pred = db.session.get(Prediction, test_pred.id)
        check_metric = db.session.get(ModelMetrics, test_metric.id)
        assert check_pred is None, "Prediction row was not deleted properly"
        assert check_metric is None, "ModelMetrics row was not deleted properly"
        print(f"  --> Confirmed Prediction row ID {test_pred.id} deleted: {check_pred is None}")
        print(f"  --> Confirmed ModelMetrics row ID {test_metric.id} deleted: {check_metric is None}")

        print("\n[SUCCESS] Phase 1 Database Read/Write/Delete verification PASSED 100%!")
        print("=" * 60)

if __name__ == '__main__':
    run_db_seed_and_verification()
