# ============================================================
#  chatbot_kb.py — Local Medical Knowledge Base
#  AI-Driven Public Health Chatbot (RAG-style local retrieval)
# ============================================================

import re
from datetime import datetime

# ─────────────────────────────────────────────
#  RED-FLAG SYMPTOM ESCALATION LIST
# ─────────────────────────────────────────────
RED_FLAG_KEYWORDS = [
    "chest pain", "chest tightness", "can't breathe", "cannot breathe",
    "difficulty breathing", "shortness of breath", "heart attack",
    "unconscious", "fainted", "fainting", "stroke", "paralysis",
    "severe bleeding", "blood vomit", "vomiting blood", "coughing blood",
    "seizure", "convulsion", "high fever above 104", "high fever above 105",
    "severe head pain", "sudden headache", "worst headache",
    "suicidal", "overdose", "poisoning", "snake bite", "anaphylaxis",
    "allergic reaction", "swollen throat", "blue lips", "blue fingernails",
    # Marathi equivalents
    "छाती दुखणे", "श्वास घेता येत नाही", "हृदयविकाराचा झटका",
    "बेशुद्ध", "जप्ती", "तीव्र ताप"
]

# ─────────────────────────────────────────────
#  LANGUAGE DETECTION (simple keyword approach)
# ─────────────────────────────────────────────
MARATHI_INDICATORS = [
    "मला", "आहे", "आहेत", "आजार", "ताप", "वेदना", "डोकेदुखी",
    "पोटदुखी", "उलटी", "खोकला", "थकवा", "काय", "कसे", "कुठे",
    "झाला", "झाली", "करावे", "सांगा", "मदत", "उपाय", "औषध"
]

