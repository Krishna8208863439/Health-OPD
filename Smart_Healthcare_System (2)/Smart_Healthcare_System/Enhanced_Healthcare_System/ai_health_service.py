"""
AI Health Service – natural-language symptom parsing, OTC suggestions,
personalized diet plans, and health chat assistant.
Uses rule-based intelligence with optional OpenAI/Gemini if API keys are set.
"""

import os
import re
import requests
import json
from symptom_engine import assess_symptoms, get_severity, get_medicines_for_disease, SYMPTOMS

def call_gemini(prompt: str, system_instruction: str = None) -> str:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                    return candidate['content']['parts'][0]['text']
    except Exception as e:
        print(f"[GEMINI] API Call failed: {e}")
    return None

def assess_symptoms_with_gemini(symptoms_or_text, user_profile=None):
    """
    Calls the Gemini API to get a structured symptom assessment and diagnosis.
    symptoms_or_text can be a list of symptoms or a raw text string.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return None

    # Format user profile info if available
    profile_info = ""
    if user_profile:
        profile_info = (
            f"User Profile details:\n"
            f"- Age: {user_profile.get('age', 'N/A')}\n"
            f"- Gender: {user_profile.get('gender', 'N/A')}\n"
            f"- City: {user_profile.get('city', 'Pune')}\n"
            f"- Diet Preference/Goal: {user_profile.get('diet_goal', 'N/A')}\n"
            f"- Medical Conditions: {user_profile.get('medical_conditions', 'None')}\n"
        )

    # Format the symptom input
    if isinstance(symptoms_or_text, list):
        symptom_desc = f"The user selected the following specific symptom tags: {', '.join(symptoms_or_text)}."
    else:
        symptom_desc = f"The user described their symptoms as follows: \"{symptoms_or_text}\"."

    # Language instruction
    lang = user_profile.get('lang', 'en') if user_profile else 'en'
    if lang == 'mr':
        lang_instruction = (
            "IMPORTANT: The user has selected Marathi as their preferred language. "
            "You MUST write ALL user-facing text fields (such as 'disease', 'description', 'doctor_advice', "
            "'medicines.PRIMARY', 'medicines.SECONDARY', 'medicines.HOME_REMEDIES', 'medicines.WHEN_TO_SEE_DOCTOR', "
            "'otc_medicines.name', 'otc_medicines.usage', 'otc_medicines.dosage', 'otc_medicines.side_effects', "
            "'alternative_diagnoses.disease', 'alternative_diagnoses.description') STRICTLY in pure, clean Marathi Devanagari script. "
            "Do NOT write in English, do NOT mix English and Marathi, do NOT use Latin characters, and do NOT use Hinglish/Latin script transliterations. "
            "The entire clinical assessment text fields MUST be completely in Marathi. Every word must be written in standard Marathi. "
            "For example, do NOT write English terms in Devanagari (like 'फ्लू' or 'मेडिसिन') if standard Marathi words like 'इन्फ्लूएंझा' or 'औषध' exist. "
            "For the doctor_advice field, always append this Marathi medical disclaimer at the end:\n"
            "**वैद्यकीय अस्वीकरण: या फक्त सामान्य ओटीसी (OTC) शिफारसी आहेत. कोणतेही औषध घेण्यापूर्वी वैद्यकीय व्यावसायिकाचा सल्ला घ्या. हे व्यावसायिक वैद्यकीय निदानासाठी पर्याय नाही.**"
        )
    else:
        lang_instruction = (
            "IMPORTANT: The user has selected English as their preferred language. "
            "You MUST write ALL user-facing text fields STRICTLY in English. Do NOT mix other languages. "
            "For the doctor_advice field, always append this English medical disclaimer at the end:\n"
            "**Medical Disclaimer: These are general OTC suggestions only. Consult a healthcare professional before taking any medication. This is NOT a substitute for professional medical diagnosis.**"
        )

    # Prompt
    prompt = (
        f"You are a professional clinical AI diagnostics assistant.\n"
        f"{profile_info}\n"
        f"Symptom inputs:\n{symptom_desc}\n\n"
        f"{lang_instruction}\n\n"
        "Please perform a symptom assessment and diagnosis. Provide the response strictly in JSON format matching the following schema:\n"
        "{\n"
        "  \"disease\": \"Primary predicted disease name (e.g. Influenza, COVID-19, Migraine, Gastroenteritis)\",\n"
        "  \"description\": \"A short medical explanation/description of the predicted disease (1-2 sentences)\",\n"
        "  \"confidence_pct\": integer_percentage_between_0_and_100,\n"
        "  \"severity\": \"HIGH 🔴\" or \"MEDIUM 🟡\" or \"LOW 🟢\",\n"
        "  \"matched_strong\": [\"list\", \"of\", \"symptoms\", \"strongly\", \"indicative\"],\n"
        "  \"matched_moderate\": [\"list\", \"of\", \"symptoms\", \"moderately\", \"indicative\"],\n"
        "  \"medicines\": {\n"
        "     \"PRIMARY\": [\"Primary prescription medicine details (e.g. Oseltamivir 75mg twice daily for 5 days)\"],\n"
        "     \"SECONDARY\": [\"Supporting or secondary medication details\"],\n"
        "     \"HOME_REMEDIES\": [\"Home care remedies, hydration, rest tips\"],\n"
        "     \"WHEN_TO_SEE_DOCTOR\": \"Specific warning signs or indicators on when to see a doctor\"\n"
        "  },\n"
        "  \"otc_medicines\": [\n"
        "     {\n"
        "       \"name\": \"OTC Medicine Name (e.g. Paracetamol 500mg)\",\n"
        "       \"usage\": \"Relief of fever and mild pain\",\n"
        "       \"dosage\": \"1 tablet every 6 hours as needed\",\n"
        "       \"side_effects\": \"Minimal, liver safety warnings\"\n"
        "     }\n"
        "  ],\n"
        "  \"alternative_diagnoses\": [\n"
        "     {\n"
        "       \"disease\": \"Alternative Disease Name\",\n"
        "       \"description\": \"Brief description\",\n"
        "       \"confidence_pct\": integer_percentage\n"
        "     }\n"
        "  ],\n"
        "  \"doctor_advice\": \"General clinical advice for the patient. ALWAYS include a bold medical disclaimer in the user's preferred language or English at the end.\",\n"
        "  \"emergency_warnings\": [\"List of severe emergency signs like chest pain, short of breath, unconscious\"]\n"
        "}\n"
        "Ensure the response is a single, valid JSON block. Return ONLY the JSON content."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                cand = result['candidates'][0]
                if 'content' in cand and 'parts' in cand['content'] and len(cand['content']['parts']) > 0:
                    text = cand['content']['parts'][0]['text'].strip()
                    parsed = json.loads(text)
                    return parsed
    except Exception as e:
        print(f"[GEMINI] Symptom assessment failed: {e}")
    return None

# ── Marathi digit → ASCII digit mapping ──
_MR_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


# ── Natural language → symptom ID keyword map ──
NLP_KEYWORDS = {
    "headache": ["headache", "head ache", "head pain", "migraine", "throbbing head",
                 "डोकेदुखी", "डोके दुखत", "डोके दुखणे", "डोक्यात", "डोक्यात दुखते", "माझे डोके दुखत"],
    "severe_headache": ["severe headache", "worst headache", "thunderclap",
                        "तीव्र डोकेदुखी", "भयंकर डोकेदुखी", "खूप डोकेदुखी"],
    "fever": ["fever", "temperature", "hot body", "feeling hot",
              "ताप", "तापमान", "ताप आला", "ताप आहे", "ताप आले", "तापाने"],
    "high_fever": ["high fever", "very high temperature", "103",
                   "तीव्र ताप", "खूप ताप", "जास्त ताप"],
    "fatigue": ["fatigue", "tired", "tiredness", "weakness", "exhausted", "low energy",
                "थकवा", "अशक्तपणा", "ग्लानी", "दमणे", "थकलेले", "शक्ती नाही"],
    "nausea": ["nausea", "nauseous", "feel sick", "queasy",
               "मळमळ", "उलटीसारखे वाटणे", "मळमळत आहे", "उलटी येणे वाटते"],
    "vomiting": ["vomiting", "throwing up", "vomit",
                 "उलटी", "उलट्या", "उलट्या होत आहेत", "उलटी झाली"],
    "dry_cough": ["dry cough", "coughing dry",
                  "कोरडा खोकला", "कोरडा खोकला आहे"],
    "productive_cough": ["productive cough", "cough with phlegm", "cough with mucus",
                         "कफ", "कफ खोकला", "खोकताना कफ", "कफ येत आहे"],
    "sore_throat": ["sore throat", "throat pain", "throat hurts",
                    "घसा दुखणे", "घसा खवखवणे", "घशात", "घसा दुखत आहे"],
    "runny_nose": ["runny nose", "stuffy nose", "blocked nose", "nasal congestion",
                   "नाक वाहणे", "नाक कोंदणे", "सर्दी", "नाक चालत आहे", "सर्दी झाली"],
    "breathing_difficulty": ["breathless", "breathing difficulty", "shortness of breath",
                             "can't breathe", "difficulty breathing",
                             "श्वास घेण्यास त्रास", "दम लागणे", "श्वास घेताना त्रास"],
    "chest_pain": ["chest pain", "chest tightness", "chest hurts",
                   "छातीत दुखणे", "छाती दुखणे", "छातीत वेदना", "छाती दुखत", "छातीत", "माझी छाती"],
    "stomach_pain": ["stomach pain", "stomach ache", "abdominal pain", "belly pain", "tummy pain",
                     "पोटदुखी", "पोटात दुखणे", "पोट दुखते", "पोटात वेदना"],
    "diarrhea": ["diarrhea", "loose motion", "loose stools", "watery stool",
                 "जुलाब", "अतिसार", "संडास", "पातळ संडास", "जुलाब झाले"],
    "constipation": ["constipation", "can't pass stool",
                     "बद्धकोष्ठता", "साफ न होणे", "शौच होत नाही"],
    "body_ache": ["body ache", "body pain", "muscle pain", "body hurts", "all over pain",
                  "अंगदुखी", "अंग दुखणे", "हातपाय दुखणे", "शरीर दुखणे", "सर्वत्र दुखत आहे",
                  "अंगात दुखत आहे", "संपूर्ण शरीर दुखत आहे"],
    "joint_pain": ["joint pain", "knee pain", "joint swelling",
                   "सांधेदुखी", "गुडघेदुखी", "सांधे दुखणे", "गुडघे दुखत आहेत"],
    "back_pain": ["back pain", "lower back pain",
                  "पाठदुखी", "कमरदुखी", "पाठ दुखत आहे"],
    "dizziness": ["dizzy", "dizziness", "lightheaded", "vertigo",
                  "चक्कर", "चक्कर येणे", "चक्कर आली", "डोळ्यांसमोर अंधारी"],
    "rash": ["rash", "skin rash", "hives", "itchy skin",
             "पुरळ", "गांधी उठणे", "खाज येणे", "त्वचेवर पुरळ"],
    "anxiety": ["anxiety", "anxious", "panic", "worried", "stressed",
                "चिंता", "अस्वस्थता", "घबराट", "मन अस्वस्थ"],
    "insomnia": ["insomnia", "can't sleep", "sleep problems",
                 "निद्रानाश", "झोप न येणे", "झोप येत नाही"],
    "frequent_urination": ["frequent urination", "urinating often", "peeing a lot",
                           "वारंवार लघवी", "लघवी जास्त", "लघवी वारंवार होते"],
    "painful_urination": ["painful urination", "burning urine", "burning when peeing",
                          "लघवी करताना जळजळ", "लघवी दुखणे", "लघवीत जळजळ"],
    "blurred_vision": ["blurred vision", "blurry eyes", "vision problems",
                       "अंधुक दिसणे", "कमी दिसणे", "नजर अंधुक"],
    "palpitations": ["palpitations", "heart racing", "fast heartbeat",
                     "छाती धडधडणे", "धडधड", "हृदय जलद धडकत आहे"],
    "loss_of_appetite": ["loss of appetite", "not hungry", "no appetite",
                         "भूक मंदावणे", "भूक न लागणे", "भूक नाही"],
    "chills": ["chills", "shivering", "shaking",
               "थंडी वाजणे", "हुडहुडी", "थरथर कापणे"],
    "wheezing": ["wheezing", "wheeze", "घरघर", "घरघर आवाज"],
    "heartburn": ["heartburn", "acid reflux", "burning chest",
                  "छातीत जळजळ", "ॲसिडिटी", "जळजळ"],
    "swollen_feet": ["swollen feet", "swollen ankles", "leg swelling",
                     "सूज", "पायाला सूज", "पाय सुजले"],
    "cold": ["cold", "common cold",
             "सर्दी", "खोकला व सर्दी"],
    "loss_of_smell": ["loss of smell", "can't smell",
                      "वास न येणे", "वास नाही"],
    "loss_of_taste": ["loss of taste", "can't taste",
                      "चव न समजणे", "चव नाही"],
}

EMERGENCY_KEYWORDS = [
    ("chest pain", "🚨 CHEST PAIN may indicate a heart attack. Call 108 immediately."),
    ("can't breathe", "🚨 SEVERE BREATHING DIFFICULTY – seek emergency care NOW. Call 108."),
    ("difficulty breathing", "🚨 Breathing difficulty detected – go to emergency if severe."),
    ("unconscious", "🚨 Loss of consciousness – call 108 immediately."),
    ("severe bleeding", "🚨 Severe bleeding – apply pressure and call 108."),
    ("seizure", "🚨 Seizure detected – call 108 and place patient on their side."),
    ("stroke", "🚨 Possible stroke – remember FAST (Face, Arms, Speech, Time). Call 108."),
    ("suicide", "🚨 Mental health emergency – call 112 or KIRAN Helpline 1800-599-0019."),
    ("worst headache", "🚨 Sudden severe headache – could be serious. Go to ER immediately."),
    ("coughing blood", "🚨 Coughing blood – seek emergency medical care."),
    ("blood in stool", "🚨 Blood in stool – see a doctor urgently."),
    # Marathi emergency keywords
    ("छातीत दुखणे", "🚨 छातीत दुखणे हृदयविकाराचे लक्षण असू शकते. ताबडतोब १०८ वर कॉल करा."),
    ("श्वास घेता येत नाही", "🚨 श्वास घेण्यास तीव्र त्रास – ताबडतोब आपत्कालीन काळजी घ्या. १०८ वर कॉल करा."),
    ("बेशुद्ध", "🚨 चेतना हरविली – ताबडतोब १०८ वर कॉल करा."),
]

EMERGENCY_SYMPTOMS = {
    "chest_pain", "breathing_difficulty", "oxygen_low", "coughing_blood",
    "confusion", "severe_headache", "neck_stiffness", "bloody_diarrhea",
    "blood_in_urine", "swollen_face", "petechiae",
}


def parse_natural_language(text: str) -> list:
    """Extract symptom IDs from free-text description (supports English + Marathi)."""
    if not text:
        return []
    # Normalise Marathi digits to ASCII so numbers like '२ दिवस' become '2 दिवस'
    text_normalised = text.translate(_MR_DIGITS)
    text_lower = text_normalised.lower().strip()
    found = set()

    for symptom_id, keywords in NLP_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found.add(symptom_id)
                break

    # Also match direct symptom display names
    for sid, display in SYMPTOMS.items():
        short = display.split("(")[0].strip().lower()
        if len(short) > 4 and short in text_lower:
            found.add(sid)

    return list(found)

OTC_MEDICINES = {
    "Paracetamol 500mg": {
        "usage": "Pain relief and fever reduction",
        "dosage": "1 tablet every 4–6 hours. Max 4g (8 tablets) per day.",
        "side_effects": "Rare: liver damage with overdose. Generally well tolerated.",
        "for_symptoms": ["headache", "fever", "body_ache", "high_fever"],
    },
    "Ibuprofen 200mg": {
        "usage": "Anti-inflammatory pain relief for headache, muscle pain, fever",
        "dosage": "1 tablet every 6–8 hours after food. Max 1200mg/day.",
        "side_effects": "Stomach upset, heartburn. Avoid if kidney/ulcer issues.",
        "for_symptoms": ["headache", "body_ache", "joint_pain", "fever"],
    },
    "Cetirizine 10mg": {
        "usage": "Antihistamine for allergies, runny nose, sneezing, rash",
        "dosage": "1 tablet once daily, preferably at night.",
        "side_effects": "Drowsiness in some people. Avoid alcohol.",
        "for_symptoms": ["runny_nose", "sneezing", "rash", "itching"],
    },
    "ORS (Oral Rehydration Solution)": {
        "usage": "Rehydration for diarrhea, vomiting, dehydration",
        "dosage": "1 sachet in 1 litre water. Sip frequently.",
        "side_effects": "None when used correctly.",
        "for_symptoms": ["diarrhea", "vomiting", "nausea"],
    },
    "Antacid (Digene / Gelusil)": {
        "usage": "Relief from acidity, heartburn, indigestion",
        "dosage": "10–20ml after meals or when needed.",
        "side_effects": "Constipation or diarrhea with prolonged use.",
        "for_symptoms": ["heartburn", "indigestion", "stomach_pain"],
    },
    "Lozenges (Strepsils)": {
        "usage": "Soothes sore throat and cough",
        "dosage": "1 lozenge every 2–3 hours. Max 8 per day.",
        "side_effects": "Mild numbness in mouth.",
        "for_symptoms": ["sore_throat", "dry_cough"],
    },
    "Dextromethorphan Syrup": {
        "usage": "Cough suppressant for dry cough",
        "dosage": "10ml every 6–8 hours. Do not exceed recommended dose.",
        "side_effects": "Drowsiness, dizziness.",
        "for_symptoms": ["dry_cough"],
    },
    "Simethicone": {
        "usage": "Relieves gas, bloating, stomach discomfort",
        "dosage": "1 tablet after meals as needed.",
        "side_effects": "Very rare side effects.",
        "for_symptoms": ["bloating", "stomach_pain"],
    },
}

DISCLAIMER = (
    "⚠️ Medical Disclaimer: These are general OTC suggestions only. "
    "Consult a healthcare professional before taking any medication. "
    "This is NOT a substitute for professional medical diagnosis."
)

DISCLAIMER_EN = DISCLAIMER
DISCLAIMER_MR = (
    "⚠️ वैद्यकीय अस्वीकरण: या फक्त सामान्य ओटीसी (OTC) शिफारसी आहेत. "
    "कोणतेही औषध घेण्यापूर्वी वैद्यकीय व्यावसायिकाचा सल्ला घ्या. "
    "हे व्यावसायिक वैद्यकीय निदानासाठी पर्याय नाही."
)

FIRST_AID_GUIDES = [
    {"title": "CPR Basics", "icon": "❤️", "steps": [
        "Check responsiveness – tap shoulder, shout.",
        "Call 108 immediately.",
        "30 chest compressions (5–6 cm deep, 100–120/min).",
        "2 rescue breaths. Repeat 30:2 cycle.",
    ]},
    {"title": "Choking", "icon": "🫁", "steps": [
        "Encourage coughing if partially blocked.",
        "5 back blows between shoulder blades.",
        "5 abdominal thrusts (Heimlich manoeuvre).",
        "Call 108 if not resolved.",
    ]},
    {"title": "Burns", "icon": "🔥", "steps": [
        "Cool under running water for 20 minutes.",
        "Remove jewellery near burn (before swelling).",
        "Cover with clean non-fluffy cloth.",
        "Do NOT apply ice, butter, or toothpaste.",
    ]},
    {"title": "Bleeding", "icon": "🩸", "steps": [
        "Apply direct pressure with clean cloth.",
        "Elevate injured limb above heart level.",
        "Do not remove embedded objects.",
        "Call 108 for severe or uncontrolled bleeding.",
    ]},
    {"title": "Seizure", "icon": "⚡", "steps": [
        "Clear area of dangerous objects.",
        "Place on side after seizure stops.",
        "Do NOT put anything in mouth.",
        "Time the seizure. Call 108 if >5 minutes.",
    ]},
]




def check_emergency(text: str, symptom_ids: list) -> list:
    """Return emergency warning messages."""
    warnings = []
    text_lower = (text or "").lower()

    for keyword, message in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            warnings.append(message)

    for sid in symptom_ids:
        if sid in EMERGENCY_SYMPTOMS:
            label = SYMPTOMS.get(sid, sid.replace("_", " ").title())
            warnings.append(f"🚨 Emergency symptom detected: {label}. Seek immediate medical care.")

    return list(dict.fromkeys(warnings))  # dedupe preserving order


def get_otc_suggestions(symptom_ids: list, disease: str = "") -> list:
    """Return structured OTC medicine suggestions."""
    suggestions = []
    seen = set()

    for name, info in OTC_MEDICINES.items():
        match = any(s in info["for_symptoms"] for s in symptom_ids)
        if match and name not in seen:
            seen.add(name)
            suggestions.append({
                "name": name,
                "usage": info["usage"],
                "dosage": info["dosage"],
                "side_effects": info["side_effects"],
            })

    if not suggestions:
        suggestions.append({
            "name": "Paracetamol 500mg",
            "usage": "General pain and fever relief",
            "dosage": "1 tablet every 4–6 hours as needed.",
            "side_effects": "Avoid overdose. Consult doctor if symptoms persist.",
        })

    return suggestions[:5]


def analyze_natural_symptoms(text: str) -> dict:
    """Full NLP symptom analysis pipeline."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            gemini_assessment = assess_symptoms_with_gemini(text)
            if gemini_assessment:
                symptom_ids = gemini_assessment.get("parsed_symptoms", [])
                parsed_labels = [SYMPTOMS.get(s, s.replace("_", " ").title()) for s in symptom_ids]
                
                top = {
                    "disease": gemini_assessment.get("disease", "Unknown Condition"),
                    "description": gemini_assessment.get("description", ""),
                    "confidence_pct": gemini_assessment.get("confidence_pct", 70)
                }
                
                results = [top]
                for r in gemini_assessment.get("alternative_diagnoses", []):
                    results.append({
                        "disease": r.get("disease"),
                        "description": r.get("description", ""),
                        "confidence_pct": r.get("confidence_pct", 30)
                    })
                
                severity = gemini_assessment.get("severity", "MEDIUM 🟡")
                medicines = gemini_assessment.get("medicines", {
                    "PRIMARY": [],
                    "SECONDARY": [],
                    "HOME_REMEDIES": [],
                    "WHEN_TO_SEE_DOCTOR": ""
                })
                otc = gemini_assessment.get("otc_medicines", [])
                emergencies = gemini_assessment.get("emergency_warnings", [])
                
                human_summary = _build_human_summary(text, symptom_ids, top, results[1:3], otc, emergencies)
                
                return {
                    "success": True,
                    "input_text": text,
                    "parsed_symptoms": symptom_ids,
                    "parsed_labels": parsed_labels,
                    "results": results,
                    "top_result": top,
                    "alt_results": results[1:],
                    "severity": severity,
                    "medicines": medicines,
                    "otc_medicines": otc,
                    "emergency_warnings": emergencies,
                    "human_summary": human_summary,
                    "disclaimer": DISCLAIMER,
                }
        except Exception as e:
            print(f"[GEMINI] analyze_natural_symptoms pipeline fallback: {e}")

    symptom_ids = parse_natural_language(text)
    emergencies = check_emergency(text, symptom_ids)

    if not symptom_ids:
        return {
            "success": False,
            "message": "Could not identify symptoms. Please describe more clearly (e.g. 'headache and fever for 2 days').",
            "parsed_symptoms": [],
            "emergency_warnings": emergencies,
        }

    results = assess_symptoms(symptom_ids)
    if not results:
        return {
            "success": False,
            "message": "Not enough information for a confident assessment. Please add more symptom details.",
            "parsed_symptoms": symptom_ids,
            "emergency_warnings": emergencies,
        }

    top = results[0]
    disease = top["disease"]
    confidence = top["confidence_pct"]
    severity = get_severity(confidence, disease)
    medicines = get_medicines_for_disease(disease, severity)
    otc = get_otc_suggestions(symptom_ids, disease)

    human_summary = _build_human_summary(text, symptom_ids, top, results[1:3], otc, emergencies)

    return {
        "success": True,
        "input_text": text,
        "parsed_symptoms": symptom_ids,
        "parsed_labels": [SYMPTOMS.get(s, s.replace("_", " ").title()) for s in symptom_ids],
        "results": results,
        "top_result": top,
        "alt_results": results[1:],
        "severity": severity,
        "medicines": medicines,
        "otc_medicines": otc,
        "emergency_warnings": emergencies,
        "human_summary": human_summary,
        "disclaimer": DISCLAIMER,
    }


