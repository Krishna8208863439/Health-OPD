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
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
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
        doctor_name TEXT DEFAULT 'Dr. Amit Sharma, MD',
        doctor_phone TEXT DEFAULT '',
        referred_hospital TEXT DEFAULT '',
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)
    
    # Alter predictions to add columns if not exists (for backward compatibility)
    try:
        cur.execute("ALTER TABLE predictions ADD COLUMN doctor_name TEXT DEFAULT 'Dr. Amit Sharma, MD'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE predictions ADD COLUMN doctor_phone TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE predictions ADD COLUMN referred_hospital TEXT DEFAULT ''")
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
        hospital_name TEXT DEFAULT 'City General Hospital',
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # Alter appointments to add hospital_name if not exists (for backward compatibility)
    try:
        cur.execute("ALTER TABLE appointments ADD COLUMN hospital_name TEXT DEFAULT 'City General Hospital'")
    except Exception:
        pass

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
    
    # === FEATURE TABLES ===

    # 5. Notifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # 6. Messages (Patient <-> Doctor)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (recipient_id) REFERENCES users(id)
    )
    """)

    # 7. Doctor Availability Slots
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctor_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        slot_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        is_booked INTEGER DEFAULT 0,
        patient_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hospital_name TEXT DEFAULT 'City General Hospital',
        FOREIGN KEY (doctor_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # Alter doctor_slots to add hospital_name if not exists (for backward compatibility)
    try:
        cur.execute("ALTER TABLE doctor_slots ADD COLUMN hospital_name TEXT DEFAULT 'City General Hospital'")
    except Exception:
        pass

    # 8. Second Opinions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS second_opinions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        prediction_id INTEGER,
        request_note TEXT,
        doctor_id INTEGER,
        doctor_note TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id),
        FOREIGN KEY (doctor_id) REFERENCES users(id)
    )
    """)

    # 9. Chatbot Logs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
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

    # Seed default specialist doctors if not exist
    DEFAULT_DOCTORS = [
        ("dr_general",  "dr.general@healthcare.com",  "Dr. Rajesh Kumar",   42, "Male",   "General Physician",    "Mumbai"),
        ("dr_cardio",   "dr.cardio@healthcare.com",   "Dr. Priya Sharma",   39, "Female", "Cardiologist",         "Mumbai"),
        ("dr_neuro",    "dr.neuro@healthcare.com",    "Dr. Amit Patel",     47, "Male",   "Neurologist",          "Delhi"),
        ("dr_ortho",    "dr.ortho@healthcare.com",    "Dr. Meena Iyer",     44, "Female", "Orthopedist",          "Bangalore"),
        ("dr_pulmo",    "dr.pulmo@healthcare.com",    "Dr. Kiran Rao",      51, "Male",   "Pulmonologist",        "Chennai"),
        ("dr_gastro",   "dr.gastro@healthcare.com",   "Dr. Sunita Nair",    38, "Female", "Gastroenterologist",   "Hyderabad"),
    ]
    doctor_pass = generate_password_hash("doctor123")
    doctor_ids = {}
    for uname, email, fname, age, gender, spec, city in DEFAULT_DOCTORS:
        existing = cur.execute("SELECT id FROM users WHERE username = ?", (uname,)).fetchone()
        if not existing:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, full_name, age, gender, contact, address, role, city)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'doctor', ?)
            """, (uname, email, doctor_pass, fname, age, gender, "+91-9000000000", spec + " Clinic", city))
            conn.commit()
        doc_row = cur.execute("SELECT id FROM users WHERE username = ?", (uname,)).fetchone()
        if doc_row:
            doctor_ids[uname] = doc_row['id']

    # Seed sample doctor availability slots if none exist
    total_slots = cur.execute("SELECT COUNT(*) FROM doctor_slots").fetchone()[0]
    if total_slots == 0 and doctor_ids:
        from datetime import date, timedelta
        slot_configs = [
            ("dr_general", "Kokilaben Dhirubhai Ambani Hospital", 1, "09:00", "09:30"),
            ("dr_general", "Kokilaben Dhirubhai Ambani Hospital", 2, "10:00", "10:30"),
            ("dr_cardio",  "Lilavati Hospital",                  1, "11:00", "11:30"),
            ("dr_cardio",  "Lilavati Hospital",                  3, "14:00", "14:30"),
            ("dr_neuro",   "All India Institute of Medical Sciences (AIIMS)", 2, "09:30", "10:00"),
            ("dr_ortho",   "Manipal Hospital",                   1, "10:00", "10:30"),
            ("dr_pulmo",   "Apollo Hospitals",                   4, "08:00", "08:30"),
            ("dr_gastro",  "Apollo Hospitals",                   2, "15:00", "15:30"),
        ]
        today = date.today()
        for uname, hosp, days_ahead, start, end in slot_configs:
            if uname in doctor_ids:
                slot_date = (today + timedelta(days=days_ahead)).isoformat()
                cur.execute("""
                    INSERT INTO doctor_slots (doctor_id, slot_date, start_time, end_time, is_booked, hospital_name)
                    VALUES (?, ?, ?, ?, 0, ?)
                """, (doctor_ids[uname], slot_date, start, end, hosp))
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
        
    user_lat = request.form.get('user_lat')
    user_lng = request.form.get('user_lng')
    try:
        user_lat = float(user_lat) if user_lat else None
    except ValueError:
        user_lat = None
        
    try:
        user_lng = float(user_lng) if user_lng else None
    except ValueError:
        user_lng = None
    
    # Find hospitals
    hospitals_list = find_hospitals(
        city=current_user.city,
        hospital_type=hospital_type,
        disease=disease,
        max_distance=max_distance,
        user_lat=user_lat,
        user_lng=user_lng
    )
    
    medicines = MEDICINE_DATABASE.get(disease, {}).get(severity, ["Consult Doctor"])
    
    # Referred Hospital and Doctor Assignment
    if hospitals_list:
        referred_hospital = hospitals_list[0]['name']
        doctor_phone = hospitals_list[0]['phone']
    else:
        referred_hospital = "City General Hospital"
        doctor_phone = "+91-XXX-XXX-XXXX"

    # Map diseases to specialties and doctor names
    specialty_docs = {
        "Cardiology": ["Dr. Devi Shetty, MS", "Dr. Naresh Trehan, MD", "Dr. K. K. Talwar, DM"],
        "Oncology": ["Dr. Suresh Advani, MD", "Dr. Rajendra Badwe, MS", "Dr. S. H. Advani, MD"],
        "Neurology": ["Dr. Ashok Panagariya, DM", "Dr. K. Sridhar, MCh", "Dr. Mukul Varma, DM"],
        "General Medicine": ["Dr. Sandeep Budhiraja, MD", "Dr. Randeep Guleria, DM", "Dr. Rajesh Chawla, MD"],
        "Emergency": ["Dr. Amit Sharma, MD", "Dr. S. K. Sarin, DM", "Dr. Balram Bhargava, DM"]
    }
    
    # Map diseases to specialties
    disease_specialty_map = {
        "Pneumonia": "Emergency",
        "Pneumonia or TB": "Emergency", 
        "Pneumonia or TB or COVID": "Emergency",
        "Bronchitis": "Emergency",
        "Influenza": "Emergency",
        "Seasonal Influenza": "Emergency",
        "Asthma": "Emergency",
        "Stomach Infection": "General Medicine",
        "Gastroenteritis": "General Medicine",
        "Food Poisoning": "General Medicine",
        "Typhoid Fever": "General Medicine",
        "Migraine": "Neurology",
        "Hypertension": "Cardiology",
        "Diabetes": "General Medicine",
        "Common Cold": "General Medicine",
        "cold and cough": "General Medicine",
        "Dengue": "Emergency",
        "Kidney Infection or Stone": "General Medicine",
        "Allergic Side Effects": "General Medicine",
        "Acidity": "General Medicine"
    }
    
    spec = disease_specialty_map.get(disease, "General Medicine")
    doc_list = specialty_docs.get(spec, specialty_docs["General Medicine"])
    
    # Use referred_hospital hash to select a deterministic doctor from the list
    h_idx = sum(ord(c) for c in referred_hospital) % len(doc_list)
    doctor_name = doc_list[h_idx]
    
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
        'doctor_name': doctor_name,
        'doctor_phone': doctor_phone,
        'referred_hospital': referred_hospital
    }
    
    pdf_filename = generate_pdf(current_user, prediction_data)
    
    symptom_count = sum(1 for v in symptoms.values() if v == 1)
    
    cur.execute("""
        INSERT INTO predictions (patient_id, patient_name, patient_age, disease, risk_percentage, 
                               health_risk_score, health_risk_category, severity, probability, 
                               symptoms, symptom_count, medicines, hospitals, doctor_advice, pdf_path, doctor_name, doctor_phone, referred_hospital)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, current_user.full_name, current_user.age, disease, risk, 
          health_risk['score'], health_risk['category'], prediction_data['severity'], prob, 
          str(symptoms), symptom_count, prediction_data['medicines'], 
          prediction_data['hospitals'], prediction_data['doctor_advice'], pdf_filename, doctor_name, doctor_phone, referred_hospital))
    
    # Auto-generate notification for the user
    notif_title = f"New AI Prediction: {disease}"
    notif_body = f"Calculated {risk}% risk for {disease}."
    notif_type = "info"
    if health_risk['score'] >= 70 or 'high' in prediction_data['severity'].lower():
        notif_title = f"🚨 High Risk Alert: {disease}"
        notif_body = f"Critical concern! Calculated {risk}% risk for {disease}. Please consult a doctor immediately."
        notif_type = "danger"
    elif health_risk['score'] >= 40 or 'medium' in prediction_data['severity'].lower():
        notif_title = f"⚠️ Moderate Risk Alert: {disease}"
        notif_body = f"Moderate concern. Calculated {risk}% risk for {disease}."
        notif_type = "warning"
        
    cur.execute("""
        INSERT INTO notifications (user_id, title, body, type)
        VALUES (?, ?, ?, ?)
    """, (current_user.id, notif_title, notif_body, notif_type))
    
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
    from hospital_finder import HOSPITALS_BY_CITY
    conn = get_db()
    cur = conn.cursor()
    appts = cur.execute("""
        SELECT * FROM appointments WHERE patient_id = ?
        ORDER BY appt_date DESC, appt_time DESC
    """, (current_user.id,)).fetchall()
    db_doctors = cur.execute("""
        SELECT id, full_name, address as spec, city
        FROM users WHERE role = 'doctor'
    """).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('appointments.html', patient=current_user, appointments=appts, today=today, HOSPITALS_BY_CITY=HOSPITALS_BY_CITY, db_doctors=db_doctors)


