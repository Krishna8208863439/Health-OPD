from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
import io
from functools import wraps
from model import train_model
from medicine_db import MEDICINE_DATABASE, HOSPITAL_DATABASE
from risk_calculator import calculate_health_risk_score, get_risk_recommendations
from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'healthcare-secret-key-2026'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Train ML Model
model, disease_map, accuracy = train_model()

# Database Setup
def get_db():
    conn = sqlite3.connect("healthcare_system.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT,
        contact TEXT,
        address TEXT,
        city TEXT DEFAULT 'Default',
        smoking TEXT DEFAULT 'no',
        blood_pressure TEXT DEFAULT 'normal',
        blood_sugar TEXT DEFAULT 'normal',
        role TEXT DEFAULT 'patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        patient_name TEXT NOT NULL,
        patient_age INTEGER NOT NULL,
        disease TEXT NOT NULL,
        risk_percentage REAL NOT NULL,
        health_risk_score INTEGER NOT NULL,
        health_risk_category TEXT NOT NULL,
        severity TEXT NOT NULL,
        probability REAL NOT NULL,
        symptoms TEXT NOT NULL,
        symptom_count INTEGER NOT NULL,
        medicines TEXT NOT NULL,
        hospitals TEXT NOT NULL,
        doctor_advice TEXT NOT NULL,
        pdf_path TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

# User Class
class User(UserMixin):
    def __init__(self, id, username, email, full_name, age, gender, contact, address, role, city='Default', smoking='no', blood_pressure='normal', blood_sugar='normal'):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.age = age
        self.gender = gender
        self.contact = contact
        self.address = address
        self.role = role
        self.city = city
        self.smoking = smoking
        self.blood_pressure = blood_pressure
        self.blood_sugar = blood_sugar

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    user = cur.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'], 
                   user['full_name'], user['age'], user['gender'],
                   user['contact'], user['address'], user['role'],
                   user.get('city', 'Default'), user.get('smoking', 'no'),
                   user.get('blood_pressure', 'normal'), user.get('blood_sugar', 'normal'))
    return None

# Role Decorator
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied. Doctor privileges required.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper Functions
def calculate_risk(prob):
    risk = round(prob * 100, 1)
    if risk <= 40:
        return risk, "LOW", "🟢"
    elif risk <= 70:
        return risk, "MEDIUM", "🟡"
    else:
        return risk, "HIGH", "🔴"