def detect_language(text: str) -> str:
    """Detect if query is in Marathi or English."""
    for word in MARATHI_INDICATORS:
        if word in text:
            return 'mr'
    return 'en'

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE — English
# ─────────────────────────────────────────────
KNOWLEDGE_BASE_EN = {
    "fever": {
        "keywords": ["fever", "temperature", "high temp", "pyrexia", "febrile", "burning up"],
        "response": """🌡️ **Fever — What You Need to Know**

**Definition:** A fever is a body temperature above 100.4°F (38°C).

**Common Causes:**
- Viral infections (flu, COVID-19, dengue)
- Bacterial infections (UTI, throat infection)
- Malaria (especially in monsoon season)
- Typhoid

**Home Management (mild fever 100–102°F):**
• Rest and stay hydrated (water, ORS, coconut water)
• Take Paracetamol / Crocin as directed
• Wear light, breathable clothing
• Use a cool damp cloth on forehead

**When to See a Doctor Immediately:**
🚨 Fever above 103°F (39.4°C)
🚨 Fever lasting more than 3 days
🚨 Difficulty breathing or chest pain
🚨 Severe headache with stiff neck (meningitis risk)
🚨 Rash with fever (dengue / measles)
🚨 Fever in a child under 3 months old

⚠️ *This is health information, not a medical diagnosis. Please consult a doctor if symptoms persist.*"""
    },

    "dengue": {
        "keywords": ["dengue", "dengue fever", "mosquito fever", "platelet", "breakbone"],
        "response": """🦟 **Dengue Fever — Complete Guide**

**What is Dengue?** A mosquito-borne viral disease spread by the Aedes mosquito (bites during day).

**Warning Signs (Dengue Warning Signs — Seek Care Immediately):**
🔴 Severe abdominal pain
🔴 Persistent vomiting
🔴 Rapid breathing
🔴 Bleeding gums or nose
🔴 Fatigue / restlessness
🔴 Blood in vomit/stool
🔴 Platelet count drops below 100,000

**Classic Symptoms:**
• Sudden high fever (104°F)
• Severe headache behind the eyes
• Muscle and joint pain ("breakbone fever")
• Skin rash (appears 3–4 days after fever)
• Nausea and vomiting

**Prevention:**
✅ Use mosquito repellent (DEET-based)
✅ Wear long sleeves/pants
✅ Use mosquito nets at night
✅ Eliminate stagnant water (coolers, pots, tires)
✅ Use camphor/neem-based coils

**Treatment:**
• No specific antiviral drug — supportive care
• Stay hydrated — drink 2–3 liters/day
• Paracetamol for fever (avoid ibuprofen/aspirin)
• Monitor platelet count daily if confirmed dengue
• Hospitalization if platelets drop below 50,000

⚠️ *Visit a doctor for blood tests if you suspect dengue. Do not self-medicate with aspirin or ibuprofen.*"""
    },

    "malaria": {
        "keywords": ["malaria", "plasmodium", "chills", "rigor", "malarial"],
        "response": """🦟 **Malaria — Prevention & Treatment**

**What is Malaria?** A life-threatening disease caused by Plasmodium parasites, spread by female Anopheles mosquitoes (bite at dusk/night).

**Symptoms:**
• Cyclical fever with chills (every 48–72 hours)
• Severe headache
• Muscle aches
• Sweating after fever breaks
• Nausea and vomiting
• Fatigue

**High-Risk Seasons:** Monsoon season (June–September) in India

**Diagnosis:** Blood smear test or Rapid Diagnostic Test (RDT) — done at any health center.

**Treatment:**
• Chloroquine or Artemisinin-based combination therapy (ACT)
• Must complete full course of antimalarials
• Severe malaria requires IV treatment — HOSPITALIZATION

**Prevention:**
✅ Sleep under insecticide-treated bed nets (ITNs)
✅ Indoor residual spraying
✅ Wear full-sleeve clothes at night
✅ Use DEET mosquito repellents
✅ Prophylactic medicine if traveling to endemic areas

🚨 **Seek immediate care** if you have fever with chills, especially after visiting a forested/rural area.

⚠️ *Malaria is curable if detected early. Please see a doctor for a blood test.*"""
    },

    "flu": {
        "keywords": ["flu", "influenza", "cold", "runny nose", "sneezing", "sore throat", "cough", "cold and cough"],
        "response": """🤧 **Flu & Common Cold — Management Guide**

**Flu vs Cold:**
| Feature | Flu | Common Cold |
|---------|-----|-------------|
| Onset | Sudden | Gradual |
| Fever | High (101-104°F) | Low or none |
| Fatigue | Severe | Mild |
| Headache | Prominent | Rare |
| Body ache | Severe | Mild |

**Home Remedies:**
• Steam inhalation (with eucalyptus/Vicks) 2–3 times daily
• Warm water with honey and ginger
• Tulsi (Holy Basil) tea
• Rest and stay warm
• Increase fluid intake
• Salt water gargle for sore throat
• Saline nasal drops for blocked nose

**Medications:**
• Antihistamines for runny nose (Cetirizine, Loratadine)
• Paracetamol for fever and body ache
• Cough syrup for productive cough

**When to See a Doctor:**
🚨 Difficulty breathing
🚨 Fever above 103°F for more than 3 days
🚨 Symptoms lasting more than 10 days
🚨 Chest pain or wheezing
🚨 Symptoms in elderly (65+), children under 5, or pregnant women

**Prevention:**
✅ Annual flu vaccination
✅ Wash hands frequently (20 seconds with soap)
✅ Avoid touching face
✅ Wear mask in crowded places
✅ Eat immunity-boosting foods (citrus, garlic, ginger)"""
    },

    "covid": {
        "keywords": ["covid", "corona", "coronavirus", "covid-19", "covid19", "omicron", "sars"],
        "response": """😷 **COVID-19 — Current Guidelines**

**Common Symptoms:**
• Fever / chills
• Cough (dry or with mucus)
• Loss of taste or smell
• Fatigue
• Sore throat
• Runny nose
• Headache
• Body aches

**Severe Symptoms (Emergency — Call 108):**
🚨 Difficulty breathing / shortness of breath
🚨 Persistent chest pain/pressure
🚨 Confusion / inability to stay awake
🚨 Bluish lips or face (low oxygen)
🚨 SpO2 below 94%

**If You Test Positive:**
• Isolate for at least 5 days (or until fever-free for 24h)
• Wear N95/surgical mask around others
• Monitor SpO2 with pulse oximeter
• Stay hydrated, rest
• Take Paracetamol for fever/body ache
• Prone positioning if breathing feels difficult

**Testing:** RTPCR test or Antigen rapid test available at government hospitals

**Vaccination:** Stay up-to-date with recommended boosters.

**Protection:**
✅ Wear well-fitted mask in crowded indoor spaces
✅ Wash hands / use sanitizer
✅ Improve ventilation
✅ Get vaccinated (Covishield, Covaxin, etc.)"""
    },

    "monsoon": {
        "keywords": ["monsoon", "rainy season", "monsoon disease", "waterborne", "flood", "rain"],
        "response": """🌧️ **Monsoon Health Advisory — India**

**Common Monsoon Diseases to Watch For:**
1. **Dengue** — Aedes mosquito, peaks July–October
2. **Malaria** — Anopheles mosquito, common in waterlogged areas
3. **Leptospirosis** — Wading in floodwater, from rat urine
4. **Typhoid** — Contaminated food/water
5. **Cholera** — Waterborne, severe diarrhea
6. **Viral fever** — Common respiratory and GI infections
7. **Fungal infections** — Skin, nails due to moisture

**Monsoon Health Dos:**
✅ Drink only boiled/filtered water
✅ Avoid street food during heavy rains
✅ Wear waterproof footwear to prevent leptospirosis
✅ Use mosquito repellent and nets
✅ Dry yourself properly to prevent fungal infections
✅ Eat home-cooked food
✅ Store food in sealed containers
✅ Wash fruits/vegetables thoroughly

**Monsoon Health Don'ts:**
❌ Don't walk barefoot in floodwater
❌ Don't eat cut fruits from street vendors
❌ Don't store water in open containers (mosquito breeding)
❌ Don't ignore fever lasting more than 2 days

**First Aid for Waterborne Illness:**
• ORS for dehydration (mix 1L water + 6 tsp sugar + ½ tsp salt)
• Rest and clear fluids
• Seek medical help if diarrhea persists beyond 24 hours"""
    },

    "diabetes": {
        "keywords": ["diabetes", "blood sugar", "glucose", "insulin", "diabetic", "sugar level", "hyperglycemia", "hypoglycemia"],
        "response": """🩺 **Diabetes — Management & Awareness**

**Types:**
- **Type 1**: Body makes no insulin (autoimmune)
- **Type 2**: Body doesn't use insulin properly (most common, 90%)
- **Gestational**: During pregnancy

**Warning Signs of Diabetes:**
• Frequent urination
• Excessive thirst
• Unexplained weight loss
• Blurred vision
• Slow-healing wounds
• Fatigue
• Tingling/numbness in hands/feet

**Blood Sugar Targets:**
| Test | Normal | Diabetic |
|------|--------|---------|
| Fasting | <100 mg/dL | ≥126 mg/dL |
| Post-meal (2h) | <140 mg/dL | ≥200 mg/dL |
| HbA1c | <5.7% | ≥6.5% |

**Lifestyle Management:**
✅ Exercise 30 min/day (walking, yoga)
✅ Low glycemic index diet (whole grains, vegetables)
✅ Monitor blood sugar regularly
✅ Take medications as prescribed
✅ Foot care — check daily for sores
✅ Regular eye and kidney checkups

**Emergency — Low Blood Sugar (Hypoglycemia):**
Symptoms: Shakiness, confusion, sweating, hunger
Treatment: 15g fast carbs (3–4 glucose tablets, ½ cup juice), wait 15 min, recheck

⚠️ *Diabetes is manageable but requires consistent care. Never adjust insulin doses without consulting your doctor.*"""
    },

    "blood_pressure": {
        "keywords": ["blood pressure", "hypertension", "bp high", "bp low", "hypotension", "high bp", "low bp", "hypertensive"],
        "response": """💉 **Blood Pressure — Guide**

**Blood Pressure Ranges:**
| Category | Systolic | Diastolic |
|----------|----------|-----------|
| Normal | <120 | <80 |
| Elevated | 120–129 | <80 |
| Stage 1 HTN | 130–139 | 80–89 |
| Stage 2 HTN | ≥140 | ≥90 |
| Hypertensive Crisis | >180 | >120 |

**Symptoms of High BP (often none — "Silent Killer"):**
• Severe headache
• Dizziness
• Nosebleed
• Shortness of breath
• Chest pain (seek emergency care)

**Lifestyle Changes for High BP:**
✅ DASH diet — fruits, vegetables, low-fat dairy, whole grains
✅ Reduce salt intake (<2.3g sodium/day)
✅ Exercise 30 min/day
✅ Limit alcohol
✅ Stop smoking
✅ Manage stress (yoga, meditation)
✅ Maintain healthy weight

**Low BP (Hypotension) — When to worry:**
• Dizziness when standing up suddenly
• Fainting
• Nausea
Treatment: Increase fluids, add a little salt, eat small frequent meals, avoid alcohol.

🚨 **Seek Emergency Care for:**
- BP >180/120 with headache/vision changes (hypertensive crisis)
- Sudden severe chest pain with high BP"""
    },

    "first_aid": {
        "keywords": ["first aid", "emergency", "injury", "wound", "bleeding", "burn", "fracture", "sprain", "cut", "bruise"],
        "response": """🏥 **First Aid — Quick Reference Guide**

**🩸 Bleeding (External):**
1. Apply direct pressure with clean cloth
2. Do NOT remove cloth if soaked — add more on top
3. Elevate injured limb above heart level
4. Seek medical care if bleeding doesn't stop in 15 min

**🔥 Burns:**
- Cool under running cold water for 20 min
- Do NOT use ice, butter, or toothpaste
- Cover with sterile dressing
- Seek care for burns larger than palm size or on face/hands/genitals

**🦴 Fracture/Sprain:**
- RICE: Rest, Ice, Compression, Elevation
- Immobilize the joint — do not try to straighten
- Seek X-ray immediately

**😮 Choking:**
- Adults: 5 back blows between shoulder blades, then 5 abdominal thrusts (Heimlich)
- Infants: 5 back blows + 5 chest thrusts

**💊 Poisoning:**
- Call Poison Control or go to ER immediately
- Do NOT induce vomiting unless instructed
- Bring container/label of substance to hospital

**🫀 CPR (Unresponsive, Not Breathing):**
1. Call 108 immediately
2. 30 chest compressions (2 inches deep, 100–120/min)
3. 2 rescue breaths
4. Continue until help arrives

📞 **Emergency Numbers: 108 (Ambulance) | 112 (Emergency)**"""
    },

    "diet": {
        "keywords": ["diet", "nutrition", "healthy eating", "food", "weight loss", "weight gain", "balanced diet", "calories"],
        "response": """🥗 **Healthy Diet — Complete Guide**

**My Plate Method:**
- 50% Fruits & Vegetables (fill half your plate)
- 25% Whole Grains (brown rice, whole wheat roti)
- 25% Protein (pulses, eggs, fish, chicken, tofu)
- Plus small amount of healthy fats

**Indian Superfoods:**
🌿 Turmeric (Haldi) — anti-inflammatory
🌿 Amla — Vitamin C powerhouse
🌿 Ghee — healthy fats (in moderation)
🌿 Curd/Yogurt — probiotics for gut health
🌿 Dal — protein + fiber
🌿 Leafy greens — iron, folate
🌿 Methi (Fenugreek) — blood sugar control

**Foods to Limit:**
❌ Deep-fried foods
❌ White sugar and refined carbs
❌ Processed/packaged foods
❌ Excessive salt
❌ Sugary beverages

**Daily Hydration:** 8–10 glasses of water/day
**Meal Timing:** 3 main meals + 2 healthy snacks

**Immunity Boosting Foods:**
• Citrus fruits (Vitamin C)
• Ginger + Garlic
• Tulsi tea
• Turmeric milk (Haldi doodh)
• Nuts and seeds"""
    },

    "mental_health": {
        "keywords": ["mental health", "depression", "anxiety", "stress", "panic", "sad", "hopeless", "therapy", "counseling", "sleep", "insomnia"],
        "response": """🧠 **Mental Health — You're Not Alone**

**Common Mental Health Conditions:**
- **Anxiety**: Excessive worry, racing thoughts, physical tension
- **Depression**: Persistent sadness, loss of interest, fatigue
- **Stress**: Overwhelm from work, relationships, or life events
- **Insomnia**: Difficulty falling/staying asleep

**Self-Care Strategies:**
✅ Regular physical exercise (even 20 min walking helps)
✅ Maintain sleep schedule (same wake/sleep time daily)
✅ Mindfulness and meditation (apps: Headspace, Calm)
✅ Social connection — talk to friends, family
✅ Limit news/social media if it causes anxiety
✅ Journaling — write your thoughts and feelings
✅ Breathing exercises (4-7-8 breathing)

**4-7-8 Breathing Technique:**
Inhale 4 sec → Hold 7 sec → Exhale 8 sec
Repeat 4 times when feeling anxious

**When to Seek Professional Help:**
🚨 Thoughts of self-harm or suicide — Call iCall: 9152987821
🚨 Inability to function at work/home
🚨 Substance use to cope
🚨 Severe panic attacks

**National Resources (India):**
📞 iCall: 9152987821
📞 Vandrevala Foundation: 1860-2662-345 (24/7)
📞 NIMHANS Helpline: 080-46110007

⚠️ *Mental health conditions are treatable. Reaching out to a counselor or therapist is a sign of strength, not weakness.*"""
    },

    "pregnancy": {
        "keywords": ["pregnancy", "pregnant", "prenatal", "antenatal", "baby", "trimester", "delivery", "labor", "morning sickness"],
        "response": """🤱 **Pregnancy — Health Guide**

**Essential Prenatal Care:**
✅ Start prenatal vitamins (folic acid 400–800mcg)
✅ Regular checkups (monthly in 1st/2nd trimester, 2-weekly in 3rd)
✅ Eat a balanced diet with extra protein and calcium
✅ Stay hydrated (10–12 cups water daily)
✅ Moderate exercise (walking, prenatal yoga)
✅ Avoid alcohol, smoking, and raw/undercooked food

**Common Discomforts & Relief:**
- **Morning sickness**: Small frequent meals, ginger tea, crackers
- **Back pain**: Prenatal yoga, supportive footwear
- **Swelling**: Elevate legs, reduce salt
- **Heartburn**: Small meals, avoid lying down after eating

**Warning Signs — Go to Hospital Immediately:**
🚨 Vaginal bleeding
🚨 Severe abdominal pain
🚨 Decreased fetal movement (after 28 weeks)
🚨 Severe headache/vision changes (pre-eclampsia)
🚨 Leaking fluid (water breaking)
🚨 Fever above 100.4°F
🚨 Painful/burning urination (UTI)

**Foods to Avoid:**
❌ Raw fish, unpasteurized dairy
❌ Papaya, pineapple (in large amounts)
❌ Excess caffeine (>200mg/day)
❌ Alcohol completely

*Attend all scheduled antenatal visits and take iron + folic acid supplements as prescribed.*"""
    },

    "cholesterol": {
        "keywords": ["cholesterol", "ldl", "hdl", "triglycerides", "lipid", "heart health", "cardiovascular"],
        "response": """❤️ **Cholesterol & Heart Health**

**Cholesterol Levels:**
| Type | Desirable |
|------|-----------|
| Total cholesterol | <200 mg/dL |
| LDL ("bad") | <100 mg/dL |
| HDL ("good") | >60 mg/dL |
| Triglycerides | <150 mg/dL |

**Foods That Lower Cholesterol:**
✅ Oats and barley (beta-glucan fiber)
✅ Fatty fish (salmon, sardines, mackerel)
✅ Nuts (walnuts, almonds — 1 handful/day)
✅ Olive oil and avocado (healthy fats)
✅ Legumes (rajma, chana, lentils)
✅ Garlic (allicin reduces LDL)
✅ Green tea

**Foods to Avoid:**
❌ Trans fats (packaged biscuits, fried snacks)
❌ Saturated fats (red meat, full-fat dairy)
❌ Refined carbs and sugary foods

**Lifestyle:**
• Exercise 30–45 min most days
• Quit smoking
• Maintain healthy weight
• Limit alcohol

⚠️ *If LDL is >160 mg/dL despite lifestyle changes, your doctor may prescribe statins. Never stop prescribed medication without consulting your doctor.*"""
    },

    "opd": {
        "keywords": ["opd", "outpatient", "queue", "token", "waiting", "appointment", "doctor visit", "hospital queue", "bed", "admission"],
        "response": """🏥 **OPD & Hospital Queue System — Help**

**How to Use the OPD Queue System:**
1. Go to **OPD Desk** from the menu
2. Select your department (General Medicine, Cardiology, etc.)
3. Choose your **Triage Level** (how urgent your condition is):
   - 🔴 Level 1 (Critical) — Life-threatening emergency
   - 🟠 Level 2 (Urgent) — Severe pain/distress
   - 🟡 Level 3 (Semi-urgent) — Moderate symptoms
   - 🟢 Level 4 (Non-urgent) — Mild symptoms
   - ⚪ Level 5 (Routine) — General checkup
4. Briefly describe your chief complaint
5. Click **Generate OPD Ticket** — You'll get a token number

**Understanding Your Queue:**
- Your position updates automatically every few seconds
- You'll get a browser notification when you're 3–5 patients away
- Estimated wait time uses real-time queue math (Little's Law)

**Bed Management:**
- Beds are assigned by doctors/nurses after consultation
- Ward types: ICU, General, Pediatric, Emergency
- Your doctor can check bed availability from the Queue Dashboard

📍 **Need help navigating the hospital?** Ask at the front desk or use the Hospital Finder feature."""
    }
}

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE — Marathi (Key Topics)
# ─────────────────────────────────────────────
KNOWLEDGE_BASE_MR = {
    "fever": {
        "keywords": ["ताप", "तापमान", "जास्त ताप", "थंडी ताप", "गरम"],
        "response": """🌡️ **ताप — महत्त्वाची माहिती**

**ताप म्हणजे काय?** शरीराचे तापमान 100.4°F (38°C) पेक्षा जास्त असणे.

**सामान्य कारणे:**
- विषाणू संसर्ग (फ्लू, डेंग्यू, कोरोना)
- जिवाणू संसर्ग (घसा दुखणे, मूत्रमार्ग)
- मलेरिया
- विषमज्वर (टायफॉइड)

**घरगुती उपाय (सौम्य ताप 100–102°F):**
• आराम करा, भरपूर पाणी प्या
• पॅरासिटामोल / क्रोसिन घ्या
• कपाळावर थंड ओला कपडा ठेवा

**लगेच डॉक्टरकडे जा जर:**
🚨 ताप 103°F पेक्षा जास्त असेल
🚨 ताप 3 दिवसांपेक्षा जास्त राहिल
🚨 श्वास घेण्यास त्रास होत असेल
🚨 तापासोबत पुरळ असेल

⚠️ *हे आरोग्य माहिती आहे, वैद्यकीय निदान नाही. तक्रारी कायम राहिल्यास डॉक्टरांना भेटा.*"""
    },

    "dengue": {
        "keywords": ["डेंग्यू", "डेंग्यु", "प्लेटलेट", "डास"],
        "response": """🦟 **डेंग्यू ताप — संपूर्ण माहिती**

**डेंग्यू म्हणजे काय?** एडीस डासाद्वारे पसरणारा विषाणूजन्य आजार.

**लक्षणे:**
• अचानक तीव्र ताप (104°F)
• डोळ्यांमागे तीव्र डोकेदुखी
• सांधेदुखी, स्नायूदुखी
• त्वचेवर पुरळ (3–4 दिवसांनंतर)
• मळमळ, उलटी

**धोक्याची चिन्हे (लगेच रुग्णालयात जा):**
🔴 पोटात तीव्र वेदना
🔴 सतत उलटी
🔴 हिरड्या/नाकातून रक्तस्त्राव
🔴 प्लेटलेट 100,000 पेक्षा कमी

**प्रतिबंध:**
✅ डास प्रतिबंधक वापरा
✅ साचलेले पाणी नष्ट करा
✅ मच्छरदाणी वापरा

⚠️ *ताप असल्यास रक्त तपासणी करा. ऍस्पिरिन/इब्युप्रोफेन देऊ नका.*"""
    },

    "malaria": {
        "keywords": ["मलेरिया", "हिवताप", "थंडी वाजणे", "थरथरणे"],
        "response": """🦟 **मलेरिया — उपचार आणि प्रतिबंध**

**मलेरिया म्हणजे काय?** मादी अनोफिलीस डासाद्वारे पसरणारा रक्तजन्य आजार.

**लक्षणे:**
• चक्रीय ताप (48–72 तासांनी थंडी वाजून ताप)
• तीव्र डोकेदुखी
• स्नायूदुखी
• घाम सुटणे
• मळमळ, उलटी

**निदान:** रक्त स्मियर चाचणी किंवा RDT — कोणत्याही आरोग्य केंद्रात उपलब्ध.

**उपचार:**
• क्लोरोक्विन किंवा आर्टेमिसिनिन-आधारित औषधे
• पूर्ण कोर्स पूर्ण करा
• गंभीर मलेरियासाठी रुग्णालयात दाखल व्हा

**प्रतिबंध:**
✅ रात्री मच्छरदाणी वापरा
✅ संपूर्ण अंग झाकेल असे कपडे घाला
✅ डास प्रतिबंधक वापरा

🚨 **ताप आणि थंडी असल्यास लगेच डॉक्टरांना भेटा.**"""
    },

    "flu": {
        "keywords": ["खोकला", "सर्दी", "घसा", "शिंका", "नाक", "फ्लू"],
        "response": """🤧 **सर्दी आणि खोकला — घरगुती उपाय**

**घरगुती उपाय:**
• आल्याचा चहा + मध — दिवसातून 2–3 वेळा
• तुळशीचा काढा
• वाफ घ्या (निलगिरी तेल टाकून) — दिवसातून 2 वेळा
• गरम मिठाच्या पाण्याने गुळण्या
• साखरेचे पाणी नाकात टाका
• भरपूर आराम करा

**औषधे:**
• पॅरासिटामोल — ताप आणि अंगदुखीसाठी
• Cetirizine — नाक वाहणे थांबवण्यासाठी
• खोकल्याचे सिरप

**डॉक्टरकडे कधी जावे:**
🚨 3 दिवसांपेक्षा जास्त ताप
🚨 श्वास घेण्यास त्रास
🚨 छाती दुखत असेल"""
    },

    "diet": {
        "keywords": ["आहार", "जेवण", "खाणे", "पोषण", "वजन", "अन्न"],
        "response": """🥗 **निरोगी आहार — संपूर्ण मार्गदर्शन**

**संतुलित आहाराचे घटक:**
• 50% भाज्या आणि फळे
• 25% धान्य (तांदूळ, गहू, ज्वारी, बाजरी)
• 25% प्रथिने (डाळ, अंडे, मासे, दूध)
• थोडे तूप/तेल (आरोग्यदायी स्निग्ध पदार्थ)

**भारतीय सुपरफूड्स:**
🌿 हळद — दाहशामक
🌿 आवळा — विटामिन C
🌿 तूप — पचनशक्ती वाढवते
🌿 दही — आतड्यांसाठी उत्तम
🌿 मेथी — रक्तशर्करा नियंत्रण
🌿 तुळस — प्रतिकारशक्ती वाढवते

**टाळायचे पदार्थ:**
❌ जास्त तळलेले पदार्थ
❌ साखरयुक्त पेये
❌ पॅकेज्ड/प्रक्रिया केलेले अन्न
❌ जास्त मीठ

**दिवसातून 8–10 ग्लास पाणी प्या.**"""
    }
}