@app.route('/appointments/book', methods=['POST'])
@login_required
def book_appointment():
    conn = get_db()
    cur = conn.cursor()
    doc_name = request.form.get('doctor_name')
    appt_date = request.form.get('appt_date')
    appt_time = request.form.get('appt_time')
    appt_type = request.form.get('appt_type')
    notes = request.form.get('notes')
    current_medications = request.form.get('current_medications')
    hospital_name = request.form.get('hospital_name', 'City General Hospital')

    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_name, appt_date, appt_time, appt_type, notes, current_medications, hospital_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id,
        doc_name,
        appt_date,
        appt_time,
        appt_type,
        notes,
        current_medications,
        hospital_name
    ))

    # Notify patient
    cur.execute("""
        INSERT INTO notifications (user_id, title, body, type)
        VALUES (?, ?, ?, ?)
    """, (current_user.id, "📅 Appointment Booked",
          f"Your appointment with {doc_name} at {hospital_name} on {appt_date} at {appt_time} is pending confirmation.",
          "info"))

    # Find doctor if they are registered as a user
    doc_user = cur.execute(
        "SELECT id FROM users WHERE role = 'doctor' AND full_name LIKE ?",
        (f"%{doc_name.split('(')[0].strip()}%",)
    ).fetchone()
    if doc_user:
        cur.execute("""
            INSERT INTO notifications (user_id, title, body, type)
            VALUES (?, ?, ?, ?)
        """, (doc_user['id'], "📅 New Appointment Request",
              f"Patient {current_user.full_name} has requested an appointment at {hospital_name} on {appt_date} at {appt_time}.",
              "info"))

    conn.commit()
    conn.close()
    flash(f'Appointment booked at {hospital_name}! You will receive a confirmation shortly.', 'success')
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
    from hospital_finder import HOSPITALS_BY_CITY
    return render_template('emergency_sos.html', patient=current_user, hospitals_data=HOSPITALS_BY_CITY)


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


