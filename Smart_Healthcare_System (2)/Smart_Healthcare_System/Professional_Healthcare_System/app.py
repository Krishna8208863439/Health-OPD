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

# Base Directory for absolute paths (crucial for PythonAnywhere hosting)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthcare_system.db")

# Database Setup
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        blood_group TEXT DEFAULT '',
        allergies TEXT DEFAULT '',
        emergency_contact_name TEXT DEFAULT '',
        emergency_contact_phone TEXT DEFAULT '',
        emergency_contact_relation TEXT DEFAULT '',
        role TEXT DEFAULT 'patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Add new columns to existing users table if they don't exist
    new_user_cols = [
        ('blood_group', 'TEXT DEFAULT ""'),
        ('allergies', 'TEXT DEFAULT ""'),
        ('emergency_contact_name', 'TEXT DEFAULT ""'),
        ('emergency_contact_phone', 'TEXT DEFAULT ""'),
        ('emergency_contact_relation', 'TEXT DEFAULT ""'),
    ]
    for col_name, col_def in new_user_cols:
        try:
            cur.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_def}')
        except Exception:
            pass
    
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
    
    # Alter predictions to add doctor_name if not exists
    try:
        cur.execute("ALTER TABLE predictions ADD COLUMN doctor_name TEXT DEFAULT 'Dr. Amit Sharma, MD'")
    except Exception:
        pass

    # === NEW FEATURE TABLES ===

    # 1. Health Vitals Tracker
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        bp_systolic INTEGER NOT NULL,
        bp_diastolic INTEGER NOT NULL,
        pulse INTEGER NOT NULL,
        temperature REAL NOT NULL,
        weight REAL NOT NULL,
        oxygen_saturation REAL,
        blood_glucose REAL,
        feeling TEXT DEFAULT 'good',
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # 2. Appointments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_name TEXT NOT NULL,
        appt_date TEXT NOT NULL,
        appt_time TEXT NOT NULL,
        appt_type TEXT NOT NULL,
        notes TEXT,
        current_medications TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # 3. Medicine Reminders
    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicine_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        frequency TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT,
        instructions TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # 4. Prescriptions (Doctor Notes)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        patient_id INTEGER,
        patient_name TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        medications TEXT,
        clinical_notes TEXT,
        special_instructions TEXT,
        tests_ordered TEXT,
        severity_assessment TEXT DEFAULT 'mild',
        followup_date TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES users(id)
    )
    """)
    
    # Seed default admin if not exists
    admin_user = cur.execute("SELECT * FROM users WHERE username = 'admin' OR email = 'admin@healthcare.com'").fetchone()
    if not admin_user:
        admin_pass = generate_password_hash("admin123")
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, age, gender, contact, address, role, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin", "admin@healthcare.com", admin_pass, "System Administrator", 35, "Other", "1234567890", "Main Office", "admin", "Delhi"))
        conn.commit()
    
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
                   user['city'] if user['city'] else 'Default', user['smoking'] if user['smoking'] else 'no',
                   user['blood_pressure'] if user['blood_pressure'] else 'normal', user['blood_sugar'] if user['blood_sugar'] else 'normal')
    return None

# Role Decorator
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash(f'Access denied. {role.capitalize()} privileges required.', 'danger')
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
    reports_dir = os.path.join(BASE_DIR, "static", "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    filename = f"Medical_Report_{patient.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
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
    logo_path = os.path.join(BASE_DIR, "static", "assets", "hospital_logo.png")
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
    
    # Assigned Doctor
    doctor_name = prediction_data.get('doctor_name', 'Dr. Amit Sharma, MD')
    c.setFont("Helvetica-Bold", 11)
    c.drawString(320, y_pos - 66, "Assigned Doctor:")
    c.setFont("Helvetica", 11)
    c.drawString(420, y_pos - 66, doctor_name)
    
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
    
    # Signature Box
    y_pos -= 45
    if y_pos < 120:
        y_pos = 120
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor('#cbd5e1'))
    c.line(380, y_pos, 540, y_pos)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(380, y_pos - 14, doctor_name)
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor('#64748b'))
    c.drawString(380, y_pos - 24, "Authorized Medical Signature")
    
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

# PWA Routes
@app.route('/service-worker.js')
def service_worker():
    return send_file(os.path.join(BASE_DIR, 'static', 'service-worker.js'), mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    return send_file(os.path.join(BASE_DIR, 'static', 'manifest.json'), mimetype='application/json')

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return redirect(url_for('index'))

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
                          user['city'] if user['city'] else 'Default', user['smoking'] if user['smoking'] else 'no',
                          user['blood_pressure'] if user['blood_pressure'] else 'normal', user['blood_sugar'] if user['blood_sugar'] else 'normal')
            login_user(user_obj)
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'doctor':
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
    
    # Assign Doctor Name
    try:
        doctor_row = cur.execute("SELECT full_name FROM users WHERE role = 'doctor' ORDER BY RANDOM() LIMIT 1").fetchone()
        doctor_name = doctor_row['full_name'] if doctor_row else "Dr. Amit Sharma, MD"
    except Exception:
        doctor_name = "Dr. Amit Sharma, MD"
    if not doctor_name.startswith("Dr. "):
        doctor_name = "Dr. " + doctor_name
    
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
        'doctor_advice': doctor_advice[severity],
        'doctor_name': doctor_name
    }
    
    pdf_filename = generate_pdf(current_user, prediction_data)
    
    symptom_count = sum(1 for v in symptoms.values() if v == 1)
    
    cur.execute("""
        INSERT INTO predictions (patient_id, patient_name, patient_age, disease, risk_percentage, 
                               health_risk_score, health_risk_category, severity, probability, 
                               symptoms, symptom_count, medicines, hospitals, doctor_advice, pdf_path, doctor_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, current_user.full_name, current_user.age, disease, risk, 
          health_risk['score'], health_risk['category'], prediction_data['severity'], prob, 
          str(symptoms), symptom_count, prediction_data['medicines'], 
          prediction_data['hospitals'], prediction_data['doctor_advice'], pdf_filename, doctor_name))
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
    filepath = os.path.join(BASE_DIR, 'static', 'reports', filename)
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

