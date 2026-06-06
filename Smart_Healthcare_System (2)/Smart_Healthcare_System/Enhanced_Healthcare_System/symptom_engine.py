"""
Real Symptom Assessment Engine
Rule-based + weighted scoring system for accurate disease prediction.
Each disease has a definitive symptom profile with required/supporting symptoms.
"""

# ─────────────────────────────────────────────
# SYMPTOM MASTER LIST  (id → display name)
# ─────────────────────────────────────────────
SYMPTOMS = {
    # General
    "fever":              "Fever (temperature above 100°F / 38°C)",
    "high_fever":         "High Fever (above 103°F / 39.4°C)",
    "chills":             "Chills / Shivering",
    "fatigue":            "Fatigue / Weakness",
    "night_sweats":       "Night Sweats",
    "weight_loss":        "Unexplained Weight Loss",
    "loss_of_appetite":   "Loss of Appetite",

    # Head / Neuro
    "headache":           "Headache",
    "severe_headache":    "Severe / Throbbing Headache",
    "dizziness":          "Dizziness / Lightheadedness",
    "confusion":          "Confusion / Disorientation",
    "neck_stiffness":     "Neck Stiffness",
    "light_sensitivity":  "Sensitivity to Light",
    "nausea":             "Nausea",
    "vomiting":           "Vomiting",

    # Respiratory
    "runny_nose":         "Runny / Stuffy Nose",
    "sneezing":           "Sneezing",
    "sore_throat":        "Sore Throat",
    "dry_cough":          "Dry Cough",
    "productive_cough":   "Productive Cough (with phlegm/mucus)",
    "coughing_blood":     "Coughing up Blood",
    "breathing_difficulty": "Difficulty Breathing / Shortness of Breath",
    "wheezing":           "Wheezing",
    "chest_pain":         "Chest Pain / Tightness",
    "chest_tightness":    "Chest Tightness / Pressure",
    "loss_of_smell":      "Loss of Smell (Anosmia)",
    "loss_of_taste":      "Loss of Taste",
    "oxygen_low":         "Low Oxygen / Feeling of Suffocation",

    # Gastro
    "stomach_pain":       "Stomach / Abdominal Pain",
    "stomach_cramps":     "Stomach Cramps",
    "diarrhea":           "Diarrhea",
    "bloody_diarrhea":    "Bloody Diarrhea",
    "constipation":       "Constipation",
    "bloating":           "Bloating / Gas",
    "heartburn":          "Heartburn / Acid Reflux / Burning in chest",
    "indigestion":        "Indigestion",
    "belching":           "Frequent Belching / Burping",
    "jaundice":           "Jaundice (Yellow skin / eyes)",

    # Musculoskeletal
    "body_ache":          "Body Ache / Muscle Pain",
    "joint_pain":         "Joint Pain / Swelling",
    "back_pain":          "Back Pain (lower or upper)",
    "flank_pain":         "Flank Pain (side / kidney area)",
    "neck_pain":          "Neck / Shoulder Pain",
    "leg_pain":           "Leg / Calf Pain",
    "swollen_joints":     "Swollen Joints",

    # Skin
    "rash":               "Skin Rash / Hives",
    "itching":            "Itching (skin, eyes, nose)",
    "skin_redness":       "Skin Redness / Swelling",
    "rash_after_meds":    "Rash After Taking Medication",
    "bruising":           "Easy Bruising",
    "petechiae":          "Tiny Red/Purple Spots on Skin (Petechiae)",
    "swollen_face":       "Swollen Face / Eyes / Lips",

    # Urinary
    "frequent_urination": "Frequent Urination",
    "painful_urination":  "Painful / Burning Urination",
    "blood_in_urine":     "Blood in Urine",
    "cloudy_urine":       "Cloudy / Dark Urine",
    "reduced_urination":  "Reduced Urine Output",

    # Cardiovascular
    "palpitations":       "Heart Palpitations / Rapid Heartbeat",
    "swollen_feet":       "Swollen Feet / Ankles",
    "high_bp":            "High Blood Pressure",

    # Eyes / ENT
    "red_eyes":           "Red / Watery Eyes",
    "eye_pain":           "Eye Pain",
    "ear_pain":           "Ear Pain",
    "tinnitus":           "Ringing in Ears (Tinnitus)",
    "bleeding_gums":      "Bleeding Gums / Nose",

    # Endocrine / Metabolic
    "excessive_thirst":   "Excessive Thirst / Dry Mouth",
    "excessive_hunger":   "Excessive Hunger",
    "blurred_vision":     "Blurred Vision",
    "slow_healing":       "Slow Healing Wounds",
    "numbness":           "Numbness / Tingling in hands or feet",

    # Mental
    "anxiety":            "Anxiety / Restlessness",
    "insomnia":           "Insomnia / Sleep Problems",
}

SYMPTOM_GROUPS = [
    ("🌡️ General", [
        "fever","high_fever","chills","fatigue","night_sweats",
        "weight_loss","loss_of_appetite"
    ]),
    ("🧠 Head / Neurological", [
        "headache","severe_headache","dizziness","confusion",
        "neck_stiffness","light_sensitivity","nausea","vomiting"
    ]),
    ("🫁 Respiratory / Chest", [
        "runny_nose","sneezing","sore_throat","dry_cough","productive_cough",
        "coughing_blood","breathing_difficulty","wheezing","chest_pain",
        "chest_tightness","loss_of_smell","loss_of_taste","oxygen_low"
    ]),
    ("🍽️ Digestive / Stomach", [
        "stomach_pain","stomach_cramps","diarrhea","bloody_diarrhea",
        "constipation","bloating","heartburn","indigestion","belching","jaundice"
    ]),
    ("🦴 Muscles / Joints / Back", [
        "body_ache","joint_pain","back_pain","flank_pain",
        "neck_pain","leg_pain","swollen_joints"
    ]),
    ("🩺 Skin / Allergy", [
        "rash","itching","skin_redness","rash_after_meds","bruising",
        "petechiae","swollen_face"
    ]),
    ("💧 Urinary", [
        "frequent_urination","painful_urination","blood_in_urine",
        "cloudy_urine","reduced_urination"
    ]),
    ("❤️ Heart / Circulation", [
        "palpitations","swollen_feet","high_bp"
    ]),
    ("👁️ Eyes / ENT", [
        "red_eyes","eye_pain","ear_pain","tinnitus","bleeding_gums"
    ]),
    ("🔬 Metabolic / Diabetes", [
        "excessive_thirst","excessive_hunger","blurred_vision",
        "slow_healing","numbness"
    ]),
    ("😰 Other", [
        "anxiety","insomnia"
    ]),
]