def _build_human_summary(text, symptom_ids, top, alts, otc, emergencies):
    labels = ", ".join(SYMPTOMS.get(s, s) for s in symptom_ids[:5])
    lines = [
        f"Based on your description: \"{text[:120]}{'...' if len(text) > 120 else ''}\"",
        f"",
        f"We identified: {labels}",
        f"",
        f"Most likely condition: **{top['disease']}** ({top['confidence_pct']}% match)",
        f"{top.get('description', '')}",
    ]
    if alts:
        lines.append(f"\nOther possibilities: {', '.join(a['disease'] for a in alts)}")
    if otc:
        lines.append(f"\nSuggested OTC medicines: {', '.join(m['name'] for m in otc)}")
    if emergencies:
        lines.append(f"\n⚠️ URGENT: {' '.join(emergencies[:2])}")
    lines.append(f"\n{DISCLAIMER}")
    return "\n".join(lines)


def generate_diet_plan(profile: dict) -> dict:
    """Generate personalized diet plan from user profile."""
    try:
        age = int(profile.get("age")) if profile.get("age") is not None else 30
    except (ValueError, TypeError):
        age = 30
        
    gender = profile.get("gender", "male") or "male"
    
    try:
        height = float(profile.get("height")) if profile.get("height") else 170.0
    except (ValueError, TypeError):
        height = 170.0
        
    try:
        weight = float(profile.get("weight")) if profile.get("weight") else 70.0
    except (ValueError, TypeError):
        weight = 70.0
        
    activity = profile.get("activity_level", "moderate")
    conditions = profile.get("medical_conditions", "") or ""
    preference = profile.get("dietary_preference", "vegetarian") or "vegetarian"
    goal = profile.get("diet_goal", "Balanced") or "Balanced"

    # Avoid division by zero
    if height <= 0:
        height = 170.0
    if weight <= 0:
        weight = 70.0

    bmi = round(weight / ((height / 100) ** 2), 1)
    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "male" else -161)
    activity_mult = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
    calories = int(bmr * activity_mult.get(activity, 1.55))

    if goal in ("Weight Loss", "weight_loss"):
        calories = int(calories * 0.8)
    elif goal in ("Muscle Gain", "muscle", "Weight Gain", "weight_gain"):
        calories = int(calories * 1.15)

    water_ml = int(weight * 35)

    veg_meals = _veg_meal_plan(goal, conditions, calories)
    nonveg_meals = _nonveg_meal_plan(goal, conditions, calories)

    grocery = _grocery_list(veg_meals if preference == "vegetarian" else nonveg_meals)

    return {
        "bmi": bmi,
        "daily_calories": calories,
        "water_intake_ml": water_ml,
        "water_intake_litres": round(water_ml / 1000, 1),
        "goal": goal,
        "preference": preference,
        "vegetarian": veg_meals,
        "non_vegetarian": nonveg_meals,
        "weekly_plan": _weekly_plan(goal, preference),
        "grocery_list": grocery,
        "nutrition": {
            "protein_g": int(weight * 1.2) if goal in ("Muscle Gain", "muscle") else int(weight * 0.8),
            "carbs_g": int(calories * 0.5 / 4),
            "fat_g": int(calories * 0.25 / 9),
            "fiber_g": 25,
        },
    }