# ==============================================================================
# NEW NEW FEATURES ROUTES
# ==============================================================================

# Helper to send notifications
def add_notification(user_id, title, body, notif_type='info'):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, title, body, type)
        VALUES (?, ?, ?, ?)
    """, (user_id, title, body, notif_type))
    conn.commit()
    conn.close()

# --- Feature 1: AI Chatbot ---
@app.route('/chatbot/ask', methods=['POST'])
@login_required
def chatbot_ask():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'response': 'Invalid request'}), 400
        
    user_msg = data['message'].strip()
    user_msg_lower = user_msg.lower()
    
    # Try calling the real Gemini API if an API key is configured
    response = None
    import os
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if api_key:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        f"You are a helpful, professional AI Health Assistant on a smart healthcare platform. "
                        f"The user is asking: '{user_msg}'. Provide a friendly, helpful, and concise medical "
                        f"answer in 2 to 4 sentences. Always include a brief disclaimer that they should consult "
                        f"a physician for severe symptoms."
                    )
                }]
            }]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=5)
            if res.status_code == 200:
                result = res.json()
                response = result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            
    # Fallback to local rule-based system if Gemini is unavailable
    if not response:
        if any(k in user_msg_lower for k in ['hi', 'hello', 'hey', 'greetings', 'namaste']):
            response = "Hello! I am your AI Health Assistant. How can I help you today? Please tell me your symptoms or health queries."
        elif any(k in user_msg_lower for k in ['fever', 'temperature', 'pyrexia', 'bukhar']):
            response = "A fever is usually a sign that your body is fighting off an infection. Please drink plenty of fluids, rest, and monitor your temperature. If it exceeds 102°F (38.9°C) or lasts more than 3 days, please consult a doctor. You can book an appointment or check available slots with our specialists."
        elif any(k in user_msg_lower for k in ['cough', 'cold', 'sneeze', 'flu', 'sardi', 'khansi']):
            response = "For cough and cold, warm liquids like herbal tea or warm water with honey can help soothe your throat. Rest well. If you experience shortness of breath, a high fever, or your cough persists for more than 10 days, please schedule a virtual or physical visit with a physician."
        elif any(k in user_msg_lower for k in ['headache', 'migraine', 'head pain', 'sir dard']):
            response = "Headaches can be triggered by stress, dehydration, lack of sleep, or eye strain. Try resting in a dark, quiet room, and stay hydrated. If the headache is sudden and severe (a 'thunderclap' headache) or accompanied by fever, neck stiffness, or confusion, seek emergency care immediately."
        elif any(k in user_msg_lower for k in ['stomach', 'belly', 'abdominal', 'nausea', 'vomit', 'diarrhea', 'pet dard']):
            response = "Abdominal discomfort or nausea can be due to indigestion, food poisoning, or virus infections. Stay hydrated by taking small sips of water or ORS. Stick to bland foods (BRAT diet: bananas, rice, applesauce, toast). If you experience severe, sharp pain, or blood in vomit/stool, consult a doctor immediately."
        elif any(k in user_msg_lower for k in ['chest pain', 'heart', 'cardiac', 'shortness of breath', 'breathless', 'dil', 'dhadkan']):
            response = "⚠️ **URGENT:** Chest pain or severe shortness of breath can be a sign of a cardiac emergency or serious pulmonary condition. Please do not ignore this. Seek emergency medical services (SOS) or go to the nearest emergency room immediately!"
        elif any(k in user_msg_lower for k in ['diabetes', 'sugar', 'glucose', 'sugar level']):
            response = "Managing diabetes involves maintaining a healthy diet low in refined sugars, regular physical activity, monitoring blood glucose levels, and taking prescribed medications. Please track your daily blood glucose in our Vitals section, and share the log with your doctor."
        elif any(k in user_msg_lower for k in ['dengue', 'platelet', 'mosquito']):
            response = "Dengue is a viral infection spread by mosquitoes. Symptoms include high fever, severe body pain (breakbone fever), and skin rashes. It is critical to stay hydrated (ORS, juices) and avoid taking Aspirin or Ibuprofen as they increase bleeding risks. Monitor platelet counts daily."
        elif any(k in user_msg_lower for k in ['kidney', 'stone', 'renal']):
            response = "Kidney stones or infections can cause severe lower back pain, painful urination, or blood in urine. Drink 3-4 liters of water daily to help flush out small stones. If you have a fever, chills, or persistent vomiting along with the pain, seek immediate medical care for a potential kidney infection."
        elif any(k in user_msg_lower for k in ['diet', 'food', 'eat', 'nutrition']):
            response = "For optimal recovery, consume a balanced diet rich in leafy vegetables, lean proteins, fruits, and whole grains. Avoid processed foods, excess sodium, and high sugars. Proper hydration is equally crucial."
        elif any(k in user_msg_lower for k in ['appointment', 'book', 'doctor', 'slot', 'milna']):
            response = "You can easily book a doctor's appointment! Use the 'Doctor Slots' or 'Appointments' links in the sidebar to see available times and lock in your session."
        elif any(k in user_msg_lower for k in ['report', 'history', 'trends', 'card']):
            response = "You can view your health progress anytime! Go to 'Symptom Trends' in the sidebar to see charts of your symptoms over time, or 'Monthly Report Card' to view and print your consolidated monthly report."
        elif any(k in user_msg_lower for k in ['thank', 'thanks', 'cool', 'awesome', 'shukriya']):
            response = "You're very welcome! I'm here to support your health journey. Let me know if you have other symptoms or questions."
        else:
            response = f"Thank you for your question about '{user_msg}'. I recommend checking our 'Predict Disease' system for symptom assessment, logging your daily vitals in the Vitals Tracker, or scheduling a consultation with one of our specialized doctors for an accurate diagnosis."

    # Save to DB
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chatbot_logs (user_id, user_message, bot_response)
        VALUES (?, ?, ?)
    """, (current_user.id, data['message'], response))
    conn.commit()
    conn.close()
    
    return jsonify({'response': response})