# ─────────────────────────────────────────────
# DISEASE PROFILES
# Each disease has:
#   required   – at least ONE of these must be present
#   strong     – each present adds high weight (10)
#   moderate   – each present adds medium weight (5)
#   weak       – each present adds low weight (2)
#   against    – each present SUBTRACTS weight (strongly contradicts disease)
#   min_score  – minimum total score to even consider this disease
# ─────────────────────────────────────────────
DISEASE_PROFILES = {

    "Common Cold": {
        "required":  ["runny_nose", "sore_throat"],
        "strong":    ["runny_nose", "sneezing", "sore_throat"],
        "moderate":  ["dry_cough", "headache", "fatigue", "fever"],
        "weak":      ["body_ache", "loss_of_appetite"],
        "against":   ["breathing_difficulty", "chest_pain", "diarrhea", "rash",
                      "jaundice", "blood_in_urine", "high_fever"],
        "min_score": 20,
        "description": "A viral upper respiratory infection caused by rhinoviruses.",
    },

    "Influenza (Flu)": {
        "required":  ["fever"],
        "strong":    ["high_fever", "body_ache", "fatigue", "chills"],
        "moderate":  ["headache", "dry_cough", "sore_throat", "runny_nose", "vomiting"],
        "weak":      ["loss_of_appetite", "dizziness"],
        "against":   ["rash", "diarrhea", "jaundice", "blood_in_urine"],
        "min_score": 25,
        "description": "A contagious respiratory illness caused by influenza viruses.",
    },

    "COVID-19": {
        "required":  ["fever", "dry_cough"],
        "strong":    ["loss_of_smell", "loss_of_taste", "fever", "dry_cough",
                      "breathing_difficulty", "fatigue"],
        "moderate":  ["headache", "body_ache", "sore_throat", "chills",
                      "oxygen_low", "chest_tightness"],
        "weak":      ["diarrhea", "nausea", "vomiting", "runny_nose"],
        "against":   ["rash", "jaundice", "blood_in_urine"],
        "min_score": 30,
        "description": "Respiratory illness caused by SARS-CoV-2 virus.",
    },

    "Pneumonia": {
        "required":  ["productive_cough", "fever"],
        "strong":    ["productive_cough", "high_fever", "breathing_difficulty",
                      "chest_pain", "chills"],
        "moderate":  ["fatigue", "body_ache", "loss_of_appetite",
                      "oxygen_low", "chest_tightness"],
        "weak":      ["nausea", "vomiting", "headache"],
        "against":   ["runny_nose", "sneezing", "rash", "diarrhea", "loss_of_smell"],
        "min_score": 30,
        "description": "Lung infection causing fluid-filled air sacs, bacterial or viral.",
    },

    "Bronchitis": {
        "required":  ["productive_cough"],
        "strong":    ["productive_cough", "dry_cough", "chest_tightness", "wheezing"],
        "moderate":  ["fever", "fatigue", "sore_throat", "breathing_difficulty"],
        "weak":      ["headache", "body_ache", "runny_nose"],
        "against":   ["high_fever", "rash", "diarrhea", "flank_pain"],
        "min_score": 20,
        "description": "Inflammation of the bronchial tubes, usually after a respiratory infection.",
    },

    "Asthma": {
        "required":  ["wheezing", "breathing_difficulty"],
        "strong":    ["wheezing", "chest_tightness", "breathing_difficulty", "dry_cough"],
        "moderate":  ["anxiety", "fatigue", "oxygen_low"],
        "weak":      ["coughing_blood", "chest_pain"],
        "against":   ["fever", "diarrhea", "rash", "flank_pain"],
        "min_score": 25,
        "description": "Chronic inflammatory disease causing airway narrowing and breathing difficulty.",
    },

    "Tuberculosis (TB)": {
        "required":  ["productive_cough", "night_sweats"],
        "strong":    ["coughing_blood", "night_sweats", "weight_loss",
                      "productive_cough", "fever"],
        "moderate":  ["fatigue", "loss_of_appetite", "chest_pain", "breathing_difficulty"],
        "weak":      ["chills", "body_ache", "back_pain"],
        "against":   ["diarrhea", "rash", "runny_nose", "loss_of_smell"],
        "min_score": 30,
        "description": "Bacterial infection (Mycobacterium tuberculosis) primarily affecting lungs.",
    },

    "Dengue Fever": {
        "required":  ["fever", "body_ache"],
        "strong":    ["high_fever", "severe_headache", "joint_pain",
                      "petechiae", "body_ache"],
        "moderate":  ["rash", "vomiting", "nausea", "bleeding_gums",
                      "red_eyes", "fatigue"],
        "weak":      ["loss_of_appetite", "chills", "stomach_pain"],
        "against":   ["runny_nose", "sore_throat", "diarrhea", "productive_cough"],
        "min_score": 30,
        "description": "Mosquito-borne viral infection causing severe flu-like symptoms.",
    },

    "Malaria": {
        "required":  ["fever", "chills"],
        "strong":    ["fever", "chills", "high_fever", "body_ache",
                      "night_sweats", "vomiting"],
        "moderate":  ["headache", "fatigue", "nausea", "jaundice", "dizziness"],
        "weak":      ["back_pain", "loss_of_appetite"],
        "against":   ["rash", "runny_nose", "sore_throat", "diarrhea",
                      "loss_of_smell", "chest_pain"],
        "min_score": 30,
        "description": "Parasitic disease transmitted by Anopheles mosquitoes.",
    },

    "Typhoid Fever": {
        "required":  ["fever", "stomach_pain"],
        "strong":    ["high_fever", "stomach_pain", "constipation",
                      "loss_of_appetite", "fatigue"],
        "moderate":  ["headache", "vomiting", "rash", "body_ache",
                      "diarrhea", "chills"],
        "weak":      ["weight_loss", "jaundice", "confusion"],
        "against":   ["runny_nose", "sneezing", "coughing_blood",
                      "loss_of_smell", "rash_after_meds"],
        "min_score": 30,
        "description": "Bacterial infection (Salmonella typhi) spread through contaminated food/water.",
    },

    "Gastroenteritis (Stomach Flu)": {
        "required":  ["vomiting", "diarrhea"],
        "strong":    ["vomiting", "diarrhea", "stomach_cramps", "nausea"],
        "moderate":  ["fever", "stomach_pain", "fatigue", "body_ache"],
        "weak":      ["headache", "chills", "loss_of_appetite"],
        "against":   ["chest_pain", "rash", "coughing_blood",
                      "loss_of_smell", "breathing_difficulty"],
        "min_score": 25,
        "description": "Inflammation of the stomach and intestines, usually from viral or bacterial infection.",
    },

    "Food Poisoning": {
        "required":  ["vomiting", "nausea"],
        "strong":    ["vomiting", "nausea", "stomach_cramps", "diarrhea"],
        "moderate":  ["fever", "stomach_pain", "bloody_diarrhea"],
        "weak":      ["headache", "fatigue", "body_ache"],
        "against":   ["chest_pain", "rash", "loss_of_smell", "coughing_blood"],
        "min_score": 25,
        "description": "Illness caused by eating contaminated food with bacteria, viruses, or toxins.",
    },

    "Acid Reflux / GERD": {
        "required":  ["heartburn"],
        "strong":    ["heartburn", "indigestion", "belching", "bloating"],
        "moderate":  ["chest_pain", "nausea", "sore_throat", "dry_cough"],
        "weak":      ["vomiting", "stomach_pain"],
        "against":   ["fever", "rash", "diarrhea", "joint_pain",
                      "coughing_blood", "loss_of_smell"],
        "min_score": 20,
        "description": "Stomach acid frequently flows back into the esophagus causing irritation.",
    },

    "Urinary Tract Infection (UTI)": {
        "required":  ["painful_urination"],
        "strong":    ["painful_urination", "frequent_urination",
                      "cloudy_urine", "blood_in_urine"],
        "moderate":  ["fever", "back_pain", "fatigue",
                      "reduced_urination", "stomach_pain"],
        "weak":      ["nausea", "chills"],
        "against":   ["chest_pain", "rash", "diarrhea", "vomiting",
                      "loss_of_smell"],
        "min_score": 25,
        "description": "Bacterial infection in the urinary system (bladder, urethra, or kidneys).",
    },

    "Kidney Infection / Pyelonephritis": {
        "required":  ["flank_pain", "fever"],
        "strong":    ["flank_pain", "fever", "back_pain",
                      "painful_urination", "blood_in_urine"],
        "moderate":  ["high_fever", "chills", "nausea",
                      "vomiting", "cloudy_urine", "fatigue"],
        "weak":      ["frequent_urination", "reduced_urination"],
        "against":   ["rash", "chest_pain", "diarrhea", "loss_of_smell"],
        "min_score": 25,
        "description": "Bacterial infection that has reached the kidneys from the urinary tract.",
    },

    "Kidney Stones": {
        "required":  ["flank_pain"],
        "strong":    ["flank_pain", "blood_in_urine", "back_pain",
                      "painful_urination"],
        "moderate":  ["nausea", "vomiting", "stomach_pain",
                      "frequent_urination", "cloudy_urine"],
        "weak":      ["fever", "chills"],
        "against":   ["fever > mild", "rash", "diarrhea", "chest_pain",
                      "loss_of_smell"],
        "min_score": 25,
        "description": "Hard deposits of minerals and salts that form inside the kidneys.",
    },

    "Hypertension": {
        "required":  ["high_bp"],
        "strong":    ["high_bp", "severe_headache", "dizziness"],
        "moderate":  ["chest_pain", "palpitations", "blurred_vision",
                      "swollen_feet", "fatigue"],
        "weak":      ["nausea", "nosebleed"],
        "against":   ["fever", "rash", "diarrhea", "vomiting",
                      "loss_of_smell"],
        "min_score": 20,
        "description": "Chronically elevated blood pressure that can damage arteries and organs.",
    },

    "Diabetes": {
        "required":  ["excessive_thirst", "frequent_urination"],
        "strong":    ["excessive_thirst", "frequent_urination",
                      "excessive_hunger", "blurred_vision",
                      "fatigue", "slow_healing"],
        "moderate":  ["numbness", "weight_loss", "frequent_urination"],
        "weak":      ["nausea", "headache", "dizziness"],
        "against":   ["fever", "rash", "diarrhea", "chest_pain",
                      "loss_of_smell"],
        "min_score": 30,
        "description": "Metabolic disease causing high blood sugar due to insulin issues.",
    },

    "Migraine": {
        "required":  ["severe_headache"],
        "strong":    ["severe_headache", "nausea", "vomiting",
                      "light_sensitivity", "dizziness"],
        "moderate":  ["headache", "fatigue", "blurred_vision"],
        "weak":      ["neck_pain", "anxiety"],
        "against":   ["fever", "rash", "diarrhea", "chest_pain",
                      "loss_of_smell"],
        "min_score": 25,
        "description": "Neurological condition causing intense, debilitating headaches.",
    },

    "Allergic Reaction": {
        "required":  ["rash", "itching"],
        "strong":    ["rash", "itching", "sneezing", "runny_nose",
                      "swollen_face", "red_eyes"],
        "moderate":  ["skin_redness", "wheezing", "rash_after_meds",
                      "breathing_difficulty"],
        "weak":      ["nausea", "fatigue"],
        "against":   ["fever", "chest_pain", "diarrhea", "loss_of_smell",
                      "coughing_blood"],
        "min_score": 20,
        "description": "Immune system reaction to a foreign substance (allergen).",
    },

    "Malnutrition / Anemia": {
        "required":  ["fatigue", "dizziness"],
        "strong":    ["fatigue", "dizziness", "weight_loss",
                      "loss_of_appetite", "numbness"],
        "moderate":  ["headache", "chills", "insomnia",
                      "blurred_vision", "body_ache"],
        "weak":      ["nausea", "anxiety"],
        "against":   ["fever", "rash", "chest_pain", "diarrhea",
                      "loss_of_smell"],
        "min_score": 20,
        "description": "Deficiency of essential nutrients affecting body function.",
    },

    "Appendicitis": {
        "required":  ["stomach_pain"],
        "strong":    ["stomach_pain", "fever", "nausea",
                      "vomiting", "loss_of_appetite"],
        "moderate":  ["chills", "constipation", "diarrhea"],
        "weak":      ["back_pain", "fatigue"],
        "against":   ["chest_pain", "rash", "loss_of_smell", "coughing_blood",
                      "runny_nose"],
        "min_score": 25,
        "description": "Inflammation of the appendix, requiring urgent medical attention.",
    },
}

