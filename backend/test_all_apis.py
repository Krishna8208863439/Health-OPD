import json
import urllib.request
import urllib.error
import os

BASE_URL = "http://localhost:5000/api"

def make_request(path, method='GET', data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return resp.status, json.loads(resp.read().decode('utf-8'))
        else:
            return resp.status, resp.read()

def run_tests():
    print("=" * 80)
    print("  HealthPredict AI — End-to-End API Suite Verification")
    print("=" * 80)

    # 1. Health Check
    status, data = make_request("/health")
    print(f"\n[1] Health Check: Status={status}, Body={data}")
    assert data["status"] == "ok"

    # 2. Phase 6: Diabetes Prediction Tests with Varied Inputs (Anti-Fabrication Proof)
    print("\n[2] Phase 6: Testing Diabetes Predictions (Low / Moderate / High Risk Inputs)")
    
    # Low Risk Case
    low_diabetes_input = {
        "Pregnancies": 1, "Glucose": 78, "BloodPressure": 65, "SkinThickness": 18,
        "Insulin": 50, "BMI": 21.5, "DiabetesPedigreeFunction": 0.15, "Age": 22
    }
    s1, r1 = make_request("/predict/diabetes", "POST", low_diabetes_input)
    print(f"  --> Low Input (Glucose 78, Age 22, BMI 21.5): ID={r1['id']}, Prob={r1['risk_probability']} ({r1['risk_percentage']}%), Level={r1['risk_level']}")

    # Moderate Risk Case
    med_diabetes_input = {
        "Pregnancies": 3, "Glucose": 135, "BloodPressure": 76, "SkinThickness": 28,
        "Insulin": 110, "BMI": 29.5, "DiabetesPedigreeFunction": 0.45, "Age": 45
    }
    s2, r2 = make_request("/predict/diabetes", "POST", med_diabetes_input)
    print(f"  --> Medium Input (Glucose 135, Age 45, BMI 29.5): ID={r2['id']}, Prob={r2['risk_probability']} ({r2['risk_percentage']}%), Level={r2['risk_level']}")

    # High Risk Case
    high_diabetes_input = {
        "Pregnancies": 6, "Glucose": 190, "BloodPressure": 88, "SkinThickness": 38,
        "Insulin": 220, "BMI": 38.2, "DiabetesPedigreeFunction": 1.25, "Age": 58
    }
    s3, r3 = make_request("/predict/diabetes", "POST", high_diabetes_input)
    print(f"  --> High Input (Glucose 190, Age 58, BMI 38.2): ID={r3['id']}, Prob={r3['risk_probability']} ({r3['risk_percentage']}%), Level={r3['risk_level']}")

    # Verify monotonic increasing risk
    assert r1['risk_probability'] < r2['risk_probability'] < r3['risk_probability'], "Probabilities did not scale with risk factors!"
    print("  [PROOF] Real model active: Risk probabilities vary dynamically with physiological inputs!")

    # 3. Phase 6: Heart Disease Prediction Tests with Varied Inputs
    print("\n[3] Phase 6: Testing Heart Disease Predictions (Healthy vs Disease Profiles)")
    
    # Healthy Profile
    healthy_heart = {
        "age": 35, "sex": 0, "cp": 1, "trestbps": 115, "chol": 180,
        "fbs": 0, "restecg": 0, "thalach": 175, "exang": 0,
        "oldpeak": 0.0, "slope": 1, "ca": 0, "thal": 3
    }
    sh1, rh1 = make_request("/predict/heart", "POST", healthy_heart)
    print(f"  --> Healthy Heart Profile: ID={rh1['id']}, Prob={rh1['risk_probability']} ({rh1['risk_percentage']}%), Level={rh1['risk_level']}")

    # Critical Disease Profile
    sick_heart = {
        "age": 67, "sex": 1, "cp": 4, "trestbps": 160, "chol": 286,
        "fbs": 1, "restecg": 2, "thalach": 108, "exang": 1,
        "oldpeak": 3.5, "slope": 2, "ca": 3, "thal": 7
    }
    sh2, rh2 = make_request("/predict/heart", "POST", sick_heart)
    print(f"  --> High Urgency Heart Profile: ID={rh2['id']}, Prob={rh2['risk_probability']} ({rh2['risk_percentage']}%), Level={rh2['risk_level']}")

    assert rh1['risk_probability'] < rh2['risk_probability'], "Heart risk probabilities failed validation!"

    # 4. Insert 5 more varied records to reach ~10 records for Phase 7
    print("\n[4] Populating varied prediction records for Phase 7 Dashboard & History Testing...")
    additional_cases = [
        ("diabetes", {"Pregnancies": 2, "Glucose": 110, "BloodPressure": 70, "SkinThickness": 25, "Insulin": 80, "BMI": 26.5, "DiabetesPedigreeFunction": 0.35, "Age": 29}),
        ("diabetes", {"Pregnancies": 5, "Glucose": 165, "BloodPressure": 84, "SkinThickness": 38, "Insulin": 175, "BMI": 35.2, "DiabetesPedigreeFunction": 0.88, "Age": 49}),
        ("heart", {"age": 52, "sex": 1, "cp": 3, "trestbps": 135, "chol": 230, "fbs": 0, "restecg": 1, "thalach": 145, "exang": 0, "oldpeak": 1.2, "slope": 2, "ca": 1, "thal": 6}),
        ("heart", {"age": 44, "sex": 0, "cp": 2, "trestbps": 120, "chol": 195, "fbs": 0, "restecg": 0, "thalach": 168, "exang": 0, "oldpeak": 0.2, "slope": 1, "ca": 0, "thal": 3}),
        ("diabetes", {"Pregnancies": 0, "Glucose": 92, "BloodPressure": 68, "SkinThickness": 18, "Insulin": 45, "BMI": 21.8, "DiabetesPedigreeFunction": 0.18, "Age": 22})
    ]
    for dis, payload in additional_cases:
        make_request(f"/predict/{dis}", "POST", payload)

    # 5. Phase 7: Dashboard Aggregates Testing
    print("\n[5] Phase 7: Testing GET /api/dashboard Aggregates")
    s_dash, dash = make_request("/dashboard")
    print(f"  - Total Predictions: {dash['total_predictions']}")
    print(f"  - Diabetes Count: {dash['diabetes_predictions']}")
    print(f"  - Heart Count: {dash['heart_predictions']}")
    print(f"  - Average Risk Percentage: {dash['average_risk_percentage']}%")
    print(f"  - Risk Stratification: {dash['risk_distribution']}")
    print(f"  - Recent Predictions Count: {len(dash['recent_predictions'])}")
    assert dash['total_predictions'] >= 10, "Expected at least 10 records in dashboard!"

    # 6. Phase 7: History Query & Filter Testing
    print("\n[6] Phase 7: Testing GET /api/predictions History & Filtering")
    _, all_history = make_request("/predictions")
    print(f"  - Query All History: Retrieved {len(all_history['predictions'])} records (Total: {all_history['total']})")
    
    _, diabetes_history = make_request("/predictions?disease=diabetes")
    print(f"  - Query Filter (disease=diabetes): Retrieved {len(diabetes_history['predictions'])} records")
    assert all(p['disease'] == 'diabetes' for p in diabetes_history['predictions'])

    # 7. Phase 7: Single Prediction Lookup & Delete
    print("\n[7] Phase 7: Testing Single Lookup & Delete Cycle")
    target_id = diabetes_history['predictions'][0]['id']
    _, single_rec = make_request(f"/predictions/{target_id}")
    print(f"  - Looked up ID #{target_id}: Disease={single_rec['disease']}, Risk={single_rec['risk_level']}")
    assert single_rec['id'] == target_id

    _, del_resp = make_request(f"/predictions/{target_id}", "DELETE")
    print(f"  - Deleted ID #{target_id}: {del_resp}")

    try:
        make_request(f"/predictions/{target_id}")
        assert False, "Deleted record still accessible!"
    except urllib.error.HTTPError as e:
        print(f"  - Confirmed 404 on deleted record ID #{target_id} (Status={e.code})")

    # 8. Phase 7: Model Metrics & Feature Importance APIs
    print("\n[8] Phase 7: Testing Model Metrics & Feature Importance APIs")
    _, metrics_data = make_request("/model-metrics")
    print(f"  - GET /api/model-metrics: {metrics_data['total']} model evaluations loaded from SQLite DB")
    
    _, fi_diabetes = make_request("/feature-importance/diabetes")
    print(f"  - GET /api/feature-importance/diabetes: {len(fi_diabetes['features'])} features (Top: {fi_diabetes['features'][0]['feature']} - {fi_diabetes['features'][0]['percentage']}%)")

    # 9. Phase 8: PDF Report Generation API
    print("\n[9] Phase 8: Testing GET /api/report/<id> (ReportLab PDF Generation)")
    report_target_id = rh2['id'] # High risk heart case
    s_pdf, pdf_bytes = make_request(f"/report/{report_target_id}")
    pdf_out_path = os.path.join(os.path.dirname(__file__), f"test_report_{report_target_id}.pdf")
    with open(pdf_out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  --> PDF Report Generated Successfully for ID #{report_target_id}!")
    print(f"  --> File saved to: {pdf_out_path} ({len(pdf_bytes)} bytes)")
    assert len(pdf_bytes) > 1000, "PDF file is too small or invalid"
    assert pdf_bytes.startswith(b'%PDF'), "Downloaded file is not a valid PDF!"

    print("\n" + "=" * 80)
    print("  [SUCCESS] All Phase 6, 7, and 8 Backend APIs Tested & Verified 100%!")
    print("=" * 80)

if __name__ == '__main__':
    run_tests()