# ─────────────────────────────────────────────
#  GENERIC RESPONSES
# ─────────────────────────────────────────────
GENERIC_RESPONSES_EN = {
    "greeting": [
        "Hello! 👋 I'm your **HealthCare+ AI Health Assistant**. I can help you with:\n\n• Disease symptoms and prevention\n• First aid guidance\n• Diet and nutrition tips\n• Monsoon health advisory\n• How to use the OPD queue system\n\nWhat health topic would you like to know about today?",
        "Hi there! I'm here to help with your health questions. You can ask me about fever, dengue, malaria, flu, diabetes, blood pressure, diet, mental health, pregnancy, and much more. How can I assist you?"
    ],
    "thanks": "You're welcome! 😊 Remember, I'm here anytime you have health questions. Stay healthy and take care! 🌟",
    "goodbye": "Take care! 👋 Remember — your health is your greatest wealth. Stay safe, eat well, and don't hesitate to consult a doctor when needed. 🏥",
    "unknown": """I'd love to help! 🤔 I may not have specific information about that topic yet, but I can assist you with:

• **Fever & Infections** — dengue, malaria, flu, COVID
• **Monsoon Diseases** — waterborne illness prevention
• **Chronic Conditions** — diabetes, blood pressure, cholesterol
• **First Aid** — burns, bleeding, fractures
• **Diet & Nutrition** — healthy eating, immunity
• **Mental Health** — stress, anxiety, sleep
• **Pregnancy** — prenatal care
• **OPD Queue** — how to use the hospital queue system

Could you rephrase your question or choose one of these topics? 😊"""
}

