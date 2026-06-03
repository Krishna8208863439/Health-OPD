from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from model import train_model
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# ================= ML =================
model, disease_map, accuracy = train_model()

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    disease TEXT,
    risk REAL,
    severity TEXT
)
""")
conn.commit()

# ================= STATIC DATA =================
medicine_db = {
    "Stomach Infection": {
        "LOW 🟢": ["Consult Doctor for Medicines"],
        "MEDIUM 🟡": ["Antibiotics", "ORS"],
        "HIGH 🔴": ["Hospital Admission"]
    }
}

doctor_advice = {
    "LOW 🟢": "Home rest, fluids, monitor symptoms.",
    "MEDIUM 🟡": "Consult doctor within 24 hours.",
    "HIGH 🔴": "Emergency hospitalization required."
}

hospital_advice = {
    "LOW 🟢": "Home / Local Clinic",
    "MEDIUM 🟡": "Primary Health Center",
    "HIGH 🔴": "Multi-Specialty Hospital"
}

def calculate_risk(prob):
    risk = round(prob * 100, 1)
    if risk <= 40:
        return risk, "LOW 🟢"
    elif risk <= 70:
        return risk, "MEDIUM 🟡"
    else:
        return risk, "HIGH 🔴"

# ================= PDF =================
def generate_pdf(disease, risk, severity, doctor, hospital, medicines):
    if not os.path.exists("static"):
        os.makedirs("static")

    filename = f"Disease_Result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("static", filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 12)

    text.textLine("Disease Prediction Result")
    text.textLine("")
    text.textLine(f"Disease       : {disease}")
    text.textLine(f"Risk %        : {risk}")
    text.textLine(f"Severity      : {severity}")
    text.textLine(f"Doctor Advice : {doctor}")
    text.textLine(f"Hospital      : {hospital}")
    text.textLine("Medicines     :")

    for med in medicines:
        text.textLine(f"  - {med}")

    c.drawText(text)
    c.save()

    return filename

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    inputs = [int(x) for x in request.form.values()]

    df = pd.DataFrame([inputs], columns=[
        'bodypain','Hollow','cold and cough','cough','fever',
        'chest pain','breathing problem','Throat pain','head pain',
        'stomach pain','diarrhea','omitting','back pain','Swollen feet'
    ])

    pid = model.predict(df)[0]
    prob = max(model.predict_proba(df)[0])

    risk, severity = calculate_risk(prob)
    disease = disease_map[pid]

    medicines = medicine_db.get(
        disease, {}
    ).get(severity, ["Consult Doctor for Medicines"])

    cur.execute(
        "INSERT INTO history VALUES (NULL,?,?,?,?)",
        (datetime.now(), disease, risk, severity)
    )
    conn.commit()

    report = f"""Disease Prediction Result
Disease       : {disease}
Risk %        : {risk}
Severity      : {severity}
Doctor Advice : {doctor_advice[severity]}
Hospital      : {hospital_advice[severity]}
Medicines     :
"""
    for m in medicines:
        report += f"  - {m}\n"

    pdf_file = generate_pdf(
        disease, risk, severity,
        doctor_advice[severity],
        hospital_advice[severity],
        medicines
    )

    return render_template(
        "result.html",
        report=report,
        pdf_file=pdf_file
    )

if __name__ == "__main__":
    app.run(debug=True)