@app.route('/chatbot/history', methods=['GET'])
@login_required
def chatbot_history():
    conn = get_db()
    cur = conn.cursor()
    logs = cur.execute("""
        SELECT user_message, bot_response, created_at 
        FROM chatbot_logs 
        WHERE user_id = ? 
        ORDER BY created_at ASC 
        LIMIT 20
    """, (current_user.id,)).fetchall()
    conn.close()
    
    history_list = []
    for log in logs:
        history_list.append({
            'user_message': log['user_message'],
            'bot_response': log['bot_response'],
            'created_at': log['created_at']
        })
    return jsonify({'history': history_list})


# --- Feature 2: Disease Outbreak Map ---
@app.route('/outbreak-map')
@login_required
def outbreak_map():
    return render_template('outbreak_map.html')

@app.route('/outbreak-map/data')
@login_required
def outbreak_map_data():
    conn = get_db()
    cur = conn.cursor()
    
    # India typical cities mapping
    city_coords = {
        'delhi': [28.6139, 77.2090],
        'mumbai': [19.0760, 72.8777],
        'bangalore': [12.9716, 77.5946],
        'chennai': [13.0827, 80.2707],
        'kolkata': [22.5726, 88.3639],
        'hyderabad': [17.3850, 78.4867],
        'pune': [18.5204, 73.8567],
        'ahmedabad': [23.0225, 72.5714],
        'jaipur': [26.9124, 75.7873],
        'lucknow': [26.8467, 80.9462],
        'default': [20.5937, 78.9629]
    }
    
    rows = cur.execute("""
        SELECT u.city, p.disease, COUNT(*) as cases_count, MAX(p.severity) as max_severity
        FROM predictions p
        JOIN users u ON p.patient_id = u.id
        GROUP BY u.city, p.disease
    """).fetchall()
    
    conn.close()
    
    data = []
    import random
    for row in rows:
        city_name = row['city'] or 'Delhi'
        city_key = city_name.strip().lower()
        
        coords = city_coords.get(city_key)
        if not coords:
            lat = city_coords['default'][0] + random.uniform(-4.0, 4.0)
            lng = city_coords['default'][1] + random.uniform(-4.0, 4.0)
            coords = [lat, lng]
            
        data.append({
            'city': city_name,
            'disease': row['disease'],
            'count': row['cases_count'],
            'lat': coords[0],
            'lng': coords[1],
            'severity': row['max_severity'] or 'Mild'
        })
        
    return jsonify(data)