def _veg_meal_plan(goal, conditions, cal):
    base = {
        "breakfast": "Oats with milk, banana, and almonds",
        "mid_morning": "Green tea + handful of walnuts",
        "lunch": "2 chapati, dal fry, mix veg sabji, curd, salad",
        "evening_snack": "Roasted makhana or fruit bowl",
        "dinner": "Moong dal khichdi, palak sabji, 1 tsp ghee",
        "water": "8–10 glasses (2–2.5 litres)",
    }
    if "diabet" in conditions.lower() or goal == "Diabetic Care":
        base = {**base,
            "breakfast": "Moong dal chilla with mint chutney",
            "lunch": "1 multigrain roti, chana curry, large salad, curd",
            "dinner": "Grilled paneer, cauliflower rice, spinach soup",
        }
    elif goal in ("Weight Loss", "weight_loss"):
        base = {**base,
            "breakfast": "Vegetable poha + green tea",
            "lunch": "Brown rice (1 cup), dal, steamed vegetables",
            "dinner": "Sautéed vegetables with tofu, no rice",
        }
    elif goal in ("Muscle Gain", "muscle", "Weight Gain"):
        base = {**base,
            "breakfast": "Oats + milk + peanut butter + banana + protein shake",
            "lunch": "Brown rice (2 cups), soya chunks curry, salad, curd",
            "dinner": "Paneer tikka, sweet potato, black dal",
        }
    elif goal == "Heart Healthy":
        base = {**base,
            "breakfast": "Fruit bowl with chia seeds + almond milk",
            "lunch": "Oats khichdi with vegetables, flaxseed salad",
            "dinner": "Tofu soup, multigrain toast, steamed broccoli",
        }
    return base


