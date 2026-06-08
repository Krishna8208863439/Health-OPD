"""
AI Health Service – natural-language symptom parsing, OTC suggestions,
personalized diet plans, and health chat assistant.
Uses rule-based intelligence with optional OpenAI/Gemini if API keys are set.
"""

import os
import re
from symptom_engine import assess_symptoms, get_severity, get_medicines_for_disease, SYMPTOMS

# ── Natural language → symptom ID keyword map ──
NLP_KEYWORDS = {
    "headache": ["headache", "head ache", "head pain", "migraine", "throbbing head"],
    "severe_headache": ["severe headache", "worst headache", "thunderclap"],
    "fever": ["fever", "temperature", "hot body", "feeling hot"],
    "high_fever": ["high fever", "very high temperature", "103"],
    "fatigue": ["fatigue", "tired", "tiredness", "weakness", "exhausted", "low energy"],
    "nausea": ["nausea", "nauseous", "feel sick", "queasy"],
    "vomiting": ["vomiting", "throwing up", "vomit"],
    "dry_cough": ["dry cough", "coughing dry"],
    "productive_cough": ["productive cough", "cough with phlegm", "cough with mucus"],
    "sore_throat": ["sore throat", "throat pain", "throat hurts"],
    "runny_nose": ["runny nose", "stuffy nose", "blocked nose", "nasal congestion"],
    "breathing_difficulty": ["breathless", "breathing difficulty", "shortness of breath", "can't breathe", "difficulty breathing"],
    "chest_pain": ["chest pain", "chest tightness", "chest hurts"],
    "stomach_pain": ["stomach pain", "stomach ache", "abdominal pain", "belly pain", "tummy pain"],
    "diarrhea": ["diarrhea", "loose motion", "loose stools", "watery stool"],
    "constipation": ["constipation", "can't pass stool"],
    "body_ache": ["body ache", "body pain", "muscle pain", "body hurts"],
    "joint_pain": ["joint pain", "knee pain", "joint swelling"],
    "back_pain": ["back pain", "lower back pain"],
    "dizziness": ["dizzy", "dizziness", "lightheaded", "vertigo"],
    "rash": ["rash", "skin rash", "hives", "itchy skin"],
    "anxiety": ["anxiety", "anxious", "panic", "worried", "stressed"],
    "insomnia": ["insomnia", "can't sleep", "sleep problems"],
    "frequent_urination": ["frequent urination", "urinating often", "peeing a lot"],
    "painful_urination": ["painful urination", "burning urine", "burning when peeing"],
    "blurred_vision": ["blurred vision", "blurry eyes", "vision problems"],
    "palpitations": ["palpitations", "heart racing", "fast heartbeat"],
    "loss_of_appetite": ["loss of appetite", "not hungry", "no appetite"],
    "chills": ["chills", "shivering", "shaking"],
    "wheezing": ["wheezing", "wheeze"],
    "heartburn": ["heartburn", "acid reflux", "burning chest"],
    "swollen_feet": ["swollen feet", "swollen ankles", "leg swelling"],
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
]

EMERGENCY_SYMPTOMS = {
    "chest_pain", "breathing_difficulty", "oxygen_low", "coughing_blood",
    "confusion", "severe_headache", "neck_stiffness", "bloody_diarrhea",
    "blood_in_urine", "swollen_face", "petechiae",
}

# ── OTC Medicine Database ──
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


def parse_natural_language(text: str) -> list:
    """Extract symptom IDs from free-text description."""
    if not text:
        return []
    text_lower = text.lower().strip()
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
    age = int(profile.get("age", 30))
    gender = profile.get("gender", "male")
    height = float(profile.get("height", 170))
    weight = float(profile.get("weight", 70))
    activity = profile.get("activity_level", "moderate")
    conditions = profile.get("medical_conditions", "")
    preference = profile.get("dietary_preference", "vegetarian")
    goal = profile.get("diet_goal", "Balanced")

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

    # Try OpenAI/Gemini if keys available
    api_response = _try_api_chat(message, ctx)
    if api_response:
        return api_response

    if any(w in msg for w in ["headache", "head pain", "migraine"]):
        return (
            "For headaches, rest in a quiet dark room and stay hydrated. "
            "OTC Paracetamol 500mg or Ibuprofen 200mg may help. "
            "Seek emergency care if sudden severe headache, vision changes, or neck stiffness. "
            f"{DISCLAIMER}"
        )
    if any(w in msg for w in ["fever", "temperature"]):
        return (
            "For fever: rest, drink plenty of fluids, and take Paracetamol 500mg every 4–6 hours. "
            "Monitor temperature. See a doctor if fever >103°F persists beyond 3 days. "
            f"{DISCLAIMER}"
        )
    if any(w in msg for w in ["diet", "food", "meal", "eat"]):
        goal = ctx.get("diet_goal", "Balanced")
        return (
            f"Based on your active diet goal ({goal}), focus on balanced meals with adequate protein, "
            "complex carbs, and vegetables. Visit the Diet Plans page for personalized meal plans. "
            "Use the Food Scanner to check if meals align with your goal."
        )
    if any(w in msg for w in ["medicine", "medication", "pill", "reminder", "alarm"]):
        return (
            "Set medicine reminders in the Meds section with name, dosage, and time. "
            "Enable notifications for alarms even when the app is closed. "
            "Always follow your doctor's prescription."
        )
    if any(w in msg for w in ["emergency", "sos", "ambulance", "108"]):
        return (
            "🚨 Emergency: Call 108 (Ambulance), 112 (ERSS), or 100 (Police). "
            "Use the SOS page for ambulance simulation and nearest hospital locator. "
            "Go to Emergency page for first aid guidelines."
        )
    if any(w in msg for w in ["water", "hydrat"]):
        glasses = ctx.get("water_glasses", 0)
        return f"You've logged {glasses} glasses today. Aim for 8–10 glasses (2–2.5 litres). Track water in Daily Wellness."
    if any(w in msg for w in ["sleep", "insomnia"]):
        return "Adults need 7–9 hours of sleep. Avoid screens 1 hour before bed. Track sleep in Daily Wellness."
    if any(w in msg for w in ["exercise", "fitness", "workout"]):
        return "Aim for 150 minutes of moderate exercise per week. Visit Fitness Coaching for personalized workout plans."

    return (
        f"Hello! I'm your HealthCare+ AI Assistant. I can help with symptoms, diet, medicines, and emergencies. "
        f"Your health score today: {ctx.get('health_score', 'N/A')}/100. "
        f"Try asking about headaches, diet plans, medicine reminders, or emergency help. {DISCLAIMER}"
    )


def _try_api_chat(message, ctx):
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
