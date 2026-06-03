# 🏥 Professional Healthcare System - AI Disease Prediction

A comprehensive, professional-grade healthcare management system with AI-powered disease prediction, patient management, doctor dashboard, and automated PDF report generation.

## ✨ Features

### 🔐 Authentication System
- **Sign Up & Login** - Secure user registration and authentication
- **Role-Based Access** - Separate interfaces for Patients and Doctors
- **Password Hashing** - Secure password storage using Werkzeug

### 👨‍⚕️ Patient Features
- **Patient Dashboard** - Personalized dashboard with recent diagnoses
- **Symptom Entry** - Interactive symptom checker with 14 different symptoms
- **AI Disease Prediction** - Machine Learning-powered disease diagnosis
- **Risk Assessment** - Automatic risk percentage calculation (Low/Medium/High)
- **Medical History** - Complete record of all past diagnoses
- **Patient Information** - Name and Age displayed on all pages

### 📊 Doctor Dashboard
- **Analytics Overview** - Total patients, diagnoses, and high-risk cases
- **Interactive Charts** - Disease distribution, severity analysis, monthly trends
- **Recent Cases** - Real-time view of latest patient diagnoses
- **Statistical Insights** - Critical rate and trend analysis

### 💊 Medical Recommendations
- **Real Medicine Names** - Actual pharmaceutical medications (e.g., Omeprazole, Ciprofloxacin)
- **Dosage Information** - Proper dosage and brand names included
- **Severity-Based Treatment** - Different medicines for Low/Medium/High severity
- **Hospital Recommendations** - Real hospital types based on severity level

### 📄 PDF Report Generation
- **Auto-Generated PDFs** - Professional medical reports created automatically
- **Hospital Logo** - Custom hospital branding on every report
- **Hospital Theme Colors** - Professional blue color scheme
- **Complete Information** - Patient details, diagnosis, medicines, hospitals, advice
- **Download Anytime** - Access reports from history page

### 📈 Analytics & Graphs
- **Disease Distribution Chart** - Doughnut chart showing disease prevalence
- **Severity Analysis** - Bar chart of Low/Medium/High risk cases
- **Monthly Trends** - Line graph showing diagnosis trends over time
- **Real-Time Data** - Charts update automatically with new diagnoses

