from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
import io
import sys
import threading
import time
from functools import wraps

# Force UTF-8 encoding for stdout and stderr to prevent UnicodeEncodeError on Windows terminals
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Import services
from medicine_db import MEDICINE_DATABASE, HOSPITAL_DATABASE
from risk_calculator import calculate_health_risk_score, get_risk_recommendations
from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url, HOSPITALS_BY_CITY
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

# ================= DATABASE SETUP =================
def get_db():
    conn = sqlite3.connect("healthcare.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
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
    for col, default_val in [
        ('city', "'Default'"),
        ('smoking', "'no'"),
        ('blood_pressure', "'normal'"),
        ('blood_sugar', "'normal'"),
        ('diet_goal', "'Balanced'")
    ]:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT DEFAULT {default_val}")
        except Exception:
            pass
    
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
    
    # Migrate medicine_reminders table to ensure all new columns exist (handles old database files on pythonanywhere)
    try:
        cur.execute("SELECT start_date FROM medicine_reminders LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating medicine_reminders table...")
        try:
            cur.execute("ALTER TABLE medicine_reminders ADD COLUMN start_date TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE medicine_reminders ADD COLUMN end_date TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE medicine_reminders ADD COLUMN instructions TEXT DEFAULT ''")
        except Exception:
            pass
        print("medicine_reminders table migrated successfully!")

    try:
        cur.execute("ALTER TABLE users ADD COLUMN is_approved INTEGER DEFAULT 1")
    except Exception:
        pass

    # Check if admin user exists
    try:
        admin_user = cur.execute("SELECT * FROM users WHERE role = 'admin' OR username = 'admin'").fetchone()
        if not admin_user:
            print("Inserting default admin user...")
            password_hash = generate_password_hash("admin123")
            cur.execute("""
                INSERT INTO users (username, email, password_hash, full_name, age, role, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("admin", "admin@healthcare.com", password_hash, "System Administrator", 30, "admin", 1))
    except Exception as e:
        print(f"Error initializing admin user: {e}")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def init_extra_tables():
    """Create extra feature tables: health_vitals, appointments, messages, lab_results, wellness_log."""
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
        doctor_notes      TEXT    DEFAULT '',
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")
    # Safe migration: add doctor_notes if missing
    try:
        cur.execute("ALTER TABLE appointments ADD COLUMN doctor_notes TEXT DEFAULT ''")
    except Exception:
        pass

    # Patient-Doctor messaging
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id   INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        body        TEXT    NOT NULL,
        is_read     INTEGER DEFAULT 0,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id)   REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )""")

    # Lab results tracker
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_results (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id  INTEGER NOT NULL,
        test_name   TEXT    NOT NULL,
        test_date   TEXT    NOT NULL,
        result_value TEXT   DEFAULT '',
        unit        TEXT    DEFAULT '',
        normal_range TEXT   DEFAULT '',
        lab_name    TEXT    DEFAULT '',
        notes       TEXT    DEFAULT '',
        status      TEXT    DEFAULT 'normal',
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")

    # Daily wellness log
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wellness_log (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id    INTEGER NOT NULL,
        log_date      TEXT    NOT NULL,
        water_glasses INTEGER DEFAULT 0,
        sleep_hours   REAL    DEFAULT 0,
        steps         INTEGER DEFAULT 0,
        mood          TEXT    DEFAULT 'okay',
        exercise_min  INTEGER DEFAULT 0,
        calories      INTEGER DEFAULT 0,
        notes         TEXT    DEFAULT '',
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")

    # New tables: food_logs, medication_logs, symptom_journal
    cur.execute("""
    CREATE TABLE IF NOT EXISTS food_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id    INTEGER NOT NULL,
        food_name     TEXT NOT NULL,
        calories      INTEGER NOT NULL,
        protein       TEXT DEFAULT '0g',
        carbs         TEXT DEFAULT '0g',
        fat           TEXT DEFAULT '0g',
        goal_fitness  TEXT DEFAULT 'success',
        log_date      TEXT NOT NULL,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS medication_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id    INTEGER NOT NULL,
        reminder_id   INTEGER NOT NULL,
        log_date      TEXT NOT NULL,
        status        TEXT NOT NULL, -- 'taken', 'skipped'
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id),
        FOREIGN KEY (reminder_id) REFERENCES medicine_reminders(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS symptom_journal (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id    INTEGER NOT NULL,
        log_date      TEXT NOT NULL,
        mood          TEXT DEFAULT 'okay',
        symptoms      TEXT NOT NULL,
        severity      TEXT DEFAULT 'mild',
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS opd_tickets (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id        INTEGER NOT NULL,
        department        TEXT NOT NULL,
        token_number      INTEGER NOT NULL,
        queue_date        TEXT NOT NULL,
        status            TEXT DEFAULT 'waiting',
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
    def __init__(self, id, username, email, full_name, age, contact, role, city='Default', smoking='no', blood_pressure='normal', blood_sugar='normal', diet_goal='Balanced', is_approved=1):
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
        self.diet_goal = diet_goal
        self.is_approved = is_approved

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
            diet_goal = user['diet_goal'] if 'diet_goal' in user.keys() else 'Balanced'
            is_approved = user['is_approved'] if 'is_approved' in user.keys() else 1
        except:
            city = 'Default'
            smoking = 'no'
            blood_pressure = 'normal'
            blood_sugar = 'normal'
            diet_goal = 'Balanced'
            is_approved = 1
        
        return User(user['id'], user['username'], user['email'], 
                   user['full_name'], user['age'], user['contact'], user['role'],
                   city, smoking, blood_pressure, blood_sugar, diet_goal, is_approved)
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

def get_daily_health_score(patient_id, date_str):
    """
    Calculate health score (1-100) for a given patient and date.
    Medication Adherence (50 pts): (taken reminders / total active reminders) * 50
    Diet Alignment (50 pts): Baseline 30 pts. Recommended (+15 pts), Caution (+5 pts), Limit (-10 pts)
    """
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Medication Adherence Component
    reminders = cur.execute("""
        SELECT id FROM medicine_reminders
        WHERE patient_id = ?
          AND is_active = 1
          AND (start_date = '' OR start_date <= ?)
          AND (end_date = '' OR end_date >= ?)
    """, (patient_id, date_str, date_str)).fetchall()
    
    med_score = 50.0
    if reminders:
        total_reminders = len(reminders)
        taken = cur.execute("""
            SELECT COUNT(*) FROM medication_logs
            WHERE patient_id = ?
              AND log_date = ?
              AND status = 'taken'
        """, (patient_id, date_str)).fetchone()[0]
        med_score = round((min(taken, total_reminders) / total_reminders) * 50.0, 1)
        
    # 2. Diet Alignment Component
    foods = cur.execute("""
        SELECT goal_fitness FROM food_logs
        WHERE patient_id = ?
          AND log_date = ?
    """, (patient_id, date_str)).fetchall()
    
    diet_score = 30.0 # Baseline
    if foods:
        score_delta = 0
        for f in foods:
            fit = f['goal_fitness']
            if fit == 'success':
                score_delta += 15
            elif fit == 'warning':
                score_delta += 5
            elif fit == 'danger':
                score_delta -= 10
        diet_score = max(0.0, min(50.0, diet_score + score_delta))
        
    conn.close()
    return int(med_score + diet_score)

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
        # Patient home dashboard
        conn = get_db()
        cur  = conn.cursor()
        today    = datetime.now().strftime('%Y-%m-%d')
        hour     = datetime.now().hour
        greeting = 'Morning' if hour < 12 else ('Afternoon' if hour < 17 else 'Evening')

        total_predictions  = cur.execute("SELECT COUNT(*) FROM predictions WHERE patient_id=?", (current_user.id,)).fetchone()[0]
        reminders_count    = cur.execute("SELECT COUNT(*) FROM medicine_reminders WHERE patient_id=? AND is_active=1", (current_user.id,)).fetchone()[0]
        vitals_count       = cur.execute("SELECT COUNT(*) FROM health_vitals WHERE patient_id=?", (current_user.id,)).fetchone()[0]
        appointments_count = cur.execute("SELECT COUNT(*) FROM appointments WHERE patient_id=? AND status NOT IN ('cancelled')", (current_user.id,)).fetchone()[0]

        latest_vitals      = cur.execute("SELECT * FROM health_vitals WHERE patient_id=? ORDER BY date DESC LIMIT 1", (current_user.id,)).fetchone()
        last_prediction    = cur.execute("SELECT * FROM predictions WHERE patient_id=? ORDER BY timestamp DESC LIMIT 1", (current_user.id,)).fetchone()
        today_wellness     = cur.execute("SELECT * FROM wellness_log WHERE patient_id=? AND log_date=?", (current_user.id, today)).fetchone()
        upcoming_reminders = cur.execute(
            "SELECT * FROM medicine_reminders WHERE patient_id=? AND is_active=1 ORDER BY reminder_time ASC LIMIT 5",
            (current_user.id,)
        ).fetchall()
        score = get_daily_health_score(current_user.id, today)
        conn.close()

        stats = {
            'total_predictions':   total_predictions,
            'reminders_count':     reminders_count,
            'vitals_count':        vitals_count,
            'appointments_count':  appointments_count,
        }
        return render_template('home.html',
            patient=current_user,
            greeting=greeting,
            stats=stats,
            latest_vitals=dict(latest_vitals) if latest_vitals else None,
            last_prediction=dict(last_prediction) if last_prediction else None,
            today_wellness=dict(today_wellness) if today_wellness else None,
            upcoming_reminders=[dict(r) for r in upcoming_reminders],
            health_score=score
        )
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
        is_approved = 0 if role == 'doctor' else 1
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, age, contact, city, smoking, blood_pressure, blood_sugar, role, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, full_name, age, contact, city, smoking, blood_pressure, blood_sugar, role, is_approved))
        conn.commit()
        conn.close()
        
        if role == 'doctor':
            flash('✅ Doctor account registered successfully! Please wait for administrator approval before logging in.', 'info')
        else:
            flash('✅ Account created successfully! Please login.', 'success')
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
            # Check approval status
            try:
                is_approved = user['is_approved'] if 'is_approved' in user.keys() else 1
            except:
                is_approved = 1
                
            if user['role'] == 'doctor' and not is_approved:
                flash('❌ Your doctor account is pending administrator approval.', 'danger')
                conn.close()
                return redirect(url_for('login'))
                
            # Handle both old and new database schemas
            try:
                city = user['city'] if 'city' in user.keys() else 'Default'
                smoking = user['smoking'] if 'smoking' in user.keys() else 'no'
                blood_pressure = user['blood_pressure'] if 'blood_pressure' in user.keys() else 'normal'
                blood_sugar = user['blood_sugar'] if 'blood_sugar' in user.keys() else 'normal'
                diet_goal = user['diet_goal'] if 'diet_goal' in user.keys() else 'Balanced'
            except:
                city = 'Default'
                smoking = 'no'
                blood_pressure = 'normal'
                blood_sugar = 'normal'
                diet_goal = 'Balanced'
            
            user_obj = User(user['id'], user['username'], user['email'],
                          user['full_name'], user['age'], user['contact'], user['role'],
                          city, smoking, blood_pressure, blood_sugar, diet_goal, is_approved)
            login_user(user_obj)
            flash(f'Welcome back, {user["full_name"]}! 👋', 'success')
            
            if user['role'] == 'doctor':
                return redirect(url_for('dashboard'))
            return redirect(url_for('index'))
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
    # Legacy route — redirect to the new rule-based assessment
    flash('Please use the new Symptom Assessment for accurate results.', 'info')
    return redirect(url_for('symptom_assessment'))

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
    
    connected_patients = cur.execute("""
        SELECT DISTINCT u.id, u.full_name, u.email, u.age, u.contact, u.city, u.diet_goal
        FROM users u
        WHERE u.role = 'patient' AND (
            u.id IN (
                SELECT patient_id FROM appointments 
                WHERE doctor_name = ?
            ) OR u.id IN (
                SELECT sender_id FROM messages WHERE receiver_id = ?
            ) OR u.id IN (
                SELECT receiver_id FROM messages WHERE sender_id = ?
            )
        )
    """, (current_user.full_name, current_user.id, current_user.id)).fetchall()
    
    conn.close()
    
    stats = {
        'total_patients': total_patients,
        'total_predictions': total_predictions,
        'high_risk': high_risk,
        'today_count': today_count,
        'avg_risk_score': round(avg_risk_score, 1),
        'high_risk_patients': high_risk_patients,
        'disease_stats': disease_stats,
        'age_disease_stats': age_disease_stats,
        'connected_patients': [dict(p) for p in connected_patients]
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

@app.route('/nearest-hospitals')
@login_required
def nearest_hospitals():
    """Nearest hospital finder page with live GPS, map, phone & route."""
    import json

    # Flatten all hospitals from every city into one list
    all_hospitals = []
    for city_key, city_list in HOSPITALS_BY_CITY.items():
        if city_key == "Default":
            continue
        for h in city_list:
            # Include city label so the JS knows which city each hospital belongs to
            entry = dict(h)
            entry['city'] = city_key
            all_hospitals.append(entry)

    hospitals_json = json.dumps(all_hospitals)
    return render_template('nearest_hospitals.html',
                           patient=current_user,
                           hospitals_json=hospitals_json)


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


# ================= DIET PLANS =================

@app.route('/diet-plans', methods=['GET', 'POST'])
@login_required
def diet_plans():
    if current_user.role != 'patient':
        flash('Only patients can access diet plans.', 'warning')
        return redirect(url_for('index'))
    
    conn = get_db()
    cur = conn.cursor()
    
    if request.method == 'POST':
        goal = request.form.get('diet_goal', 'Balanced')
        cur.execute("UPDATE users SET diet_goal = ? WHERE id = ?", (goal, current_user.id))
        conn.commit()
        # Update current user object in session
        current_user.diet_goal = goal
        flash(f'Active diet plan successfully updated to: {goal}!', 'success')
        conn.close()
        return redirect(url_for('diet_plans'))
        
    conn.close()
    return render_template('diet_plan.html', patient=current_user)


# ================= FOOD SCANNER =================

@app.route('/food-scanner')
@login_required
def food_scanner():
    if current_user.role != 'patient':
        flash('Only patients can access the food scanner.', 'warning')
        return redirect(url_for('index'))
    return render_template('food_scanner.html', patient=current_user)


@app.route('/api/food/scan', methods=['POST'])
@login_required
def scan_food():
    if current_user.role != 'patient':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    import food_scanner_service

    data = request.get_json() or {}
    food_name = data.get('food_name', '').strip()
    image_data = data.get('image_data', '')

    api_vision_used = "N/A"
    api_nutrition_used = "N/A"
    confidence = 1.0

    # Step 1: Vision identification if image is provided and name is not explicitly passed
    if image_data and not food_name:
        try:
            food_name, confidence, api_vision_used = food_scanner_service.identify_food_from_image(image_data)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Vision analysis failed: {str(e)}'}), 500

    if not food_name:
        return jsonify({'status': 'error', 'message': 'Please provide a food name or upload a clear food image.'}), 400

    # Step 2: Fetch nutrition info
    try:
        nutrition, api_nutrition_used = food_scanner_service.get_food_nutrition(food_name)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Nutrition lookup failed: {str(e)}'}), 500

    # Step 3: Check dietary goal compatibility
    diet_goal = getattr(current_user, 'diet_goal', 'Balanced')
    fits, rationale, color_class = food_scanner_service.evaluate_goal_fitness(nutrition, diet_goal)

    return jsonify({
        'status': 'success',
        'food_name': nutrition['name'],
        'calories': nutrition['calories'],
        'protein': f"{nutrition['protein']}g",
        'carbs': f"{nutrition['carbs']}g",
        'fat': f"{nutrition['fat']}g",
        'diet_goal': diet_goal,
        'fits_goal': fits,
        'rationale': rationale,
        'color_class': color_class,
        'api_vision_used': api_vision_used,
        'api_nutrition_used': api_nutrition_used,
        'confidence': round(confidence * 100)
    })


@app.route('/api/food/log', methods=['POST'])
@login_required
def log_food_calories():
    if current_user.role != 'patient':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    data = request.get_json() or {}
    try:
        calories = int(data.get('calories', 0))
    except (ValueError, TypeError):
        calories = 0
    food_name = data.get('food_name', 'Scanned Food')
    
    if calories <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid calories'}), 400
        
    today = datetime.now().strftime('%Y-%m-%d')
    protein = data.get('protein', '0g')
    carbs = data.get('carbs', '0g')
    fat = data.get('fat', '0g')
    goal_fitness = data.get('goal_fitness', 'success')

    conn = get_db()
    cur  = conn.cursor()

    # Log to detailed food tracker
    cur.execute("""
        INSERT INTO food_logs (patient_id, food_name, calories, protein, carbs, fat, goal_fitness, log_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, food_name, calories, protein, carbs, fat, goal_fitness, today))
    
    existing = cur.execute(
        "SELECT id, calories, notes FROM wellness_log WHERE patient_id=? AND log_date=?",
        (current_user.id, today)
    ).fetchone()
    
    if existing:
        new_cals = (existing['calories'] or 0) + calories
        new_notes = (existing['notes'] or '').strip()
        log_entry = f"Scanned: {food_name} (+{calories} kcal)"
        if new_notes:
            new_notes = f"{new_notes} | {log_entry}"
        else:
            new_notes = log_entry
            
        cur.execute("""
            UPDATE wellness_log 
            SET calories = ?, notes = ? 
            WHERE id = ?
        """, (new_cals, new_notes, existing['id']))
    else:
        new_notes = f"Scanned: {food_name} (+{calories} kcal)"
        cur.execute("""
            INSERT INTO wellness_log (patient_id, log_date, water_glasses, sleep_hours, steps, mood, exercise_min, calories, notes)
            VALUES (?, ?, 0, 0, 0, 'okay', 0, ?, ?)
        """, (current_user.id, today, calories, new_notes))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': f'Logged {calories} kcal for {food_name}!'})


# ================= FITNESS COACHING =================

@app.route('/fitness-coaching')
@login_required
def fitness_coaching():
    if current_user.role != 'patient':
        flash('Only patients can access fitness coaching.', 'warning')
        return redirect(url_for('index'))
    return render_template('fitness_coaching.html', patient=current_user)


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
    now_hhmm = request.args.get('client_time', '').strip()
    today    = request.args.get('client_date', '').strip()

    if not now_hhmm:
        now_hhmm = datetime.now().strftime('%H:%M')
    if not today:
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


# ================= MESSAGING (Patient ↔ Doctor) =================

@app.route('/messages')
@login_required
def messages():
    conn = get_db()
    cur  = conn.cursor()
    if current_user.role == 'patient':
        # List all doctors patient has messaged or can message
        doctors = cur.execute("SELECT id, full_name, username FROM users WHERE role='doctor'").fetchall()
        # Get conversation partner from query param
        partner_id = request.args.get('with', type=int)
        partner = None
        conv = []
        if partner_id:
            partner = cur.execute("SELECT id, full_name FROM users WHERE id=?", (partner_id,)).fetchone()
            conv = cur.execute("""
                SELECT m.*, u.full_name as sender_name
                FROM messages m JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id=? AND m.receiver_id=?)
                   OR (m.sender_id=? AND m.receiver_id=?)
                ORDER BY m.created_at ASC
            """, (current_user.id, partner_id, partner_id, current_user.id)).fetchall()
            # Mark received as read
            cur.execute("UPDATE messages SET is_read=1 WHERE receiver_id=? AND sender_id=?",
                        (current_user.id, partner_id))
            conn.commit()
    else:
        # Doctor: list all patients who messaged them
        doctors = []
        partner_id = request.args.get('with', type=int)
        partner = None
        conv = []
        if partner_id:
            partner = cur.execute("SELECT id, full_name FROM users WHERE id=?", (partner_id,)).fetchone()
            conv = cur.execute("""
                SELECT m.*, u.full_name as sender_name
                FROM messages m JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id=? AND m.receiver_id=?)
                   OR (m.sender_id=? AND m.receiver_id=?)
                ORDER BY m.created_at ASC
            """, (current_user.id, partner_id, partner_id, current_user.id)).fetchall()
            cur.execute("UPDATE messages SET is_read=1 WHERE receiver_id=? AND sender_id=?",
                        (current_user.id, partner_id))
            conn.commit()

    # Unread count per conversation partner
    inbox = cur.execute("""
        SELECT sender_id, u.full_name, COUNT(*) as cnt
        FROM messages m JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id=? AND m.is_read=0
        GROUP BY m.sender_id
    """, (current_user.id,)).fetchall()

    # Conversation list
    threads = cur.execute("""
        SELECT DISTINCT
            CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END as partner_id,
            u.full_name as partner_name,
            u.role as partner_role
        FROM messages m JOIN users u
          ON u.id = CASE WHEN m.sender_id=? THEN m.receiver_id ELSE m.sender_id END
        WHERE sender_id=? OR receiver_id=?
        ORDER BY m.created_at DESC
    """, (current_user.id, current_user.id, current_user.id, current_user.id)).fetchall()

    conn.close()
    return render_template('messages.html',
                           patient=current_user,
                           doctors=[dict(d) for d in doctors],
                           partner=dict(partner) if partner else None,
                           partner_id=partner_id,
                           conv=[dict(c) for c in conv],
                           inbox=[dict(i) for i in inbox],
                           threads=[dict(t) for t in threads])


@app.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    receiver_id = request.form.get('receiver_id', type=int)
    body        = request.form.get('body', '').strip()
    if not receiver_id or not body:
        flash('Cannot send empty message.', 'danger')
        return redirect(url_for('messages'))
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("INSERT INTO messages (sender_id, receiver_id, body) VALUES (?,?,?)",
                (current_user.id, receiver_id, body))
    conn.commit()
    conn.close()
    return redirect(url_for('messages', **{'with': receiver_id}))


@app.route('/api/messages/unread')
@login_required
def unread_count():
    conn = get_db()
    cur  = conn.cursor()
    cnt  = cur.execute("SELECT COUNT(*) FROM messages WHERE receiver_id=? AND is_read=0",
                       (current_user.id,)).fetchone()[0]
    conn.close()
    return jsonify({'unread': cnt})


# ================= LAB RESULTS TRACKER =================

@app.route('/lab-results')
@login_required
def lab_results():
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM lab_results WHERE patient_id=? ORDER BY test_date DESC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('lab_results.html',
                           patient=current_user,
                           results=[dict(r) for r in rows],
                           today=today)


@app.route('/lab-results/add', methods=['POST'])
@login_required
def add_lab_result():
    conn = get_db()
    cur  = conn.cursor()
    val   = request.form.get('result_value','').strip()
    unit  = request.form.get('unit','').strip()
    nrng  = request.form.get('normal_range','').strip()
    # Auto-determine status
    status = 'normal'
    try:
        v = float(val)
        if nrng and '-' in nrng:
            lo, hi = nrng.split('-')
            if v < float(lo.strip()) or v > float(hi.strip()):
                status = 'abnormal'
        elif nrng and '<' in nrng:
            hi = float(nrng.replace('<','').strip())
            if v >= hi:
                status = 'abnormal'
        elif nrng and '>' in nrng:
            lo = float(nrng.replace('>','').strip())
            if v <= lo:
                status = 'abnormal'
    except Exception:
        status = 'normal'

    cur.execute("""
        INSERT INTO lab_results
            (patient_id, test_name, test_date, result_value, unit,
             normal_range, lab_name, notes, status)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        current_user.id,
        request.form.get('test_name','').strip(),
        request.form.get('test_date', datetime.now().strftime('%Y-%m-%d')),
        val, unit, nrng,
        request.form.get('lab_name','').strip(),
        request.form.get('notes','').strip(),
        status
    ))
    conn.commit()
    conn.close()
    flash('✅ Lab result saved!', 'success')
    return redirect(url_for('lab_results'))


@app.route('/lab-results/delete/<int:rid>', methods=['POST'])
@login_required
def delete_lab_result(rid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM lab_results WHERE id=? AND patient_id=?", (rid, current_user.id))
    conn.commit()
    conn.close()
    flash('Lab result deleted.', 'info')
    return redirect(url_for('lab_results'))


# ================= DAILY WELLNESS LOG =================

@app.route('/wellness')
@login_required
def wellness():
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM wellness_log WHERE patient_id=? ORDER BY log_date DESC LIMIT 30",
        (current_user.id,)
    ).fetchall()
    today = datetime.now().strftime('%Y-%m-%d')
    today_log = cur.execute(
        "SELECT * FROM wellness_log WHERE patient_id=? AND log_date=?",
        (current_user.id, today)
    ).fetchone()
    conn.close()
    return render_template('wellness.html',
                           patient=current_user,
                           logs=[dict(r) for r in rows],
                           today=today,
                           today_log=dict(today_log) if today_log else None)


@app.route('/wellness/save', methods=['POST'])
@login_required
def save_wellness():
    log_date = request.form.get('log_date', datetime.now().strftime('%Y-%m-%d'))
    conn = get_db()
    cur  = conn.cursor()
    existing = cur.execute(
        "SELECT id FROM wellness_log WHERE patient_id=? AND log_date=?",
        (current_user.id, log_date)
    ).fetchone()

    def _i(k, default=0):
        try: return int(request.form.get(k, default) or default)
        except: return default
    def _f2(k, default=0):
        try: return float(request.form.get(k, default) or default)
        except: return default

    vals = (
        _i('water_glasses'), _f2('sleep_hours'), _i('steps'),
        request.form.get('mood','okay'),
        _i('exercise_min'), _i('calories'),
        request.form.get('notes','').strip()
    )

    if existing:
        cur.execute("""
            UPDATE wellness_log SET water_glasses=?, sleep_hours=?, steps=?,
            mood=?, exercise_min=?, calories=?, notes=?
            WHERE patient_id=? AND log_date=?
        """, (*vals, current_user.id, log_date))
    else:
        cur.execute("""
            INSERT INTO wellness_log
                (patient_id, log_date, water_glasses, sleep_hours, steps,
                 mood, exercise_min, calories, notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (current_user.id, log_date, *vals))

    conn.commit()
    conn.close()
    flash('✅ Wellness log saved!', 'success')
    return redirect(url_for('wellness'))


@app.route('/wellness/delete/<int:wid>', methods=['POST'])
@login_required
def delete_wellness(wid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM wellness_log WHERE id=? AND patient_id=?", (wid, current_user.id))
    conn.commit()
    conn.close()
    flash('Entry deleted.', 'info')
    return redirect(url_for('wellness'))


# ================= DOCTOR APPOINTMENT MANAGEMENT =================

@app.route('/doctor/appointments')
@login_required
@role_required('doctor')
def doctor_appointments():
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute("""
        SELECT a.*, u.full_name as patient_name, u.age, u.contact, u.email
        FROM appointments a JOIN users u ON a.patient_id = u.id
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """).fetchall()
    conn.close()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('doctor_appointments.html',
                           doctor=current_user,
                           appointments=[dict(r) for r in rows],
                           today=today)


@app.route('/doctor/appointments/update/<int:appt_id>', methods=['POST'])
@login_required
@role_required('doctor')
def update_appointment(appt_id):
    status       = request.form.get('status', 'confirmed')
    doctor_notes = request.form.get('doctor_notes', '').strip()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE appointments SET status=?, doctor_notes=? WHERE id=?",
        (status, doctor_notes, appt_id)
    )
    conn.commit()
    conn.close()
    flash(f'✅ Appointment {status}.', 'success')
    return redirect(url_for('doctor_appointments'))


# ================= ADMIN ROUTES =================
@app.route('/admin/doctors')
@login_required
def admin_doctors():
    if current_user.role != 'admin':
        flash('Access denied. Administrator permissions required.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db()
    cur = conn.cursor()
    pending_doctors = cur.execute("SELECT * FROM users WHERE role = 'doctor' AND is_approved = 0").fetchall()
    approved_doctors = cur.execute("SELECT * FROM users WHERE role = 'doctor' AND is_approved = 1").fetchall()
    conn.close()
    
    return render_template('admin_doctors.html', 
                           pending_doctors=[dict(d) for d in pending_doctors],
                           approved_doctors=[dict(d) for d in approved_doctors])


@app.route('/admin/approve-doctor/<int:doctor_id>', methods=['POST'])
@login_required
def approve_doctor(doctor_id):
    if current_user.role != 'admin':
        flash('Access denied. Administrator permissions required.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_approved = 1 WHERE id = ? AND role = 'doctor'", (doctor_id,))
    conn.commit()
    conn.close()
    
    flash('Doctor account approved successfully!', 'success')
    return redirect(url_for('admin_doctors'))


@app.route('/admin/reject-doctor/<int:doctor_id>', methods=['POST'])
@login_required
def reject_doctor(doctor_id):
    if current_user.role != 'admin':
        flash('Access denied. Administrator permissions required.', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ? AND role = 'doctor'", (doctor_id,))
    conn.commit()
    conn.close()
    
    flash('Doctor account rejected and deleted.', 'info')
    return redirect(url_for('admin_doctors'))


@app.route('/api/medication/log', methods=['POST'])
@login_required
def log_medication():
    if current_user.role != 'patient':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    data = request.get_json() or {}
    reminder_id = data.get('reminder_id')
    status = data.get('status', 'taken') # 'taken', 'skipped'
    
    if not reminder_id:
        return jsonify({'status': 'error', 'message': 'Reminder ID is required.'}), 400

    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cur = conn.cursor()
    
    # Check if already logged today
    existing = cur.execute("""
        SELECT id FROM medication_logs
        WHERE patient_id = ? AND reminder_id = ? AND log_date = ?
    """, (current_user.id, reminder_id, today)).fetchone()
    
    if existing:
        cur.execute("""
            UPDATE medication_logs SET status = ?
            WHERE id = ?
        """, (status, existing['id']))
    else:
        cur.execute("""
            INSERT INTO medication_logs (patient_id, reminder_id, log_date, status)
            VALUES (?, ?, ?, ?)
        """, (current_user.id, reminder_id, today, status))
        
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': f'Medication logged as {status}!'})


@app.route('/symptom-journal', methods=['GET', 'POST'])
@login_required
def symptom_journal():
    if current_user.role != 'patient':
        flash('Only patients can access the symptom journal.', 'warning')
        return redirect(url_for('index'))
        
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        mood = request.form.get('mood', 'okay')
        symptoms = request.form.get('symptoms', '').strip()
        severity = request.form.get('severity', 'mild')
        
        if not symptoms:
            flash('Symptom entry cannot be empty.', 'danger')
        else:
            existing = cur.execute("""
                SELECT id FROM symptom_journal
                WHERE patient_id = ? AND log_date = ?
            """, (current_user.id, today)).fetchone()
            
            if existing:
                cur.execute("""
                    UPDATE symptom_journal
                    SET mood = ?, symptoms = ?, severity = ?
                    WHERE id = ?
                """, (mood, symptoms, severity, existing['id']))
            else:
                cur.execute("""
                    INSERT INTO symptom_journal (patient_id, log_date, mood, symptoms, severity)
                    VALUES (?, ?, ?, ?, ?)
                """, (current_user.id, today, mood, symptoms, severity))
            conn.commit()
            flash('✅ Symptom entry saved successfully!', 'success')
            
    entries = cur.execute("""
        SELECT * FROM symptom_journal
        WHERE patient_id = ?
        ORDER BY log_date DESC LIMIT 30
    """, (current_user.id,)).fetchall()
    
    conn.close()
    return render_template('symptom_journal.html', patient=current_user, entries=[dict(e) for e in entries], today=today)


@app.route('/export-health-report')
@login_required
def export_health_report():
    if current_user.role != 'patient':
        flash('Only patients can export health reports.', 'warning')
        return redirect(url_for('index'))

    import health_report_pdf
    
    patient_id = current_user.id
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cur = conn.cursor()
    
    food_logs = cur.execute("""
        SELECT * FROM food_logs
        WHERE patient_id = ? AND log_date = ?
        ORDER BY created_at ASC
    """, (patient_id, today)).fetchall()
    
    med_logs = cur.execute("""
        SELECT ml.*, mr.medicine_name, mr.reminder_time
        FROM medication_logs ml
        JOIN medicine_reminders mr ON ml.reminder_id = mr.id
        WHERE ml.patient_id = ? AND ml.log_date = ?
    """, (patient_id, today)).fetchall()
    
    symptom_logs = cur.execute("""
        SELECT * FROM symptom_journal
        WHERE patient_id = ? AND log_date = ?
    """, (patient_id, today)).fetchall()
    
    score = get_daily_health_score(patient_id, today)
    conn.close()
    
    filename = f"Health_Report_{current_user.full_name.replace(' ', '_')}_{today}.pdf"
    reports_dir = os.path.join(os.path.dirname(__file__), "static", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    file_path = os.path.join(reports_dir, filename)
    
    try:
        health_report_pdf.generate_health_report(
            patient_name=current_user.full_name,
            age=current_user.age,
            contact=current_user.contact,
            diet_goal=getattr(current_user, 'diet_goal', 'Balanced'),
            health_score=score,
            food_logs=[dict(f) for f in food_logs],
            medication_logs=[dict(m) for m in med_logs],
            symptom_logs=[dict(s) for s in symptom_logs],
            file_path=file_path
        )
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f"Error generating health report: {str(e)}", "danger")
        return redirect(url_for('symptom_journal'))


@app.route('/doctor/patient/<int:patient_id>')
@login_required
@role_required('doctor')
def doctor_patient_view(patient_id):
    conn = get_db()
    cur = conn.cursor()
    
    patient_row = cur.execute("SELECT * FROM users WHERE id = ? AND role = 'patient'", (patient_id,)).fetchone()
    if not patient_row:
        flash('Patient not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
        
    patient_obj = User(
        patient_row['id'], patient_row['username'], patient_row['email'],
        patient_row['full_name'], patient_row['age'], patient_row['contact'], patient_row['role'],
        patient_row['city'], patient_row['smoking'], patient_row['blood_pressure'], patient_row['blood_sugar'],
        patient_row['diet_goal'], patient_row['is_approved']
    )
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    food_logs = cur.execute("""
        SELECT * FROM food_logs
        WHERE patient_id = ?
        ORDER BY log_date DESC, created_at DESC LIMIT 30
    """, (patient_id,)).fetchall()
    
    med_logs = cur.execute("""
        SELECT ml.*, mr.medicine_name, mr.reminder_time
        FROM medication_logs ml
        JOIN medicine_reminders mr ON ml.reminder_id = mr.id
        WHERE ml.patient_id = ?
        ORDER BY ml.log_date DESC, ml.created_at DESC LIMIT 30
    """, (patient_id,)).fetchall()
    
    symptom_logs = cur.execute("""
        SELECT * FROM symptom_journal
        WHERE patient_id = ?
        ORDER BY log_date DESC LIMIT 30
    """, (patient_id,)).fetchall()
    
    score = get_daily_health_score(patient_id, today)
    conn.close()
    
    return render_template(
        'doctor_patient_view.html',
        doctor=current_user,
        patient=patient_obj,
        food_logs=[dict(f) for f in food_logs],
        medication_logs=[dict(m) for m in med_logs],
        symptom_logs=[dict(s) for s in symptom_logs],
        health_score=score
    )


@app.route('/doctor/patient/<int:patient_id>/export')
@login_required
@role_required('doctor')
def doctor_export_patient_report(patient_id):
    conn = get_db()
    cur = conn.cursor()
    
    patient_row = cur.execute("SELECT * FROM users WHERE id = ? AND role = 'patient'", (patient_id,)).fetchone()
    if not patient_row:
        flash('Patient not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
        
    import health_report_pdf
    today = datetime.now().strftime('%Y-%m-%d')
    
    food_logs = cur.execute("""
        SELECT * FROM food_logs
        WHERE patient_id = ? AND log_date = ?
        ORDER BY created_at ASC
    """, (patient_id, today)).fetchall()
    
    med_logs = cur.execute("""
        SELECT ml.*, mr.medicine_name, mr.reminder_time
        FROM medication_logs ml
        JOIN medicine_reminders mr ON ml.reminder_id = mr.id
        WHERE ml.patient_id = ? AND ml.log_date = ?
    """, (patient_id, today)).fetchall()
    
    symptom_logs = cur.execute("""
        SELECT * FROM symptom_journal
        WHERE patient_id = ? AND log_date = ?
    """, (patient_id, today)).fetchall()
    
    score = get_daily_health_score(patient_id, today)
    conn.close()
    
    filename = f"Health_Report_{patient_row['full_name'].replace(' ', '_')}_{today}.pdf"
    reports_dir = os.path.join(os.path.dirname(__file__), "static", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    file_path = os.path.join(reports_dir, filename)
    
    try:
        health_report_pdf.generate_health_report(
            patient_name=patient_row['full_name'],
            age=patient_row['age'],
            contact=patient_row['contact'],
            diet_goal=patient_row['diet_goal'] if 'diet_goal' in patient_row.keys() else 'Balanced',
            health_score=score,
            food_logs=[dict(f) for f in food_logs],
            medication_logs=[dict(m) for m in med_logs],
            symptom_logs=[dict(s) for s in symptom_logs],
            file_path=file_path
        )
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f"Error generating patient health report: {str(e)}", "danger")
        return redirect(url_for('doctor_patient_view', patient_id=patient_id))


# ================= OPD LIVE QUEUE DESK =================

def get_serving_token(department, today):
    conn = get_db()
    cur = conn.cursor()
    tickets = cur.execute("""
        SELECT token_number, created_at FROM opd_tickets
        WHERE department = ? AND queue_date = ? AND status != 'cancelled'
        ORDER BY token_number ASC
    """, (department, today)).fetchall()
    
    if not tickets:
        conn.close()
        return 0
        
    oldest_created_str = tickets[0]['created_at']
    try:
        oldest_time = datetime.strptime(oldest_created_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        oldest_time = datetime.now()
        
    elapsed_minutes = (datetime.now() - oldest_time).total_seconds() / 60.0
    serving_index = int(elapsed_minutes // 10)
    max_token = tickets[-1]['token_number']
    serving_token = min(tickets[0]['token_number'] + serving_index, max_token)
    conn.close()
    return serving_token

@app.route('/opd-desk')
@login_required
def opd_desk():
    if current_user.role != 'patient':
        flash('Only patients can access the OPD Desk.', 'warning')
        return redirect(url_for('index'))
        
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cur = conn.cursor()
    
    # Query patient's active ticket for today
    ticket = cur.execute("""
        SELECT * FROM opd_tickets
        WHERE patient_id = ? AND queue_date = ? AND status != 'cancelled'
        LIMIT 1
    """, (current_user.id, today)).fetchone()
    
    ticket_dict = dict(ticket) if ticket else None
    
    serving_token = 0
    patients_ahead = 0
    est_wait_time = 0
    
    if ticket_dict:
        serving_token = get_serving_token(ticket_dict['department'], today)
        
        # Calculate patients ahead who are currently waiting
        patients_ahead_row = cur.execute("""
            SELECT COUNT(*) FROM opd_tickets
            WHERE department = ? AND queue_date = ? 
              AND token_number >= ? AND token_number < ?
              AND status != 'cancelled'
        """, (ticket_dict['department'], today, serving_token, ticket_dict['token_number'])).fetchone()
        patients_ahead = patients_ahead_row[0] if patients_ahead_row else 0
        
        # 10 minutes estimated per patient ahead
        est_wait_time = patients_ahead * 10
        
        # Update active serving state dynamically
        if ticket_dict['token_number'] < serving_token:
            ticket_dict['status'] = 'completed'
        elif ticket_dict['token_number'] == serving_token:
            ticket_dict['status'] = 'serving'
            
    conn.close()
    
    return render_template(
        'opd_desk.html',
        patient=current_user,
        ticket=ticket_dict,
        serving_token=serving_token,
        patients_ahead=patients_ahead,
        est_wait_time=est_wait_time,
        today=today
    )

@app.route('/api/opd/generate', methods=['POST'])
@login_required
def generate_opd_ticket():
    if current_user.role != 'patient':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    department = request.form.get('department', '').strip()
    if not department:
        return jsonify({'status': 'error', 'message': 'Department is required.'}), 400
        
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cur = conn.cursor()
    
    # Verify no active ticket exists for today
    existing = cur.execute("""
        SELECT id FROM opd_tickets
        WHERE patient_id = ? AND queue_date = ? AND status != 'cancelled'
    """, (current_user.id, today)).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'status': 'error', 'message': 'You already have an active OPD ticket for today.'}), 400
        
    # Get next token number
    max_token_row = cur.execute("""
        SELECT MAX(token_number) FROM opd_tickets
        WHERE department = ? AND queue_date = ?
    """, (department, today)).fetchone()
    
    next_token = (max_token_row[0] or 0) + 1
    created_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cur.execute("""
        INSERT INTO opd_tickets (patient_id, department, token_number, queue_date, status, created_at)
        VALUES (?, ?, ?, ?, 'waiting', ?)
    """, (current_user.id, department, next_token, today, created_at_str))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'message': f'OPD Ticket generated successfully for {department}! Your Token Number is {next_token}.',
        'token_number': next_token,
        'department': department
    })

@app.route('/api/opd/cancel/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_opd_ticket(ticket_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Verify ownership
    ticket = cur.execute("""
        SELECT id FROM opd_tickets WHERE id = ? AND patient_id = ?
    """, (ticket_id, current_user.id)).fetchone()
    
    if not ticket:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Ticket not found or unauthorized.'}), 404
        
    cur.execute("UPDATE opd_tickets SET status = 'cancelled' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'OPD Ticket cancelled successfully.'})

@app.route('/api/opd/serving-status')
@login_required
def opd_serving_status():
    today = datetime.now().strftime('%Y-%m-%d')
    department = request.args.get('department')
    if not department:
        return jsonify({'status': 'error', 'message': 'Department is required.'}), 400
        
    serving = get_serving_token(department, today)
    return jsonify({'status': 'success', 'serving_token': serving})


@app.route('/sw.js')
def serve_sw():
    return send_file(os.path.join(os.path.dirname(__file__), 'static', 'sw.js'), mimetype='application/javascript')


@app.route('/debug')
def debug_diagnostics():
    import sys
    db_status = "Unknown"
    db_path = os.path.abspath('healthcare.db')
    try:
        conn = get_db()
        cur = conn.cursor()
        # Test database read/write
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS temp_debug (val TEXT)")
        cur.execute("INSERT INTO temp_debug VALUES ('test')")
        cur.execute("SELECT * FROM temp_debug")
        cur.fetchone()
        cur.execute("DROP TABLE temp_debug")
        conn.commit()
        db_status = "Connected & Writable"
        conn.close()
    except Exception as e:
        db_status = f"Database Error: {str(e)}"
        
    reportlab_installed = "No"
    try:
        import reportlab
        reportlab_installed = "Yes"
    except ImportError:
        reportlab_installed = "No"

    env_info = {
        'cwd': os.getcwd(),
        'db_path': db_path,
        'python_version': sys.version,
        'os': sys.platform,
        'db_status': db_status,
        'reportlab_installed': reportlab_installed
    }
    
    return render_template('debug.html', env_info=env_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)


