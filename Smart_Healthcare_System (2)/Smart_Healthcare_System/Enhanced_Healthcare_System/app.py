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
import os
import io
import threading
import time
from functools import wraps

# Import services
from model import train_model
from analytics import AnalyticsEngine
from medicine_db import MEDICINE_DATABASE, HOSPITAL_DATABASE
from risk_calculator import calculate_health_risk_score, get_risk_recommendations
from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url
from symptom_engine import (
    assess_symptoms, get_severity, get_medicines_for_disease,
    SYMPTOMS, SYMPTOM_GROUPS
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================= ML MODEL =================
model, disease_map, accuracy = train_model()

# ================= DATABASE SETUP =================
def get_db():
    conn = sqlite3.connect("healthcare.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        contact TEXT,
        city TEXT DEFAULT 'Default',
        smoking TEXT DEFAULT 'no',
        blood_pressure TEXT DEFAULT 'normal',
        blood_sugar TEXT DEFAULT 'normal',
        role TEXT DEFAULT 'patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Predictions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
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
    
    # Migrate existing users table if needed
    try:
        # Check if new columns exist
        cur.execute("SELECT city FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Add new columns to existing users table
        print("Migrating users table...")
        try:
            cur.execute("ALTER TABLE users ADD COLUMN city TEXT DEFAULT 'Default'")
        except:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN smoking TEXT DEFAULT 'no'")
        except:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN blood_pressure TEXT DEFAULT 'normal'")
        except:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN blood_sugar TEXT DEFAULT 'normal'")
        except:
            pass
        print("Users table migrated successfully!")
    
    # Migrate existing predictions table if needed
    try:
        # Check if new columns exist
        cur.execute("SELECT health_risk_score FROM predictions LIMIT 1")
    except sqlite3.OperationalError:
        # Add new columns to existing predictions table
        print("Migrating predictions table...")
        try:
            cur.execute("ALTER TABLE predictions ADD COLUMN health_risk_score INTEGER DEFAULT 50")
        except:
            pass
        try:
            cur.execute("ALTER TABLE predictions ADD COLUMN health_risk_category TEXT DEFAULT 'Moderate Risk'")
        except:
            pass
        try:
            cur.execute("ALTER TABLE predictions ADD COLUMN symptom_count INTEGER DEFAULT 0")
        except:
            pass
        print("Predictions table migrated successfully!")
        
    try:
        cur.execute("ALTER TABLE predictions ADD COLUMN doctor_name TEXT DEFAULT ''")
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
    
    # Medicine reminders table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicine_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT DEFAULT '',
        reminder_time TEXT NOT NULL,
        frequency TEXT DEFAULT 'daily',
        start_date TEXT DEFAULT '',
        end_date TEXT DEFAULT '',
        instructions TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        last_fired TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def init_extra_tables():
    """Create extra feature tables: health_vitals, appointments."""
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_vitals (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id      INTEGER NOT NULL,
        date            TEXT    NOT NULL,
        systolic_bp     REAL,
        diastolic_bp    REAL,
        blood_sugar     REAL,
        weight_kg       REAL,
        heart_rate      REAL,
        temperature_c   REAL,
        notes           TEXT    DEFAULT '',
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id        INTEGER NOT NULL,
        doctor_name       TEXT    NOT NULL,
        appointment_date  TEXT    NOT NULL,
        appointment_time  TEXT    NOT NULL,
        visit_type        TEXT    DEFAULT 'consultation',
        reason            TEXT    DEFAULT '',
        status            TEXT    DEFAULT 'pending',
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")
    conn.commit()
    conn.close()
    print("Extra tables initialized!")

init_db()
init_extra_tables()

# ================= USER CLASS =================
class User(UserMixin):
    def __init__(self, id, username, email, full_name, age, contact, role, city='Default', smoking='no', blood_pressure='normal', blood_sugar='normal'):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.age = age
        self.contact = contact
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
        # Handle both old and new database schemas
        try:
            city = user['city'] if 'city' in user.keys() else 'Default'
            smoking = user['smoking'] if 'smoking' in user.keys() else 'no'
            blood_pressure = user['blood_pressure'] if 'blood_pressure' in user.keys() else 'normal'
            blood_sugar = user['blood_sugar'] if 'blood_sugar' in user.keys() else 'normal'
        except:
            city = 'Default'
            smoking = 'no'
            blood_pressure = 'normal'
            blood_sugar = 'normal'
        
        return User(user['id'], user['username'], user['email'], 
                   user['full_name'], user['age'], user['contact'], user['role'],
                   city, smoking, blood_pressure, blood_sugar)
    return None

# ================= ROLE DECORATOR =================
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ================= HELPER FUNCTIONS =================
def calculate_risk(prob):
    risk = round(prob * 100, 1)
    if risk <= 40:
        return risk, "LOW 🟢"
    elif risk <= 70:
        return risk, "MEDIUM 🟡"
    else:
        return risk, "HIGH 🔴"

def generate_pdf(patient, prediction_data):
    """Generate professional PDF with hospital branding"""
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(__file__), "static", "reports")
    
    # Create the directory structure
    try:
        os.makedirs(reports_dir, exist_ok=True)
        print(f"Reports directory created/verified: {reports_dir}")
    except Exception as e:
        print(f"Error creating reports directory: {e}")
        # Fallback to current directory
        reports_dir = os.path.dirname(__file__)
    
    filename = f"Medical_Report_{patient.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    print(f"Generating PDF at: {filepath}")
    
    try:
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Hospital branding colors
        primary_blue = colors.HexColor('#0066CC')
        success_green = colors.HexColor('#28A745')
        warning_yellow = colors.HexColor('#FFC107')
        danger_red = colors.HexColor('#DC3545')
        
        # Header with logo
        c.setFillColor(primary_blue)
        c.rect(0, height - 100, width, 100, fill=True, stroke=False)
        
        # Hospital logo (if exists)
        logo_path = os.path.join(os.path.dirname(__file__), "static", "assets", "hospital_logo.png")
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 40, height - 90, width=60, height=60, preserveAspectRatio=True, mask='auto')
            except:
                pass  # Skip logo if there's an error
        
        # Hospital name
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(120, height - 50, "HealthCare Plus Hospital")
        c.setFont("Helvetica", 12)
        c.drawString(120, height - 70, "Advanced Disease Prediction & Care")
        
        # Patient Information Section
        y_position = height - 140
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y_position, "MEDICAL REPORT")
        
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Patient Information:")
        c.setFont("Helvetica", 11)
        y_position -= 20
        c.drawString(60, y_position, f"Name: {patient.full_name}")
        y_position -= 18
        c.drawString(60, y_position, f"Age: {patient.age} years")
        y_position -= 18
        c.drawString(60, y_position, f"Contact: {patient.contact or 'N/A'}")
        y_position -= 18
        c.drawString(60, y_position, f"Report Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # Prediction Results Section
        y_position -= 35
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Diagnosis Results:")
        
        y_position -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y_position, f"Predicted Disease: {prediction_data['disease']}")
        
        y_position -= 20
        c.setFont("Helvetica", 11)
        c.drawString(60, y_position, f"Risk Level: {prediction_data['risk_percentage']}%")
        
        y_position -= 20
        severity_text = prediction_data['severity']
        severity_color = success_green if 'LOW' in severity_text else (warning_yellow if 'MEDIUM' in severity_text else danger_red)
        c.setFillColor(severity_color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y_position, f"Severity: {severity_text}")
        
        # Health Risk Score (NEW)
        if 'health_risk_score' in prediction_data:
            y_position -= 20
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y_position, f"Health Risk Score: {prediction_data['health_risk_score']}/100")
            c.setFont("Helvetica", 10)
            c.drawString(60, y_position - 15, f"Category: {prediction_data.get('health_risk_category', 'N/A')}")
            y_position -= 35
        
        # Medicines Section
        y_position -= 20
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Recommended Medicines:")
        
        medicines = prediction_data['medicines'].split(',')
        for med in medicines[:5]:  # Limit to 5 medicines
            y_position -= 18
            c.setFont("Helvetica", 10)
            c.drawString(60, y_position, f"• {med.strip()}")
        
        # Hospital Recommendations
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Hospital Recommendations:")
        
        hospitals = prediction_data['hospitals'].split(',')
        for hosp in hospitals[:3]:  # Limit to 3 hospitals
            y_position -= 18
            c.setFont("Helvetica", 10)
            c.drawString(60, y_position, f"• {hosp.strip()}")
        
        # Doctor Advice
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Doctor's Advice:")
        y_position -= 18
        c.setFont("Helvetica", 10)
        
        # Wrap text for doctor advice
        advice_text = prediction_data['doctor_advice']
        max_width = 500
        words = advice_text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                c.drawString(60, y_position, line)
                y_position -= 15
                line = word + " "
        if line:
            c.drawString(60, y_position, line)
        
        # Footer
        c.setFillColor(primary_blue)
        c.rect(0, 0, width, 50, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 9)
        c.drawString(40, 25, "HealthCare Plus Hospital | 24/7 Emergency Services")
        c.drawString(40, 12, "Contact: +1-800-HEALTH | Email: care@healthcareplus.com")
        
        c.save()
        print(f"PDF generated successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        # Return a placeholder filename
        return f"Error_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# ================= ROUTES =================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('dashboard'))
        return redirect(url_for('symptom_assessment'))
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
        contact = request.form.get('contact')
        city = request.form.get('city', 'Default')
        smoking = request.form.get('smoking', 'no')
        blood_pressure = request.form.get('blood_pressure', 'normal')
        blood_sugar = request.form.get('blood_sugar', 'normal')
        role = request.form.get('role', 'patient')
        
        conn = get_db()
        cur = conn.cursor()
        
        # Check if user exists
        existing_user = cur.execute("SELECT * FROM users WHERE email = ? OR username = ?", 
                                   (email, username)).fetchone()
        if existing_user:
            flash('Email or username already exists!', 'danger')
            conn.close()
            return redirect(url_for('signup'))
        
        # Create user
        password_hash = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, age, contact, city, smoking, blood_pressure, blood_sugar, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, full_name, age, contact, city, smoking, blood_pressure, blood_sugar, role))
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
            # Handle both old and new database schemas
            try:
                city = user['city'] if 'city' in user.keys() else 'Default'
                smoking = user['smoking'] if 'smoking' in user.keys() else 'no'
                blood_pressure = user['blood_pressure'] if 'blood_pressure' in user.keys() else 'normal'
                blood_sugar = user['blood_sugar'] if 'blood_sugar' in user.keys() else 'normal'
            except:
                city = 'Default'
                smoking = 'no'
                blood_pressure = 'normal'
                blood_sugar = 'normal'
            
            user_obj = User(user['id'], user['username'], user['email'],
                          user['full_name'], user['age'], user['contact'], user['role'],
                          city, smoking, blood_pressure, blood_sugar)
            login_user(user_obj)
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            if user['role'] == 'doctor':
                return redirect(url_for('dashboard'))
            return redirect(url_for('symptom_entry'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/symptom-entry')
@login_required
def symptom_entry():
    return render_template('symptom_entry.html', patient=current_user)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    # IMPORTANT: In the training data:
    # 1 = HAS the symptom
    # 2 = DOESN'T have the symptom
    # This is OPPOSITE of what we might expect!
    
    # Convert checkbox values to model format
    def convert_symptom(value):
        # Checkbox checked (1) → Model value 1 (HAS symptom)
        # Checkbox unchecked (0) → Model value 2 (NO symptom)
        return 1 if int(value) == 1 else 2
    
    # For fever, if checked, use a typical fever temperature (102)
    # If not checked, use normal temperature (98)
    fever_value = 102 if int(request.form.get('fever', 0)) == 1 else 98
    
    symptom_values = [
        convert_symptom(request.form.get('bodypain', 0)),
        convert_symptom(request.form.get('Hollow', 0)),
        convert_symptom(request.form.get('cold_cough', 0)),
        convert_symptom(request.form.get('cough', 0)),
        fever_value,  # Special handling for fever
        convert_symptom(request.form.get('chest_pain', 0)),
        convert_symptom(request.form.get('breathing_problem', 0)),
        convert_symptom(request.form.get('throat_pain', 0)),
        convert_symptom(request.form.get('head_pain', 0)),
        convert_symptom(request.form.get('stomach_pain', 0)),
        convert_symptom(request.form.get('diarrhea', 0)),
        convert_symptom(request.form.get('omitting', 0)),
        convert_symptom(request.form.get('back_pain', 0)),
        convert_symptom(request.form.get('swollen_feet', 0))
    ]
    
    # Column names must match training data exactly
    column_names = ['bodypain', 'Hollow', 'cold and cough', 'cough', 'fever',
                   'chest pain', 'breathing problem', 'Throat pain', 'head pain',
                   'stomach pain', 'diarrhea', 'omitting', 'back pain', 'Swollen feet']
    
    # Create DataFrame for prediction with correct column order
    df = pd.DataFrame([symptom_values], columns=column_names)
    
    # Debug: Print the input to verify
    print(f"Input symptoms: {df.values[0]}")
    
    # Make prediction
    pid = model.predict(df)[0]
    prob = max(model.predict_proba(df)[0])
    
    print(f"Predicted PID: {pid}, Probability: {prob}")
    
    risk, severity = calculate_risk(prob)
    disease = disease_map[pid]
    
    print(f"Disease: {disease}, Severity: {severity}")
    
    # Get past history count
    conn = get_db()
    cur = conn.cursor()
    past_history_count = cur.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id = ?", 
        (current_user.id,)
    ).fetchone()[0]
    
    # Calculate comprehensive health risk score
    symptoms_dict = {}
    for i, col in enumerate(column_names):
        if col == 'fever':
            symptoms_dict[col] = 1 if symptom_values[i] > 100 else 0
        else:
            symptoms_dict[col] = 1 if symptom_values[i] == 1 else 0

    patient_data = {
        'age': current_user.age,
        'smoking': current_user.smoking,
        'blood_pressure': current_user.blood_pressure,
        'blood_sugar': current_user.blood_sugar
    }

    health_risk = calculate_health_risk_score(
        patient_data,
        symptoms_dict,
        severity,
        past_history_count
    )

    # ── Get medicines from MEDICINE_DATABASE ──────────────────────────────────
    severity_key = severity.split()[0]  # LOW / MEDIUM / HIGH
    disease_meds = MEDICINE_DATABASE.get(disease, MEDICINE_DATABASE.get("Common Cold", {}))
    medicines = disease_meds.get(severity_key, disease_meds.get("LOW", ["Consult a doctor"]))
    if not isinstance(medicines, list):
        medicines = ["Consult a doctor"]
    
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
        "LOW": "Monitor symptoms at home. Stay hydrated and get adequate rest. Consult a doctor if symptoms worsen.",
        "MEDIUM": "Consult a doctor within 24 hours. Follow prescribed medications and monitor your condition closely.",
        "HIGH": "Seek immediate medical attention. Visit the emergency department or call an ambulance if symptoms are severe."
    }
    
    severity_key = severity.split()[0]  # Extract LOW, MEDIUM, or HIGH

    # Prepare prediction data
    prediction_data = {
        'disease': disease,
        'risk_percentage': risk,
        'health_risk_score': health_risk['score'],
        'health_risk_category': health_risk['category'],
        'health_risk_color': health_risk['color'],
        'health_risk_icon': health_risk['icon'],
        'severity': severity,
        'probability': prob,
        'medicines': ', '.join(medicines),
        'hospitals': ', '.join([h['name'] for h in hospitals_list[:5]]),
        'doctor_advice': doctor_advice[severity_key],
        'doctor_name': doctor_name,
        'doctor_phone': doctor_phone,
        'referred_hospital': referred_hospital
    }
    
    # Generate PDF
    pdf_filename = generate_pdf(current_user, prediction_data)
    
    # Save to database
    symptom_count = sum(1 for v in symptoms_dict.values() if v == 1)
    
    cur.execute("""
        INSERT INTO predictions (patient_id, disease, risk_percentage, health_risk_score, 
                               health_risk_category, severity, probability, symptoms, symptom_count,
                               medicines, hospitals, doctor_advice, pdf_path, doctor_name, doctor_phone, referred_hospital)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, disease, risk, health_risk['score'], health_risk['category'],
          severity, prob, str(symptoms_dict), symptom_count, prediction_data['medicines'],
          prediction_data['hospitals'], prediction_data['doctor_advice'], pdf_filename, doctor_name, doctor_phone, referred_hospital))
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
    # Use absolute path for proper handling
    reports_dir = os.path.join(os.path.dirname(__file__), 'static', 'reports')
    filepath = os.path.join(reports_dir, filename)
    
    print(f"Attempting to download: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")
    
    if os.path.exists(filepath):
        try:
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"Error sending file: {e}")
            flash(f'Error downloading file: {str(e)}', 'danger')
            return redirect(url_for('history'))
    else:
        print(f"File not found at: {filepath}")
        flash('File not found! The PDF may not have been generated correctly.', 'danger')
        return redirect(url_for('history'))

@app.route('/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    
    # Get statistics
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
        SELECT DISTINCT patient_id, disease, health_risk_score, 
               health_risk_category, timestamp
        FROM predictions 
        WHERE health_risk_score >= 60
        ORDER BY health_risk_score DESC, timestamp DESC
        LIMIT 20
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
                WHEN u.age < 18 THEN 'Under 18'
                WHEN u.age < 30 THEN '18-29'
                WHEN u.age < 45 THEN '30-44'
                WHEN u.age < 60 THEN '45-59'
                ELSE '60+'
            END as age_group,
            p.disease,
            COUNT(*) as count
        FROM predictions p
        JOIN users u ON p.patient_id = u.id
        GROUP BY age_group, p.disease
        ORDER BY age_group, count DESC
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
        'disease_stats': disease_stats,
        'age_disease_stats': age_disease_stats
    }
    
    return render_template('dashboard_enhanced.html', 
                         doctor=current_user,
                         stats=stats)

@app.route('/analytics-data')
@login_required
@role_required('doctor')
def analytics_data():
    from flask import jsonify
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
                WHEN u.age < 18 THEN 'Under 18'
                WHEN u.age < 30 THEN '18-29'
                WHEN u.age < 45 THEN '30-44'
                WHEN u.age < 60 THEN '45-59'
                ELSE '60+'
            END as age_group,
            COUNT(*) as count
        FROM predictions p
        JOIN users u ON p.patient_id = u.id
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

@app.route('/emergency')
@login_required
def emergency():
    return render_template('emergency.html', patient=current_user)

# ================= REAL SYMPTOM ASSESSMENT =================

@app.route('/assessment')
@login_required
def symptom_assessment():
    return render_template('symptom_assessment.html', patient=current_user)


@app.route('/assessment/predict', methods=['POST'])
@login_required
def assess_predict():
    # Collect selected symptoms
    present_symptoms = request.form.getlist('symptoms')
    symptom_severity = request.form.get('symptom_severity', 'moderate')
    symptom_duration = request.form.get('symptom_duration', '1-3 days')

    # Run the symptom assessment engine
    results = assess_symptoms(present_symptoms)

    if not results:
        flash('Not enough symptom information to make a diagnosis. Please select more symptoms.', 'danger')
        return redirect(url_for('symptom_assessment'))

    # Top result
    top = results[0]
    disease_name    = top['disease']
    confidence_pct  = top['confidence_pct']
    severity_str    = get_severity(confidence_pct, disease_name)

    # Colour per confidence
    if confidence_pct >= 70:
        top['color'] = '#DC3545'
    elif confidence_pct >= 45:
        top['color'] = '#FFC107'
    else:
        top['color'] = '#28A745'

    # Colour alternate results
    alt_colors = ['#6c757d', '#6c757d', '#6c757d', '#6c757d']
    for i, r in enumerate(results[1:], 0):
        if r['confidence_pct'] >= 70:
            r['color'] = '#DC3545'
        elif r['confidence_pct'] >= 45:
            r['color'] = '#FFC107'
        else:
            r['color'] = '#28A745'

    # Get medicines
    medicines = get_medicines_for_disease(disease_name, severity_str)

    # Hospital preferences
    hospital_type = request.form.get('hospital_type')
    max_distance  = request.form.get('max_distance')
    user_lat      = request.form.get('user_lat')
    user_lng      = request.form.get('user_lng')

    try:
        max_distance = float(max_distance) if max_distance else None
    except ValueError:
        max_distance = None
    try:
        user_lat = float(user_lat) if user_lat else None
    except ValueError:
        user_lat = None
    try:
        user_lng = float(user_lng) if user_lng else None
    except ValueError:
        user_lng = None

    hospitals_list = find_hospitals(
        city=current_user.city,
        hospital_type=hospital_type,
        disease=disease_name,
        max_distance=max_distance,
        user_lat=user_lat,
        user_lng=user_lng
    )

    # Doctor assignment
    specialty_docs = {
        "Pulmonology / Chest":  ["Dr. Randeep Guleria, DM", "Dr. S.K. Jindal, DM"],
        "Infectious Disease":   ["Dr. Sandeep Budhiraja, MD", "Dr. Rajesh Chawla, MD"],
        "Cardiology":           ["Dr. Devi Shetty, MS", "Dr. Naresh Trehan, MD"],
        "Neurology":            ["Dr. Ashok Panagariya, DM", "Dr. K. Sridhar, MCh"],
        "Gastroenterology":     ["Dr. S.K. Sarin, DM", "Dr. Y.K. Joshi, DM"],
        "Nephrology / Urology": ["Dr. Sanjay Pandya, MCh", "Dr. Rajiv Sinha, MCh"],
        "Endocrinology":        ["Dr. A.K. Das, MD", "Dr. Shashank Joshi, MD"],
        "General Medicine":     ["Dr. Suresh Advani, MD", "Dr. Amit Sharma, MD"],
        "Surgery / Emergency":  ["Dr. P.K. Dave, MS", "Dr. R.P. Goyal, MS"],
    }

    disease_specialty = {
        "Common Cold":                    "General Medicine",
        "Influenza (Flu)":                "General Medicine",
        "COVID-19":                        "Pulmonology / Chest",
        "Pneumonia":                       "Pulmonology / Chest",
        "Bronchitis":                      "Pulmonology / Chest",
        "Asthma":                          "Pulmonology / Chest",
        "Tuberculosis (TB)":               "Pulmonology / Chest",
        "Dengue Fever":                    "Infectious Disease",
        "Malaria":                         "Infectious Disease",
        "Typhoid Fever":                   "Infectious Disease",
        "Gastroenteritis (Stomach Flu)":   "Gastroenterology",
        "Food Poisoning":                  "Gastroenterology",
        "Acid Reflux / GERD":             "Gastroenterology",
        "Urinary Tract Infection (UTI)":   "Nephrology / Urology",
        "Kidney Infection / Pyelonephritis":"Nephrology / Urology",
        "Kidney Stones":                   "Nephrology / Urology",
        "Hypertension":                    "Cardiology",
        "Diabetes":                        "Endocrinology",
        "Migraine":                        "Neurology",
        "Allergic Reaction":               "General Medicine",
        "Malnutrition / Anemia":           "General Medicine",
        "Appendicitis":                    "Surgery / Emergency",
    }

    specialty    = disease_specialty.get(disease_name, "General Medicine")
    doc_list     = specialty_docs.get(specialty, specialty_docs["General Medicine"])
    doctor_name  = doc_list[hash(disease_name) % len(doc_list)]
    doctor_phone = hospitals_list[0]['phone'] if hospitals_list else "+91-800-HEALTH"

    doctor_advice_map = {
        "HIGH 🔴":   "Seek immediate medical attention. Visit the emergency department or call 108. This condition requires urgent professional medical care.",
        "MEDIUM 🟡": "Consult a doctor within 24 hours. Follow prescribed medications strictly. Monitor your condition and seek immediate care if symptoms worsen.",
        "LOW 🟢":    "Monitor symptoms at home. Stay hydrated and rest adequately. Consult a doctor if symptoms persist beyond 3–5 days or worsen.",
    }
    doctor_advice = doctor_advice_map.get(severity_str, doctor_advice_map["MEDIUM 🟡"])

    # Generate PDF (reuse existing generate_pdf function)
    prediction_data_for_pdf = {
        'disease':              disease_name,
        'risk_percentage':      confidence_pct,
        'health_risk_score':    confidence_pct,
        'health_risk_category': severity_str,
        'severity':             severity_str,
        'probability':          confidence_pct / 100,
        'medicines':            ' | '.join(medicines.get('PRIMARY', [])),
        'hospitals':            ', '.join([h['name'] for h in hospitals_list[:3]]),
        'doctor_advice':        doctor_advice,
        'doctor_name':          doctor_name,
        'doctor_phone':         doctor_phone,
        'referred_hospital':    hospitals_list[0]['name'] if hospitals_list else 'City Hospital',
    }
    pdf_filename = generate_pdf(current_user, prediction_data_for_pdf)

    # Save to predictions table
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO predictions
            (patient_id, disease, risk_percentage, health_risk_score,
             health_risk_category, severity, probability, symptoms, symptom_count,
             medicines, hospitals, doctor_advice, pdf_path, doctor_name, doctor_phone, referred_hospital)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.id, disease_name, confidence_pct, confidence_pct,
        severity_str, severity_str, confidence_pct / 100,
        str(present_symptoms), len(present_symptoms),
        ' | '.join(medicines.get('PRIMARY', [])),
        ', '.join([h['name'] for h in hospitals_list[:5]]),
        doctor_advice, pdf_filename,
        doctor_name, doctor_phone,
        hospitals_list[0]['name'] if hospitals_list else 'City Hospital'
    ))
    conn.commit()
    conn.close()

    return render_template(
        'assessment_result.html',
        patient=current_user,
        top_result=top,
        alt_results=results[1:],
        severity=severity_str,
        medicines=medicines,
        hospitals=hospitals_list,
        doctor_name=doctor_name,
        doctor_phone=doctor_phone,
        specialty=specialty,
        doctor_advice=doctor_advice,
        symptom_duration=symptom_duration,
        symptom_count=len(present_symptoms),
        pdf_file=pdf_filename,
        get_maps_url=get_google_maps_url,
        get_directions_url=get_directions_url,
    )



# ================= HEALTH VITALS TRACKER =================

@app.route('/vitals')
@login_required
def vitals():
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM health_vitals WHERE patient_id = ? ORDER BY date DESC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    vitals_list = [dict(r) for r in rows]
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('vitals.html', patient=current_user,
                           vitals_list=vitals_list, today=today)


@app.route('/vitals/add', methods=['POST'])
@login_required
def add_vitals():
    def _f(key):
        v = request.form.get(key, '').strip()
        try: return float(v) if v else None
        except: return None

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO health_vitals
            (patient_id, date, systolic_bp, diastolic_bp, blood_sugar,
             weight_kg, heart_rate, temperature_c, notes)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        current_user.id,
        request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
        _f('systolic_bp'), _f('diastolic_bp'), _f('blood_sugar'),
        _f('weight_kg'),   _f('heart_rate'),   _f('temperature_c'),
        request.form.get('notes', '').strip()
    ))
    conn.commit()
    conn.close()
    flash('✅ Vitals saved successfully!', 'success')
    return redirect(url_for('vitals'))


@app.route('/vitals/delete/<int:vid>', methods=['POST'])
@login_required
def delete_vitals(vid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM health_vitals WHERE id = ? AND patient_id = ?",
                (vid, current_user.id))
    conn.commit()
    conn.close()
    flash('Vitals entry deleted.', 'info')
    return redirect(url_for('vitals'))


# ================= PROFILE MANAGEMENT =================

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    cur  = conn.cursor()
    total = cur.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id = ?", (current_user.id,)
    ).fetchone()[0]
    reminders = cur.execute(
        "SELECT COUNT(*) FROM medicine_reminders WHERE patient_id = ? AND is_active = 1",
        (current_user.id,)
    ).fetchone()[0]
    vitals_count = cur.execute(
        "SELECT COUNT(*) FROM health_vitals WHERE patient_id = ?", (current_user.id,)
    ).fetchone()[0]
    last = cur.execute(
        "SELECT disease FROM predictions WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 1",
        (current_user.id,)
    ).fetchone()
    conn.close()
    stats = {
        'total_predictions': total,
        'reminders_count':   reminders,
        'vitals_count':      vitals_count,
        'last_disease':      last['disease'] if last else None,
    }
    return render_template('profile.html', patient=current_user, stats=stats)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    full_name      = request.form.get('full_name', '').strip()
    age            = request.form.get('age', current_user.age)
    contact        = request.form.get('contact', '').strip()
    city           = request.form.get('city', '').strip()
    smoking        = request.form.get('smoking', 'no')
    blood_pressure = request.form.get('blood_pressure', 'normal')
    blood_sugar    = request.form.get('blood_sugar', 'normal')

    if not full_name:
        flash('Name cannot be empty.', 'danger')
        return redirect(url_for('profile'))

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE users
        SET full_name=?, age=?, contact=?, city=?,
            smoking=?, blood_pressure=?, blood_sugar=?
        WHERE id=?
    """, (full_name, age, contact, city, smoking, blood_pressure,
          blood_sugar, current_user.id))
    conn.commit()
    conn.close()
    flash('✅ Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw  = request.form.get('current_password', '')
    new_pw      = request.form.get('new_password', '')
    confirm_pw  = request.form.get('confirm_password', '')

    conn = get_db()
    cur  = conn.cursor()
    user = cur.execute("SELECT * FROM users WHERE id = ?", (current_user.id,)).fetchone()

    if not check_password_hash(user['password_hash'], current_pw):
        flash('Current password is incorrect.', 'danger')
        conn.close()
        return redirect(url_for('profile'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        conn.close()
        return redirect(url_for('profile'))

    if len(new_pw) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        conn.close()
        return redirect(url_for('profile'))

    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(new_pw), current_user.id))
    conn.commit()
    conn.close()
    flash('✅ Password changed successfully!', 'success')
    return redirect(url_for('profile'))


# ================= BMI CALCULATOR =================

@app.route('/bmi')
@login_required
def bmi_calculator():
    return render_template('bmi_calculator.html', patient=current_user)


# ================= APPOINTMENTS =================

@app.route('/appointments')
@login_required
def appointments():
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM appointments WHERE patient_id = ? ORDER BY appointment_date DESC, appointment_time DESC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('appointments.html', patient=current_user,
                           appointments=[dict(r) for r in rows], today=today)


@app.route('/appointments/book', methods=['POST'])
@login_required
def book_appointment():
    doctor_name      = request.form.get('doctor_name', '').strip()
    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()
    visit_type       = request.form.get('visit_type', 'consultation')
    reason           = request.form.get('reason', '').strip()

    if not doctor_name or not appointment_date or not appointment_time:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('appointments'))

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO appointments
            (patient_id, doctor_name, appointment_date, appointment_time,
             visit_type, reason, status)
        VALUES (?,?,?,?,?,?,?)
    """, (current_user.id, doctor_name, appointment_date, appointment_time,
          visit_type, reason, 'pending'))
    conn.commit()
    conn.close()
    flash(f'✅ Appointment booked with {doctor_name} on {appointment_date} at {appointment_time}!', 'success')
    return redirect(url_for('appointments'))


@app.route('/appointments/cancel/<int:appt_id>', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE appointments SET status = 'cancelled' WHERE id = ? AND patient_id = ?",
        (appt_id, current_user.id)
    )
    conn.commit()
    conn.close()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('appointments'))


# ================= HEALTH TIPS =================

import random

HEALTH_TIPS_DATA = [
    # Nutrition
    {"icon":"🥗","title":"Eat a Rainbow of Vegetables","body":"Aim for 5 different coloured vegetables daily. Each colour provides unique antioxidants and micronutrients. Green leafy vegetables are especially rich in folate, iron, and calcium.","category":"nutrition","color":"#28A745"},
    {"icon":"💧","title":"Drink Water Before Meals","body":"Drinking 500ml of water 30 minutes before meals can reduce calorie intake by 13% and improve digestion. Aim for 8–10 glasses of water per day.","category":"nutrition","color":"#0066CC"},
    {"icon":"🫘","title":"Include Protein in Every Meal","body":"Protein keeps you full longer and helps maintain muscle mass. Good sources: eggs, dal, paneer, chicken, fish, tofu, sprouts. Aim for 0.8–1g per kg body weight daily.","category":"nutrition","color":"#28A745"},
    {"icon":"🌾","title":"Choose Whole Grains Over Refined","body":"Replace white rice, maida, and white bread with brown rice, whole wheat atta, and oats. Whole grains reduce diabetes risk by 25–30% and lower cholesterol.","category":"nutrition","color":"#F59E0B"},
    {"icon":"🧂","title":"Reduce Salt Intake","body":"WHO recommends <5g of salt per day. Excess salt raises blood pressure. Use lemon juice, herbs, and spices to flavour food instead of salt.","category":"nutrition","color":"#EF4444"},
    {"icon":"🫒","title":"Use Healthy Oils","body":"Cook with cold-pressed mustard oil, olive oil, or coconut oil. Avoid reusing fried oil — it forms harmful trans fats. Limit total fat to 25–30% of daily calories.","category":"nutrition","color":"#28A745"},
    # Exercise
    {"icon":"🚶","title":"Walk 10,000 Steps Daily","body":"Regular walking lowers blood pressure, reduces bad cholesterol, and improves mood. A 30-minute brisk walk burns 150–200 kcal and reduces heart disease risk by 30%.","category":"exercise","color":"#0066CC"},
    {"icon":"🏊","title":"Swimming is the Best All-Round Exercise","body":"Swimming engages 90% of muscle groups, is easy on joints, and is excellent for asthma patients. Even 20 minutes 3× a week improves cardiovascular fitness significantly.","category":"exercise","color":"#0066CC"},
    {"icon":"🧘","title":"Add Stretching to Your Routine","body":"5–10 minutes of stretching after exercise or before bed improves flexibility, prevents injury, and reduces muscle soreness. Focus on hamstrings, hip flexors, and shoulders.","category":"exercise","color":"#6f42c1"},
    {"icon":"💪","title":"Strength Training Prevents Osteoporosis","body":"Weight-bearing exercises 2–3× per week increase bone density and prevent osteoporosis. Simple bodyweight exercises (squats, push-ups) are highly effective — no gym needed.","category":"exercise","color":"#EF4444"},
    # Mental Health
    {"icon":"🧘","title":"Practice Deep Breathing Daily","body":"4-7-8 breathing: inhale 4 seconds, hold 7, exhale 8. Activates the parasympathetic nervous system, reduces cortisol, and lowers blood pressure within minutes.","category":"mental","color":"#6f42c1"},
    {"icon":"📵","title":"Digital Detox for 1 Hour Before Bed","body":"Blue light from screens suppresses melatonin production by up to 50%. Avoiding screens 1 hour before sleep improves sleep quality and reduces anxiety.","category":"mental","color":"#6f42c1"},
    {"icon":"🤝","title":"Maintain Strong Social Connections","body":"Strong social relationships reduce risk of depression by 50% and add 7.5 years to life expectancy. Call a friend or family member — it's more powerful than any supplement.","category":"mental","color":"#EC4899"},
    {"icon":"📓","title":"Journaling Reduces Anxiety","body":"Writing 3 things you are grateful for each morning lowers cortisol by 23% over 4 weeks. Even 5 minutes of journaling improves emotional processing and mental clarity.","category":"mental","color":"#F59E0B"},
    # Sleep
    {"icon":"😴","title":"Maintain a Consistent Sleep Schedule","body":"Going to bed and waking up at the same time — even on weekends — regulates your circadian rhythm. Irregular sleep patterns are linked to obesity, diabetes, and depression.","category":"sleep","color":"#3B82F6"},
    {"icon":"🌡️","title":"Keep Your Bedroom Cool","body":"The optimal sleep temperature is 18–22°C. Your core body temperature needs to drop to initiate sleep. A cool room improves deep sleep duration by up to 15%.","category":"sleep","color":"#3B82F6"},
    {"icon":"☕","title":"Cut Caffeine After 2 PM","body":"Caffeine has a half-life of 5–6 hours. A coffee at 3 PM means 50% of caffeine is still in your system at 9 PM. Switch to herbal tea (chamomile, ashwagandha) in the evenings.","category":"sleep","color":"#F59E0B"},
    # Prevention
    {"icon":"🩺","title":"Annual Health Check-up is Essential","body":"A yearly full-body check (CBC, lipid profile, blood sugar, thyroid, kidney function) can detect 80% of lifestyle diseases before symptoms appear. Prevention costs 10× less than treatment.","category":"prevention","color":"#0066CC"},
    {"icon":"🦷","title":"Oral Health Affects Heart Health","body":"Gum disease bacteria can enter the bloodstream and increase risk of heart disease and stroke by 20%. Brush twice daily, floss, and visit a dentist every 6 months.","category":"prevention","color":"#28A745"},
    {"icon":"🚭","title":"Quitting Smoking Reverses Damage","body":"Within 20 minutes of quitting: heart rate normalises. Within 12 hours: CO levels drop. Within 1 year: heart disease risk halves. Within 5 years: stroke risk equals a non-smoker's.","category":"prevention","color":"#EF4444"},
    {"icon":"🌞","title":"Vitamin D: The Sunshine Vitamin","body":"70% of Indians are Vitamin D deficient. 15–20 minutes of direct sun exposure (arms and legs) between 10 AM–2 PM produces 10,000 IU. Deficiency linked to depression, osteoporosis, and low immunity.","category":"prevention","color":"#F59E0B"},
    # Diabetes
    {"icon":"🩸","title":"Monitor Blood Sugar Regularly","body":"Fasting blood sugar > 126 mg/dL on 2 separate tests confirms diabetes. Check HbA1c every 3 months — it reflects average blood sugar over 3 months. Target: below 7% for diabetics.","category":"diabetes","color":"#DC3545"},
    {"icon":"🥑","title":"Low-Glycemic Foods Control Blood Sugar","body":"Foods with GI < 55 cause slow sugar release: basmati rice, oats, sweet potato, most vegetables, legumes, nuts. Replace sugary snacks with a handful of almonds or a small apple.","category":"diabetes","color":"#28A745"},
    {"icon":"👣","title":"Check Your Feet Every Day","body":"Diabetic neuropathy can mask foot injuries. Check between toes daily for cuts, blisters, or redness. Wear cotton socks and proper footwear. Never walk barefoot even at home.","category":"diabetes","color":"#EF4444"},
    # Heart
    {"icon":"❤️","title":"Know Your Numbers","body":"Keep track: BP < 120/80 mmHg, LDL cholesterol < 100 mg/dL, fasting blood sugar < 100 mg/dL, BMI 18.5–24.9. These four numbers predict 80% of heart attack risk.","category":"heart","color":"#DC3545"},
    {"icon":"🐟","title":"Omega-3 for a Stronger Heart","body":"2 servings of fatty fish per week (salmon, mackerel, sardines, tuna) reduces heart attack risk by 36%. Vegetarian sources: flaxseeds, walnuts, chia seeds. Or take fish oil supplements.","category":"heart","color":"#0066CC"},
    {"icon":"🚫","title":"Avoid Trans Fats Completely","body":"Trans fats (vanaspati, margarine, packaged bakery items) raise LDL and lower HDL simultaneously — the worst combination for heart health. Read food labels and avoid 'partially hydrogenated oils'.","category":"heart","color":"#EF4444"},
    # Immunity
    {"icon":"🧄","title":"Garlic is a Natural Antibiotic","body":"Allicin in raw garlic has proven antimicrobial and antiviral properties. 1–2 crushed raw garlic cloves per day reduces frequency of colds by 63%. Let garlic sit 10 minutes after crushing for maximum allicin.","category":"immunity","color":"#6f42c1"},
    {"icon":"🍋","title":"Vitamin C Boosts Immunity Naturally","body":"Vitamin C increases production of white blood cells. Best sources: amla (Indian gooseberry — 600mg/100g), guava, kiwi, bell peppers, citrus fruits. The body cannot store it — consume daily.","category":"immunity","color":"#F59E0B"},
    {"icon":"🌿","title":"Turmeric: Nature's Anti-inflammatory","body":"Curcumin in turmeric is a powerful anti-inflammatory. To absorb it: take with black pepper (piperine increases absorption by 2000%) and healthy fat. Golden milk (haldi doodh) is the traditional way.","category":"immunity","color":"#F59E0B"},
    {"icon":"🥛","title":"Probiotics Strengthen Your Gut Immune System","body":"70% of your immune system lives in your gut. Daily curd/yogurt, buttermilk, or fermented foods (idli, dosa, kanji) maintain healthy gut bacteria and reduce respiratory infections.","category":"immunity","color":"#28A745"},
]

TIPS_OF_DAY = [
    "Drink a glass of warm water with half a lemon every morning — it kick-starts digestion, provides Vitamin C, and alkalises the body.",
    "Take a 5-minute walk every hour if you have a desk job. Sitting for more than 8 hours daily increases mortality risk even if you exercise.",
    "The best time to exercise is whenever you will actually do it consistently — morning, evening or lunch break — consistency beats timing.",
    "Replace one processed snack today with a handful of mixed nuts — almonds, walnuts, and cashews. Your heart will thank you.",
    "Try box breathing before bed: 4 seconds inhale, 4 hold, 4 exhale, 4 hold. Repeat 4 times to calm your nervous system completely.",
    "Add 1 teaspoon of flaxseeds to your breakfast. They provide Omega-3, fibre, and lignans that protect against cancer and heart disease.",
    "Check your posture right now. Rounded shoulders and forward head posture cause neck pain and reduce lung capacity by up to 30%.",
    "Smile more — it genuinely lowers cortisol and blood pressure. Even a forced smile tricks the brain into reducing stress hormones.",
    "The last meal of the day should be at least 2–3 hours before sleep. Late-night eating raises blood sugar, disrupts sleep, and causes acid reflux.",
    "Fresh air and nature reduce stress hormones. Spend at least 20 minutes outside in green space today — no screens allowed.",
]

@app.route('/health-tips')
@login_required
def health_tips():
    # Pick a tip of the day based on today's date (deterministic)
    day_index = datetime.now().timetuple().tm_yday % len(TIPS_OF_DAY)
    return render_template('health_tips.html', patient=current_user,
                           tips=HEALTH_TIPS_DATA,
                           tip_of_day=TIPS_OF_DAY[day_index])


# ================= MEDICINE REMINDERS =================

@app.route('/reminders')
@login_required
def reminders():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM medicine_reminders WHERE patient_id = ? ORDER BY reminder_time ASC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    # Convert to plain dicts for easy template access
    reminder_list = [dict(r) for r in rows]
    return render_template('medicine_reminders.html', patient=current_user, reminders=reminder_list)


@app.route('/reminders/add', methods=['POST'])
@login_required
def add_reminder():
    medicine_name = request.form.get('medicine_name', '').strip()
    dosage        = request.form.get('dosage', '').strip()
    reminder_time = request.form.get('reminder_time', '').strip()
    frequency     = request.form.get('frequency', 'daily')
    start_date    = request.form.get('start_date', '').strip()
    end_date      = request.form.get('end_date', '').strip()
    instructions  = request.form.get('instructions', '').strip()

    if not medicine_name or not reminder_time:
        flash('Medicine name and alarm time are required.', 'danger')
        return redirect(url_for('reminders'))

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO medicine_reminders
            (patient_id, medicine_name, dosage, reminder_time, frequency, start_date, end_date, instructions, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (current_user.id, medicine_name, dosage, reminder_time, frequency, start_date, end_date, instructions))
    conn.commit()
    conn.close()
    flash(f'✅ Alarm set for {medicine_name} at {reminder_time}!', 'success')
    return redirect(url_for('reminders'))


@app.route('/reminders/toggle/<int:reminder_id>', methods=['POST'])
@login_required
def toggle_reminder(reminder_id):
    conn = get_db()
    cur  = conn.cursor()
    row = cur.execute(
        "SELECT * FROM medicine_reminders WHERE id = ? AND patient_id = ?",
        (reminder_id, current_user.id)
    ).fetchone()
    if row:
        new_state = 0 if row['is_active'] else 1
        cur.execute("UPDATE medicine_reminders SET is_active = ? WHERE id = ?", (new_state, reminder_id))
        conn.commit()
        flash('Reminder ' + ('resumed ▶' if new_state else 'paused ⏸'), 'info')
    conn.close()
    return redirect(url_for('reminders'))


@app.route('/reminders/delete/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "DELETE FROM medicine_reminders WHERE id = ? AND patient_id = ?",
        (reminder_id, current_user.id)
    )
    conn.commit()
    conn.close()
    flash('Reminder deleted.', 'info')
    return redirect(url_for('reminders'))


@app.route('/api/reminders/due-now')
@login_required
def reminders_due_now():
    """API endpoint polled by the frontend every 30 s to check if any alarm is due."""
    now_hhmm = datetime.now().strftime('%H:%M')
    today    = datetime.now().strftime('%Y-%m-%d')

    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute("""
        SELECT * FROM medicine_reminders
        WHERE patient_id = ?
          AND is_active = 1
          AND reminder_time = ?
          AND (start_date = '' OR start_date <= ?)
          AND (end_date   = '' OR end_date   >= ?)
          AND (last_fired != ? OR last_fired = '')
    """, (current_user.id, now_hhmm, today, today, today)).fetchall()

    # Update last_fired so we don't fire the same reminder twice in one minute
    for row in rows:
        cur.execute("UPDATE medicine_reminders SET last_fired = ? WHERE id = ?", (today, row['id']))
    conn.commit()
    conn.close()

    return jsonify({'reminders': [dict(r) for r in rows]})


# ================= BACKGROUND ALARM THREAD =================
# Runs server-side every 60 seconds.
# Triggers an OS desktop notification (Windows toast) as a fallback
# when the user has the app open but the browser tab is closed.

def _background_alarm_worker():
    """Background thread: checks medicine reminders every 60 seconds."""
    import subprocess

    def windows_toast(title, msg):
        """Show a Windows toast notification using PowerShell."""
        try:
            ps_script = (
                f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
                f"ContentType = WindowsRuntime] | Out-Null; "
                f"$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
                f"[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
                f"$textNodes = $template.GetElementsByTagName('text'); "
                f"$textNodes[0].AppendChild($template.CreateTextNode('{title}')) | Out-Null; "
                f"$textNodes[1].AppendChild($template.CreateTextNode('{msg}')) | Out-Null; "
                f"$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
                f"$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('HealthCare Plus'); "
                f"$notifier.Show($toast);"
            )
            subprocess.Popen(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    print("🔔 Medicine alarm background thread started.")
    while True:
        try:
            now_hhmm = datetime.now().strftime('%H:%M')
            today    = datetime.now().strftime('%Y-%m-%d')

            conn = get_db()
            cur  = conn.cursor()
            due_reminders = cur.execute("""
                SELECT mr.*, u.full_name
                FROM medicine_reminders mr
                JOIN users u ON mr.patient_id = u.id
                WHERE mr.is_active = 1
                  AND mr.reminder_time = ?
                  AND (mr.start_date = '' OR mr.start_date <= ?)
                  AND (mr.end_date   = '' OR mr.end_date   >= ?)
                  AND (mr.last_fired != ? OR mr.last_fired = '')
            """, (now_hhmm, today, today, today)).fetchall()

            for row in due_reminders:
                title = f"💊 Medicine Reminder – {row['full_name']}"
                body  = f"Time to take: {row['medicine_name']}"
                if row['dosage']:
                    body += f" — {row['dosage']}"
                if row['instructions']:
                    body += f" ({row['instructions']})"

                # Windows toast notification (shows even if browser is closed)
                windows_toast(title, body)
                print(f"[ALARM] {title}: {body}")

                # Mark as fired today so we don't repeat
                cur.execute(
                    "UPDATE medicine_reminders SET last_fired = ? WHERE id = ?",
                    (today, row['id'])
                )

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ALARM-THREAD ERROR] {e}")

        time.sleep(60)   # check every minute


# Start the alarm background thread once (daemon so it stops with the server)
_alarm_thread = threading.Thread(target=_background_alarm_worker, daemon=True)
_alarm_thread.start()


if __name__ == '__main__':
    app.run(debug=True, port=5001)