### 🎨 Professional UI
- **Hospital Theme** - Deep blue (#1E3A8A) and bright blue (#3B82F6) colors
- **Modern Design** - Clean, professional medical interface
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Hover effects and transitions
- **Icon Integration** - Font Awesome icons throughout

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Hospital Logo
```bash
python create_logo.py
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access the System
Open your browser and navigate to:
```
http://localhost:5002
```

## 📋 Usage Guide

### For Patients

1. **Sign Up**
   - Click "Sign Up Here" on login page
   - Fill in your details (Name, Email, Age, Gender, Contact)
   - Select "Patient" as role
   - Create account

2. **Login**
   - Enter your email and password
   - Click "Login"

3. **Check Symptoms**
   - Click "Check Symptoms" from dashboard
   - Select all symptoms you're experiencing
   - Click "Analyze Symptoms & Predict Disease"

4. **View Results**
   - See predicted disease and risk level
   - Review recommended medicines
   - Check hospital recommendations
   - Read doctor's advice
   - Download PDF report

5. **View History**
   - Click "History" in navigation
   - See all past diagnoses
   - Download previous reports

### For Doctors

1. **Sign Up as Doctor**
   - Register with "Doctor" role

2. **Access Dashboard**
   - View total patients and diagnoses
   - Monitor high-risk cases
   - Analyze disease distribution
   - Track monthly trends

3. **Review Recent Cases**
   - See latest patient diagnoses
   - Check severity levels
   - Monitor critical cases

## 🗂️ Project Structure

```
Professional_Healthcare_System/
│
├── app.py                      # Main Flask application
├── model.py                    # ML model training
├── medicine_db.py              # Medicine and hospital database
├── create_logo.py              # Hospital logo generator
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── Health.csv                  # Training dataset
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   ├── signup.html            # Registration page
│   ├── patient_dashboard.html # Patient dashboard
│   ├── symptom_entry.html     # Symptom checker
│   ├── result.html            # Diagnosis results
│   ├── history.html           # Medical history
│   └── doctor_dashboard.html  # Doctor analytics
│
└── static/                     # Static files
    ├── assets/                # Images and logos
    │   └── hospital_logo.png  # Hospital logo
    └── reports/               # Generated PDF reports
```

## 🔬 Machine Learning Model

- **Algorithm**: Random Forest Classifier
- **Features**: 14 symptoms
- **Training**: 80-20 train-test split
- **Accuracy**: Displayed on model training

### Symptoms Analyzed
1. Body Pain
2. Hollow Feeling
3. Cold & Cough
4. Cough
5. Fever
6. Chest Pain
7. Breathing Problem
8. Throat Pain
9. Headache
10. Stomach Pain
11. Diarrhea
12. Vomiting
13. Back Pain
14. Swollen Feet

## 💊 Medicine Database

The system includes real pharmaceutical medications for various diseases:

- **Stomach Infection**: Omeprazole, Ciprofloxacin, Metronidazole, ORS
- **Pneumonia**: Amoxicillin, Azithromycin, Levofloxacin, Albuterol
- **Common Cold**: Acetaminophen, Pseudoephedrine, Vitamin C
- **Influenza**: Oseltamivir (Tamiflu), Ibuprofen
- **Bronchitis**: Azithromycin, Albuterol Inhaler, Prednisone
- **Migraine**: Sumatriptan (Imitrex), Naproxen
- **Gastroenteritis**: ORS, Loperamide, Probiotics
- **Hypertension**: Amlodipine, Lisinopril, Metoprolol
- **Diabetes**: Metformin, Glimepiride, Insulin
- **Asthma**: Albuterol Inhaler, Fluticasone, Montelukast

## 🏥 Hospital Recommendations

- **Low Risk**: Primary Care Clinic, Community Health Center
- **Medium Risk**: City General Hospital, Regional Medical Center
- **High Risk**: Tertiary Care Hospital, University Medical Center ICU

## 🎨 Color Scheme

- **Primary Blue**: #1E3A8A (Deep Blue)
- **Accent Blue**: #3B82F6 (Bright Blue)
- **Success Green**: #10B981
- **Warning Orange**: #F59E0B
- **Danger Red**: #EF4444

## 📊 Database Schema

### Users Table
- id, username, email, password_hash
- full_name, age, gender, contact, address
- role (patient/doctor), created_at

### Predictions Table
- id, patient_id, patient_name, patient_age
- disease, risk_percentage, severity, probability
- symptoms, medicines, hospitals, doctor_advice
- pdf_path, timestamp

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- Role-based access control
- SQL injection prevention with parameterized queries
- CSRF protection

## 🌟 Key Highlights

✅ Complete authentication system (Sign Up & Login)
✅ Patient name and age on all pages
✅ Real medicine names with dosages
✅ Real hospital recommendations
✅ Auto PDF generation with hospital logo
✅ Professional hospital theme colors
✅ Doctor dashboard with analytics
✅ Interactive charts and graphs
✅ Medical history tracking
✅ Download PDF reports
✅ Responsive design
✅ Professional UI/UX

## 📝 Notes

- The system uses SQLite database (healthcare_system.db)
- PDF reports are stored in static/reports/
- Hospital logo is in static/assets/
- All passwords are securely hashed
- Session timeout is 2 hours

## 🆘 Support

For issues or questions:
- Check the console for error messages
- Ensure all dependencies are installed
- Verify Python version (3.8+)
- Make sure Health.csv is present

## 📄 License

This project is for educational and demonstration purposes.

## 👨‍💻 Developer

Professional Healthcare System - 2026
AI-Powered Disease Prediction & Management

---

**🏥 HealthCare Plus Medical Center**
*Advanced AI-Powered Disease Prediction & Treatment*
📞 +1-800-HEALTH-911 | 📧 care@healthcareplus.com