GENERIC_RESPONSES_MR = {
    "greeting": "नमस्कार! 👋 मी **HealthCare+ AI आरोग्य सहाय्यक** आहे. मी तुम्हाला खालील विषयांवर मदत करू शकतो:\n\n• आजारांची लक्षणे आणि प्रतिबंध\n• प्रथमोपचार मार्गदर्शन\n• आहार आणि पोषण टिप्स\n• पावसाळी आरोग्य सल्ला\n\nआज तुम्हाला कोणत्या आरोग्य विषयाबद्दल जाणून घ्यायचे आहे?",
    "thanks": "धन्यवाद! 😊 निरोगी राहा आणि काळजी घ्या! 🌟",
    "goodbye": "काळजी घ्या! 👋 तुमचे आरोग्य हीच तुमची सर्वात मोठी संपत्ती आहे. 🏥",
    "unknown": "मला नक्की माहीत नाही, पण मी ताप, डेंग्यू, मलेरिया, सर्दी, मधुमेह, रक्तदाब, आहार, आणि प्रथमोपचार याबद्दल मदत करू शकतो. कृपया पुन्हा विचारा."
}

# ─────────────────────────────────────────────
#  MAIN CHATBOT ENGINE
# ─────────────────────────────────────────────
def check_red_flags(text: str) -> bool:
    """Returns True if the query contains red-flag emergency keywords."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in RED_FLAG_KEYWORDS)

def get_red_flag_response(lang: str) -> str:
    if lang == 'mr':
        return """🚨 **आणीबाणी — तातडीने कृती करा!**

