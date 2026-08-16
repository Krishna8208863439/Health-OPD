# HealthPredict AI — Clinical Risk Prediction Platform

> **Clinical Decision-Support & Disease Risk Stratification Engine**  
> Powered by Trained Supervised Machine Learning Classifiers, Native Feature Explainability, and Verifiable Telemetry.

---

## ⚠️ Mandatory Medical Disclaimer

> **IMPORTANT NOTICE:**  
> **HealthPredict AI provides machine-learning-based risk estimates for educational and decision-support purposes only. It does not diagnose, treat, cure, or prevent any disease. Always consult a qualified healthcare professional for medical advice.**

---

## 🌟 Platform Highlights & Anti-Fabrication Architecture

- **Zero Mock / Hardcoded Data**: Every prediction probability, risk level tier, and dashboard metric is computed deterministically by serialized scikit-learn models and persisted directly into SQLite tables.
- **Trained Clinical ML Models**:
  - **Type 2 Diabetes Screening**: Trained on the **Pima Indians Diabetes Database** (NIDDK). Selected model: **Gradient Boosting** (ROC-AUC: `0.8217`, Sensitivity/Recall: `57.41%`).
  - **Coronary Heart Disease Risk**: Trained on the **UCI Cleveland Heart Disease Database** (303 records, 13 clinical biomarkers). Selected model: **Random Forest** (Accuracy: `91.80%`, Sensitivity/Recall: `92.86%`, ROC-AUC: `0.9535`).
- **Explainable AI (XAI)**: Native Gini impurity and gradient split feature importance breakdowns serialized to JSON and dynamically rendered as visual contribution bars.
- **Automated PDF Clinical Reports**: On-demand single-page medical summary generation using ReportLab including patient inputs, risk stratification, key drivers, and disclaimer.
- **Modern Full-Stack Architecture**:
  - **Frontend**: React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts
  - **Backend**: Python Flask REST API + SQLAlchemy ORM + SQLite + Joblib + ReportLab

---

## 📂 Project Structure

```
Smart_Healthcare_System/
├── backend/
│   ├── app.py                     # Flask application factory, error handling & routes
│   ├── config.py                  # Environment configuration & SQLite URI
│   ├── models.py                  # SQLAlchemy ORM (Prediction, ModelMetrics)
│   ├── routes/
│   │   └── api_routes.py          # REST endpoints (Predictions, Dashboard, Reports)
│   ├── services/
│   │   ├── predictor.py           # Imputation, scaling, inference & DB persistence
│   │   └── pdf_generator.py       # ReportLab PDF clinical report engine
│   ├── test_all_apis.py           # End-to-end backend verification test suite
│   ├── dump_metrics.py            # SQLite model evaluation inspector
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/            # Navbar, Footer (with disclaimer)
│   │   ├── pages/                 # Landing, Diabetes, Heart, Result, Dashboard, History, Models
│   │   ├── services/api.js        # Axios API client
│   │   ├── App.jsx                # React Router setup
│   │   └── main.jsx               # Entry point
│   ├── package.json               # Node dependencies
│   ├── vite.config.js             # Vite configuration with /api proxy
│   └── tailwind.config.js         # Design tokens & color system
├── ml/
│   ├── datasets/
│   │   ├── diabetes.csv           # Pima Indians Diabetes dataset
│   │   ├── heart.csv              # UCI Cleveland Heart Disease dataset
│   │   └── README.md              # Dataset provenance and schema documentation
│   ├── models/                    # Serialized .pkl models, scalers, imputers, and JSON feature importances
│   ├── train_diabetes.py          # Diabetes ML pipeline training & evaluation
│   ├── train_heart.py             # Heart disease ML pipeline training & evaluation
│   └── feature_importance.py      # Feature importance JSON artifact generator
├── database/
│   └── healthpredict.db           # SQLite database
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup & ML Training

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run ML training pipelines (trains models, saves .pkl artifacts, and populates ModelMetrics DB)
python ../ml/train_diabetes.py
python ../ml/train_heart.py
python ../ml/feature_importance.py

# Start Flask Backend Server (Runs on http://localhost:5000)
python app.py
```

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite Development Server (Runs on http://localhost:5173)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health & uptime check |
| `POST` | `/api/predict/diabetes` | Submit biometric inputs for Type 2 Diabetes risk evaluation |
| `POST` | `/api/predict/heart` | Submit clinical inputs for Coronary Heart Disease evaluation |
| `GET` | `/api/dashboard` | Aggregated telemetry, condition volume, and risk distributions |
| `GET` | `/api/predictions` | Query patient history with filters (`disease`, `risk_level`, `search`) |
| `GET` | `/api/predictions/:id` | Fetch single prediction record with input values and feature weights |
| `DELETE` | `/api/predictions/:id` | Delete a prediction record from the registry |
| `GET` | `/api/model-metrics` | Retrieve evaluation metrics for all 6 trained classifier architectures |
| `GET` | `/api/feature-importance/:disease` | Retrieve feature importance breakdown (`diabetes` or `heart`) |
| `GET` | `/api/report/:id` | Download official single-page clinical PDF report |

---

## 🔬 Model Benchmark Summary

### Type 2 Diabetes (Pima Indians NIDDK)
| Architecture | Accuracy | Precision | Recall (Sensitivity) | F1-Score | ROC-AUC | Status |
|---|---|---|---|---|---|---|
| Logistic Regression | 70.78% | 60.00% | 50.00% | 0.5455 | 0.8130 | Evaluated |
| Random Forest | 75.97% | 69.77% | 55.56% | 0.6186 | 0.8106 | Evaluated |
| **Gradient Boosting** | **74.03%** | **64.58%** | **57.41%** | **0.6078** | **0.8217** | **PRIMARY** |

### Coronary Heart Disease (UCI Cleveland)
| Architecture | Accuracy | Precision | Recall (Sensitivity) | F1-Score | ROC-AUC | Status |
|---|---|---|---|---|---|---|
| Logistic Regression | 86.89% | 81.25% | 92.86% | 0.8667 | 0.9513 | Evaluated |
| **Random Forest** | **91.80%** | **89.66%** | **92.86%** | **0.9123** | **0.9535** | **PRIMARY** |
| Gradient Boosting | 83.61% | 76.47% | 92.86% | 0.8387 | 0.9481 | Evaluated |

---

## 🛡️ License & Compliance

Open-source educational and clinical research platform under the MIT License.