def _nonveg_meal_plan(goal, conditions, cal):
    base = {
        "breakfast": "2 boiled eggs, whole wheat toast, low-fat milk",
        "mid_morning": "Apple + green tea",
        "lunch": "Chicken breast (120g), brown rice, vegetables, salad",
        "evening_snack": "Boiled egg or roasted chana",
        "dinner": "Fish curry (100g), chapati, green salad",
        "water": "8–10 glasses (2–2.5 litres)",
    }
    if "diabet" in conditions.lower() or goal == "Diabetic Care":
        base = {**base,
            "breakfast": "Egg white omelette with spinach",
            "lunch": "Grilled chicken (100g), 1 roti, salad, curd",
            "dinner": "Grilled fish, sautéed vegetables, light soup",
        }
    elif goal in ("Weight Loss", "weight_loss"):
        base = {**base,
            "breakfast": "Veggie omelette (2 eggs) + green tea",
            "lunch": "Grilled chicken salad (150g), lemon dressing",
            "dinner": "Grilled salmon (120g) with steamed vegetables",
        }
    elif goal in ("Muscle Gain", "muscle", "Weight Gain"):
        base = {**base,
            "breakfast": "4 egg whites + oats + whey protein shake",
            "lunch": "Chicken curry (200g), brown rice (2 cups), salad",
            "dinner": "Grilled fish (150g), sweet potato, asparagus",
        }
    return base


def _weekly_plan(goal, preference):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    themes = {
        "Weight Loss": ["High Protein", "Low Carb", "Salad Day", "Lean Protein", "Soup Day", "Light Meals", "Meal Prep"],
        "Muscle Gain": ["Heavy Protein", "Carb Load", "Recovery", "Strength", "Active", "Cheat Meal", "Rest & Recover"],
        "Diabetic Care": ["Low GI", "Fiber Rich", "No Sugar", "Whole Grains", "Lean Meals", "Veggie Focus", "Balance"],
        "Heart Healthy": ["Low Sodium", "Omega-3", "Plant Based", "Whole Grains", "Light Dinner", "Fresh Produce", "Balance"],
        "Balanced": ["Indian Classic", "South Indian", "North Indian", "Protein Focus", "Veggie Day", "Family Meal", "Light"],
    }
    theme_list = themes.get(goal, themes["Balanced"])
    return [{"day": d, "theme": theme_list[i % len(theme_list)]} for i, d in enumerate(days)]


def _grocery_list(meals):
    items = set()
    text = " ".join(meals.values()).lower()
    mapping = {
        "oats": "Oats (500g)", "milk": "Milk (1L)", "banana": "Bananas (6)",
        "dal": "Mixed Dal (500g)", "chapati": "Whole Wheat Flour (1kg)",
        "rice": "Brown Rice (1kg)", "paneer": "Paneer (200g)",
        "egg": "Eggs (12)", "chicken": "Chicken Breast (500g)",
        "fish": "Fish fillets (300g)", "vegetable": "Mixed Vegetables (1kg)",
        "salad": "Salad greens", "almond": "Almonds (200g)",
        "makhana": "Makhana (200g)", "curd": "Curd/Yogurt (500g)",
        "spinach": "Spinach (250g)", "tofu": "Tofu (200g)",
    }
    for key, item in mapping.items():
        if key in text:
            items.add(item)
    return sorted(items) if items else ["Oats", "Dal", "Vegetables", "Fruits", "Milk", "Eggs/Chicken (as per preference)"]