# ─────────────────────────────────────────────
# MEDICINE DATABASE (Real Indian + Generic brands)
# ─────────────────────────────────────────────
REAL_MEDICINES = {
    "Common Cold": {
        "PRIMARY": [
            "Paracetamol 500mg (Crocin, Calpol, Dolo-500) – for fever and body ache",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet) – for runny nose and sneezing",
            "Pseudoephedrine + Chlorpheniramine (Actifed, Sudafed) – nasal decongestant",
        ],
        "SECONDARY": [
            "Dextromethorphan Syrup (Benadryl DR, Robitussin DM) – for dry cough",
            "Vitamin C 500mg (Limcee, Celin) – immune support",
            "Zinc 20mg (Zincovit, Zinopin) – recovery support",
            "Nasal Saline Spray (Otrivin Saline, Nasivion Saline) – for blocked nose",
            "Menthol Lozenges (Strepsils, Vicks Medicated) – sore throat relief",
        ],
        "HOME_REMEDIES": [
            "Steam inhalation with 2–3 drops of Eucalyptus oil – twice daily",
            "Warm salt-water gargle – 3 times a day",
            "Honey + Ginger tea – 2 cups daily",
            "Adequate rest and 8–10 glasses of water daily",
        ],
        "WHEN_TO_SEE_DOCTOR": "If fever exceeds 102°F, symptoms worsen after 7 days, or severe chest pain develops.",
    },

    "Influenza (Flu)": {
        "PRIMARY": [
            "Oseltamivir 75mg (Tamiflu, Fluvir, Antiflu) – antiviral, start within 48 hrs",
            "Paracetamol 650mg (Crocin Advance, Dolo-650) – fever and body ache",
            "Ibuprofen 400mg (Brufen, Combiflam, Advil) – pain and inflammation",
        ],
        "SECONDARY": [
            "Cetirizine 10mg (Zyrtec, Alerid) – runny nose",
            "Ambroxol 30mg (Mucolite, Ambrodil) – loosen mucus",
            "Electrolyte sachets (Electral, ORS) – hydration",
            "Vitamin C 1000mg + Zinc (Zincovit-C) – immune boost",
        ],
        "HOME_REMEDIES": [
            "Complete bed rest for 5–7 days",
            "Warm fluids: soups, herbal teas, warm water",
            "Chicken soup – anti-inflammatory properties",
            "Steam inhalation twice daily",
        ],
        "WHEN_TO_SEE_DOCTOR": "If breathing becomes difficult, fever above 103°F for more than 3 days, or severe chest pain.",
    },

    "COVID-19": {
        "PRIMARY": [
            "Paracetamol 650mg (Dolo-650, Crocin Advance) – fever and pain relief",
            "Ivermectin 12mg (Ivecop, Ivermectol) – per doctor's advice only",
            "Favipiravir 800mg / 200mg (FabiFlu, Fabivir) – antiviral, doctor prescription required",
            "Pulse oximeter monitoring – keep SpO₂ above 94%",
        ],
        "SECONDARY": [
            "Zinc 50mg + Vitamin D3 60,000 IU – immune support",
            "Vitamin C 1000mg (Limcee) – daily",
            "Budesonide Inhaler (Budecort, Pulmicort) – if cough/wheeze",
            "Low Molecular Weight Heparin (Clexane) – if hospitalized, clot prevention",
            "Dexamethasone 6mg – only for severe cases under medical supervision",
        ],
        "HOME_REMEDIES": [
            "Home isolation, well-ventilated room",
            "Prone positioning (sleeping on stomach) – improves oxygen levels",
            "Warm salt water gargle and steam inhalation",
            "Turmeric milk (Haldi Doodh) – twice daily",
            "Kadha (herbal decoction): tulsi, ginger, black pepper, cinnamon",
        ],
        "WHEN_TO_SEE_DOCTOR": "IMMEDIATELY if SpO₂ drops below 93%, breathing rate > 24/min, persistent chest pain, or confusion.",
    },

    "Pneumonia": {
        "PRIMARY": [
            "Amoxicillin-Clavulanate 625mg (Augmentin, Clavam, Moxclav) – antibiotic",
            "Azithromycin 500mg (Azithral, Zithromax, Azee-500) – for atypical pneumonia",
            "Levofloxacin 750mg (Levoflox, Tavanic) – broad-spectrum antibiotic",
        ],
        "SECONDARY": [
            "Prednisolone 40mg (Wysolone, Omnacortil) – reduce inflammation",
            "Salbutamol inhaler (Asthalin, Ventolin) – if wheezing",
            "N-Acetylcysteine 600mg (Mucomyst, Fluimucil) – mucus clearance",
            "Oxygen therapy – if SpO₂ < 92%",
            "Paracetamol 650mg (Dolo-650) – fever control",
        ],
        "HOME_REMEDIES": [
            "Complete bed rest – no strenuous activity",
            "Breathing exercises and steam inhalation",
            "High fluid intake – at least 2.5L daily",
            "Avoid smoking and cold air",
        ],
        "WHEN_TO_SEE_DOCTOR": "URGENT – Pneumonia requires medical diagnosis and antibiotics. Visit immediately if breathing is labored.",
    },

    "Bronchitis": {
        "PRIMARY": [
            "Ambroxol 30mg (Mucolite, Ambrodil, Mucosolvan) – expectorant",
            "Salbutamol inhaler (Asthalin, Ventolin) – bronchodilator",
            "Azithromycin 500mg (Azithral, Azee) – if bacterial cause suspected",
        ],
        "SECONDARY": [
            "Guaifenesin syrup (Mucinex, Grilinctus) – expectorant",
            "Montelukast 10mg (Montair, Singulair) – airway inflammation",
            "Dextromethorphan (Benadryl DR) – cough suppression at night",
            "Paracetamol 500mg (Crocin) – for fever/ache",
        ],
        "HOME_REMEDIES": [
            "Steam inhalation with Vicks VapoRub – twice daily",
            "Honey + turmeric in warm water – morning",
            "Avoid smoking, dust, and cold air",
            "Humidifier in the room at night",
        ],
        "WHEN_TO_SEE_DOCTOR": "If cough lasts more than 3 weeks, coughing blood, or difficulty breathing at rest.",
    },

    "Asthma": {
        "PRIMARY": [
            "Salbutamol inhaler 100mcg (Asthalin, Ventolin, Airomir) – reliever, as needed",
            "Budesonide inhaler 200mcg (Budecort, Pulmicort) – controller, daily use",
            "Formoterol + Budesonide (Foracort 200, Symbicort) – combination",
        ],
        "SECONDARY": [
            "Montelukast 10mg (Montair, Singulair, Montek LC) – anti-inflammatory",
            "Prednisolone 40mg short course (Wysolone) – during flare-ups",
            "Ipratropium inhaler (Atrovent, Ipravent) – bronchodilator",
            "Nebulization with Duolin (Salbutamol + Ipratropium) – for attacks",
        ],
        "HOME_REMEDIES": [
            "Identify and avoid triggers (dust, pollen, cold air, smoke)",
            "Use peak flow meter to monitor lung function daily",
            "Breathing exercises: diaphragmatic and pursed-lip breathing",
            "Swimming is the best exercise for asthma patients",
        ],
        "WHEN_TO_SEE_DOCTOR": "IMMEDIATELY if reliever inhaler provides no relief, lips turn blue, or unable to speak in full sentences.",
    },

    "Tuberculosis (TB)": {
        "PRIMARY": [
            "DOTS Regimen (Directly Observed Treatment) – under government program",
            "Isoniazid 300mg (INH, Lycazid) – daily",
            "Rifampicin 600mg (Rifacin, R-Cin) – daily",
            "Pyrazinamide 1500mg (Pyzina, Pyrodase) – first 2 months",
            "Ethambutol 1200mg (Myambutol, Comb-4) – first 2 months",
        ],
        "SECONDARY": [
            "Pyridoxine (Vitamin B6) 40mg – to prevent INH neuropathy",
            "Hepatoprotective agents (Liv-52, Silymarin) – liver protection",
            "High-protein diet – eggs, meat, pulses, milk",
        ],
        "HOME_REMEDIES": [
            "NEVER skip doses – complete the full 6-month course",
            "Eat nutritious high-protein meals 3 times daily",
            "Good ventilation and sunlight in living area",
            "Wear mask to prevent spreading to family members",
        ],
        "WHEN_TO_SEE_DOCTOR": "MANDATORY – TB requires a full 6-month antibiotic course under medical supervision. Visit a DOTS center.",
    },

    "Dengue Fever": {
        "PRIMARY": [
            "Paracetamol 650mg (Dolo-650, Crocin Advance) – fever and pain ONLY",
            "⚠️ AVOID NSAIDs (Ibuprofen, Aspirin, Diclofenac) – increases bleeding risk",
            "Oral Rehydration Solution (Electral, ORS-WHO) – prevent dehydration",
        ],
        "SECONDARY": [
            "Carica Papaya leaf extract 1100mg (Caripill, PlatMax) – helps raise platelets",
            "Vitamin C 1000mg (Limcee) – daily",
            "Platelet transfusion – if platelets < 10,000 or active bleeding",
        ],
        "HOME_REMEDIES": [
            "Complete bed rest – avoid any physical exertion",
            "Papaya leaf juice – 30ml twice daily (raises platelets)",
            "Pomegranate juice – iron and platelet support",
            "Daily platelet count monitoring at lab",
            "Use mosquito nets and repellents",
        ],
        "WHEN_TO_SEE_DOCTOR": "URGENTLY if: platelets fall below 20,000, vomiting blood, bleeding gums/nose, severe abdominal pain, or restlessness.",
    },

    "Malaria": {
        "PRIMARY": [
            "Artemether + Lumefantrine (Coartem, AL) – first-line treatment",
            "Chloroquine 500mg (Lariago, Malarex) – for P. vivax malaria",
            "Primaquine 15mg (Malirid) – P. vivax radical cure (requires G6PD test)",
            "Artesunate injection – for severe falciparum malaria (hospital)",
        ],
        "SECONDARY": [
            "Paracetamol 650mg (Dolo-650) – fever control",
            "ORS (Electral) – hydration",
            "Folic acid 5mg – support recovery",
        ],
        "HOME_REMEDIES": [
            "Complete rest and warm fluids during fever phase",
            "Use mosquito nets (insecticide-treated) while sleeping",
            "Wear full-sleeve clothes at dusk and dawn",
            "Remove stagnant water around home",
        ],
        "WHEN_TO_SEE_DOCTOR": "URGENTLY – Malaria requires blood test confirmation and prescription treatment. Delay is dangerous.",
    },

    "Typhoid Fever": {
        "PRIMARY": [
            "Azithromycin 500mg × 7 days (Azithral, Zithromax) – first-line",
            "Cefixime 400mg × 14 days (Cefix, Zifi) – oral alternative",
            "Ciprofloxacin 500mg BD × 10 days (Ciplox, Cifran) – alternative",
        ],
        "SECONDARY": [
            "Paracetamol 650mg (Dolo-650) – fever control",
            "ORS (Electral) – hydration",
            "Ondansetron 4mg (Emeset, Zofran) – nausea/vomiting",
            "Probiotics (Econorm, Bifilac) – gut recovery after antibiotics",
        ],
        "HOME_REMEDIES": [
            "Boil and cool all drinking water",
            "Eat soft, easily digestible foods: khichdi, curd, banana",
            "Avoid raw fruits and vegetables during treatment",
            "Complete the full antibiotic course even if feeling better",
        ],
        "WHEN_TO_SEE_DOCTOR": "If fever persists beyond 5 days of treatment, severe stomach pain, or unconsciousness – emergency.",
    },

    "Gastroenteritis (Stomach Flu)": {
        "PRIMARY": [
            "ORS (WHO-ORS, Electral, Jeevani) – most important, prevent dehydration",
            "Ondansetron 4mg (Emeset, Zofran, Ondem) – stop vomiting",
            "Racecadotril 100mg (Hidrasec, Redotil) – reduce secretory diarrhea",
        ],
        "SECONDARY": [
            "Probiotics (Econorm sachets, Enterogermina) – gut flora restoration",
            "Zinc 20mg – especially in children, reduces diarrhea duration",
            "Domperidone 10mg (Domstal, Motilium) – nausea",
            "Loperamide 2mg (Imodium, Eldoper) – reduce diarrhea in adults only",
        ],
        "HOME_REMEDIES": [
            "BRAT diet: Banana, Rice, Apple, Toast – easy on the gut",
            "Sip ORS or coconut water every 15–20 minutes",
            "Avoid dairy, fatty and spicy foods until fully recovered",
            "Ginger tea – anti-nausea",
        ],
        "WHEN_TO_SEE_DOCTOR": "If unable to keep any fluid down for 24 hours, blood in stool/vomit, signs of dehydration (sunken eyes, no urine), or fever above 102°F.",
    },

    "Food Poisoning": {
        "PRIMARY": [
            "ORS (Electral, WHO-ORS) – immediate rehydration",
            "Ondansetron 4mg (Emeset, Zofran) – vomiting relief",
            "Activated Charcoal (Carbomix) – absorbs toxins, within first 2 hours",
        ],
        "SECONDARY": [
            "Ciprofloxacin 500mg (Ciplox) – if bacterial food poisoning suspected",
            "Metronidazole 400mg (Flagyl, Metrogyl) – for amoebic infections",
            "Probiotics (Econorm) – gut recovery",
            "Paracetamol 500mg – fever and pain",
        ],
        "HOME_REMEDIES": [
            "Stop eating for 2–3 hours to let stomach settle",
            "Small sips of ORS or clear broth every few minutes",
            "Ginger + honey tea – anti-nausea",
            "Cumin (jeera) water – digestive calming",
        ],
        "WHEN_TO_SEE_DOCTOR": "If bloody vomit or diarrhea, high fever, severe dehydration, neurological symptoms, or no improvement after 48 hours.",
    },

    "Acid Reflux / GERD": {
        "PRIMARY": [
            "Pantoprazole 40mg (Pan-40, Pantop, Protonix) – 30 min before meal",
            "Omeprazole 20mg (Omez, Prilosec) – morning empty stomach",
            "Rabeprazole 20mg (Razo, Aciphex) – proton pump inhibitor",
        ],
        "SECONDARY": [
            "Antacid suspension (Digene, Gelusil, Mucaine) – immediate relief",
            "Domperidone 10mg (Domstal) – gut motility",
            "Sucralfate 1g (Sucral, Carafate) – mucosal protection",
            "Famotidine 20mg (Pepcid, Famocid) – H2 blocker",
        ],
        "HOME_REMEDIES": [
            "Eat smaller, more frequent meals – avoid large meals",
            "Don't lie down for 2–3 hours after eating",
            "Elevate head of bed by 6–8 inches",
            "Cold milk or coconut water – immediate relief",
            "Avoid: coffee, tea, spicy food, alcohol, citrus, chocolate",
        ],
        "WHEN_TO_SEE_DOCTOR": "If symptoms persist more than 2 weeks, difficulty swallowing, weight loss, or vomiting blood.",
    },

    "Urinary Tract Infection (UTI)": {
        "PRIMARY": [
            "Nitrofurantoin 100mg (Macrobid, Martifur) × 5–7 days – first-line UTI",
            "Trimethoprim-Sulfamethoxazole (Bactrim, Septran) × 3 days",
            "Ciprofloxacin 500mg (Ciplox, Cifran) × 3–7 days",
        ],
        "SECONDARY": [
            "Phenazopyridine 200mg (Pyridium, Uristat) – pain/burning relief",
            "Cranberry extract tablets (Cran-Max) – prevent recurrence",
            "Probiotics (Lactobacillus) – restore normal flora",
        ],
        "HOME_REMEDIES": [
            "Drink 10–12 glasses of water daily to flush bacteria",
            "Cranberry juice (unsweetened) – 2 glasses daily",
            "Urinate immediately after sexual activity",
            "Wipe front to back – prevent contamination",
            "Avoid holding urine for long periods",
        ],
        "WHEN_TO_SEE_DOCTOR": "If fever develops, back/flank pain, blood in urine, or no improvement after 2–3 days of treatment.",
    },

    "Kidney Infection / Pyelonephritis": {
        "PRIMARY": [
            "Ciprofloxacin 500mg BD × 10–14 days (Ciplox, Cifran) – first-line",
            "Cefixime 400mg OD × 14 days (Cefix, Zifi) – oral option",
            "IV Ceftriaxone 1g (Monocef, Rocephin) – if hospitalized",
        ],
        "SECONDARY": [
            "Paracetamol 650mg (Dolo-650) – fever and pain",
            "IV Fluids (Normal Saline) – if vomiting or dehydrated",
            "Tramadol 50mg (Ultram, Tramazac) – for severe pain",
        ],
        "HOME_REMEDIES": [
            "Drink 3–4 liters of water daily",
            "Warm compress on flank/back – pain relief",
            "Complete the full antibiotic course",
            "Avoid caffeinated drinks and alcohol",
        ],
        "WHEN_TO_SEE_DOCTOR": "URGENTLY – Kidney infection is serious. If high fever with chills, vomiting, or back pain – go to emergency.",
    },

    "Kidney Stones": {
        "PRIMARY": [
            "Tamsulosin 0.4mg (Urimax, Flomax) – relaxes ureter, helps stone pass",
            "Diclofenac 75mg (Voveran, Voltaren) – severe pain (colic)",
            "Tramadol 50mg (Ultram, Tramazac) – for severe renal colic",
        ],
        "SECONDARY": [
            "Potassium Citrate (Uralyt-U) – alkalinizes urine, prevents stone growth",
            "Alpha-blockers (Tamsulosin) – facilitate stone passage",
            "ESWL (lithotripsy) or ureteroscopy – if stone >5mm or not passing",
        ],
        "HOME_REMEDIES": [
            "Drink 3–4 liters of water daily – the best prevention",
            "Lemon juice (citric acid) in water – 2 glasses daily",
            "Reduce salt intake (<2300mg sodium/day)",
            "Limit animal protein and oxalate-rich foods (spinach, nuts)",
        ],
        "WHEN_TO_SEE_DOCTOR": "URGENTLY if: unbearable pain, fever with chills, blood in urine, or inability to urinate.",
    },

    "Hypertension": {
        "PRIMARY": [
            "Amlodipine 5mg (Amlong, Norvasc, Amlip) – calcium channel blocker",
            "Telmisartan 40mg (Telma, Telsartan, Micardis) – ARB",
            "Losartan 50mg (Cozaar, Losar, Repace) – ARB",
        ],
        "SECONDARY": [
            "Metoprolol 50mg (Betaloc, Lopressor, Seloken) – beta-blocker",
            "Hydrochlorothiazide 12.5mg (HCTZ, Aquazide) – diuretic",
            "Combination: Telmisartan 40 + Amlodipine 5mg (Telma-AM) – for better control",
        ],
        "HOME_REMEDIES": [
            "DASH diet: low sodium (<2g/day), high potassium",
            "Exercise 30 minutes daily (brisk walk)",
            "Reduce stress: yoga, meditation",
            "No smoking; limit alcohol",
            "Monitor BP twice daily and maintain a log",
        ],
        "WHEN_TO_SEE_DOCTOR": "If BP > 180/110, severe headache, chest pain, vision changes, or confusion – emergency immediately.",
    },

    "Diabetes": {
        "PRIMARY": [
            "Metformin 500mg–2000mg (Glycomet, Glucophage, Obimet) – first-line T2DM",
            "Glimepiride 1–2mg (Amaryl, Glimer, Glimpid) – sulfonylurea",
            "Insulin (Mixtard 30/70, Lantus, Humalog) – if oral medicines insufficient",
        ],
        "SECONDARY": [
            "Sitagliptin 100mg (Januvia, Zita) – DPP-4 inhibitor",
            "Empagliflozin 10mg (Jardiance, Empaglyn) – SGLT-2 inhibitor",
            "Vildagliptin 50mg (Galvus, Zomelis) – DPP-4 inhibitor",
            "Metformin + Sitagliptin (Janumet, Kombiglyze) – combination",
        ],
        "HOME_REMEDIES": [
            "Diabetic diet: low glycemic index foods, avoid sugar/refined carbs",
            "Exercise 45 min daily (brisk walk, swimming) – lowers blood sugar",
            "Fenugreek seeds soaked overnight – reduces blood sugar",
            "Bitter gourd (karela) juice – 30ml morning empty stomach",
            "Monitor blood sugar (fasting + post-meal) daily",
        ],
        "WHEN_TO_SEE_DOCTOR": "If blood sugar > 300mg/dL, nausea/vomiting with high sugar, fruity breath, or confusion – emergency.",
    },

    "Migraine": {
        "PRIMARY": [
            "Sumatriptan 50mg (Suminat, Imitrex, Imigran) – triptan, take at onset",
            "Rizatriptan 10mg (Maxalt, Rizact) – fast-dissolving triptan",
            "Naproxen 500mg + Sumatriptan (Treximet) – combination",
        ],
        "SECONDARY": [
            "Propranolol 40mg (Inderal, Ciplar) – daily preventive",
            "Topiramate 25mg (Topamax, Epitomax) – preventive",
            "Amitriptyline 10mg (Tryptomer, Elavil) – preventive at night",
            "Metoclopramide 10mg (Perinorm, Reglan) – nausea during attack",
        ],
        "HOME_REMEDIES": [
            "Rest in a dark, quiet room immediately at onset",
            "Cold ice pack on forehead and back of neck",
            "Peppermint oil applied to temples",
            "Identify and avoid triggers: bright light, stress, certain foods",
            "Stay hydrated – dehydration is a common trigger",
        ],
        "WHEN_TO_SEE_DOCTOR": "If worst headache of your life (thunderclap), headache with fever/stiff neck, confusion, or neurological symptoms – emergency.",
    },

    "Allergic Reaction": {
        "PRIMARY": [
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet) – non-drowsy antihistamine",
            "Levocetirizine 5mg (L-Cetiz, Levorid) – more potent",
            "Fexofenadine 180mg (Allegra, Fexidine) – for chronic allergy",
        ],
        "SECONDARY": [
            "Montelukast 10mg + Levocetirizine 5mg (Montair-LC) – combo for allergic rhinitis",
            "Prednisolone 20mg short course (Wysolone) – if severe",
            "Adrenaline auto-injector (EpiPen) – only for anaphylaxis",
            "Calamine lotion – skin rash/itching topical relief",
        ],
        "HOME_REMEDIES": [
            "Identify and strictly avoid the allergen",
            "Cool water compresses – skin rash relief",
            "Aloe vera gel – soothe skin inflammation",
            "Turmeric milk – anti-inflammatory",
            "Wear a medical bracelet if you have severe allergies",
        ],
        "WHEN_TO_SEE_DOCTOR": "IMMEDIATELY if: throat swelling, difficulty breathing, lips/face swelling, dizziness, or drop in blood pressure (anaphylaxis).",
    },

    "Malnutrition / Anemia": {
        "PRIMARY": [
            "Ferrous Sulfate 325mg (Fersolate, Fero-Grad) – iron deficiency anemia",
            "Vitamin B12 1500mcg (Cobalamin, Methylcobalamin, Cobadex-CZS)",
            "Folic Acid 5mg (Folvite) – folate deficiency",
        ],
        "SECONDARY": [
            "Multivitamin + Multimineral (Supradyn, Revital, Becosules)",
            "Protein supplements (whey protein, Protinex) – malnutrition",
            "Vitamin D3 60,000 IU weekly (Calcirol, Uprise-D3) – if deficient",
        ],
        "HOME_REMEDIES": [
            "Iron-rich foods: spinach, jaggery, dates, pomegranate, red meat",
            "Vitamin C with iron-rich meals – improves absorption",
            "Beetroot juice – natural hemoglobin booster",
            "Soaked almonds + raisins + dates daily",
            "High-protein diet: eggs, lentils, milk, fish",
        ],
        "WHEN_TO_SEE_DOCTOR": "If extreme fatigue, pale skin, breathlessness, rapid heartbeat, or fainting – check CBC blood test urgently.",
    },

    "Appendicitis": {
        "PRIMARY": [
            "⚠️ APPENDICITIS IS A SURGICAL EMERGENCY – do not delay",
            "Appendectomy (laparoscopic or open surgery) – definitive treatment",
            "IV Ceftriaxone + Metronidazole – pre-operative antibiotics",
        ],
        "SECONDARY": [
            "IV Paracetamol (Perfalgan) – pain control pre-surgery",
            "IV Fluids – hydration before surgery",
            "NPO (Nothing by Mouth) after diagnosis",
        ],
        "HOME_REMEDIES": [
            "⚠️ DO NOT apply heat pad to abdomen",
            "⚠️ DO NOT take laxatives or enemas",
            "⚠️ DO NOT delay going to hospital",
            "Go to emergency room immediately",
        ],
        "WHEN_TO_SEE_DOCTOR": "EMERGENCY – Go to hospital immediately. Delay can cause rupture, which is life-threatening.",
    },
}

