from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
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
from functools import wraps

# Import services
from model import train_model
from analytics import AnalyticsEngine
from medicine_db import MEDICINE_DATABASE, HOSPITAL_DATABASE
from risk_calculator import calculate_health_risk_score, get_risk_recommendations
from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url

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
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

init_db()

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
        return redirect(url_for('symptom_entry'))
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
    
    # Get recommendations
    medicines = MEDICINE_DATABASE.get(disease, {}).get(severity.split()[0], ["Consult Doctor"])
    
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
        'doctor_advice': doctor_advice[severity_key]
    }
    
    # Generate PDF
    pdf_filename = generate_pdf(current_user, prediction_data)
    
    # Save to database
    symptom_count = sum(1 for v in symptoms_dict.values() if v == 1)
    
    cur.execute("""
        INSERT INTO predictions (patient_id, disease, risk_percentage, health_risk_score, 
                               health_risk_category, severity, probability, symptoms, symptom_count,
                               medicines, hospitals, doctor_advice, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (current_user.id, disease, risk, health_risk['score'], health_risk['category'],
          severity, prob, str(symptoms_dict), symptom_count, prediction_data['medicines'],
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)

