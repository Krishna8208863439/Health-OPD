"""
Health Risk Score Calculator (0-100)
Calculates comprehensive health risk based on multiple factors
"""

def calculate_health_risk_score(patient_data, symptoms, disease_severity, past_history_count=0):
    """
    Calculate Health Risk Score (0-100) based on:
    - Age
    - Symptoms count
    - Disease severity
    - Past history
    - Lifestyle factors (smoking, BP, sugar)
    
    Returns: risk_score (0-100), risk_category, risk_color
    """
    risk_score = 0
    
    # 1. Age Factor (0-25 points)
    age = patient_data.get('age', 0)
    if age < 18:
        risk_score += 5
    elif age < 40:
        risk_score += 10
    elif age < 60:
        risk_score += 15
    else:
        risk_score += 25
    
    # 2. Symptoms Count (0-20 points)
    symptom_count = sum(1 for v in symptoms.values() if v == 1)
    if symptom_count <= 2:
        risk_score += 5
    elif symptom_count <= 4:
        risk_score += 10
    elif symptom_count <= 6:
        risk_score += 15
    else:
        risk_score += 20
    
    # 3. Disease Severity (0-30 points)
    if 'LOW' in disease_severity:
        risk_score += 10
    elif 'MEDIUM' in disease_severity:
        risk_score += 20
    else:  # HIGH
        risk_score += 30
    
    # 4. Past History (0-15 points)
    if past_history_count == 0:
        risk_score += 0
    elif past_history_count <= 2:
        risk_score += 5
    elif past_history_count <= 5:
        risk_score += 10
    else:
        risk_score += 15
    
    # 5. Lifestyle Factors (0-10 points)
    lifestyle_risk = 0
    
    # Smoking
    if patient_data.get('smoking', 'no') == 'yes':
        lifestyle_risk += 4
    
    # Blood Pressure
    bp_status = patient_data.get('blood_pressure', 'normal')
    if bp_status == 'high':
        lifestyle_risk += 3
    elif bp_status == 'low':
        lifestyle_risk += 1
    
    # Blood Sugar
    sugar_status = patient_data.get('blood_sugar', 'normal')
    if sugar_status == 'high':
        lifestyle_risk += 3
    elif sugar_status == 'prediabetic':
        lifestyle_risk += 2
    
    risk_score += lifestyle_risk
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Determine category and color
    if risk_score < 30:
        category = "Low Risk"
        color = "#10B981"  # Green
        icon = "🟢"
    elif risk_score < 60:
        category = "Moderate Risk"
        color = "#F59E0B"  # Orange
        icon = "🟡"
    elif risk_score < 80:
        category = "High Risk"
        color = "#EF4444"  # Red
        icon = "🔴"
    else:
        category = "Critical Risk"
        color = "#991B1B"  # Dark Red
        icon = "🚨"
    
    return {
        'score': risk_score,
        'category': category,
        'color': color,
        'icon': icon,
        'breakdown': {
            'age_factor': min(25, risk_score),
            'symptom_factor': symptom_count,
            'severity_factor': disease_severity,
            'history_factor': past_history_count,
            'lifestyle_factor': lifestyle_risk
        }
    }


def get_risk_recommendations(risk_score):
    """Get personalized recommendations based on risk score"""
    if risk_score < 30:
        return [
            "✓ Continue healthy lifestyle habits",
            "✓ Regular health checkups recommended",
            "✓ Stay hydrated and maintain good sleep",
            "✓ Light exercise 3-4 times per week"
        ]
    elif risk_score < 60:
        return [
            "⚠ Schedule a doctor consultation within 48 hours",
            "⚠ Monitor symptoms closely",
            "⚠ Avoid strenuous activities",
            "⚠ Follow prescribed medications strictly",
            "⚠ Keep emergency contacts ready"
        ]
    elif risk_score < 80:
        return [
            "🚨 Seek medical attention within 24 hours",
            "🚨 Do not ignore symptoms",
            "🚨 Have someone monitor your condition",
            "🚨 Keep hospital bag ready",
            "🚨 Avoid being alone"
        ]
    else:
        return [
            "🆘 IMMEDIATE MEDICAL ATTENTION REQUIRED",
            "🆘 Visit emergency room or call ambulance",
            "🆘 Do not delay treatment",
            "🆘 Inform family members immediately",
            "🆘 Keep all medical records ready"
        ]