# --- Feature 3: Monthly Health Report Card ---
@app.route('/report-card')
@login_required
@role_required('patient')
def report_card():
    conn = get_db()
    cur = conn.cursor()
    
    # Get last 30 days vitals
    vitals = cur.execute("""
        SELECT * FROM vitals 
        WHERE patient_id = ? AND logged_at >= datetime('now', '-30 days')
        ORDER BY logged_at DESC
    """, (current_user.id,)).fetchall()
    
    # Get last 30 days predictions
    preds = cur.execute("""
        SELECT * FROM predictions 
        WHERE patient_id = ? AND timestamp >= datetime('now', '-30 days')
        ORDER BY timestamp DESC
    """, (current_user.id,)).fetchall()
    
    # Get active medicines
    meds = cur.execute("""
        SELECT * FROM medicine_reminders 
        WHERE patient_id = ? AND is_active = 1
    """, (current_user.id,)).fetchall()
    
    conn.close()
    
    avg_vitals = {
        'bp_systolic': 0, 'bp_diastolic': 0, 'pulse': 0, 
        'temperature': 0.0, 'weight': 0.0, 'oxygen': 0.0, 'count': 0
    }
    
    if vitals:
        for v in vitals:
            avg_vitals['bp_systolic'] += v['bp_systolic']
            avg_vitals['bp_diastolic'] += v['bp_diastolic']
            avg_vitals['pulse'] += v['pulse']
            avg_vitals['temperature'] += v['temperature']
            avg_vitals['weight'] += v['weight']
            avg_vitals['oxygen'] += v['oxygen_saturation'] if v['oxygen_saturation'] else 98.0
        n = len(vitals)
        avg_vitals['bp_systolic'] = int(avg_vitals['bp_systolic'] / n)
        avg_vitals['bp_diastolic'] = int(avg_vitals['bp_diastolic'] / n)
        avg_vitals['pulse'] = int(avg_vitals['pulse'] / n)
        avg_vitals['temperature'] = round(avg_vitals['temperature'] / n, 1)
        avg_vitals['weight'] = round(avg_vitals['weight'] / n, 1)
        avg_vitals['oxygen'] = round(avg_vitals['oxygen'] / n, 1)
        avg_vitals['count'] = n
        
    return render_template('report_card.html', patient=current_user, vitals=vitals, avg_vitals=avg_vitals, predictions=preds, medicines=meds)

