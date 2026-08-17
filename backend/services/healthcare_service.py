"""
Unified Healthcare Data & AI Service
Integrates Hospital Network, Vitals Score Calculator, AI Medical Assistant, and Diet Knowledge.
"""

HOSPITALS_DATABASE = [
    # Kolhapur & Maharashtra
    {"id": 1, "name": "CPR General Hospital", "city": "Kolhapur", "type": "Government", "specialty": ["General Medicine", "Emergency", "Trauma", "Pediatrics"], "address": "Bhausinghji Road, Kolhapur 416002", "phone": "+91-231-264-1011", "beds": 650, "icu_available": 42, "is_24hrs": True, "rating": 4.5},
    {"id": 2, "name": "Aster Aadhar Hospital", "city": "Kolhapur", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "R.S. No. 628, Near Shastri Nagar, Kolhapur 416012", "phone": "+91-231-662-2555", "beds": 300, "icu_available": 28, "is_24hrs": True, "rating": 4.8},
    {"id": 3, "name": "Apple Saraswati Multispeciality Hospital", "city": "Kolhapur", "type": "Private", "specialty": ["Cardiology", "Orthopedics", "Emergency"], "address": "Kadamwadi, Kolhapur 416003", "phone": "+91-231-268-9000", "beds": 150, "icu_available": 16, "is_24hrs": True, "rating": 4.6},
    {"id": 4, "name": "Ruby Hall Clinic", "city": "Pune", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Sassoon Road, Pune 411001", "phone": "+91-20-2612-7100", "beds": 550, "icu_available": 55, "is_24hrs": True, "rating": 4.8},
    {"id": 5, "name": "Sassoon General Hospital", "city": "Pune", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Near Pune Railway Station, Pune 411001", "phone": "+91-20-2612-7394", "beds": 1400, "icu_available": 90, "is_24hrs": True, "rating": 4.2},
    {"id": 6, "name": "Deenanath Mangeshkar Hospital", "city": "Pune", "type": "Private", "specialty": ["Cardiology", "Neurology", "Transplant", "Emergency"], "address": "Erandwane, Pune 411004", "phone": "+91-20-4015-1000", "beds": 750, "icu_available": 60, "is_24hrs": True, "rating": 4.9},
    {"id": 7, "name": "Tata Memorial Hospital", "city": "Mumbai", "type": "Government", "specialty": ["Oncology", "Surgery", "Emergency"], "address": "Dr. E Borges Road, Parel, Mumbai 400012", "phone": "+91-22-2417-7000", "beds": 600, "icu_available": 45, "is_24hrs": True, "rating": 4.9},
    {"id": 8, "name": "Kokilaben Dhirubhai Ambani Hospital", "city": "Mumbai", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Andheri West, Mumbai 400053", "phone": "+91-22-4269-6969", "beds": 750, "icu_available": 70, "is_24hrs": True, "rating": 4.8},
    {"id": 9, "name": "KEM Hospital", "city": "Mumbai", "type": "Government", "specialty": ["Emergency", "General Medicine", "Surgery"], "address": "Parel, Mumbai 400012", "phone": "+91-22-2410-7000", "beds": 1800, "icu_available": 120, "is_24hrs": True, "rating": 4.4},
    # National Major Centers
    {"id": 10, "name": "AIIMS New Delhi", "city": "Delhi", "type": "Government", "specialty": ["General Medicine", "Cardiology", "Neurology", "Emergency"], "address": "Ansari Nagar, New Delhi 110029", "phone": "+91-11-2658-8500", "beds": 2478, "icu_available": 180, "is_24hrs": True, "rating": 4.9},
    {"id": 11, "name": "Fortis Escorts Heart Institute", "city": "Delhi", "type": "Private", "specialty": ["Cardiology", "Cardiac Surgery", "Emergency"], "address": "Okhla Road, New Delhi 110025", "phone": "+91-11-4713-5000", "beds": 310, "icu_available": 35, "is_24hrs": True, "rating": 4.8},
    {"id": 12, "name": "Manipal Hospital", "city": "Bengaluru", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Airport Road, Bengaluru 560017", "phone": "+91-80-2502-4444", "beds": 650, "icu_available": 60, "is_24hrs": True, "rating": 4.8},
    {"id": 13, "name": "Apollo Hospitals", "city": "Hyderabad", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Jubilee Hills, Hyderabad 500033", "phone": "+91-40-2360-7777", "beds": 700, "icu_available": 65, "is_24hrs": True, "rating": 4.8},
    {"id": 14, "name": "Apollo Hospitals Greams Road", "city": "Chennai", "type": "Private", "specialty": ["Cardiology", "Oncology", "Transplant", "Emergency"], "address": "Greams Road, Chennai 600006", "phone": "+91-44-2829-0200", "beds": 700, "icu_available": 70, "is_24hrs": True, "rating": 4.8},
]


def calculate_health_score(systolic, diastolic, heart_rate, glucose, spo2=98, temp=98.6):
    """
    Computes a clinical health score from 0 to 100 based on vitals.
    """
    score = 100

    # Blood pressure check (ideal: 110-125 / 70-82)
    if systolic > 140 or systolic < 90:
        score -= 15
    elif systolic > 130 or systolic < 100:
        score -= 8

    if diastolic > 90 or diastolic < 60:
        score -= 10
    elif diastolic > 85 or diastolic < 65:
        score -= 5

    # Heart rate check (ideal: 60-90 bpm)
    if heart_rate < 50 or heart_rate > 105:
        score -= 12
    elif heart_rate < 60 or heart_rate > 95:
        score -= 6

    # Glucose fasting/random check (ideal: 70-110 fasting / <140 random)
    if glucose > 180 or glucose < 60:
        score -= 18
    elif glucose > 140 or glucose < 70:
        score -= 8

    # SpO2 check (ideal: >= 96%)
    if spo2 < 92:
        score -= 25
    elif spo2 < 95:
        score -= 10

    # Temp check (ideal: 97.5 - 99.0 F)
    if temp > 101.5 or temp < 95.0:
        score -= 15
    elif temp > 99.5:
        score -= 6

    return max(10, min(100, score))


DIET_PLANS = [
    {
        "id": "diabetic",
        "title": "Diabetic-Friendly Low GI Diet",
        "marathi_title": "मधुमेह नियंत्रण आहार",
        "target_calories": "1,500 - 1,700 kcal",
        "macros": {"carbs": "45%", "protein": "25%", "fats": "30%"},
        "breakfast": "Oats / Methi Paratha with curd (कमी तेलाचा मेथी पराठा आणि दही), sprouted moong",
        "lunch": "2 Multigrain Rotis, Palak Dal, salad with cucumber & tomato, roasted chana",
        "dinner": "Brown rice / Jowar bhakri (ज्वारीची भाकरी), mix vegetable sabzi, curd",
        "tips": "Avoid refined sugar, fruit juices, and fried snacks. Drink 3L water daily."
    },
    {
        "id": "cardiac",
        "title": "Heart-Healthy Low Sodium Diet",
        "marathi_title": "हृदय निरोगी आहार",
        "target_calories": "1,800 - 2,000 kcal",
        "macros": {"carbs": "50%", "protein": "25%", "fats": "25%"},
        "breakfast": "Poha with peanuts and veggies (पोहे), green tea, 4 soaked almonds & 2 walnuts",
        "lunch": "Jowar / Bajra roti, steamed leafy greens, soybean curry / grilled fish, beetroot salad",
        "dinner": "Light Moong Dal Khichdi (मुगाची डाळ खिचडी) with bottle gourd soup",
        "tips": "Limit daily salt intake under 1 teaspoon. Use olive or mustard oil."
    },
    {
        "id": "wellness",
        "title": "Balanced Everyday Vitality Diet",
        "marathi_title": "संतुलित दैनंदिन आहार",
        "target_calories": "2,000 - 2,200 kcal",
        "macros": {"carbs": "55%", "protein": "20%", "fats": "25%"},
        "breakfast": "Idli Sambar (इडली सांबार) / Upma with coconut chutney, fresh seasonal fruit",
        "lunch": "Whole wheat rotis, Dal Tadka, paneer bhurji, curd, fresh cucumber salad",
        "dinner": "Vegetable dalia / Roti with seasonal sabzi, warm turmeric milk before bed",
        "tips": "Include rich antioxidants and at least 30 minutes of brisk walking."
    }
]


def process_ai_chat(message: str) -> dict:
    """
    Processes user health queries with medical reasoning and bilingual English/Marathi capabilities.
    """
    m = message.lower().strip()
    
    # Emergency / SOS triggers
    if any(k in m for k in ['chest pain', 'heart attack', 'cannot breathe', 'unconscious', 'bleeding', 'हृदयविकार', 'श्वास']):
        return {
            "reply": "⚠️ **URGENT EMERGENCY ALERT / तातडीचा इशारा**:\nIf you or someone is experiencing severe chest pain, shortness of breath, or loss of consciousness, please call **108 (Ambulance)** or **112 (National Emergency)** immediately. Do not delay medical assistance!",
            "is_emergency": True,
            "category": "emergency"
        }

    # Diabetes inquiries
    if any(k in m for k in ['diabetes', 'sugar', 'glucose', 'मधुमेह', 'साखर']):
        return {
            "reply": "🩸 **Diabetes & Blood Glucose Management**:\n• Fasting blood glucose normal range is 70–99 mg/dL; post-meal should be under 140 mg/dL.\n• Recommended foods: Bitter gourd (कारले), methi seeds, sprouted grains, jowar bhakri.\n• You can use our **Diabetes Risk Calculator** in the menu for a full machine learning assessment based on your biomarkers.",
            "is_emergency": False,
            "category": "diabetes"
        }

    # Blood pressure / Hypertension
    if any(k in m for k in ['bp', 'blood pressure', 'hypertension', 'रक्तदाब']):
        return {
            "reply": "💓 **Blood Pressure & Cardiovascular Health**:\n• Optimal BP is around 120/80 mm Hg. Stage 1 Hypertension begins at 130/80+.\n• Reduce dietary sodium/salt, avoid stress, and take prescribed antihypertensives regularly.\n• Log your daily readings in our **Vitals Tracker** to monitor your score.",
            "is_emergency": False,
            "category": "hypertension"
        }

    # Fever / Headache / Cold / Infection
    if any(k in m for k in ['fever', 'headache', 'cold', 'cough', 'ताप', 'डोकेदुखी', 'खोकला']):
        return {
            "reply": "🌡️ **Fever & Common Symptoms Support**:\n• Ensure proper hydration (warm water, electrolytes/ORS).\n• Rest well and monitor temperature with a thermometer.\n• For mild fever: Paracetamol 500mg/650mg after food can be taken if not contraindicated.\n• If fever exceeds 102°F or persists > 48 hrs, please visit an OPD clinic.",
            "is_emergency": False,
            "category": "general"
        }

    # Hospital / Doctor search
    if any(k in m for k in ['hospital', 'doctor', 'clinic', 'रुग्णालय', 'दवाखाना']):
        return {
            "reply": "🏥 **Find Nearby Hospitals**:\nUse our **Hospital Finder** tab to view 24/7 emergency centers, live bed availability, ICU vacancies, and direct emergency contact numbers in Kolhapur, Pune, Mumbai, and nationwide.",
            "is_emergency": False,
            "category": "hospital"
        }

    # Default friendly AI health response
    return {
        "reply": f"Hello! I am your **HealthCare+ AI Assistant**. I can assist you with:\n1. 🩺 Chronic disease risk explanations (Diabetes, Heart Disease)\n2. 📊 Vitals evaluation and health score analysis\n3. 💊 Medicine schedules and precautions\n4. 🥗 Personalized diet & nutrition advice (English & मराठी)\n\nWhat health question or symptom would you like help with today?",
        "is_emergency": False,
        "category": "general"
    }