# ─────────────────────────────────────────────
# CORE ASSESSMENT ENGINE
# ─────────────────────────────────────────────
def assess_symptoms(present_symptoms: list) -> list:
    """
    Given a list of symptom IDs that the patient has,
    return a ranked list of (disease_name, score, confidence_pct, match_details).
    """
    present_set = set(present_symptoms)
    results = []

    for disease, profile in DISEASE_PROFILES.items():
        # Check required symptoms
        required = profile.get("required", [])
        if required and not any(s in present_set for s in required):
            continue  # Disease ruled out – no required symptom present

        score = 0
        matched_strong   = []
        matched_moderate = []
        matched_weak     = []

        # Count and score required symptoms that are not already scored
        for s in required:
            if s in present_set:
                if s not in profile.get("strong", []) and s not in profile.get("moderate", []) and s not in profile.get("weak", []):
                    score += 10

        for s in profile.get("strong", []):
            if s in present_set:
                score += 10
                matched_strong.append(s)

        for s in profile.get("moderate", []):
            if s in present_set:
                score += 5
                matched_moderate.append(s)

        for s in profile.get("weak", []):
            if s in present_set:
                score += 2
                matched_weak.append(s)

        for s in profile.get("against", []):
            if s in present_set:
                score -= 8

        # Skip if below minimum threshold (scaled down dynamically to allow matching on few symptoms)
        min_s = profile.get("min_score", 20)
        min_threshold = max(5, int(min_s * 0.4))
        if score < min_threshold:
            continue

        results.append({
            "disease":          disease,
            "score":            score,
            "matched_strong":   matched_strong,
            "matched_moderate": matched_moderate,
            "matched_weak":     matched_weak,
            "description":      profile.get("description", ""),
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Normalise to confidence percentage (top score = 100%)
    if results:
        top_score = results[0]["score"]
        for r in results:
            r["confidence_pct"] = min(99, round((r["score"] / max(top_score, 1)) * 100))

    return results[:5]  # Return top 5 candidates


def get_severity(confidence_pct: int, disease: str) -> str:
    """Return severity string based on confidence and disease type."""
    critical_diseases = {"Appendicitis", "COVID-19", "Pneumonia", "Tuberculosis (TB)",
                         "Malaria", "Kidney Infection / Pyelonephritis",
                         "Dengue Fever", "Typhoid Fever"}
    if disease in critical_diseases or confidence_pct >= 75:
        return "HIGH 🔴"
    elif confidence_pct >= 50:
        return "MEDIUM 🟡"
    else:
        return "LOW 🟢"


def get_medicines_for_disease(disease: str, severity: str) -> dict:
    """Return medicine info dict for a given disease."""
    meds = REAL_MEDICINES.get(disease)
    if not meds:
        # Fuzzy match
        for key in REAL_MEDICINES:
            if disease.lower() in key.lower() or key.lower() in disease.lower():
                meds = REAL_MEDICINES[key]
                break
    if not meds:
        meds = {
            "PRIMARY":   ["Consult a doctor for prescription medicines"],
            "SECONDARY": ["Paracetamol 500mg for fever/pain as needed"],
            "HOME_REMEDIES": ["Rest, hydration, and healthy diet"],
            "WHEN_TO_SEE_DOCTOR": "If symptoms persist for more than 3 days.",
        }
    return meds