@app.route('/report-card/pdf')
@login_required
@role_required('patient')
def report_card_pdf():
    reports_dir = os.path.join(BASE_DIR, "static", "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    filename = f"Monthly_Report_Card_{current_user.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    conn = get_db()
    cur = conn.cursor()
    vitals = cur.execute("""
        SELECT * FROM vitals WHERE patient_id = ? AND logged_at >= datetime('now', '-30 days')
    """, (current_user.id,)).fetchall()
    preds = cur.execute("""
        SELECT * FROM predictions WHERE patient_id = ? AND timestamp >= datetime('now', '-30 days')
    """, (current_user.id,)).fetchall()
    conn.close()
    
    # Calculate averages
    avg_bp = "N/A"
    avg_temp = "N/A"
    avg_pulse = "N/A"
    avg_oxygen = "N/A"
    
    if vitals:
        bps = [v['bp_systolic'] for v in vitals]
        bpd = [v['bp_diastolic'] for v in vitals]
        temps = [v['temperature'] for v in vitals]
        pulses = [v['pulse'] for v in vitals]
        oxys = [v['oxygen_saturation'] for v in vitals if v['oxygen_saturation']]
        
        avg_bp = f"{int(sum(bps)/len(bps))}/{int(sum(bpd)/len(bpd))} mmHg"
        avg_temp = f"{round(sum(temps)/len(temps), 1)} F"
        avg_pulse = f"{int(sum(pulses)/len(pulses))} bpm"
        if oxys:
            avg_oxygen = f"{round(sum(oxys)/len(oxys), 1)}%"
            
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Theme Colors
    primary_color = colors.HexColor('#1E3A8A')
    
    # Header
    c.setFillColor(primary_color)
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 55, "MONTHLY HEALTH REPORT CARD")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 80, f"Generated: {datetime.now().strftime('%B %Y')} | Smart Healthcare System")
    
    # Patient Info Box
    c.setFillColor(colors.HexColor('#F8FAFC'))
    c.rect(40, height - 230, width - 80, 90, fill=True, stroke=True)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(55, height - 165, "PATIENT INFORMATION")
    c.setFont("Helvetica", 10)
    c.drawString(55, height - 190, f"Name: {current_user.full_name}")
    c.drawString(55, height - 210, f"Age / Gender: {current_user.age} / {current_user.gender}")
    c.drawString(300, height - 190, f"Email: {current_user.email}")
    c.drawString(300, height - 210, f"City: {current_user.city}")
    
    # Vitals Summary Box
    y = height - 260
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "30-Day Vitals Averages")
    
    c.setFillColor(colors.HexColor('#F1F5F9'))
    c.rect(40, y - 90, width - 80, 75, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(60, y - 40, f"Average Blood Pressure: {avg_bp}")
    c.drawString(60, y - 65, f"Average Body Temperature: {avg_temp}")
    c.drawString(320, y - 40, f"Average Pulse Rate: {avg_pulse}")
    c.drawString(320, y - 65, f"Average Oxygen Level: {avg_oxygen}")
    
    # Predictions summary
    y = y - 130
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Disease Risk Prediction Assessments (Last 30 Days)")
    
    y_pos = y - 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_pos, "Date")
    c.drawString(140, y_pos, "Disease Predicted")
    c.drawString(300, y_pos, "Risk Score")
    c.drawString(400, y_pos, "Severity")
    
    c.setStrokeColor(colors.HexColor('#CBD5E1'))
    c.line(40, y_pos - 5, width - 40, y_pos - 5)
    
    c.setFont("Helvetica", 9)
    y_pos = y_pos - 20
    
    max_rows = 8
    displayed = 0
    for p in preds:
        if displayed >= max_rows:
            break
        dt = p['timestamp'][:10]
        c.drawString(40, y_pos, dt)
        c.drawString(140, y_pos, p['disease'])
        c.drawString(300, y_pos, f"{int(p['risk_percentage'])}%")
        c.drawString(400, y_pos, p['severity'])
        y_pos -= 20
        displayed += 1
        
    if not preds:
        c.drawString(40, y_pos, "No prediction diagnostic records found for this period.")
        
    # Signature
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, 80, "AI Medical Assistant Signature")
    c.line(40, 115, 200, 115)
    c.drawString(380, 80, "Chief Medical Advisor")
    c.line(380, 115, 540, 115)
    
    c.showPage()
    c.save()
    
    return send_file(filepath, as_attachment=True)


