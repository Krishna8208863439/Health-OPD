# Real Medicine Database with actual pharmaceutical names
MEDICINE_DATABASE = {
    "Stomach Infection": {
        "LOW": [
            "Omeprazole 20mg (Prilosec)",
            "Ranitidine 150mg (Zantac)",
            "Probiotics (Lactobacillus)",
            "Oral Rehydration Solution (ORS)",
            "Loperamide 2mg (Imodium)"
        ],
        "MEDIUM": [
            "Ciprofloxacin 500mg",
            "Metronidazole 400mg (Flagyl)",
            "Omeprazole 40mg",
            "Ondansetron 4mg (Zofran)",
            "Oral Rehydration Solution (ORS)",
            "Probiotics (VSL#3)"
        ],
        "HIGH": [
            "IV Ciprofloxacin 400mg",
            "IV Metronidazole 500mg",
            "IV Pantoprazole 40mg",
            "IV Ondansetron 8mg",
            "IV Fluid Replacement",
            "Hospitalization Required"
        ]
    },
    "Pneumonia": {
        "LOW": [
            "Amoxicillin 500mg",
            "Azithromycin 250mg (Z-Pack)",
            "Acetaminophen 500mg (Tylenol)",
            "Guaifenesin 200mg (Mucinex)",
            "Rest and Hydration"
        ],
        "MEDIUM": [
            "Amoxicillin-Clavulanate 875mg (Augmentin)",
            "Levofloxacin 750mg (Levaquin)",
            "Prednisone 20mg",
            "Albuterol Inhaler",
            "Acetaminophen 650mg",
            "Oxygen Therapy if needed"
        ],
        "HIGH": [
            "IV Ceftriaxone 1g",
            "IV Azithromycin 500mg",
            "IV Methylprednisolone 40mg",
            "Oxygen Therapy",
            "ICU Monitoring",
            "Mechanical Ventilation if required"
        ]
    },
    "Common Cold": {
        "LOW": [
            "Acetaminophen 500mg (Tylenol)",
            "Pseudoephedrine 30mg (Sudafed)",
            "Dextromethorphan 15mg (Robitussin)",
            "Vitamin C 1000mg",
            "Zinc Lozenges",
            "Rest and Fluids"
        ],
        "MEDIUM": [
            "Ibuprofen 400mg (Advil)",
            "Phenylephrine 10mg",
            "Guaifenesin 400mg",
            "Chlorpheniramine 4mg",
            "Steam Inhalation"
        ],
        "HIGH": [
            "Consult Doctor",
            "Rule out Bacterial Infection",
            "Possible Antibiotic Coverage"
        ]
    },
    "Influenza": {
        "LOW": [
            "Oseltamivir 75mg (Tamiflu)",
            "Acetaminophen 650mg",
            "Ibuprofen 400mg",
            "Rest and Hydration",
            "Vitamin C"
        ],
        "MEDIUM": [
            "Oseltamivir 75mg twice daily",
            "Acetaminophen 1000mg",
            "Codeine Cough Syrup",
            "Electrolyte Solution",
            "Monitor for complications"
        ],
        "HIGH": [
            "IV Oseltamivir",
            "IV Fluids",
            "Oxygen Support",
            "Hospitalization",
            "ICU if respiratory distress"
        ]
    },
    "Bronchitis": {
        "LOW": [
            "Dextromethorphan 20mg",
            "Guaifenesin 400mg",
            "Ibuprofen 400mg",
            "Honey and Warm Water",
            "Steam Inhalation"
        ],
        "MEDIUM": [
            "Azithromycin 500mg",
            "Albuterol Inhaler",
            "Prednisone 20mg",
            "Codeine Cough Syrup",
            "Nebulization"
        ],
        "HIGH": [
            "IV Antibiotics",
            "Oxygen Therapy",
            "Bronchodilators",
            "Corticosteroids",
            "Hospitalization"
        ]
    },
    "Migraine": {
        "LOW": [
            "Ibuprofen 600mg",
            "Acetaminophen 1000mg",
            "Caffeine 100mg",
            "Rest in Dark Room",
            "Cold Compress"
        ],
        "MEDIUM": [
            "Sumatriptan 50mg (Imitrex)",
            "Naproxen 500mg",
            "Metoclopramide 10mg (Reglan)",
            "Magnesium 400mg",
            "Avoid Triggers"
        ],
        "HIGH": [
            "IV Sumatriptan",
            "IV Prochlorperazine",
            "IV Magnesium Sulfate",
            "IV Dexamethasone",
            "Emergency Care"
        ]
    },
    "Gastroenteritis": {
        "LOW": [
            "Oral Rehydration Solution",
            "Loperamide 2mg",
            "Probiotics",
            "Zinc Supplements",
            "BRAT Diet"
        ],
        "MEDIUM": [
            "Ciprofloxacin 500mg",
            "Ondansetron 8mg",
            "IV Fluids (Outpatient)",
            "Electrolyte Replacement",
            "Anti-spasmodics"
        ],
        "HIGH": [
            "IV Antibiotics",
            "IV Antiemetics",
            "IV Fluid Resuscitation",
            "Hospitalization",
            "Monitor Electrolytes"
        ]
    },
    "Hypertension": {
        "LOW": [
            "Lifestyle Modifications",
            "Low Sodium Diet",
            "Exercise",
            "Stress Management",
            "Monitor BP"
        ],
        "MEDIUM": [
            "Amlodipine 5mg (Norvasc)",
            "Lisinopril 10mg (Prinivil)",
            "Hydrochlorothiazide 12.5mg",
            "Low Sodium Diet",
            "Regular Monitoring"
        ],
        "HIGH": [
            "Amlodipine 10mg",
            "Lisinopril 20mg",
            "Metoprolol 50mg",
            "Emergency BP Control",
            "Cardiology Consultation"
        ]
    },
    "Diabetes": {
        "LOW": [
            "Metformin 500mg",
            "Diet Control",
            "Exercise",
            "Blood Sugar Monitoring",
            "Lifestyle Changes"
        ],
        "MEDIUM": [
            "Metformin 1000mg",
            "Glimepiride 2mg",
            "Insulin (if needed)",
            "Regular Monitoring",
            "Diabetic Diet"
        ],
        "HIGH": [
            "Insulin Therapy",
            "Metformin 2000mg",
            "Endocrinology Referral",
            "Continuous Monitoring",
            "Hospitalization if DKA"
        ]
    },
    "Asthma": {
        "LOW": [
            "Albuterol Inhaler PRN",
            "Montelukast 10mg (Singulair)",
            "Avoid Triggers",
            "Peak Flow Monitoring"
        ],
        "MEDIUM": [
            "Fluticasone Inhaler (Flovent)",
            "Albuterol Inhaler",
            "Prednisone 40mg",
            "Nebulization",
            "Pulmonology Follow-up"
        ],
        "HIGH": [
            "IV Methylprednisolone",
            "Continuous Nebulization",
            "Oxygen Therapy",
            "ICU Admission",
            "Mechanical Ventilation if needed"
        ]
    },
    "Acidity": {
        "LOW": [
            "Antacids Syrup (Digene, Gelusil)",
            "Ranitidine 150mg (Aciloc, Rantac)",
            "Famotidine 20mg (Pepcid)",
            "Avoid spicy/oily food",
            "Drink cold milk"
        ],
        "MEDIUM": [
            "Omeprazole 20mg (Omez)",
            "Pantoprazole 40mg (Pan-40)",
            "Esomeprazole 40mg (Nexium)",
            "Sucralfate Suspension (for mucosal coating)",
            "Consult gastroenterologist if persistent"
        ],
        "HIGH": [
            "IV Pantoprazole 40mg",
            "IV Rabeprazole 20mg",
            "Gastrointestinal Endoscopy (eval)",
            "Hospital observation if severe chest pain (rule out cardiac issues)"
        ]
    },
    "Allergic Side Effects": {
        "LOW": [
            "Cetirizine 10mg (Alerid, Zyrtec)",
            "Loratadine 10mg (Claritin)",
            "Calamine Lotion for skin rash",
            "Avoid suspected allergen"
        ],
        "MEDIUM": [
            "Fexofenadine 120mg (Allegra)",
            "Levocetirizine 5mg + Montelukast 10mg (Montair LC)",
            "Hydroxyzine 25mg (Atarax) for intense itching",
            "Short course of Prednisolone 5mg (Wysolone) if advised by doctor"
        ],
        "HIGH": [
            "Epinephrine Injection (EpiPen) for anaphylaxis",
            "IV Hydrocortisone 100mg",
            "IV Pheniramine Maleate (Avil)",
            "Oxygen support & emergency airway management",
            "Immediate Emergency Room (ER) visit"
        ]
    },
    "cold and cough": {
        "LOW": [
            "Paracetamol 500mg (Calpol, Crocin) for mild fever",
            "Dextromethorphan Syrup (Benadryl DR) for dry cough",
            "Vitamin C 500mg (Limcee)",
            "Warm saline gargles",
            "Steam inhalation"
        ],
        "MEDIUM": [
            "Ibuprofen 400mg (Brufen)",
            "Guaifenesin Syrup (Mucinex) for wet cough",
            "Chlorpheniramine + Phenylephrine (Decongestant)",
            "Steam inhalation with Eucalyptus oil",
            "Cetirizine 10mg for running nose"
        ],
        "HIGH": [
            "Rule out secondary bacterial infection",
            "Consult general physician",
            "Chest X-ray if cough persists > 2 weeks",
            "Possible Antibiotic course (e.g. Azithromycin) under medical supervision"
        ]
    },
    "Pneumonia or TB": {
        "LOW": [
            "Amoxicillin 500mg",
            "Azithromycin 250mg (Azee)",
            "Paracetamol 500mg for fever",
            "Warm fluids and bed rest"
        ],
        "MEDIUM": [
            "Amoxicillin-Clavulanate 625mg (Augmentin)",
            "Levofloxacin 500mg (Loxof)",
            "Sputum test for Acid-Fast Bacilli (AFB) to rule out TB",
            "Chest X-ray",
            "Pulmonology consultation"
        ],
        "HIGH": [
            "IV Ceftriaxone 1g + IV Azithromycin 500mg",
            "DOTS regimen (Anti-Tubercular Therapy) if TB is confirmed",
            "Oxygen support",
            "Hospitalization in respiratory isolation ward if TB suspected"
        ]
    },
    "Pneumonia or TB or COVID": {
        "LOW": [
            "Paracetamol 650mg (Dolo 650) for fever",
            "Vitamin C + Zinc supplements",
            "Azithromycin 500mg",
            "Pulse Oximeter monitoring (SpO2)",
            "Home isolation"
        ],
        "MEDIUM": [
            "Budesonide Inhaler (Budecort)",
            "Prednisolone 20mg (Wysolone) under medical guidance",
            "Chest HRCT Scan",
            "Sputum culture and RT-PCR/RAT for COVID-19",
            "Oxygen concentration monitoring"
        ],
        "HIGH": [
            "IV Remdesivir / IV Dexamethasone",
            "High Flow Nasal Oxygen (HFNO) or Ventilator support",
            "Anticoagulation therapy (Low Molecular Weight Heparin)",
            "ICU admission and continuous monitoring"
        ]
    },
    "Kidney Infection or Stone": {
        "LOW": [
            "Ciprofloxacin 500mg (Ciplox) for infection",
            "Tamsulosin 0.4mg (Urimax) to help pass stone",
            "Paracetamol 650mg for mild pain",
            "Drink 3-4 liters of water daily"
        ],
        "MEDIUM": [
            "Nitrofurantoin 100mg (Martifur) for UTI",
            "Tramadol 50mg or Diclofenac 50mg (Voveran) for renal colic pain",
            "Ultrasound (USG) of Abdomen and Pelvis (KUB)",
            "Urine Routine & Culture test"
        ],
        "HIGH": [
            "IV Ceftriaxone 1g or IV Piperacillin-Tazobactam",
            "IV Fluids for hydration",
            "IV Tramadol or IV Fentanyl for severe pain",
            "Urological intervention (Lithotripsy, DJ Stenting, or Surgery)",
            "Hospitalization"
        ]
    },
    "Dengue": {
        "LOW": [
            "Paracetamol 500mg/650mg (Dolo/Calpol) for fever & pain",
            "Oral Rehydration Solution (ORS)",
            "Avoid NSAIDs like Ibuprofen/Aspirin (increases bleeding risk!)",
            "Complete bed rest",
            "Daily platelet count monitoring"
        ],
        "MEDIUM": [
            "IV Fluid therapy to prevent plasma leakage",
            "Carica Papaya leaf extract tablets (Caripill)",
            "Monitor Hematocrit levels regularly",
            "Close clinical observation for warning signs (abdominal pain, vomiting)"
        ],
        "HIGH": [
            "Intravenous fluid resuscitation",
            "Platelet transfusion (if count falls below 10,000 or bleeding occurs)",
            "Blood transfusion (if severe bleeding)",
            "ICU monitoring for Dengue Shock Syndrome (DSS)"
        ]
    }
}

# Real Hospital Recommendations by Severity
HOSPITAL_DATABASE = {
    "LOW": [
        "Primary Care Clinic",
        "Community Health Center",
        "Urgent Care Center",
        "Family Medicine Clinic"
    ],
    "MEDIUM": [
        "City General Hospital",
        "Regional Medical Center",
        "Multi-Specialty Hospital",
        "University Hospital",
        "District Health Center"
    ],
    "HIGH": [
        "Tertiary Care Hospital - Emergency Department",
        "University Medical Center - ICU",
        "Trauma Center Level 1",
        "Specialized Super-Specialty Hospital",
        "Academic Medical Center"
    ]
}