# =============================================
# FEATURE 1: HEALTH VITALS TRACKER
# =============================================

@app.route('/vitals')
@login_required
def vitals_tracker():
    conn = get_db()
    cur = conn.cursor()
    vitals_history = cur.execute("""
        SELECT * FROM vitals WHERE patient_id = ?
        ORDER BY logged_at DESC LIMIT 30
    """, (current_user.id,)).fetchall()
    conn.close()

    # Build chart data
    vitals_list = list(reversed(vitals_history))
    chart_data = {
        'dates': [v['logged_at'][:10] for v in vitals_list],
        'systolic': [v['bp_systolic'] for v in vitals_list],
        'diastolic': [v['bp_diastolic'] for v in vitals_list],
        'pulse': [v['pulse'] for v in vitals_list],
        'weight': [v['weight'] for v in vitals_list],
        'oxygen': [v['oxygen_saturation'] for v in vitals_list],
    }

    return render_template('vitals_tracker.html',
                           patient=current_user,
                           vitals_history=vitals_history,
                           vitals_chart_data=chart_data)


@app.route('/vitals/log', methods=['POST'])
@login_required
def log_vitals():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO vitals (patient_id, bp_systolic, bp_diastolic, pulse, temperature,
                            weight, oxygen_saturation, blood_glucose, feeling)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id,
        int(request.form.get('bp_systolic', 120)),
        int(request.form.get('bp_diastolic', 80)),
        int(request.form.get('pulse', 72)),
        float(request.form.get('temperature', 98.6)),
        float(request.form.get('weight', 70)),
        float(request.form.get('oxygen_saturation')) if request.form.get('oxygen_saturation') else None,
        float(request.form.get('blood_glucose')) if request.form.get('blood_glucose') else None,
        request.form.get('feeling', 'good')
    ))
    conn.commit()
    conn.close()
    flash('Vitals logged successfully! Keep tracking your health.', 'success')
    return redirect(url_for('vitals_tracker'))


