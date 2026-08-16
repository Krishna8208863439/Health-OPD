# HealthPredict AI — Datasets Documentation

This directory houses the authentic machine learning datasets used for training and evaluating clinical risk prediction models.

## 1. Diabetes Dataset
- **Source**: UCI Machine Learning Repository / National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)
- **Dataset**: Pima Indians Diabetes Database
- **Mirror**: `https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv`
- **File**: `ml/datasets/diabetes.csv`
- **Attributes (9 columns)**:
  1. `Pregnancies`: Number of times pregnant
  2. `Glucose`: Plasma glucose concentration (2 hours in an oral glucose tolerance test)
  3. `BloodPressure`: Diastolic blood pressure (mm Hg)
  4. `SkinThickness`: Triceps skin fold thickness (mm)
  5. `Insulin`: 2-Hour serum insulin (mu U/ml)
  6. `BMI`: Body mass index (weight in kg/(height in m)^2)
  7. `DiabetesPedigreeFunction`: Diabetes pedigree function
  8. `Age`: Age (years)
  9. `Outcome`: Class variable (0: Non-Diabetic, 1: Diabetic)
- **Zero-Value Treatment**: Zeros in `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, and `BMI` represent missing physiological measurements and are imputed with training-set medians.

---

## 2. Heart Disease Dataset
- **Source**: UCI Machine Learning Repository (Cleveland Heart Disease Database)
- **Mirror**: `https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data`
- **File**: `ml/datasets/heart.csv`
- **Attributes (14 columns)**: Age, Sex, Chest Pain Type (cp), Resting BP (trestbps), Cholesterol (chol), Fasting Blood Sugar (fbs), Resting ECG (restecg), Max Heart Rate (thalach), Exercise Induced Angina (exang), ST Depression (oldpeak), ST Slope (slope), Major Vessels (ca), Thalassemia (thal), Target / Outcome (0: Normal, 1: Disease).