# --- Feature 4: Doctor Availability Slots ---
@app.route('/doctor/slots', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def doctor_slots():
    from hospital_finder import HOSPITALS_BY_CITY
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        slot_date = request.form.get('slot_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hospital_name = request.form.get('hospital_name', 'City General Hospital')

        if slot_date and start_time and end_time:
            cur.execute("""
                INSERT INTO doctor_slots (doctor_id, slot_date, start_time, end_time, is_booked, hospital_name)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (current_user.id, slot_date, start_time, end_time, hospital_name))
            conn.commit()
            flash(f'Availability slot at {hospital_name} added successfully!', 'success')

    slots = cur.execute("""
        SELECT s.*, u.full_name as patient_name
        FROM doctor_slots s
        LEFT JOIN users u ON s.patient_id = u.id
        WHERE s.doctor_id = ?
        ORDER BY s.slot_date ASC, s.start_time ASC
    """, (current_user.id,)).fetchall()

    conn.close()
    datetime_now = datetime.now().strftime('%Y-%m-%d')
    return render_template('doctor_slots.html', doctor=current_user, slots=slots,
                           HOSPITALS_BY_CITY=HOSPITALS_BY_CITY, datetime_now=datetime_now)

@app.route('/doctor/slots/delete/<int:slot_id>', methods=['POST'])
@login_required
@role_required('doctor')
def delete_doctor_slot(slot_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM doctor_slots WHERE id = ? AND doctor_id = ? AND is_booked = 0", (slot_id, current_user.id))
    conn.commit()
    conn.close()
    flash('Slot removed.', 'info')
    return redirect(url_for('doctor_slots'))

@app.route('/appointments/book-slot', methods=['GET'])
@login_required
@role_required('patient')
def book_slot_view():
    conn = get_db()
    cur = conn.cursor()
    
    slots = cur.execute("""
        SELECT s.*, u.full_name as doctor_name
        FROM doctor_slots s
        JOIN users u ON s.doctor_id = u.id
        WHERE s.is_booked = 0 AND s.slot_date >= date('now')
        ORDER BY s.slot_date ASC, s.start_time ASC
    """).fetchall()
    
    conn.close()
    return render_template('book_slot.html', patient=current_user, slots=slots)

@app.route('/appointments/book-slot/<int:slot_id>', methods=['POST'])
@login_required
@role_required('patient')
def book_slot(slot_id):
    conn = get_db()
    cur = conn.cursor()

    slot = cur.execute("""
        SELECT s.*, u.full_name as doctor_name
        FROM doctor_slots s
        JOIN users u ON s.doctor_id = u.id
        WHERE s.id = ? AND s.is_booked = 0
    """, (slot_id,)).fetchone()

    if not slot:
        conn.close()
        flash('This slot is no longer available.', 'danger')
        return redirect(url_for('book_slot_view'))

    hosp = slot['hospital_name'] if slot['hospital_name'] else 'City General Hospital'

    cur.execute("""
        UPDATE doctor_slots
        SET is_booked = 1, patient_id = ?
        WHERE id = ?
    """, (current_user.id, slot_id))

    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_name, appt_date, appt_time, appt_type, notes, status, hospital_name)
        VALUES (?, ?, ?, ?, 'General Consultation', 'Booked via availability slot system', 'confirmed', ?)
    """, (current_user.id, slot['doctor_name'], slot['slot_date'], slot['start_time'], hosp))

    cur.execute("""
        INSERT INTO notifications (user_id, title, body, type)
        VALUES (?, ?, ?, ?)
    """, (current_user.id, "📅 Appointment Confirmed",
          f"Your appointment with {slot['doctor_name']} at {hosp} on {slot['slot_date']} at {slot['start_time']} is confirmed.",
          "success"))

    cur.execute("""
        INSERT INTO notifications (user_id, title, body, type)
        VALUES (?, ?, ?, ?)
    """, (slot['doctor_id'], "📅 New Slot Booking",
          f"Patient {current_user.full_name} has booked your slot at {hosp} on {slot['slot_date']} at {slot['start_time']}.",
          "info"))

    conn.commit()
    conn.close()

    flash(f"Slot booked! Appointment with {slot['doctor_name']} at {hosp} confirmed.", 'success')
    return redirect(url_for('appointments'))


# --- Feature 5: Notifications ---
@app.route('/notifications')
@login_required
def notifications_view():
    conn = get_db()
    cur = conn.cursor()
    notifs = cur.execute("""
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    return render_template('notifications.html', user=current_user, notifications=notifs)

@app.route('/notifications/count', methods=['GET'])
@login_required
def notifications_count():
    conn = get_db()
    cur = conn.cursor()
    res = cur.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0", (current_user.id,)).fetchone()
    conn.close()
    return jsonify({'count': res['count'] if res else 0})

@app.route('/notifications/mark-read/<int:notif_id>', methods=['POST'])
@login_required
def notifications_mark_read(notif_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, current_user.id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def notifications_mark_all_read():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (current_user.id,))
    conn.commit()
    conn.close()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications_view'))


# --- Feature 6: Patient-Doctor Messaging ---
@app.route('/messages', methods=['GET'])
@login_required
@role_required('patient')
def patient_messages():
    conn = get_db()
    cur = conn.cursor()
    
    doctors = cur.execute("SELECT id, full_name, email FROM users WHERE role = 'doctor'").fetchall()
    
    latest_rx = cur.execute("""
        SELECT doctor_id FROM prescriptions 
        WHERE patient_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    """, (current_user.id,)).fetchone()
    
    default_doctor_id = latest_rx['doctor_id'] if latest_rx else (doctors[0]['id'] if doctors else None)
    
    conn.close()
    return render_template('messages.html', patient=current_user, doctors=doctors, default_doctor_id=default_doctor_id)

@app.route('/doctor/messages', methods=['GET'])
@login_required
@role_required('doctor')
def doctor_messages_list():
    conn = get_db()
    cur = conn.cursor()
    
    patients = cur.execute("""
        SELECT DISTINCT u.id, u.full_name, u.email
        FROM users u
        JOIN messages m ON (m.sender_id = u.id OR m.recipient_id = u.id)
        WHERE (m.sender_id = ? OR m.recipient_id = ?) AND u.role = 'patient'
    """, (current_user.id, current_user.id)).fetchall()
    
    if not patients:
        patients = cur.execute("SELECT id, full_name, email FROM users WHERE role = 'patient' LIMIT 20").fetchall()
        
    conn.close()
    return render_template('doctor_messages.html', doctor=current_user, patients=patients)

@app.route('/messages/send', methods=['POST'])
@login_required
def message_send():
    recipient_id = request.form.get('recipient_id')
    body = request.form.get('body')
    
    if not recipient_id or not body:
        return jsonify({'error': 'Missing recipient or body'}), 400
        
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (sender_id, recipient_id, body, is_read)
        VALUES (?, ?, ?, 0)
    """, (current_user.id, recipient_id, body.strip()))
    conn.commit()
    conn.close()
    
    # Notify recipient
    add_notification(
        recipient_id,
        f"💬 New Message from {current_user.full_name}",
        body[:50] + ("..." if len(body) > 50 else ""),
        "info"
    )
    
    return jsonify({'status': 'success'})

@app.route('/messages/poll', methods=['GET'])
@login_required
def message_poll():
    other_id = request.args.get('other_user_id')
    last_id = request.args.get('last_id', 0, type=int)
    
    if not other_id:
        return jsonify({'error': 'Missing other_user_id'}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE messages SET is_read = 1 
        WHERE sender_id = ? AND recipient_id = ? AND id > ?
    """, (other_id, current_user.id, last_id))
    conn.commit()
    
    messages = cur.execute("""
        SELECT id, sender_id, recipient_id, body, created_at
        FROM messages
        WHERE ((sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?))
          AND id > ?
        ORDER BY id ASC
    """, (current_user.id, other_id, other_id, current_user.id, last_id)).fetchall()
    
    conn.close()
    
    msg_list = []
    for msg in messages:
        msg_list.append({
            'id': msg['id'],
            'sender_id': msg['sender_id'],
            'recipient_id': msg['recipient_id'],
            'body': msg['body'],
            'created_at': msg['created_at']
        })
        
    return jsonify({'messages': msg_list})


# --- Feature 7: Symptom Trend Tracker ---
@app.route('/symptom-trends')
@login_required
@role_required('patient')
def symptom_trends():
    conn = get_db()
    cur = conn.cursor()
    preds = cur.execute("""
        SELECT disease, risk_percentage, health_risk_score, severity, symptoms, timestamp 
        FROM predictions 
        WHERE patient_id = ? 
        ORDER BY timestamp ASC
    """, (current_user.id,)).fetchall()
    conn.close()
    
    timeline = []
    for p in preds:
        symptom_list = []
        try:
            import ast
            sym_dict = ast.literal_eval(p['symptoms'])
            symptom_list = [k.replace('_', ' ').capitalize() for k, v in sym_dict.items() if v == 1]
        except Exception:
            pass
            
        timeline.append({
            'date': p['timestamp'][:10],
            'disease': p['disease'],
            'risk': p['risk_percentage'],
            'severity': p['severity'],
            'score': p['health_risk_score'],
            'symptoms': symptom_list
        })
        
    return render_template('symptom_trends.html', patient=current_user, timeline=timeline)


# --- Feature 8: Second Opinion Request ---
@app.route('/second-opinion/request', methods=['POST'])
@login_required
@role_required('patient')
def second_opinion_request():
    prediction_id = request.form.get('prediction_id')
    doctor_id = request.form.get('doctor_id')
    request_note = request.form.get('request_note')
    
    if not prediction_id or not doctor_id:
        flash('Invalid second opinion request submission.', 'danger')
        return redirect(url_for('history'))
        
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO second_opinions (patient_id, prediction_id, request_note, doctor_id, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (current_user.id, prediction_id, request_note, doctor_id))
    
    conn.commit()
    conn.close()
    
    # Notify doctor
    add_notification(
        doctor_id,
        "🩺 Second Opinion Request",
        f"Patient {current_user.full_name} requested a second opinion review.",
        "info"
    )
    
    flash('Second opinion requested successfully! The doctor will review your case.', 'success')
    return redirect(url_for('second_opinions_view'))

@app.route('/second-opinions')
@login_required
@role_required('patient')
def second_opinions_view():
    conn = get_db()
    cur = conn.cursor()
    
    requests = cur.execute("""
        SELECT so.*, p.disease, p.risk_percentage, p.timestamp as prediction_time, u.full_name as doctor_name
        FROM second_opinions so
        JOIN predictions p ON so.prediction_id = p.id
        JOIN users u ON so.doctor_id = u.id
        WHERE so.patient_id = ?
        ORDER BY so.created_at DESC
    """, (current_user.id,)).fetchall()
    
    doctors = cur.execute("SELECT id, full_name FROM users WHERE role = 'doctor'").fetchall()
    predictions = cur.execute("SELECT id, disease, risk_percentage, timestamp FROM predictions WHERE patient_id = ? ORDER BY timestamp DESC", (current_user.id,)).fetchall()
    
    conn.close()
    return render_template('second_opinions.html', patient=current_user, requests=requests, doctors=doctors, predictions=predictions)

@app.route('/doctor/second-opinions')
@login_required
@role_required('doctor')
def doctor_second_opinions():
    conn = get_db()
    cur = conn.cursor()
    
    requests = cur.execute("""
        SELECT so.*, p.disease, p.risk_percentage, p.symptoms, p.timestamp as prediction_time, u.full_name as patient_name, u.age as patient_age, u.gender as patient_gender
        FROM second_opinions so
        JOIN predictions p ON so.prediction_id = p.id
        JOIN users u ON so.patient_id = u.id
        WHERE so.doctor_id = ?
        ORDER BY so.status DESC, so.created_at DESC
    """, (current_user.id,)).fetchall()
    
    conn.close()
    return render_template('doctor_second_opinions.html', doctor=current_user, requests=requests)

@app.route('/doctor/second-opinions/<int:so_id>/respond', methods=['POST'])
@login_required
@role_required('doctor')
def doctor_second_opinion_respond(so_id):
    doctor_note = request.form.get('doctor_note')
    
    if not doctor_note:
        flash('Response note cannot be empty.', 'danger')
        return redirect(url_for('doctor_second_opinions'))
        
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE second_opinions
        SET doctor_note = ?, status = 'resolved'
        WHERE id = ? AND doctor_id = ?
    """, (doctor_note, so_id, current_user.id))
    
    so = cur.execute("SELECT patient_id FROM second_opinions WHERE id = ?", (so_id,)).fetchone()
    
    conn.commit()
    conn.close()
    
    if so:
        # Notify patient
        add_notification(
            so['patient_id'],
            "🩺 Second Opinion Review Completed",
            f"Dr. {current_user.full_name} has provided expert feedback on your second opinion request.",
            "success"
        )
        
    flash('Second opinion review saved and sent to the patient.', 'success')
    return redirect(url_for('doctor_second_opinions'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