# =============================================
# FEATURE 2: APPOINTMENT BOOKING
# =============================================

@app.route('/appointments')
@login_required
def appointments():
    conn = get_db()
    cur = conn.cursor()
    appts = cur.execute("""
        SELECT * FROM appointments WHERE patient_id = ?
        ORDER BY appt_date DESC, appt_time DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('appointments.html', patient=current_user, appointments=appts, today=today)


@app.route('/appointments/book', methods=['POST'])
@login_required
def book_appointment():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_name, appt_date, appt_time, appt_type, notes, current_medications)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id,
        request.form.get('doctor_name'),
        request.form.get('appt_date'),
        request.form.get('appt_time'),
        request.form.get('appt_type'),
        request.form.get('notes'),
        request.form.get('current_medications')
    ))
    conn.commit()
    conn.close()
    flash('Appointment booked successfully! You will receive a confirmation shortly.', 'success')
    return redirect(url_for('appointments'))


@app.route('/appointments/cancel/<int:appt_id>', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE appointments SET status = 'cancelled'
        WHERE id = ? AND patient_id = ?
    """, (appt_id, current_user.id))
    conn.commit()
    conn.close()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('appointments'))


# =============================================
# FEATURE 3: MEDICINE REMINDERS
# =============================================

@app.route('/reminders')
@login_required
def medicine_reminders():
    conn = get_db()
    cur = conn.cursor()
    reminders = cur.execute("""
        SELECT * FROM medicine_reminders WHERE patient_id = ?
        ORDER BY is_active DESC, created_at DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('medicine_reminders.html', patient=current_user, reminders=reminders, today=today)


@app.route('/reminders/add', methods=['POST'])
@login_required
def add_reminder():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medicine_reminders (patient_id, medicine_name, dosage, reminder_time,
                                        frequency, start_date, end_date, instructions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id,
        request.form.get('medicine_name'),
        request.form.get('dosage'),
        request.form.get('reminder_time'),
        request.form.get('frequency'),
        request.form.get('start_date'),
        request.form.get('end_date') or None,
        request.form.get('instructions')
    ))
    conn.commit()
    conn.close()
    flash('Medicine reminder added successfully!', 'success')
    return redirect(url_for('medicine_reminders'))


@app.route('/reminders/toggle/<int:rem_id>', methods=['POST'])
@login_required
def toggle_reminder(rem_id):
    conn = get_db()
    cur = conn.cursor()
    rem = cur.execute('SELECT is_active FROM medicine_reminders WHERE id = ? AND patient_id = ?',
                      (rem_id, current_user.id)).fetchone()
    if rem:
        new_state = 0 if rem['is_active'] else 1
        cur.execute('UPDATE medicine_reminders SET is_active = ? WHERE id = ?', (new_state, rem_id))
        conn.commit()
    conn.close()
    return redirect(url_for('medicine_reminders'))


@app.route('/reminders/delete/<int:rem_id>', methods=['POST'])
@login_required
def delete_reminder(rem_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM medicine_reminders WHERE id = ? AND patient_id = ?',
                (rem_id, current_user.id))
    conn.commit()
    conn.close()
    flash('Reminder deleted.', 'info')
    return redirect(url_for('medicine_reminders'))


# =============================================
# FEATURE 4: BMI & NUTRITION CALCULATOR
# =============================================

def get_bmi_diet_plan(bmi, health_goal, diet_preference):
    """Generate a personalized diet plan based on BMI, goal and diet preference."""
    # Base diet plans
    balanced_breakfast = ['Oatmeal with fruits and nuts', '2 whole eggs or paneer', 'Green tea or black coffee', 'Whole wheat toast']
    veg_breakfast = ['Poha with vegetables', 'Sprouts salad', 'Milk or soy milk', 'Fruit bowl']
    vegan_breakfast = ['Smoothie bowl with seeds', 'Tofu scramble', 'Oat porridge', 'Fresh fruit']
    low_carb_breakfast = ['Egg omelette with cheese', 'Avocado', 'Greek yogurt', 'Nuts']

    plans = {
        'balanced': {
            'breakfast': balanced_breakfast,
            'lunch': ['Brown rice or roti (2)', 'Dal or chicken curry', 'Salad', 'Curd/yogurt'],
            'snacks': ['Handful of nuts', 'Fruit (apple/banana)', 'Buttermilk'],
            'dinner': ['Chapati (2)', 'Vegetable sabzi', 'Soup', 'Salad'],
            'avoid': ['Fried foods', 'Sugary drinks', 'Processed snacks', 'Excess salt', 'Alcohol']
        },
        'vegetarian': {
            'breakfast': veg_breakfast,
            'lunch': ['Dal tadka + 2 roti', 'Paneer sabzi', 'Raita + salad'],
            'snacks': ['Fruits', 'Roasted chana', 'Lassi'],
            'dinner': ['Khichdi', 'Vegetable curry', 'Curd'],
            'avoid': ['White bread', 'Sugary sweets', 'Deep fried snacks', 'Processed cheese']
        },
        'vegan': {
            'breakfast': vegan_breakfast,
            'lunch': ['Quinoa + lentils', 'Mixed vegetables', 'Chickpea curry'],
            'snacks': ['Hummus with veggies', 'Nuts & seeds', 'Fruits'],
            'dinner': ['Tofu stir-fry', 'Brown rice', 'Steamed vegetables'],
            'avoid': ['Dairy products', 'Processed vegan junk food', 'Excess oil', 'Refined sugar']
        },
        'low_carb': {
            'breakfast': low_carb_breakfast,
            'lunch': ['Grilled chicken or fish', 'Salad with olive oil', 'Boiled eggs'],
            'snacks': ['Cheese', 'Nuts', 'Boiled eggs'],
            'dinner': ['Paneer/chicken', 'Stir-fried vegetables', 'Soup (no noodles)'],
            'avoid': ['Rice', 'Bread', 'Potatoes', 'Sugar', 'Fruit juices']
        },
        'high_protein': {
            'breakfast': ['Protein shake', '3 boiled eggs or paneer', 'Oats', 'Nuts'],
            'lunch': ['Grilled chicken breast 200g', 'Brown rice', 'Broccoli + salad'],
            'snacks': ['Protein bar', 'Paneer cubes', 'Greek yogurt', 'Nuts'],
            'dinner': ['Baked fish or tofu', 'Quinoa', 'Mixed vegetables'],
            'avoid': ['Simple carbs', 'Junk food', 'Alcohol', 'Excess fats']
        }
    }

    plan = plans.get(diet_preference, plans['balanced'])

    # Tips based on BMI and goal
    if bmi < 18.5:
        tips = [
            {'icon': '🍽️', 'title': 'Eat More Frequently', 'text': 'Have 5-6 small meals per day to increase calorie intake.'},
            {'icon': '💪', 'title': 'Strength Training', 'text': 'Focus on resistance exercises to build muscle mass.'},
            {'icon': '🥛', 'title': 'Protein Rich Foods', 'text': 'Include dairy, eggs, nuts and legumes in every meal.'},
            {'icon': '😴', 'title': 'Quality Sleep', 'text': 'Get 7-9 hours of sleep to support muscle growth.'},
        ]
    elif bmi <= 24.9:
        tips = [
            {'icon': '✅', 'title': 'Maintain Balance', 'text': 'You have a healthy weight. Focus on maintaining it with a balanced diet.'},
            {'icon': '🏃', 'title': 'Stay Active', 'text': '150 minutes of moderate exercise per week is recommended.'},
            {'icon': '💧', 'title': 'Hydration', 'text': 'Drink 8-10 glasses of water daily.'},
            {'icon': '🥗', 'title': 'Variety', 'text': 'Eat a rainbow of vegetables and fruits for micronutrients.'},
        ]
    elif bmi <= 29.9:
        tips = [
            {'icon': '📉', 'title': 'Reduce Portions', 'text': 'Reduce portion sizes by 10-15% and avoid second servings.'},
            {'icon': '🚶', 'title': 'Daily Walk', 'text': 'Walk 10,000 steps daily. Start with 30 minutes after meals.'},
            {'icon': '❌', 'title': 'Cut Refined Carbs', 'text': 'Avoid white rice, bread, and sugary beverages.'},
            {'icon': '📊', 'title': 'Track Calories', 'text': 'Use a food diary or app to monitor your daily intake.'},
        ]
    else:
        tips = [
            {'icon': '👨‍⚕️', 'title': 'Consult a Doctor', 'text': 'Obesity increases risk of diabetes and heart disease. Seek medical advice.'},
            {'icon': '🥗', 'title': 'Low Calorie Foods', 'text': 'Fill half your plate with vegetables at every meal.'},
            {'icon': '🚫', 'title': 'Avoid Junk Food', 'text': 'Eliminate processed, fried, and sugary foods completely.'},
            {'icon': '🏊', 'title': 'Low Impact Exercise', 'text': 'Swimming and cycling are gentler on joints for overweight individuals.'},
        ]

    return plan, tips


@app.route('/bmi', methods=['GET', 'POST'])
@login_required
def calculate_bmi():
    bmi_result = None
    form_data = None

    if request.method == 'POST':
        height_cm = float(request.form.get('height_cm', 170))
        weight_kg = float(request.form.get('weight_kg', 70))
        age = int(request.form.get('age', current_user.age))
        activity_level = request.form.get('activity_level', 'moderate')
        health_goal = request.form.get('health_goal', 'maintain')
        diet_preference = request.form.get('diet_preference', 'balanced')

        form_data = {
            'height_cm': height_cm, 'weight_kg': weight_kg, 'age': age,
            'activity_level': activity_level
        }

        # BMI Calculation
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 1)

        # Category
        if bmi < 18.5:
            category, color, bg_color = 'Underweight', '#3b82f6', '#eff6ff'
            description = 'You are underweight. Focus on gaining healthy weight through a nutrient-rich diet.'
        elif bmi <= 24.9:
            category, color, bg_color = 'Normal Weight ✅', '#059669', '#f0fdf4'
            description = 'Great! You have a healthy BMI. Maintain it with balanced diet and exercise.'
        elif bmi <= 29.9:
            category, color, bg_color = 'Overweight', '#d97706', '#fffbeb'
            description = 'You are slightly overweight. A healthy diet and regular exercise can help.'
        else:
            category, color, bg_color = 'Obese', '#dc2626', '#fff1f2'
            description = 'BMI indicates obesity. Please consult a healthcare provider for guidance.'

        # Ideal weight range (using BMI 18.5-24.9)
        ideal_min = round(18.5 * height_m ** 2, 1)
        ideal_max = round(24.9 * height_m ** 2, 1)

        # Daily calorie needs (Mifflin-St Jeor formula)
        if current_user.gender == 'Female':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

        activity_mult = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725, 'extreme': 1.9}
        calories = round(bmr * activity_mult.get(activity_level, 1.55))

        # Adjust for goal
        if health_goal == 'lose_weight':
            calories -= 500
        elif health_goal == 'gain_muscle':
            calories += 300

        water_intake = round(weight_kg * 0.033, 1)
        diet_plan, tips = get_bmi_diet_plan(bmi, health_goal, diet_preference)

        bmi_result = {
            'bmi': bmi, 'category': category, 'color': color, 'bg_color': bg_color,
            'description': description, 'ideal_weight_min': ideal_min,
            'ideal_weight_max': ideal_max, 'calories': calories,
            'water_intake': water_intake, 'diet_plan': diet_plan, 'tips': tips
        }

    return render_template('bmi_calculator.html', patient=current_user,
                           bmi_result=bmi_result, form_data=form_data)


# =============================================
# FEATURE 5: EMERGENCY SOS
# =============================================

@app.route('/emergency-sos')
@login_required
def emergency_sos():
    return render_template('emergency_sos.html', patient=current_user)


# =============================================
# FEATURE 6: PATIENT PROFILE EDIT
# =============================================

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        # Check if email already taken by another user
        new_email = request.form.get('email')
        existing = cur.execute('SELECT id FROM users WHERE email = ? AND id != ?',
                               (new_email, current_user.id)).fetchone()
        if existing:
            flash('Email already in use by another account.', 'danger')
            conn.close()
            return redirect(url_for('edit_profile'))

        cur.execute("""
            UPDATE users SET
                full_name = ?, email = ?, age = ?, gender = ?, contact = ?,
                address = ?, city = ?, smoking = ?, blood_pressure = ?, blood_sugar = ?,
                blood_group = ?, allergies = ?,
                emergency_contact_name = ?, emergency_contact_phone = ?, emergency_contact_relation = ?
            WHERE id = ?
        """, (
            request.form.get('full_name'),
            new_email,
            int(request.form.get('age', current_user.age)),
            request.form.get('gender'),
            request.form.get('contact'),
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('smoking', 'no'),
            request.form.get('blood_pressure', 'normal'),
            request.form.get('blood_sugar', 'normal'),
            request.form.get('blood_group', ''),
            request.form.get('allergies', ''),
            request.form.get('emergency_contact_name', ''),
            request.form.get('emergency_contact_phone', ''),
            request.form.get('emergency_contact_relation', ''),
            current_user.id
        ))
        conn.commit()
        conn.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient_dashboard'))

    # For GET - pass patient with extra fields as a dict-like object
    conn = get_db()
    cur = conn.cursor()
    patient_row = cur.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()
    # Make it accessible via .get()
    patient_dict = dict(patient_row) if patient_row else {}

    class PatientProxy:
        def __init__(self, user, extra):
            self.__dict__.update(vars(user))
            self._extra = extra
        def get(self, key, default=''):
            return self._extra.get(key, default)

    proxy = PatientProxy(current_user, patient_dict)
    return render_template('edit_profile.html', patient=proxy)


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    if new_pw != confirm_pw:
        flash('New passwords do not match!', 'danger')
        return redirect(url_for('edit_profile'))

    conn = get_db()
    cur = conn.cursor()
    user = cur.execute('SELECT password_hash FROM users WHERE id = ?', (current_user.id,)).fetchone()

    if not check_password_hash(user['password_hash'], current_pw):
        flash('Current password is incorrect!', 'danger')
        conn.close()
        return redirect(url_for('edit_profile'))

    cur.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                (generate_password_hash(new_pw), current_user.id))
    conn.commit()
    conn.close()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('edit_profile'))


# =============================================
# FEATURE 7: DOCTOR PRESCRIPTIONS
# =============================================

@app.route('/doctor/prescriptions')
@login_required
@role_required('doctor')
def doctor_prescriptions():
    conn = get_db()
    cur = conn.cursor()
    prescriptions = cur.execute("""
        SELECT * FROM prescriptions WHERE doctor_id = ?
        ORDER BY timestamp DESC
    """, (current_user.id,)).fetchall()
    all_patients = cur.execute("""
        SELECT id, full_name, email FROM users WHERE role = 'patient'
        ORDER BY full_name
    """).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('doctor_prescriptions.html',
                           doctor=current_user,
                           prescriptions=prescriptions,
                           all_patients=all_patients,
                           today=today)


@app.route('/doctor/prescriptions/save', methods=['POST'])
@login_required
@role_required('doctor')
def save_prescription():
    # Build medications string from arrays
    med_names = request.form.getlist('med_name[]')
    med_dosages = request.form.getlist('med_dosage[]')
    med_freqs = request.form.getlist('med_frequency[]')
    med_durations = request.form.getlist('med_duration[]')
    med_instructions = request.form.getlist('med_instructions[]')

    meds_parts = []
    for i, name in enumerate(med_names):
        if name.strip():
            dosage = med_dosages[i] if i < len(med_dosages) else ''
            freq = med_freqs[i] if i < len(med_freqs) else ''
            dur = med_durations[i] if i < len(med_durations) else ''
            inst = med_instructions[i] if i < len(med_instructions) else ''
            meds_parts.append(f"{name} {dosage} - {freq.replace('_', ' ')} for {dur} ({inst})")
    medications_str = ' | '.join(meds_parts)

    # Try to match patient name to a patient_id
    search = request.form.get('patient_name_search', '')
    patient_id = None
    conn = get_db()
    cur = conn.cursor()
    # Extract name from pattern "Name (ID: X)"
    patient_name = search.split(' (ID:')[0].strip()
    p = cur.execute('SELECT id FROM users WHERE full_name = ?', (patient_name,)).fetchone()
    if p:
        patient_id = p['id']

    cur.execute("""
        INSERT INTO prescriptions (doctor_id, patient_id, patient_name, diagnosis, medications,
                                   clinical_notes, special_instructions, tests_ordered,
                                   severity_assessment, followup_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id, patient_id, patient_name,
        request.form.get('diagnosis'),
        medications_str,
        request.form.get('clinical_notes'),
        request.form.get('special_instructions'),
        request.form.get('tests_ordered'),
        request.form.get('severity_assessment', 'mild'),
        request.form.get('followup_date') or None
    ))
    conn.commit()
    conn.close()
    flash('Prescription saved successfully!', 'success')
    return redirect(url_for('doctor_prescriptions'))