def generate_pdf(patient, prediction_data):
    """Generate professional PDF with hospital logo and branding"""
    if not os.path.exists("static/reports"):
        os.makedirs("static/reports")
    
    filename = f"Medical_Report_{patient.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("static/reports", filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Hospital Theme Colors
    primary_color = colors.HexColor('#1E3A8A')  # Deep Blue
    accent_color = colors.HexColor('#3B82F6')   # Bright Blue
    success_color = colors.HexColor('#10B981')  # Green
    warning_color = colors.HexColor('#F59E0B')  # Orange
    danger_color = colors.HexColor('#EF4444')   # Red
    
    # Header Background
    c.setFillColor(primary_color)
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    
    # Hospital Logo
    logo_path = "static/assets/hospital_logo.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 110, width=80, height=80, preserveAspectRatio=True, mask='auto')
    
    # Hospital Name and Details
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(140, height - 50, "HealthCare Plus Medical Center")
    c.setFont("Helvetica", 11)
    c.drawString(140, height - 70, "Advanced AI-Powered Disease Prediction & Treatment")
    c.drawString(140, height - 88, "📞 +1-800-HEALTH-911  |  📧 care@healthcareplus.com")
    c.drawString(140, height - 104, "🏥 123 Medical Plaza, Healthcare City, HC 12345")
    
    # Report Title
    y_pos = height - 150
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, y_pos, "MEDICAL DIAGNOSIS REPORT")
    
    # Report ID and Date
    c.setFont("Helvetica", 10)
    c.drawString(400, y_pos, f"Report ID: MR-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    c.drawString(400, y_pos - 15, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    c.drawString(400, y_pos - 30, f"Time: {datetime.now().strftime('%I:%M %p')}")
    
    # Patient Information Box
    y_pos -= 60
    c.setFillColor(accent_color)
    c.setStrokeColor(accent_color)
    c.setLineWidth(2)
    c.rect(40, y_pos - 80, 515, 85, fill=False, stroke=True)
    
    c.setFillColor(accent_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y_pos - 10, "PATIENT INFORMATION")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_pos - 30, "Name:")
    c.setFont("Helvetica", 11)
    c.drawString(150, y_pos - 30, patient.full_name)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_pos - 48, "Age:")
    c.setFont("Helvetica", 11)
    c.drawString(150, y_pos - 48, f"{patient.age} years")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_pos - 66, "Contact:")
    c.setFont("Helvetica", 11)
    c.drawString(150, y_pos - 66, patient.contact or 'N/A')
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(320, y_pos - 30, "Gender:")
    c.setFont("Helvetica", 11)
    c.drawString(420, y_pos - 30, patient.gender or 'N/A')
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(320, y_pos - 48, "Patient ID:")
    c.setFont("Helvetica", 11)
    c.drawString(420, y_pos - 48, f"PT-{str(patient.id).zfill(6)}")
    
    # Diagnosis Results
    y_pos -= 110
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y_pos, "DIAGNOSIS RESULTS")
    
    y_pos -= 25
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Predicted Disease:")
    c.setFont("Helvetica", 12)
    c.drawString(200, y_pos, prediction_data['disease'])
    
    y_pos -= 22
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Risk Percentage:")
    c.setFont("Helvetica", 12)
    c.drawString(200, y_pos, f"{prediction_data['risk_percentage']}%")
    
    y_pos -= 22
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Severity Level:")
    
    severity_text = prediction_data['severity']
    if 'LOW' in severity_text:
        c.setFillColor(success_color)
    elif 'MEDIUM' in severity_text:
        c.setFillColor(warning_color)
    else:
        c.setFillColor(danger_color)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, y_pos, severity_text)
    
    # Recommended Medicines
    y_pos -= 35
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y_pos, "RECOMMENDED MEDICINES")
    
    medicines = prediction_data['medicines'].split(',')
    for i, med in enumerate(medicines[:6], 1):
        y_pos -= 18
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, f"{i}. {med.strip()}")
    
    # Hospital Recommendations
    y_pos -= 30
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y_pos, "RECOMMENDED HOSPITALS")
    
    hospitals = prediction_data['hospitals'].split(',')
    for i, hosp in enumerate(hospitals[:4], 1):
        y_pos -= 18
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, f"{i}. {hosp.strip()}")
    
    # Doctor's Advice
    y_pos -= 30
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y_pos, "DOCTOR'S ADVICE")
    
    y_pos -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    
    advice_text = prediction_data['doctor_advice']
    max_width = 500
    words = advice_text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if c.stringWidth(test_line, "Helvetica", 10) < max_width:
            line = test_line
        else:
            c.drawString(50, y_pos, line)
            y_pos -= 14
            line = word + " "
    if line:
        c.drawString(50, y_pos, line)
    
    # Footer
    c.setFillColor(primary_color)
    c.rect(0, 0, width, 60, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, 35, "HealthCare Plus Medical Center")
    c.setFont("Helvetica", 9)
    c.drawString(40, 20, "24/7 Emergency Services | Accredited by National Health Board")
    c.drawString(40, 8, "This is a computer-generated report. For queries, contact: support@healthcareplus.com")
    
    c.save()
    return filename

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        city = request.form.get('city', 'Default')
        smoking = request.form.get('smoking', 'no')
        blood_pressure = request.form.get('blood_pressure', 'normal')
        blood_sugar = request.form.get('blood_sugar', 'normal')
        role = request.form.get('role', 'patient')
        
        conn = get_db()
        cur = conn.cursor()
        
        existing_user = cur.execute("SELECT * FROM users WHERE email = ? OR username = ?", 
                                   (email, username)).fetchone()
        if existing_user:
            flash('Email or username already exists!', 'danger')
            conn.close()
            return redirect(url_for('signup'))
        
        password_hash = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, age, gender, contact, address, city, smoking, blood_pressure, blood_sugar, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, full_name, age, gender, contact, address, city, smoking, blood_pressure, blood_sugar, role))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        user = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['email'],
                          user['full_name'], user['age'], user['gender'],
                          user['contact'], user['address'], user['role'],
                          user.get('city', 'Default'), user.get('smoking', 'no'),
                          user.get('blood_pressure', 'normal'), user.get('blood_sugar', 'normal'))
            login_user(user_obj)
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            if user['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/patient-dashboard')
@login_required
def patient_dashboard():
    conn = get_db()
    cur = conn.cursor()
    recent_predictions = cur.execute("""
        SELECT * FROM predictions 
        WHERE patient_id = ? 
        ORDER BY timestamp DESC LIMIT 5
    """, (current_user.id,)).fetchall()
    conn.close()
    
    return render_template('patient_dashboard.html', patient=current_user, recent_predictions=recent_predictions)

