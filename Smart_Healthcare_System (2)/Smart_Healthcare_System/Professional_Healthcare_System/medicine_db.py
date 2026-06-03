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