तुमच्या प्रश्नात गंभीर आरोग्य लक्षणे दिसत आहेत.

**ताबडतोब कॉल करा:**
📞 **108** — रुग्णवाहिका (Ambulance)
📞 **112** — आपत्कालीन सेवा

**रुग्णाला एकटे सोडू नका. जवळच्या रुग्णालयात न्या.**

जर तुम्हाला मानसिक त्रास होत असेल तर:
📞 iCall: 9152987821"""
    else:
        return """🚨 **EMERGENCY — Please Act Immediately!**

Your question indicates a potentially life-threatening situation.

**Call Emergency Services Now:**
📞 **108** — Ambulance
📞 **112** — Emergency Response

**Do NOT leave the patient alone. Go to the nearest hospital immediately.**

If you or someone is in a mental health crisis:
📞 iCall: 9152987821 (free, confidential)

*I'm an AI assistant — please get real medical help right away.*"""

def get_chatbot_response(user_message: str, conversation_history: list = None) -> dict:
    """
    Main chatbot engine:
    1. Detect language
    2. Check red flags
    3. Search knowledge base
    4. Return contextual response
    """
    text = user_message.strip()
    if not text:
        return {"response": "Please type your health question!", "language": "en", "is_emergency": False}

    lang = detect_language(text)
    text_lower = text.lower()

    # 1. Check for emergency red flags
    if check_red_flags(text):
        return {
            "response": get_red_flag_response(lang),
            "language": lang,
            "is_emergency": True,
            "topic": "emergency"
        }

    # 2. Check for greeting
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                 "namaste", "namaskar", "नमस्कार", "हॅलो", "हाय"]
    if any(g in text_lower for g in greetings) and len(text) < 30:
        kb = GENERIC_RESPONSES_MR if lang == 'mr' else GENERIC_RESPONSES_EN
        resp = kb['greeting'] if isinstance(kb['greeting'], str) else kb['greeting'][0]
        return {"response": resp, "language": lang, "is_emergency": False, "topic": "greeting"}

    # 3. Check for thanks
    thanks_words = ["thank", "thanks", "thank you", "dhanyawad", "धन्यवाद", "shukriya"]
    if any(w in text_lower for w in thanks_words):
        kb = GENERIC_RESPONSES_MR if lang == 'mr' else GENERIC_RESPONSES_EN
        return {"response": kb['thanks'], "language": lang, "is_emergency": False, "topic": "thanks"}

    # 4. Check for goodbye
    bye_words = ["bye", "goodbye", "thank bye", "ok bye", "bye bye", "निरोप"]
    if any(w in text_lower for w in bye_words):
        kb = GENERIC_RESPONSES_MR if lang == 'mr' else GENERIC_RESPONSES_EN
        return {"response": kb['goodbye'], "language": lang, "is_emergency": False, "topic": "bye"}

    # 5. Search knowledge base
    kb = KNOWLEDGE_BASE_MR if lang == 'mr' else KNOWLEDGE_BASE_EN
    best_match = None
    best_score = 0

    for topic, data in kb.items():
        for keyword in data['keywords']:
            if keyword in text_lower:
                score = len(keyword)  # Longer keyword = more specific match
                if score > best_score:
                    best_score = score
                    best_match = topic

    if best_match:
        return {
            "response": kb[best_match]['response'],
            "language": lang,
            "is_emergency": False,
            "topic": best_match
        }

    # 6. Try English KB as fallback even for Marathi queries
    if lang == 'mr' and not best_match:
        for topic, data in KNOWLEDGE_BASE_EN.items():
            for keyword in data['keywords']:
                if keyword in text_lower:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = topic
        if best_match:
            return {
                "response": KNOWLEDGE_BASE_EN[best_match]['response'],
                "language": 'en',
                "is_emergency": False,
                "topic": best_match
            }

    # 7. No match found
    kb = GENERIC_RESPONSES_MR if lang == 'mr' else GENERIC_RESPONSES_EN
    return {
        "response": kb['unknown'],
        "language": lang,
        "is_emergency": False,
        "topic": "unknown"
    }