@app.route('/symptom-entry')
@login_required
def symptom_entry():
    return render_template('symptom_entry.html', patient=current_user)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    symptoms = {
        'bodypain': int(request.form.get('bodypain', 0)),
        'Hollow': int(request.form.get('Hollow', 0)),
        'cold and cough': int(request.form.get('cold_cough', 0)),
        'cough': int(request.form.get('cough', 0)),
        'fever': int(request.form.get('fever', 0)),
        'chest pain': int(request.form.get('chest_pain', 0)),
        'breathing problem': int(request.form.get('breathing_problem', 0)),
        'Throat pain': int(request.form.get('throat_pain', 0)),
        'head pain': int(request.form.get('head_pain', 0)),
        'stomach pain': int(request.form.get('stomach_pain', 0)),
        'diarrhea': int(request.form.get('diarrhea', 0)),
        'omitting': int(request.form.get('omitting', 0)),
        'back pain': int(request.form.get('back_pain', 0)),
        'Swollen feet': int(request.form.get('swollen_feet', 0))
    }
    
    df = pd.DataFrame([list(symptoms.values())], columns=list(symptoms.keys()))
    
    pid = model.predict(df)[0]
    prob = max(model.predict_proba(df)[0])
    
    risk, severity, icon = calculate_risk(prob)
    disease = disease_map[pid]
    
    # Get past history count
    conn = get_db()
    cur = conn.cursor()
    past_history_count = cur.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id = ?", 
        (current_user.id,)
    ).fetchone()[0]
    
    # Calculate comprehensive health risk score
    patient_data = {
        'age': current_user.age,
        'smoking': current_user.smoking,
        'blood_pressure': current_user.blood_pressure,
        'blood_sugar': current_user.blood_sugar
    }
    
    health_risk = calculate_health_risk_score(
        patient_data, 
        symptoms, 
        f"{severity} {icon}",
        past_history_count
    )
    
    # Get hospital filters from form
    hospital_type = request.form.get('hospital_type')  # Government/Private
    max_distance = request.form.get('max_distance')
    if max_distance:
        max_distance = float(max_distance)
    
    # Find hospitals
    hospitals_list = find_hospitals(
        city=current_user.city,
        hospital_type=hospital_type,
        disease=disease,
        max_distance=max_distance
    )
    
    medicines = MEDICINE_DATABASE.get(disease, {}).get(severity, ["Consult Doctor"])
    
    doctor_advice = {
        "LOW": "Monitor symptoms at home. Stay hydrated, get adequate rest. Consult if symptoms worsen.",
        "MEDIUM": "Consult a doctor within 24 hours. Follow prescribed medications and monitor closely.",
        "HIGH": "Seek immediate medical attention. Visit emergency or call ambulance if severe."
    }
    
    prediction_data = {
        'disease': disease,
        'risk_percentage': risk,
        'health_risk_score': health_risk['score'],
        'health_risk_category': health_risk['category'],
        'health_risk_color': health_risk['color'],
        'health_risk_icon': health_risk['icon'],
        'severity': f"{severity} {icon}",
        'probability': prob,
        'medicines': ', '.join(medicines),
        'hospitals': ', '.join([h['name'] for h in hospitals_list[:5]]),
        'doctor_advice': doctor_advice[severity]
    }
    
    pdf_filename = generate_pdf(current_user, prediction_data)
    
    symptom_count = sum(1 for v in symptoms.values() if v == 1)
    
    cur.execute("""
        INSERT INTO predictions (patient_id, patient_name, patient_age, disease, risk_percentage, 
                               health_risk_score, health_risk_category, severity, probability, 
                               symptoms, symptom_count, medicines, hospitals, doctor_advice, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, current_user.full_name, current_user.age, disease, risk, 
          health_risk['score'], health_risk['category'], prediction_data['severity'], prob, 
          str(symptoms), symptom_count, prediction_data['medicines'], 
          prediction_data['hospitals'], prediction_data['doctor_advice'], pdf_filename))
    conn.commit()
    conn.close()
    
    # Get recommendations
    recommendations = get_risk_recommendations(health_risk['score'])
    
    return render_template('result_enhanced.html', 
                         patient=current_user,
                         prediction=prediction_data,
                         health_risk=health_risk,
                         recommendations=recommendations,
                         pdf_file=pdf_filename,
                         medicines=medicines,
                         hospitals=hospitals_list,
                         get_maps_url=get_google_maps_url,
                         get_directions_url=get_directions_url)

@app.route('/history')
@login_required
def history():
    conn = get_db()
    cur = conn.cursor()
    predictions = cur.execute("""
        SELECT * FROM predictions 
        WHERE patient_id = ? 
        ORDER BY timestamp DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    
    return render_template('history.html', patient=current_user, predictions=predictions)

@app.route('/download/<filename>')
@login_required
def download_pdf(filename):
    filepath = os.path.join('static/reports', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    flash('File not found!', 'danger')
    return redirect(url_for('history'))

@app.route('/doctor-dashboard')
@login_required
@role_required('doctor')
def doctor_dashboard():
    conn = get_db()
    cur = conn.cursor()
    
    total_patients = cur.execute("SELECT COUNT(DISTINCT patient_id) FROM predictions").fetchone()[0]
    total_predictions = cur.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    high_risk = cur.execute("SELECT COUNT(*) FROM predictions WHERE severity LIKE '%HIGH%'").fetchone()[0]
    
    # Daily patient count (today)
    today_count = cur.execute("""
        SELECT COUNT(DISTINCT patient_id) FROM predictions 
        WHERE DATE(timestamp) = DATE('now')
    """).fetchone()[0]
    
    # High-risk patients (health risk score >= 60)
    high_risk_patients = cur.execute("""
        SELECT DISTINCT patient_name, patient_age, disease, health_risk_score, 
               health_risk_category, timestamp
        FROM predictions 
        WHERE health_risk_score >= 60
        ORDER BY health_risk_score DESC, timestamp DESC
        LIMIT 20
    """).fetchall()
    
    recent_cases = cur.execute("""
        SELECT * FROM predictions 
        ORDER BY timestamp DESC LIMIT 10
    """).fetchall()
    
    # Most common diseases
    disease_stats = cur.execute("""
        SELECT disease, COUNT(*) as count 
        FROM predictions 
        GROUP BY disease 
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    # Age-wise disease distribution
    age_disease_stats = cur.execute("""
        SELECT 
            CASE 
                WHEN patient_age < 18 THEN 'Under 18'
                WHEN patient_age < 30 THEN '18-29'
                WHEN patient_age < 45 THEN '30-44'
                WHEN patient_age < 60 THEN '45-59'
                ELSE '60+'
            END as age_group,
            disease,
            COUNT(*) as count
        FROM predictions
        GROUP BY age_group, disease
        ORDER BY age_group, count DESC
    """).fetchall()
    
    severity_stats = cur.execute("""
        SELECT 
            CASE 
                WHEN severity LIKE '%LOW%' THEN 'Low'
                WHEN severity LIKE '%MEDIUM%' THEN 'Medium'
                WHEN severity LIKE '%HIGH%' THEN 'High'
            END as severity_level,
            COUNT(*) as count
        FROM predictions
        GROUP BY severity_level
    """).fetchall()
    
    # Average health risk score
    avg_risk_score = cur.execute("""
        SELECT AVG(health_risk_score) FROM predictions
    """).fetchone()[0] or 0
    
    conn.close()
    
    stats = {
        'total_patients': total_patients,
        'total_predictions': total_predictions,
        'high_risk': high_risk,
        'today_count': today_count,
        'avg_risk_score': round(avg_risk_score, 1),
        'high_risk_patients': high_risk_patients,
        'recent_cases': recent_cases,
        'disease_stats': disease_stats,
        'age_disease_stats': age_disease_stats,
        'severity_stats': severity_stats
    }
    
    return render_template('doctor_dashboard_enhanced.html', doctor=current_user, stats=stats)

@app.route('/analytics-data')
@login_required
@role_required('doctor')
def analytics_data():
    conn = get_db()
    cur = conn.cursor()
    
    disease_data = cur.execute("""
        SELECT disease, COUNT(*) as count 
        FROM predictions 
        GROUP BY disease 
        ORDER BY count DESC LIMIT 10
    """).fetchall()
    
    severity_data = cur.execute("""
        SELECT 
            CASE 
                WHEN severity LIKE '%LOW%' THEN 'Low Risk'
                WHEN severity LIKE '%MEDIUM%' THEN 'Medium Risk'
                WHEN severity LIKE '%HIGH%' THEN 'High Risk'
            END as severity_level,
            COUNT(*) as count
        FROM predictions
        GROUP BY severity_level
    """).fetchall()
    
    monthly_data = cur.execute("""
        SELECT strftime('%Y-%m', timestamp) as month, COUNT(*) as count
        FROM predictions
        GROUP BY month
        ORDER BY month DESC LIMIT 6
    """).fetchall()
    
    # Age-wise distribution
    age_data = cur.execute("""
        SELECT 
            CASE 
                WHEN patient_age < 18 THEN 'Under 18'
                WHEN patient_age < 30 THEN '18-29'
                WHEN patient_age < 45 THEN '30-44'
                WHEN patient_age < 60 THEN '45-59'
                ELSE '60+'
            END as age_group,
            COUNT(*) as count
        FROM predictions
        GROUP BY age_group
        ORDER BY 
            CASE age_group
                WHEN 'Under 18' THEN 1
                WHEN '18-29' THEN 2
                WHEN '30-44' THEN 3
                WHEN '45-59' THEN 4
                ELSE 5
            END
    """).fetchall()
    
    # Daily patient trend (last 7 days)
    daily_data = cur.execute("""
        SELECT DATE(timestamp) as date, COUNT(DISTINCT patient_id) as count
        FROM predictions
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY date
        ORDER BY date
    """).fetchall()
    
    conn.close()
    
    return jsonify({
        'diseases': {
            'labels': [row[0] for row in disease_data],
            'data': [row[1] for row in disease_data]
        },
        'severity': {
            'labels': [row[0] for row in severity_data],
            'data': [row[1] for row in severity_data]
        },
        'monthly': {
            'labels': [row[0] for row in monthly_data][::-1],
            'data': [row[1] for row in monthly_data][::-1]
        },
        'age': {
            'labels': [row[0] for row in age_data],
            'data': [row[1] for row in age_data]
        },
        'daily': {
            'labels': [row[0] for row in daily_data],
            'data': [row[1] for row in daily_data]
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)