# =============================================
# DOCTOR DASHBOARD EXTENSION ROUTES
# =============================================

@app.route('/doctor/appointments')
@login_required
@role_required('doctor')
def doctor_appointments():
    conn = get_db()
    cur = conn.cursor()
    # Fetch all appointments with patient name
    appts = cur.execute("""
        SELECT a.*, u.full_name as patient_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        ORDER BY a.appt_date DESC, a.appt_time DESC
    """).fetchall()
    conn.close()
    return render_template('doctor_appointments.html', appointments=appts)


@app.route('/doctor/appointments/<int:appt_id>/update', methods=['POST'])
@login_required
@role_required('doctor')
def doctor_update_appointment(appt_id):
    status = request.form.get('status')
    if status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('doctor_appointments'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appt_id))
    conn.commit()
    conn.close()
    flash(f'Appointment status updated to {status}!', 'success')
    return redirect(url_for('doctor_appointments'))


@app.route('/doctor/patient-list')
@login_required
@role_required('doctor')
def doctor_patient_list():
    conn = get_db()
    cur = conn.cursor()
    patients = cur.execute("""
        SELECT * FROM predictions
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return render_template('doctor_patient_list.html', patients=patients)


@app.route('/doctor/export-csv')
@login_required
@role_required('doctor')
def doctor_export_csv():
    import csv
    from flask import Response
    
    conn = get_db()
    cur = conn.cursor()
    predictions = cur.execute("""
        SELECT id, patient_name, patient_age, disease, risk_percentage, health_risk_score, severity, timestamp
        FROM predictions
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    
    # Generate CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Patient Name', 'Age', 'Disease', 'Risk %', 'Health Risk Score', 'Severity', 'Timestamp'])
    for r in predictions:
        cw.writerow(list(r))
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=patient_records.csv"}
    )