def ai_chat_response(message: str, user_context: dict = None) -> str:
    """Rule-based health chat with optional API fallback."""
    ctx = user_context or {}
    msg = message.lower().strip()
    lang = ctx.get('lang', 'en')

    # Try OpenAI/Gemini if keys available
    api_response = _try_api_chat(message, ctx)
    if api_response:
        return api_response

    # Headache Matchers
    headache_kws = ["headache", "head pain", "migraine",
                    "डोकेदुखी", "डोके दुखत", "डोके दुखणे", "डोक्यात", "माझे डोके दुखत"]
    if any(w in msg for w in headache_kws):
        if lang == 'mr':
            return (
                "🧠 **डोकेदुखी / Headache**\n\n"
                "**Marathi:** डोकेदुखीसाठी, शांत आणि अंधाऱ्या खोलीत विश्रांती घ्या आणि पुरेसे पाणी प्या. "
                "ओटीसी पॅरासिटामॉल ५०० एमजी (Paracetamol 500mg) किंवा आयबुप्रोफेन २०० एमजी मदत करू शकतात. "
                "अचानक तीव्र डोकेदुखी, दृष्टीमध्ये बदल किंवा मान आखडणे असल्यास ताबडतोब डॉक्टरांकडे जा.\n"
                f"**English:** Rest in a quiet dark room and stay hydrated. Take Paracetamol 500mg every 4-6 hrs. "
                f"Seek emergency care for sudden severe headache or neck stiffness.\n\n{DISCLAIMER_MR}"
            )
        else:
            return (
                "🧠 **Headache / डोकेदुखी**\n\n"
                "**English:** Rest in a quiet dark room and stay hydrated. "
                "OTC Paracetamol 500mg or Ibuprofen 200mg may help. "
                "Seek emergency care if sudden severe headache, vision changes, or neck stiffness.\n"
                "**मराठी:** शांत अंधाऱ्या खोलीत विश्रांती घ्या, पाणी प्या. पॅरासिटामॉल ५०० मिग्रॅ घ्या.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Fever Matchers
    fever_kws = ["fever", "temperature", "ताप", "तापमान", "ताप आला", "ताप आहे"]
    if any(w in msg for w in fever_kws):
        if lang == 'mr':
            return (
                "🌡️ **ताप / Fever**\n\n"
                "**Marathi:** विश्रांती घ्या, भरपूर पाणी आणि द्रव प्या. "
                "दर ४–६ तासांनी पॅरासिटामॉल ५०० एमजी घ्या. "
                "ताप १०३°F पेक्षा जास्त असल्यास किंवा ३ दिवसांपेक्षा जास्त काळ राहिल्यास डॉक्टरांचा सल्ला घ्या.\n"
                "**English:** Rest & drink fluids. Take Paracetamol 500mg every 4-6 hrs. "
                "See doctor if fever > 103°F or persists > 3 days.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🌡️ **Fever / ताप**\n\n"
                "**English:** Rest, drink plenty of fluids, and take Paracetamol 500mg every 4–6 hours. "
                "Monitor temperature. See a doctor if fever >103°F persists beyond 3 days.\n"
                "**मराठी:** विश्रांती घ्या, पाणी प्या, पॅरासिटामॉल ५०० मिग्रॅ घ्या. ताप जास्त असल्यास डॉक्टरांकडे जा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Nausea / Vomiting Matchers
    nausea_kws = ["nausea", "vomit", "nauseous", "queasy", "throwing up",
                  "मळमळ", "उलटी", "उलट्या", "मळमळत आहे", "उलटी येणे"]
    if any(w in msg for w in nausea_kws):
        if lang == 'mr':
            return (
                "🤢 **मळमळ / उलटी – Nausea/Vomiting**\n\n"
                "**Marathi:** लहान लहान घोटात थंड पाणी किंवा ORS प्या. "
                "मसालेदार आणि जड पदार्थ टाळा. आल्याचा चहा (Ginger tea) मळमळ कमी करतो. "
                "उलट्या जास्त होत असल्यास किंवा रक्त असल्यास ताबडतोब डॉक्टरांकडे जा.\n"
                "**English:** Sip cold water or ORS slowly. Avoid spicy/heavy food. "
                "Ginger tea helps nausea. See a doctor if vomiting is persistent or blood-tinged.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🤢 **Nausea/Vomiting / मळमळ/उलटी**\n\n"
                "**English:** Sip small amounts of cold water or ORS. Avoid spicy or heavy food. "
                "Ginger tea may help. See a doctor if vomiting persists >6 hours or contains blood.\n"
                "**मराठी:** थंड पाणी किंवा ORS हळूहळू प्या. आल्याचा चहा उपयुक्त आहे.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Cough / Cold Matchers
    cough_kws = ["cough", "cold", "sore throat", "runny nose", "sneezing",
                 "खोकला", "सर्दी", "कोरडा खोकला", "कफ", "घसा दुखणे", "नाक वाहणे"]
    if any(w in msg for w in cough_kws):
        if lang == 'mr':
            return (
                "🤧 **खोकला / सर्दी – Cough/Cold**\n\n"
                "**Marathi:** उबदार पाणी आणि गरम पेये घ्या. "
                "मध आणि आलं असलेला चहा घसा दुखण्यासाठी उपयुक्त आहे. "
                "कोरड्या खोकल्यासाठी Dextromethorphan Syrup किंवा Strepsils लोझेंज वापरा. "
                "सर्दीसाठी सेटीरिझिन (Cetirizine 10mg) उपयुक्त आहे. "
                "खोकला ७ दिवसांपेक्षा जास्त काळ राहिल्यास डॉक्टरांचा सल्ला घ्या.\n"
                "**English:** Warm fluids, honey-ginger tea for throat. "
                "Strepsils/Dextromethorphan for cough. Cetirizine for cold/sneezing.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🤧 **Cough/Cold / खोकला/सर्दी**\n\n"
                "**English:** Drink warm fluids, honey-ginger tea helps soothe sore throat. "
                "For dry cough: Strepsils lozenges or Dextromethorphan Syrup. "
                "For runny nose/sneezing: Cetirizine 10mg once daily at night. "
                "See a doctor if cough persists >7 days or with blood.\n"
                "**मराठी:** गरम पाणी, मध-आलं चहा प्या. खोकल्यासाठी Strepsils वापरा. "
                "सर्दीसाठी सेटीरिझिन घ्या.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Body Ache Matchers
    bodyache_kws = ["body ache", "body pain", "muscle pain", "body hurts",
                    "अंगदुखी", "अंग दुखणे", "हातपाय दुखणे", "शरीर दुखणे",
                    "अंगात दुखत आहे", "संपूर्ण शरीर दुखत"]
    if any(w in msg for w in bodyache_kws):
        if lang == 'mr':
            return (
                "💪 **अंगदुखी – Body Ache**\n\n"
                "**Marathi:** विश्रांती घ्या आणि भरपूर पाणी प्या. "
                "उबदार पाण्याने शेक करा. आयबुप्रोफेन २०० एमजी (Ibuprofen 200mg) "
                "किंवा पॅरासिटामॉल ५०० एमजी जेवणानंतर घ्या. "
                "ताप बरोबर अंगदुखी असल्यास व्हायरल इन्फेक्शन असू शकते – विश्रांती घ्या.\n"
                "**English:** Rest and hydrate. Warm compress. "
                "Take Ibuprofen 200mg or Paracetamol 500mg after food.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "💪 **Body Ache / अंगदुखी**\n\n"
                "**English:** Rest and stay hydrated. Apply warm compress. "
                "Take Ibuprofen 200mg (after food) or Paracetamol 500mg for relief. "
                "Body ache with fever may indicate viral infection — rest is key.\n"
                "**मराठी:** विश्रांती घ्या, पाणी प्या, उबदार शेक करा. "
                "आयबुप्रोफेन किंवा पॅरासिटामॉल घ्या.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Stomach / Digestive Matchers
    stomach_kws = ["stomach pain", "stomach ache", "abdominal pain", "diarrhea",
                   "loose motion", "constipation", "heartburn", "acidity", "indigestion",
                   "पोटदुखी", "पोटात दुखणे", "जुलाब", "अतिसार", "बद्धकोष्ठता",
                   "छातीत जळजळ", "ॲसिडिटी", "अपचन", "पोट दुखते"]
    if any(w in msg for w in stomach_kws):
        if lang == 'mr':
            return (
                "🍽️ **पोटाचा त्रास – Digestive Issues**\n\n"
                "**Marathi:**\n"
                "• पोटदुखीसाठी: ओमेप्राझोल (Omeprazole) किंवा अँटासिड (Antacid) घ्या\n"
                "• जुलाबासाठी: ORS प्या, तेलकट आणि मसालेदार अन्न टाळा\n"
                "• बद्धकोष्ठतेसाठी: भरपूर पाणी, फायबरयुक्त अन्न आणि व्यायाम करा\n"
                "• ॲसिडिटीसाठी: जेवणानंतर Antacid (Digene/Gelusil) घ्या, मसालेदार अन्न टाळा\n"
                "**English:** Antacid for heartburn, ORS for diarrhea, fiber for constipation.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🍽️ **Digestive Issues / पोटाचा त्रास**\n\n"
                "**English:**\n"
                "• Stomach pain/acidity: Antacid (Digene/Gelusil) after meals\n"
                "• Diarrhea: ORS solution, BRAT diet (Banana, Rice, Applesauce, Toast)\n"
                "• Constipation: High-fiber foods, plenty of water, light exercise\n"
                "• Indigestion: Simethicone after meals, avoid spicy/oily food\n"
                "**मराठी:** जुलाबासाठी ORS, ॲसिडिटीसाठी Antacid, बद्धकोष्ठतेसाठी फायबर खा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Dizziness Matchers
    dizzy_kws = ["dizzy", "dizziness", "lightheaded", "vertigo",
                 "चक्कर", "चक्कर येणे", "चक्कर आली", "डोळ्यांसमोर अंधारी"]
    if any(w in msg for w in dizzy_kws):
        if lang == 'mr':
            return (
                "😵 **चक्कर येणे – Dizziness**\n\n"
                "**Marathi:** बसा किंवा झोपा, उठण्याची घाई करू नका. "
                "पुरेसे पाणी प्या (निर्जलीकरण हे एक कारण आहे). "
                "रक्तदाब तपासा. जेवण वेळेवर घ्या (कमी रक्तशर्करा टाळा). "
                "वारंवार चक्कर येत असल्यास कान, नाक, घसा (ENT) तज्ज्ञांचा सल्ला घ्या.\n"
                "**English:** Sit/lie down, hydrate, check blood pressure. "
                "Frequent dizziness needs ENT or physician evaluation.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "😵 **Dizziness / चक्कर येणे**\n\n"
                "**English:** Sit or lie down immediately to prevent falling. "
                "Stay hydrated (dehydration is a common cause). "
                "Check your blood pressure. Eat on time to avoid low blood sugar. "
                "If frequent, see an ENT specialist or physician.\n"
                "**मराठी:** बसा, पाणी प्या, रक्तदाब तपासा. वारंवार येत असल्यास डॉक्टरांकडे जा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Anxiety / Stress Matchers
    anxiety_kws = ["anxiety", "anxious", "panic", "worried", "stress", "mental health",
                   "चिंता", "अस्वस्थता", "घबराट", "मन अस्वस्थ", "तणाव", "मानसिक"]
    if any(w in msg for w in anxiety_kws):
        if lang == 'mr':
            return (
                "🧘 **चिंता / मानसिक स्वास्थ्य – Anxiety/Mental Health**\n\n"
                "**Marathi:** दीर्घ श्वास घ्या (4-7-8 श्वासाची पद्धत). "
                "दिवसातून 10-15 मिनिटे ध्यान (meditation) किंवा प्राणायाम करा. "
                "नियमित व्यायाम, पुरेशी झोप आणि सामाजिक संपर्क मदत करतो. "
                "तीव्र चिंता, निराशा किंवा मानसिक त्रासासाठी KIRAN Helpline: 1800-599-0019 वर कॉल करा.\n"
                "**English:** Deep breathing, meditation, regular exercise. "
                "KIRAN Mental Health Helpline: 1800-599-0019 (free, 24x7).\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🧘 **Anxiety/Mental Health / चिंता**\n\n"
                "**English:** Practice deep breathing (4-7-8 method), daily meditation/pranayama. "
                "Regular exercise, sufficient sleep, and social connection help greatly. "
                "KIRAN Mental Health Helpline: 1800-599-0019 (Free 24x7).\n"
                "**मराठी:** दीर्घ श्वास, ध्यान, व्यायाम करा. KIRAN: 1800-599-0019.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Rash / Skin Matchers
    rash_kws = ["rash", "skin", "hives", "itching", "itchy",
                "पुरळ", "खाज येणे", "त्वचेवर", "गांधी उठणे"]
    if any(w in msg for w in rash_kws):
        if lang == 'mr':
            return (
                "🩹 **त्वचेचा पुरळ / खाज – Skin Rash**\n\n"
                "**Marathi:** प्रभावित भागावर ओलसर थंड कापड लावा. "
                "सेटीरिझिन (Cetirizine 10mg) रात्री एकदा घेतल्यास खाज कमी होते. "
                "डिटर्जंट, धुळ, किंवा नवीन पदार्थ टाळा जे ॲलर्जी कारणीभूत असू शकतात. "
                "पुरळ चेहऱ्यावर किंवा श्वास घेण्यास त्रास असल्यास ताबडतोब डॉक्टरांकडे जा.\n"
                "**English:** Cool compress on rash. Cetirizine 10mg for itching. "
                "Avoid allergens. See doctor if rash spreads or breathing is affected.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🩹 **Skin Rash / त्वचेचा पुरळ**\n\n"
                "**English:** Apply cool damp compress. Cetirizine 10mg once at night reduces itching. "
                "Avoid known allergens (detergent, dust, new foods). "
                "See a doctor immediately if rash is on face or breathing is affected.\n"
                "**मराठी:** थंड कापड लावा, सेटीरिझिन घ्या. चेहऱ्यावर असल्यास ताबडतोब डॉक्टरांकडे जा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Chest Pain / Heart Matchers — EMERGENCY
    chest_kws = ["chest pain", "heart", "chest tightness", "palpitation",
                 "छातीत दुखणे", "छाती दुखणे", "धडधड", "छातीत वेदना"]
    if any(w in msg for w in chest_kws):
        if lang == 'mr':
            return (
                "🚨 **छातीत दुखणे – Chest Pain (आणीबाणी)**\n\n"
                "**Marathi:** छातीत दुखणे हे हृदयविकाराचे लक्षण असू शकते. "
                "ताबडतोब रुग्णाला झोपवा, घट्ट कपडे सैल करा. "
                "**ताबडतोब १०८ वर कॉल करा.** "
                "जवळ Aspirin 325mg असल्यास ॲलर्जी नसल्याची खात्री करून घ्या. "
                "स्वतः गाडी चालवू नका – रुग्णवाहिका बोलवा.\n"
                "**English:** CALL 108 IMMEDIATELY. Chest pain may indicate heart attack. "
                "Lay patient down, loosen tight clothing. Do NOT drive — call ambulance.\n\n"
                "🆘 **Emergency: 108 | 112**"
            )
        else:
            return (
                "🚨 **Chest Pain — EMERGENCY**\n\n"
                "**English:** Chest pain can indicate a heart attack. "
                "CALL 108 IMMEDIATELY. Lay the patient down, loosen tight clothing. "
                "Do NOT drive yourself — call an ambulance.\n"
                "**मराठी:** ताबडतोब १०८ वर कॉल करा. हे हृदयविकाराचे लक्षण असू शकते.\n\n"
                "🆘 **Emergency: 108 | 112**"
            )

    # Diet Matchers
    diet_kws = ["diet", "food", "meal", "eat", "nutrition", "weight",
                "आहार", "जेवण", "खाणे", "वजन कमी", "वजन", "पोषण"]
    if any(w in msg for w in diet_kws):
        goal = ctx.get("diet_goal", "Balanced")
        goal_display = goal
        if lang == 'mr':
            goals_map = {
                "Balanced": "संतुलित", "Weight Loss": "वजन कमी करणे",
                "Weight Gain": "वजन वाढवणे", "Muscle Gain": "स्नायू वाढवणे",
                "Diabetic Care": "मधुमेह काळजी", "Heart Healthy": "हृदय निरोगी",
            }
            goal_display = goals_map.get(goal, goal)
            return (
                f"🥗 **आहार योजना – Diet Plan**\n\n"
                f"**Marathi:** तुमचे सध्याचे आहाराचे ध्येय: **{goal_display}**\n"
                "पुरेसे प्रोटीन, कॉम्प्लेक्स कार्ब्स आणि हिरव्या भाज्या असलेल्या संतुलित आहारावर लक्ष केंद्रित करा. "
                "वैयक्तिकृत आहार योजनांसाठी 'आहार योजना' (Diet Plans) पानाला भेट द्या.\n"
                f"**English:** Your diet goal: {goal}. Balanced protein, complex carbs & vegetables. "
                "Visit the Diet Plans page for personalized meal plans.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                f"🥗 **Diet Plan / आहार योजना**\n\n"
                f"**English:** Your active diet goal: **{goal_display}**\n"
                "Focus on balanced meals with adequate protein, complex carbs, and vegetables. "
                "Visit the Diet Plans page for personalized meal plans. "
                "Use the Food Scanner to check if meals align with your goal.\n"
                f"**मराठी:** आहाराचे ध्येय: {goals_map.get(goal, goal) if False else goal}. "
                "Diet Plans पानावर जा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Medicine Matchers
    med_kws = ["medicine", "medication", "pill", "reminder", "alarm",
               "औषध", "स्मरणपत्र", "अलार्म", "औषधे"]
    if any(w in msg for w in med_kws):
        if lang == 'mr':
            return (
                "💊 **औषध स्मरणपत्र – Medicine Reminder**\n\n"
                "**Marathi:** नाव, डोस आणि वेळेसह 'औषधे' (Meds) विभागात औषध स्मरणपत्रे सेट करा. "
                "ॲप बंद असतानाही अलार्मसाठी सूचना (notifications) सक्षम करा. "
                "नेहमी तुमच्या डॉक्टरांच्या प्रिस्क्रिप्शनचे अनुसरण करा.\n"
                "**English:** Go to Meds section → Add reminder with medicine name, dosage, and time. "
                "Enable notifications for alerts even when app is closed.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "💊 **Medicine Reminder / औषध स्मरणपत्र**\n\n"
                "**English:** Set medicine reminders in the Meds section with name, dosage, and time. "
                "Enable notifications for alarms even when the app is closed. "
                "Always follow your doctor's prescription.\n"
                "**मराठी:** 'औषधे' विभागात स्मरणपत्र सेट करा. Notifications सक्षम ठेवा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Emergency Matchers
    emergency_kws = ["emergency", "sos", "ambulance", "108", "help urgent",
                     "आपत्कालीन", "मदत", "रुग्णवाहिका", "१०८"]
    if any(w in msg for w in emergency_kws):
        if lang == 'mr':
            return (
                "🚨 **आपत्कालीन परिस्थिती – Emergency**\n\n"
                "**Marathi:** १०८ (रुग्णवाहिका), ११२ (ERSS) किंवा १०० (पोलीस) वर कॉल करा. "
                "रुग्णवाहिका आणि जवळचे रुग्णालय शोधण्यासाठी 'मदत' (SOS) पानाचा वापर करा. "
                "प्रथमोपचार मार्गदर्शनासाठी आपत्कालीन (Emergency) पानावर जा.\n"
                "**English:** Call 108 (Ambulance), 112 (ERSS), 100 (Police). "
                "Use the SOS page for nearest hospital locator.\n\n"
                "🆘 **Emergency: 108 | 112 | 100**"
            )
        else:
            return (
                "🚨 **Emergency / आपत्कालीन**\n\n"
                "**English:** Call 108 (Ambulance), 112 (ERSS), or 100 (Police). "
                "Use the SOS page for ambulance simulation and nearest hospital locator. "
                "Go to Emergency page for first aid guidelines.\n"
                "**मराठी:** ताबडतोब १०८ (रुग्णवाहिका), ११२ (ERSS) वर कॉल करा.\n\n"
                "🆘 **Emergency: 108 | 112 | 100**"
            )

    # Water Matchers
    water_kws = ["water", "hydrat", "drink", "पाणी", "जल", "पिऊ", "पिणे"]
    if any(w in msg for w in water_kws):
        glasses = ctx.get("water_glasses", 0)
        if lang == 'mr':
            return (
                f"💧 **पाण्याचे सेवन – Water Intake**\n\n"
                f"**Marathi:** तुम्ही आज **{glasses} ग्लास** पाणी प्यायल्याची नोंद केली आहे. "
                "दररोज ८–१० ग्लास (२–२.५ लिटर) पाणी पिण्याचे ध्येय ठेवा. "
                "उन्हाळ्यात किंवा व्यायामानंतर जास्त पाणी घ्या. "
                "निरोगीपणा (Daily Wellness) विभागात पाण्याचा मागोवा ठेवा.\n"
                f"**English:** You've logged {glasses} glasses. Aim for 8–10 glasses/day.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                f"💧 **Water Intake / पाण्याचे सेवन**\n\n"
                f"**English:** You've logged **{glasses} glasses** today. "
                "Aim for 8–10 glasses (2–2.5 litres) per day. "
                "Increase intake during summer or after exercise. "
                "Track water in the Daily Wellness section.\n"
                f"**मराठी:** आज {glasses} ग्लास. दिवसाला ८–१० ग्लास पाण्याचे ध्येय ठेवा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Sleep Matchers
    sleep_kws = ["sleep", "insomnia", "tired", "झोप", "निद्रानाश", "झोप येत नाही"]
    if any(w in msg for w in sleep_kws):
        if lang == 'mr':
            return (
                "😴 **झोपेचा त्रास – Sleep Issues**\n\n"
                "**Marathi:** प्रौढांना दररोज ७–९ तास झोपेची गरज असते. "
                "झोपण्याच्या १ तास आधी मोबाइल/स्क्रीन टाळा. "
                "खोली अंधारी आणि थंड ठेवा. "
                "झोपण्यापूर्वी उबदार दूध किंवा कॅमोमाइल चहा घ्या. "
                "निरोगीपणा (Daily Wellness) विभागात झोपेचा मागोवा घ्या.\n"
                "**English:** 7-9 hrs sleep. No screens 1 hr before bed. Cool, dark room helps.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "😴 **Sleep Issues / झोपेचा त्रास**\n\n"
                "**English:** Adults need 7–9 hours of sleep. "
                "Avoid screens 1 hour before bed. Keep room dark and cool. "
                "Try warm milk or chamomile tea before sleep. "
                "Track sleep in Daily Wellness section.\n"
                "**मराठी:** ७–९ तास झोप आवश्यक आहे. झोपण्यापूर्वी स्क्रीन टाळा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Exercise Matchers
    exercise_kws = ["exercise", "fitness", "workout", "gym", "yoga",
                    "व्यायाम", "फिटनेस", "कसरत", "योग"]
    if any(w in msg for w in exercise_kws):
        if lang == 'mr':
            return (
                "🏃 **व्यायाम – Fitness**\n\n"
                "**Marathi:** दर आठवड्याला किमान १५० मिनिटे मध्यम व्यायामाचे ध्येय ठेवा. "
                "चालणे, पोहणे किंवा सायकलिंग उत्तम पर्याय आहेत. "
                "दिवसातून ३०-४५ मिनिटे योग किंवा प्राणायाम करा. "
                "वैयक्तिकृत कसरत योजनांसाठी 'फिटनेस कोच' (Fitness Coaching) पानाला भेट द्या.\n"
                "**English:** Aim for 150 mins/week moderate exercise. "
                "Walking, swimming, cycling are great options.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🏃 **Fitness / व्यायाम**\n\n"
                "**English:** Aim for 150 minutes of moderate exercise per week. "
                "Walking, swimming, cycling, or yoga are excellent options. "
                "Visit Fitness Coaching for personalized workout plans.\n"
                "**मराठी:** आठवड्याला १५० मिनिटे व्यायाम करा. Fitness Coaching पान पहा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Blood Sugar / Diabetes Matchers
    diabetes_kws = ["diabetes", "blood sugar", "sugar", "insulin",
                    "मधुमेह", "रक्तशर्करा", "साखर", "इन्सुलिन"]
    if any(w in msg for w in diabetes_kws):
        if lang == 'mr':
            return (
                "🍬 **मधुमेह – Diabetes**\n\n"
                "**Marathi:** नियमित रक्त तपासणी करा. कमी GI असलेले पदार्थ खा. "
                "साखर, मैदा आणि जास्त तेलकट पदार्थ टाळा. "
                "नियमित व्यायाम करा आणि वजन नियंत्रित ठेवा. "
                "डॉक्टरांनी सांगितल्यास इन्सुलिन किंवा औषधे वेळेवर घ्या.\n"
                "**English:** Regular blood sugar monitoring, low-GI diet, exercise. "
                "Take prescribed insulin/medicines on time.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "🍬 **Diabetes / मधुमेह**\n\n"
                "**English:** Monitor blood sugar regularly. Eat low-GI foods. "
                "Avoid sugar, refined flour, and excessive oil. "
                "Regular exercise helps control blood sugar. "
                "Take prescribed insulin or medicines on time.\n"
                "**मराठी:** नियमित रक्त तपासणी करा, कमी GI आहार घ्या, व्यायाम करा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # Blood Pressure Matchers
    bp_kws = ["blood pressure", "hypertension", "bp high", "bp low",
              "रक्तदाब", "उच्च रक्तदाब", "बीपी"]
    if any(w in msg for w in bp_kws):
        if lang == 'mr':
            return (
                "❤️ **रक्तदाब – Blood Pressure**\n\n"
                "**Marathi:** मीठाचे प्रमाण कमी करा. नियमित व्यायाम करा. "
                "तणाव कमी करण्यासाठी ध्यान करा. दारू आणि सिगारेट टाळा. "
                "नियमितपणे रक्तदाब मोजा. डॉक्टरांनी सांगितलेली औषधे वेळेवर घ्या.\n"
                "**English:** Reduce salt, exercise regularly, manage stress. "
                "Monitor BP regularly. Take prescribed medicines on time.\n\n"
                f"{DISCLAIMER_MR}"
            )
        else:
            return (
                "❤️ **Blood Pressure / रक्तदाब**\n\n"
                "**English:** Reduce salt intake, exercise regularly, manage stress through meditation. "
                "Avoid alcohol and smoking. Monitor blood pressure regularly. "
                "Take prescribed antihypertensive medicines on time.\n"
                "**मराठी:** मीठ कमी करा, व्यायाम करा, ध्यान करा, नियमित रक्तदाब मोजा.\n\n"
                f"{DISCLAIMER_EN}"
            )

    # 1. Hospital Matcher
    hospital_kws = ["hospital", "clinic", "medical center", "hospitals", "route", "map", "location",
                    "रुग्णालय", "रुग्णालये", "दवाखाना", "क्लिनिक", "मार्ग", "नकाशा", "जवळचे"]
    if any(w in msg for w in hospital_kws):
        user_city = ctx.get("city", "Pune")
        user_lat = ctx.get("latitude")
        user_lng = ctx.get("longitude")
        try:
            user_lat = float(user_lat) if user_lat is not None else None
            user_lng = float(user_lng) if user_lng is not None else None
        except (ValueError, TypeError):
            user_lat = None
            user_lng = None

        from hospital_finder import find_hospitals, get_directions_url
        hospitals = find_hospitals(city=user_city, user_lat=user_lat, user_lng=user_lng)
        if not hospitals:
            hospitals = find_hospitals(city="Default")
            
        closest_hospitals = hospitals[:3]
        user_loc = {"lat": user_lat, "lng": user_lng} if (user_lat is not None and user_lng is not None) else None

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                hosp_data = []
                for h in closest_hospitals:
                    dir_url = get_directions_url(h, user_location=user_loc)
                    hosp_data.append({
                        "name": h.get("name"),
                        "address": h.get("address"),
                        "distance_km": round(h.get("distance", 0), 2),
                        "rating": h.get("rating"),
                        "beds": h.get("beds"),
                        "route_url": dir_url
                    })
                
                prompt = (
                    f"The user is looking for the nearest hospitals. User city is: {user_city}.\n"
                    f"Here is the list of nearest hospitals based on their location:\n"
                    f"{json.dumps(hosp_data, indent=2)}\n\n"
                    f"Please format this into a friendly, helpful guide for the user in BOTH English and Marathi (bilingual format, with clear sections for each language).\n"
                    f"For each hospital, include its name, distance (in km), rating, total beds, and a clickable Markdown link for the route using the provided `route_url` (with the text 'Click here for the nearest route on Map' in English, and 'नकाशावर सर्वात जवळचा मार्ग मिळवण्यासाठी येथे क्लिक करा' in Marathi).\n"
                    f"Add any helpful advice for the user (e.g., calling 108 in case of an emergency, checking bed availability).\n"
                    f"Always end with the medical disclaimer:\n"
                    f"English: **{DISCLAIMER_EN}**\n"
                    f"Marathi: **{DISCLAIMER_MR}**"
                )
                
                system_instruction = "You are a professional medical assistant guide for the HealthCare+ app. You format hospital locator outputs clearly in bilingual English and Marathi."
                ai_resp = call_gemini(prompt, system_instruction)
                if ai_resp:
                    return ai_resp
            except Exception as e:
                print(f"[GEMINI] Hospital formatting failed: {e}")

        # Fallback to local rule-based formatting
        en_hosp_list = []
        for h in closest_hospitals[:2]:
            dir_url = get_directions_url(h, user_location=user_loc)
            en_hosp_list.append(
                f"- **{h['name']}**\n"
                f"  - Address: {h['address']}\n"
                f"  - Distance: {round(h['distance'], 2)} km\n"
                f"  - Rating: {h['rating']}/5\n"
                f"  - Beds: {h['beds']} beds\n"
                f"  - Route: [Click here for the nearest route on Map]({dir_url})"
            )
        en_hosp_text = "\n".join(en_hosp_list)
        
        mr_hosp_list = []
        for h in closest_hospitals[:2]:
            dir_url = get_directions_url(h, user_location=user_loc)
            mr_hosp_list.append(
                f"- **{h['name']}**\n"
                f"  - पत्ता: {h['address']}\n"
                f"  - अंतर: {round(h['distance'], 2)} किमी\n"
                f"  - रेटिंग: {h['rating']}/5\n"
                f"  - बेड: {h['beds']} खाटा\n"
                f"  - मार्ग: [Click here for the nearest route on Map]({dir_url})"
            )
        mr_hosp_text = "\n".join(mr_hosp_list)
        
        return (
            f"🏥 **Nearest Hospitals & Routing / जवळची रुग्णालये आणि मार्ग**\n\n"
            f"**English:**\n"
            f"Here are the nearest hospitals based on your location ({user_city}):\n"
            f"{en_hosp_text}\n\n"
            f"**मराठी:**\n"
            f"तुमच्या स्थानानुसार ({user_city}) जवळील रुग्णालये खालीलप्रमाणे आहेत:\n"
            f"{mr_hosp_text}\n\n"
            f"{DISCLAIMER_EN}"
        )

    # 2. Health Score Matcher
    score_kws = ["health score", "my score", "what is my score", "check score", "check health score",
                 "आरोग्य स्कोअर", "माझा स्कोअर", "माझा आरोग्य स्कोअर"]
    if any(w in msg for w in score_kws):
        score = ctx.get("health_score", 100)
        return (
            f"📈 **Daily Health Score / दैनिक आरोग्य स्कोअर**\n\n"
            f"**English:**\n"
            f"Your daily health score today is **{score}/100**.\n"
            f"Excellent! Your medication adherence and dietary choices are outstanding today. Keep up the perfect work!\n\n"
            f"**मराठी:**\n"
            f"तुमचा आजचा दैनिक आरोग्य स्कोअर **{score}/100** आहे.\n"
            f"उत्कृष्ट! तुमचे औषधोपचार आणि आहाराचे पर्याय आज खूप छान आहेत. असेच उत्तम काम करत राहा!\n\n"
            f"{DISCLAIMER_EN}"
        )

    # 3. Daily Symptom Journal History Matcher
    journal_kws = ["symptom journal", "symptom history", "symptoms log", "journal history", "my history", "journal log",
                   "लक्षणे नोंद", "माझा इतिहास", "जर्नल इतिहास", "जर्नल"]
    if any(w in msg for w in journal_kws):
        user_id = ctx.get("user_id")
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "healthcare.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = []
        if user_id:
            rows = cur.execute("""
                SELECT log_date, mood, symptoms, severity FROM symptom_journal
                WHERE patient_id = ?
                ORDER BY log_date DESC
            """, (user_id,)).fetchall()
        conn.close()
        
        if not rows:
            return (
                f"📋 **Daily Symptom Journal / दैनिक लक्षण जर्नल**\n\n"
                f"**English:** No symptom records logged yet.\n"
                f"**मराठी:** अद्याप कोणतीही लक्षणांची नोंद केलेली नाही.\n\n"
                f"{DISCLAIMER_EN}"
            )
            
        en_logs = []
        mr_logs = []
        for r in rows:
            date_val = r['log_date']
            mood_val = r['mood']
            sym_val = r['symptoms']
            sev_val = r['severity']
            mood_emoji = "😃" if mood_val == 'happy' else "😐" if mood_val == 'okay' else "😴" if mood_val == 'tired' else "🤒"
            en_logs.append(f"- **{date_val}**: Mood: {mood_val.capitalize()} {mood_emoji} | Severity: {sev_val.capitalize()} | Symptoms: {sym_val}")
            mr_logs.append(f"- **{date_val}**: मनःस्थिती (Mood): {mood_val} {mood_emoji} | तीव्रता: {sev_val} | लक्षणे: {sym_val}")
            
        en_text = "\n".join(en_logs[:5])
        mr_text = "\n".join(mr_logs[:5])
        
        return (
            f"📋 **Symptom Journal History (Newest first) / लक्षण जर्नल इतिहास (नवीन आधी)**\n\n"
            f"**English:**\n"
            f"Here is your daily symptom journal history:\n"
            f"{en_text}\n\n"
            f"**मराठी:**\n"
            f"तुमचा दैनिक लक्षण जर्नलचा इतिहास खालीलप्रमाणे आहे:\n"
            f"{mr_text}\n\n"
            f"{DISCLAIMER_EN}"
        )

    # 4. Daily Wellness Matcher
    wellness_kws = ["wellness", "daily wellness", "hydration", "sleep", "exercise", "stress",
                    "कल्याण", "आरोग्य सल्ला", "पाणी पिणे", "झोप", "तणाव"]
    if any(w in msg for w in wellness_kws):
        user_id = ctx.get("user_id")
        from datetime import datetime
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "healthcare.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        wellness_log = None
        if user_id:
            today_str = datetime.now().strftime('%Y-%m-%d')
            wellness_log = cur.execute("""
                SELECT water_glasses, sleep_hours, steps, exercise_min FROM wellness_log
                WHERE patient_id = ? AND log_date = ?
            """, (user_id, today_str)).fetchone()
        conn.close()
        
        water = wellness_log['water_glasses'] if wellness_log else ctx.get("water_glasses", 0)
        sleep = wellness_log['sleep_hours'] if (wellness_log and wellness_log['sleep_hours'] is not None) else 0.0
        steps = wellness_log['steps'] if (wellness_log and wellness_log['steps'] is not None) else 0
        exercise = wellness_log['exercise_min'] if (wellness_log and wellness_log['exercise_min'] is not None) else 0
        
        return (
            f"🌱 **Daily Wellness Advice / दैनिक कल्याण सल्ला**\n\n"
            f"**English:**\n"
            f"Here is your tracked wellness activity today:\n"
            f"• Hydration: **{water} glasses** (Aim for 8-10 glasses)\n"
            f"• Sleep: **{sleep} hours** (Aim for 7-9 hours)\n"
            f"• Steps: **{steps} steps** (Aim for 8,000-10,000 steps)\n"
            f"• Exercise: **{exercise} minutes** (Aim for 30 minutes)\n\n"
            f"*Wellness Tips:*\n"
            f"1. **Hydration**: Drink a glass of water every 2 hours.\n"
            f"2. **Sleep**: Turn off screens at least 1 hour before sleeping.\n"
            f"3. **Stress**: Take 5 minutes for deep breathing when feeling stressed.\n"
            f"4. **Exercise**: Go for a quick 15-minute walk after lunch.\n\n"
            f"**मराठी:**\n"
            f"आजची तुमची नोंदवलेली निरोगीपणाची माहिती:\n"
            f"• पाणी पिणे: **{water} ग्लास** (८-१० ग्लासचे ध्येय ठेवा)\n"
            f"• झोप: **{sleep} तास** (७-९ तासांचे ध्येय ठेवा)\n"
            f"• पावले: **{steps} पावले** (८,०००-१०,००० पावलांचे ध्येय ठेवा)\n"
            f"• व्यायाम: **{exercise} मिनिटे** (३० मिनिटांचे ध्येय ठेवा)\n\n"
            f"*कल्याण टिप्स:*\n"
            f"१. **हायड्रेशन**: दर २ तासांनी एक ग्लास पाणी प्या.\n"
            f"२. **झोप**: झोपण्यापूर्वी किमान १ तास स्क्रीन बंद करा.\n"
            f"३. **तणाव**: तणाव जाणवल्यास ५ मिनिटे दीर्घ श्वास घ्या.\n"
            f"४. **व्यायाम**: दुपारच्या जेवणानंतर १५ मिनिटे हलके फिरा.\n\n"
            f"{DISCLAIMER_EN}"
        )

    # Default/Fallback
    if lang == 'mr':
        return (
            f"🤖 **नमस्कार! HealthCare+ एआय सहाय्यक**\n\n"
            f"मी लक्षणे, आहार, औषधे आणि आपत्कालीन परिस्थितीबाबत मदत करू शकतो. "
            f"आजचा तुमचा आरोग्य स्कोअर: **{ctx.get('health_score', 'N/A')}/100**.\n\n"
            "तुम्ही खालील प्रश्न विचारू शकता:\n"
            "• डोकेदुखी, ताप, खोकला, अंगदुखी, पोटदुखी\n"
            "• आहार योजना, वजन कमी करणे\n"
            "• औषध स्मरणपत्र\n"
            "• आपत्कालीन मदत (१०८)\n\n"
            f"{DISCLAIMER_MR}"
        )
    else:
        return (
            f"🤖 **Hello! HealthCare+ AI Assistant**\n\n"
            f"I can help with symptoms, diet, medicines, and emergencies. "
            f"Your health score today: **{ctx.get('health_score', 'N/A')}/100**.\n\n"
            "You can ask about:\n"
            "• Headache, fever, cough, cold, body ache, stomach pain\n"
            "• Diet plans, weight management\n"
            "• Medicine reminders\n"
            "• Emergency help (108)\n\n"
            f"{DISCLAIMER_EN}"
        )


def _try_api_chat(message, ctx):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            lang = ctx.get('lang', 'en')
            system_instruction = (
                "You are a professional AI health assistant for a platform called HealthCare+.\n"
                f"User Context: {json.dumps(ctx)}\n"
                "Guidelines:\n"
                "1. Respond friendly and professionally in the user's preferred language (e.g., 'mr' for Marathi, 'en' for English).\n"
                "2. If the user's language is 'mr' (Marathi), you MUST write the entire response strictly in clean, pure Marathi Devanagari script. "
                "Do NOT mix English and Marathi, do NOT use Latin characters, and do NOT use Hinglish or Latin-script transliterations. The output must be completely, 100% in Marathi. "
                "Write all terms, headings, and explanations in standard Marathi.\n"
                "3. If they ask about symptoms, diet, lifestyle, or general health issues, provide clear suggestions.\n"
                "4. ALWAYS append the official bold medical disclaimer at the end:\n"
                "   For English: **Medical Disclaimer: These are general OTC suggestions only. Consult a healthcare professional before taking any medication. This is NOT a substitute for professional medical diagnosis.**\n"
                "   For Marathi: **वैद्यकीय अस्वीकरण: या फक्त सामान्य ओटीसी (OTC) शिफारसी आहेत. कोणतेही औषध घेण्यापूर्वी वैद्यकीय व्यावसायिकाचा सल्ला घ्या. हे व्यावसायिक वैद्यकीय निदानासाठी पर्याय नाही.**\n"
            )
            prompt = f"User message: {message}\nProvide a response based on the guidelines."
            resp = call_gemini(prompt, system_instruction)
            if resp:
                # Ensure disclaimer is present
                disclaimer = DISCLAIMER_MR if lang == 'mr' else DISCLAIMER_EN
                bold_disclaimer = f"**{disclaimer.replace('**', '').replace('⚠️ ', '')}**"
                if bold_disclaimer not in resp and disclaimer not in resp:
                    resp += f"\n\n{bold_disclaimer}"
                return resp
        except Exception as e:
            print(f"[GEMINI] Chat API failed: {e}")

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import urllib.request, json
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": f"You are a helpful health assistant. User context: {ctx}. Always include medical disclaimer."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
            }).encode()
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass
    return None