# ─────────────────────────────────────────────
#  QUICK REPLY SUGGESTIONS (for chatbot UI chips)
# ─────────────────────────────────────────────
QUICK_REPLIES_EN = [
    "Dengue symptoms", "Malaria prevention", "Fever home remedy",
    "Monsoon health tips", "Diabetes diet", "Blood pressure control",
    "First aid for bleeding", "COVID-19 guidelines", "How to use OPD queue"
]

QUICK_REPLIES_MR = [
    "डेंग्यूची लक्षणे", "ताप उपाय", "मलेरिया प्रतिबंध",
    "पावसाळी आजार", "मधुमेह आहार", "रक्तदाब नियंत्रण",
    "OPD queue कसे वापरावे"
]

def get_quick_replies(lang: str = 'en') -> list:
    return QUICK_REPLIES_MR if lang == 'mr' else QUICK_REPLIES_EN


# Topic icons for UI display
TOPIC_ICONS = {
    "fever": "🌡️", "dengue": "🦟", "malaria": "🦟", "flu": "🤧",
    "covid": "😷", "monsoon": "🌧️", "diabetes": "🩺", "blood_pressure": "💉",
    "first_aid": "🏥", "diet": "🥗", "mental_health": "🧠", "pregnancy": "🤱",
    "cholesterol": "❤️", "opd": "🏥", "greeting": "👋", "emergency": "🚨",
    "unknown": "🤔"
}