@app.route('/doctor/live-feed')
@login_required
@role_required('doctor')
def doctor_live_feed():
    conn = get_db()
    cur = conn.cursor()
    recent = cur.execute("""
        SELECT patient_name, disease, patient_age, risk_percentage, severity, timestamp
        FROM predictions
        ORDER BY timestamp DESC LIMIT 10
    """).fetchall()
    conn.close()
    
    cases = []
    for r in recent:
        cases.append({
            'patient_name': r['patient_name'],
            'disease': r['disease'],
            'patient_age': r['patient_age'],
            'risk_percentage': r['risk_percentage'],
            'severity': r['severity'],
            'timestamp': r['timestamp']
        })
    return jsonify(cases)


@app.route('/doctor/pending-count')
@login_required
@role_required('doctor')
def doctor_pending_count():
    conn = get_db()
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'").fetchone()[0] or 0
    conn.close()
    return jsonify({'count': count})


# =============================================
# FEATURE 8: ADMINISTRATIVE PORTAL
# =============================================

@app.route('/admin-dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor()
    
    # KPI statistics
    total_patients = cur.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'").fetchone()[0] or 0
    total_doctors = cur.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'").fetchone()[0] or 0
    total_admins = cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0] or 0
    total_diagnoses = cur.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] or 0
    total_appointments = cur.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] or 0
    total_prescriptions = cur.execute("SELECT COUNT(*) FROM prescriptions").fetchone()[0] or 0
    
    # Recent users
    recent_users = cur.execute("""
        SELECT id, username, email, full_name, role, city 
        FROM users 
        ORDER BY id DESC LIMIT 5
    """).fetchall()
    
    # Recent diagnostic cases
    recent_cases = cur.execute("""
        SELECT patient_name, disease, severity, health_risk_score, timestamp 
        FROM predictions 
        ORDER BY timestamp DESC LIMIT 5
    """).fetchall()

    # Disease frequency for chart analytics
    disease_stats = cur.execute("""
        SELECT disease, COUNT(*) as count 
        FROM predictions 
        GROUP BY disease 
        ORDER BY count DESC LIMIT 5
    """).fetchall()
    
    disease_labels = [row['disease'] for row in disease_stats]
    disease_counts = [row['count'] for row in disease_stats]
    
    conn.close()
    
    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'total_diagnoses': total_diagnoses,
        'total_appointments': total_appointments,
        'total_prescriptions': total_prescriptions,
        'recent_users': recent_users,
        'recent_cases': recent_cases,
        'disease_labels': disease_labels,
        'disease_counts': disease_counts
    }
    
    return render_template('admin_dashboard.html', stats=stats)


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    conn = get_db()
    cur = conn.cursor()
    users = cur.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/save', methods=['POST'])
