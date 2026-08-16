import sys
import os
from app import create_app
from models import ModelMetrics

app = create_app()
with app.app_context():
    metrics = ModelMetrics.query.all()
    print("=" * 95)
    print(f"  HealthPredict AI — ModelMetrics Table Dump ({len(metrics)} Records)")
    print("=" * 95)
    print(f"{'ID':<4} | {'Disease':<10} | {'Model Name':<22} | {'Accuracy':<9} | {'Precision':<10} | {'Recall':<8} | {'F1':<8} | {'ROC-AUC':<8}")
    print("-" * 95)
    for m in metrics:
        print(f"{m.id:<4} | {m.disease:<10} | {m.model_name:<22} | {m.accuracy:<9.4f} | {m.precision:<10.4f} | {m.recall:<8.4f} | {m.f1_score:<8.4f} | {m.roc_auc:<8.4f}")
    print("=" * 95)