@login_required
@role_required('admin')
def admin_save_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    age = request.form.get('age') or 30
    gender = request.form.get('gender') or 'Other'
    contact = request.form.get('contact') or ''
    address = request.form.get('address') or ''
    city = request.form.get('city') or 'Default'
    role = request.form.get('role', 'patient')
    
    if not username or not email or not password or not full_name:
        flash('All primary fields are required!', 'danger')
        return redirect(url_for('admin_users'))
        
    conn = get_db()
    cur = conn.cursor()
    
    existing = cur.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username)).fetchone()
    if existing:
        flash('Username or email already exists!', 'danger')
        conn.close()
        return redirect(url_for('admin_users'))
        
    pwd_hash = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users (username, email, password_hash, full_name, age, gender, contact, address, city, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, email, pwd_hash, full_name, age, gender, contact, address, city, role))
    conn.commit()
    conn.close()
    flash(f'Account for {full_name} created successfully as {role.capitalize()}!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_change_role(user_id):
    new_role = request.form.get('role')
    if new_role not in ['patient', 'doctor', 'admin']:
        flash('Invalid role!', 'danger')
        return redirect(url_for('admin_users'))
        
    if user_id == current_user.id:
        flash('You cannot modify your own administrative role!', 'danger')
        return redirect(url_for('admin_users'))
        
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    flash('User role updated successfully!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own administrative account!', 'danger')
        return redirect(url_for('admin_users'))
        
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash('User account deleted successfully from the system!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/predictions')
@login_required
@role_required('admin')
def admin_predictions():
    conn = get_db()
    cur = conn.cursor()
    preds = cur.execute("SELECT * FROM predictions ORDER BY timestamp DESC").fetchall()
    conn.close()
    return render_template('admin_predictions.html', predictions=preds)


@app.route('/admin/predictions/<int:pred_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_prediction(pred_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()
    flash('Diagnostic medical record deleted successfully!', 'success')
    return redirect(url_for('admin_predictions'))


@app.route('/admin/appointments')
@login_required
@role_required('admin')
def admin_appointments():
    conn = get_db()
    cur = conn.cursor()
    appts = cur.execute("""
        SELECT a.*, u.full_name as patient_name 
        FROM appointments a 
        JOIN users u ON a.patient_id = u.id 
        ORDER BY a.appt_date DESC, a.appt_time DESC
    """).fetchall()
    conn.close()
    return render_template('admin_appointments.html', appointments=appts)


@app.route('/admin/appointments/<int:appt_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_appointment(appt_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
    conn.commit()
    conn.close()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('admin_appointments'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
