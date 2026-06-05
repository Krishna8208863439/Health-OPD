"""
Real medicine names and hospital recommendations database
"""

# Real Medicine Database with Indian pharmaceutical names and brands
MEDICINE_DATABASE = {
    "Stomach Infection": {
        "LOW": [
            "Omeprazole 20mg (Omez, Prilosec, Omez-D)",
            "Ranitidine 150mg (Aciloc, Rantac, Zinetac)",
            "Probiotics (Econorm, VSL#3, Bifilac, Sporlac)",
            "ORS - Oral Rehydration Solution (Electral, Jeevani)",
            "Loperamide 2mg (Eldoper, Imodium, Lopamide)",
            "Domperidone 10mg (Domstal, Motilium, Vomistop)",
            "Pantoprazole 20mg (Pantop, Protonix, Pan-D)",
            "Simethicone 40mg (Gas-X, Digene, Gelusil)",
            "Bismuth Subsalicylate (Pepto-Bismol, Pepsamar)"
        ],
        "MEDIUM": [
            "Ciprofloxacin 500mg (Ciplox, Cifran, Ciprobay)",
            "Metronidazole 400mg (Flagyl, Metrogyl, Metronid)",
            "Omeprazole 40mg (Omez, Prilosec, Omez-D)",
            "Ondansetron 4mg (Emeset, Zofran, Ondem)",
            "ORS - Frequent intake (Electral, Jeevani)",
            "Probiotics (Econorm, Enterogermina, Bifilac)",
            "Norfloxacin 400mg (Norflox, Norbactin, Noroxin)",
            "Tinidazole 500mg (Fasigyn, Tindamax, Tiniba)",
            "Racecadotril 100mg (Hidrasec, Redotil)"
        ],
        "HIGH": [
            "IV Ciprofloxacin 400mg (Ciplox IV)",
            "IV Metronidazole 500mg (Flagyl IV)",
            "IV Pantoprazole 40mg (Pantop IV, Protonix IV)",
            "IV Ondansetron 8mg (Emeset IV, Zofran IV)",
            "IV Fluid Replacement (Normal Saline, Ringer's Lactate)",
            "IV Ceftriaxone 1g (Monocef, Rocephin)",
            "Hospitalization Required"
        ]
    },
    "Pneumonia": {
        "LOW": [
            "Amoxicillin 500mg (Novamox, Amoxil, Moxikind)",
            "Azithromycin 250mg (Azithral, Zithromax, Azee)",
            "Paracetamol 500mg (Crocin, Dolo, Calpol)",
            "Guaifenesin 200mg (Benadryl Expectorant, Grilinctus)",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet)",
            "Steam inhalation with Vicks VapoRub",
            "Ambroxol 30mg (Mucolite, Ambrodil, Mucosolvan)",
            "Dextromethorphan 15mg (Benadryl DR, Robitussin)",
            "Vitamin C 1000mg (Limcee, Celin, Redoxon)",
            "Rest and Hydration"
        ],
        "MEDIUM": [
            "Amoxicillin-Clavulanate 875mg (Augmentin, Clavam, Moxclav)",
            "Levofloxacin 750mg (Levaquin, Levoflox, Tavanic)",
            "Prednisolone 20mg (Wysolone, Omnacortil, Predmet)",
            "Salbutamol Inhaler (Asthalin, Ventolin, Airomir)",
            "Paracetamol 650mg (Crocin Advance, Dolo 650)",
            "Clarithromycin 500mg (Klacid, Biaxin, Claribid)",
            "Montelukast 10mg (Montair, Singulair, Montek)",
            "N-Acetylcysteine 600mg (Mucomyst, Fluimucil)",
            "Oxygen Therapy if needed"
        ],
        "HIGH": [
            "IV Ceftriaxone 1g (Monocef, Rocephin, Intacef)",
            "IV Azithromycin 500mg (Azithral IV, Zithromax IV)",
            "IV Methylprednisolone 40mg (Solu-Medrol, Medrol)",
            "IV Levofloxacin 750mg (Levoflox IV, Tavanic IV)",
            "Oxygen Therapy with BiPAP/CPAP",
            "ICU Monitoring",
            "Mechanical Ventilation if required",
            "IV Piperacillin-Tazobactam (Tazact, Zosyn)"
        ]
    },
    "Common Cold": {
        "LOW": [
            "Paracetamol 500mg (Crocin, Dolo, Calpol)",
            "Pseudoephedrine 30mg (Sudafed, Actifed)",
            "Dextromethorphan 15mg (Benadryl DR, Robitussin DM)",
            "Vitamin C 1000mg (Limcee, Celin, Redoxon)",
            "Zinc Lozenges (Zincovit, Cold-Eeze, Halls)",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet)",
            "Loratadine 10mg (Claritin, Lorfast, Lorano)",
            "Menthol Lozenges (Strepsils, Vicks, Halls)",
            "Saline Nasal Spray (Nasivion, Otrivin)",
            "Honey and Ginger Tea"
        ],
        "MEDIUM": [
            "Ibuprofen 400mg (Brufen, Combiflam, Advil)",
            "Phenylephrine 10mg (Sudafed PE, Nasivion)",
            "Guaifenesin 400mg (Mucinex, Grilinctus)",
            "Chlorpheniramine 4mg (Avil, Chlor-Trimeton)",
            "Diphenhydramine 25mg (Benadryl, Allerdryl)",
            "Acetaminophen + Phenylephrine (Tylenol Cold)",
            "Steam Inhalation with Vicks VapoRub",
            "Throat Lozenges (Strepsils, Tyrozets)",
            "Nasal Decongestant (Otrivin, Nasivion)"
        ],
        "HIGH": [
            "Consult Doctor for Complications",
            "Rule out Bacterial Infection",
            "Possible Antibiotic Coverage (Azithromycin)",
            "Chest X-ray if needed",
            "Complete Blood Count (CBC)",
            "Throat Culture if Strep suspected"
        ]
    },
    "Influenza": {
        "LOW": [
            "Oseltamivir 75mg (Tamiflu, Fluvir, Antiflu)",
            "Paracetamol 650mg (Crocin Advance, Dolo 650)",
            "Ibuprofen 400mg (Brufen, Combiflam, Advil)",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet)",
            "Vitamin C 1000mg (Limcee, Celin, Redoxon)",
            "Zinc Supplements (Zincovit, Supradyn, Revital)",
            "Throat Lozenges (Strepsils, Tyrozets, Vicks)",
            "Saline Gargle",
            "Rest and Hydration",
            "Steam Inhalation"
        ],
        "MEDIUM": [
            "Oseltamivir 75mg twice daily (Tamiflu, Fluvir)",
            "Paracetamol 1000mg (Crocin, Dolo)",
            "Codeine Cough Syrup (Corex, Phensedyl)",
            "Electrolyte Solution (Electral, Jeevani, Pedialyte)",
            "Ambroxol 30mg (Mucolite, Ambrodil)",
            "Montelukast 10mg (Montair, Singulair)",
            "Prednisolone 20mg (Wysolone, Omnacortil)",
            "Monitor for complications",
            "Bed Rest for 5-7 days"
        ],
        "HIGH": [
            "IV Oseltamivir (Tamiflu IV)",
            "IV Fluids (Normal Saline, Ringer's Lactate)",
            "IV Paracetamol (Perfalgan, Ofirmev)",
            "Oxygen Support",
            "IV Methylprednisolone (Solu-Medrol)",
            "Hospitalization Required",
            "ICU if respiratory distress",
            "Mechanical Ventilation if needed"
        ]
    },
    "Bronchitis": {
        "LOW": [
            "Dextromethorphan 20mg (Benadryl DR, Robitussin DM)",
            "Guaifenesin 400mg (Mucinex, Grilinctus)",
            "Ibuprofen 400mg (Brufen, Combiflam, Advil)",
            "Honey and Warm Water",
            "Steam Inhalation with Vicks VapoRub",
            "Ambroxol 30mg (Mucolite, Ambrodil, Mucosolvan)",
            "Bromhexine 8mg (Bisolvon, Mucosolvan)",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet)",
            "Throat Lozenges (Strepsils, Tyrozets)",
            "Warm Salt Water Gargle"
        ],
        "MEDIUM": [
            "Azithromycin 500mg (Azithral, Zithromax, Azee)",
            "Salbutamol Inhaler (Asthalin, Ventolin, Airomir)",
            "Prednisolone 20mg (Wysolone, Omnacortil)",
            "Codeine Cough Syrup (Corex, Phensedyl)",
            "Nebulization with Duolin (Salbutamol + Ipratropium)",
            "Montelukast 10mg (Montair, Singulair, Montek)",
            "N-Acetylcysteine 600mg (Mucomyst, Fluimucil)",
            "Theophylline 200mg (Deriphyllin, Theo-24)",
            "Budesonide Inhaler (Budecort, Pulmicort)"
        ],
        "HIGH": [
            "IV Antibiotics (Ceftriaxone, Azithromycin)",
            "IV Methylprednisolone (Solu-Medrol)",
            "Oxygen Therapy",
            "Continuous Nebulization",
            "Bronchodilators (Salbutamol, Terbutaline)",
            "IV Aminophylline",
            "Corticosteroids",
            "Hospitalization Required",
            "ICU if severe respiratory distress"
        ]
    },
    "Migraine": {
        "LOW": [
            "Ibuprofen 600mg (Brufen, Combiflam, Advil)",
            "Paracetamol 1000mg (Crocin, Dolo, Tylenol)",
            "Aspirin 500mg (Disprin, Ecosprin, Bayer)",
            "Caffeine 100mg (with Paracetamol - Saridon)",
            "Sumatriptan 50mg (Suminat, Imitrex, Imigran)",
            "Rizatriptan 10mg (Maxalt, Rizact)",
            "Cold Compress on forehead",
            "Rest in Dark, Quiet Room",
            "Magnesium 400mg (Mag-Ox, Slow-Mag)",
            "Riboflavin (Vitamin B2) 400mg"
        ],
        "MEDIUM": [
            "Sumatriptan 50mg (Suminat, Imitrex, Imigran)",
            "Naproxen 500mg (Naprosyn, Aleve, Flanax)",
            "Metoclopramide 10mg (Perinorm, Reglan, Maxolon)",
            "Diclofenac 50mg (Voveran, Voltaren, Cataflam)",
            "Ergotamine + Caffeine (Cafergot, Migergot)",
            "Propranolol 40mg (Inderal, Ciplar) for prevention",
            "Topiramate 25mg (Topamax, Epitomax) for prevention",
            "Avoid Triggers (stress, certain foods)",
            "Regular Sleep Schedule"
        ],
        "HIGH": [
            "IV Sumatriptan 6mg (Imitrex IV)",
            "IV Prochlorperazine 10mg (Compazine IV)",
            "IV Magnesium Sulfate 2g",
            "IV Dexamethasone 8mg (Decadron IV)",
            "IV Dihydroergotamine (DHE-45)",
            "IV Ketorolac 30mg (Toradol IV)",
            "Emergency Care Required",
            "Neurological Consultation",
            "Rule out Secondary Headache"
        ]
    },
    "Gastroenteritis": {
        "LOW": [
            "ORS (Electral, Jeevani, Pedialyte, WHO-ORS)",
            "Loperamide 2mg (Eldoper, Imodium, Lopamide)",
            "Probiotics (Econorm, Enterogermina, Bifilac, Sporlac)",
            "Zinc Supplements (Zincovit, Supradyn, Revital)",
            "Simethicone 40mg (Gas-X, Digene, Gelusil)",
            "Domperidone 10mg (Domstal, Motilium, Vomistop)",
            "BRAT Diet (Banana, Rice, Apple, Toast)",
            "Oral Rehydration Therapy",
            "Avoid Dairy and Fatty Foods"
        ],
        "MEDIUM": [
            "Ciprofloxacin 500mg (Ciplox, Cifran, Ciprobay)",
            "Ondansetron 8mg (Emeset, Zofran, Ondem)",
            "Metronidazole 400mg (Flagyl, Metrogyl, Metronid)",
            "IV Fluids (Outpatient - Normal Saline)",
            "Electrolyte Replacement (Electral, Jeevani)",
            "Dicyclomine 20mg (Cyclopam, Bentyl, Meftal-Spas)",
            "Racecadotril 100mg (Hidrasec, Redotil)",
            "Norfloxacin 400mg (Norflox, Norbactin)",
            "Pantoprazole 40mg (Pantop, Protonix)"
        ],
        "HIGH": [
            "IV Antibiotics (Ceftriaxone, Ciprofloxacin)",
            "IV Antiemetics (Ondansetron, Metoclopramide)",
            "IV Fluid Resuscitation (Normal Saline, Ringer's)",
            "IV Pantoprazole 40mg (Pantop IV)",
            "Hospitalization Required",
            "Monitor Electrolytes (Na+, K+, Cl-)",
            "Stool Culture and Sensitivity",
            "Complete Blood Count (CBC)"
        ]
    },
    "Hypertension": {
        "LOW": [
            "Lifestyle Modifications (Diet, Exercise)",
            "Low Sodium Diet (<2g/day)",
            "Regular Exercise (30 min/day)",
            "Stress Management Techniques",
            "Monitor BP regularly (Home monitoring)",
            "Amlodipine 2.5mg (Amlong, Norvasc, Amlip)",
            "Losartan 25mg (Cozaar, Losar, Repace)",
            "Hydrochlorothiazide 12.5mg (Aquazide, Microzide)",
            "Weight Management",
            "Limit Alcohol Consumption"
        ],
        "MEDIUM": [
            "Amlodipine 5mg (Amlong, Norvasc, Amlip)",
            "Lisinopril 10mg (Prinivil, Listril, Zestril)",
            "Telmisartan 40mg (Telma, Micardis, Telsartan)",
            "Hydrochlorothiazide 25mg (Aquazide, HCTZ)",
            "Metoprolol 50mg (Betaloc, Lopressor, Seloken)",
            "Atenolol 50mg (Tenormin, Aten, Blokium)",
            "Combination: Amlodipine + Telmisartan (Telma-AM)",
            "Low Sodium Diet (<1.5g/day)",
            "Regular BP Monitoring",
            "Cardiology Follow-up"
        ],
        "HIGH": [
            "Amlodipine 10mg (Amlong, Norvasc)",
            "Lisinopril 20mg (Prinivil, Listril)",
            "Metoprolol 100mg (Betaloc, Lopressor)",
            "IV Labetalol (Trandate IV) for crisis",
            "IV Nicardipine (Cardene IV)",
            "Emergency BP Control (<180/110)",
            "Cardiology Consultation Urgent",
            "Rule out End-organ Damage",
            "Hospitalization if BP >180/120"
        ]
    },
    "Diabetes": {
        "LOW": [
            "Metformin 500mg (Glycomet, Glucophage, Obimet)",
            "Diet Control (Low Carb, High Fiber)",
            "Regular Exercise (30-45 min/day)",
            "Blood Sugar Monitoring (Glucometer)",
            "Lifestyle Changes (Weight Management)",
            "Glimepiride 1mg (Amaryl, Glimer, Glimpid)",
            "Vildagliptin 50mg (Galvus, Zomelis)",
            "Pioglitazone 15mg (Actos, Pioz, Piopar)",
            "HbA1c Monitoring (Every 3 months)",
            "Diabetic Diet Counseling"
        ],
        "MEDIUM": [
            "Metformin 1000mg (Glycomet GP, Glucophage XR)",
            "Glimepiride 2mg (Amaryl, Glimer, Glimpid)",
            "Sitagliptin 100mg (Januvia, Zita, Sitamet)",
            "Insulin (if needed) - Mixtard, Humulin",
            "Empagliflozin 10mg (Jardiance, Empaglyn)",
            "Teneligliptin 20mg (Tenelia, Ziten)",
            "Regular Monitoring (FBS, PPBS, HbA1c)",
            "Diabetic Diet (Carb Counting)",
            "Endocrinology Consultation",
            "Foot Care and Eye Checkup"
        ],
        "HIGH": [
            "Insulin Therapy (Mixtard, Lantus, Humalog)",
            "Metformin 2000mg (Maximum dose)",
            "IV Insulin (Regular Insulin) for DKA",
            "IV Fluids (Normal Saline) for DKA",
            "Endocrinology Referral Urgent",
            "Continuous Glucose Monitoring",
            "Hospitalization if DKA/HHS",
            "ICU if severe DKA",
            "Electrolyte Correction (K+, PO4)"
        ]
    },
    "Asthma": {
        "LOW": [
            "Salbutamol Inhaler PRN (Asthalin, Ventolin, Airomir)",
            "Montelukast 10mg (Montair, Singulair, Montek)",
            "Budesonide Inhaler (Budecort, Pulmicort, Budesal)",
            "Formoterol Inhaler (Foracort, Symbicort)",
            "Avoid Triggers (Dust, Pollen, Smoke)",
            "Peak Flow Monitoring (Peak Flow Meter)",
            "Theophylline 200mg (Deriphyllin, Theo-24)",
            "Cetirizine 10mg (Zyrtec, Alerid) for allergies",
            "Steam Inhalation",
            "Regular Exercise (Swimming preferred)"
        ],
        "MEDIUM": [
            "Budesonide Inhaler (Budecort, Pulmicort) - Controller",
            "Salbutamol Inhaler (Asthalin, Ventolin) - Reliever",
            "Prednisolone 40mg (Wysolone, Omnacortil) - Short course",
            "Nebulization with Duolin (Salbutamol + Ipratropium)",
            "Formoterol + Budesonide (Foracort, Symbicort)",
            "Montelukast 10mg (Montair, Singulair)",
            "Pulmonology Follow-up",
            "Asthma Action Plan",
            "Spacer Device for Inhalers"
        ],
        "HIGH": [
            "IV Methylprednisolone 40mg (Solu-Medrol)",
            "Continuous Nebulization (Salbutamol + Ipratropium)",
            "IV Aminophylline 250mg",
            "Oxygen Therapy (Target SpO2 >92%)",
            "IV Magnesium Sulfate 2g",
            "ICU Admission if severe",
            "Mechanical Ventilation if needed",
            "Arterial Blood Gas Analysis",
            "Chest X-ray to rule out pneumothorax"
        ]
    },
    "Seasonal Influenza": {
        "LOW": [
            "Oseltamivir 75mg (Tamiflu, Fluvir, Antiflu)",
            "Paracetamol 650mg (Crocin Advance, Dolo 650)",
            "Ibuprofen 400mg (Brufen, Combiflam, Advil)",
            "Cetirizine 10mg (Zyrtec, Alerid, Cetrizet)",
            "Vitamin C 1000mg (Limcee, Celin, Redoxon)",
            "Zinc Supplements (Zincovit, Supradyn, Revital)",
            "Throat Lozenges (Strepsils, Tyrozets, Vicks)",
            "Saline Gargle",
            "Rest and Hydration",
            "Steam Inhalation"
        ],
        "MEDIUM": [
            "Oseltamivir 75mg twice daily (Tamiflu, Fluvir)",
            "Paracetamol 1000mg (Crocin, Dolo)",
            "Codeine Cough Syrup (Corex, Phensedyl)",
            "Electrolyte Solution (Electral, Jeevani, Pedialyte)",
            "Ambroxol 30mg (Mucolite, Ambrodil)",
            "Montelukast 10mg (Montair, Singulair)",
            "Prednisolone 20mg (Wysolone, Omnacortil)",
            "Monitor for complications",
            "Bed Rest for 5-7 days"
        ],
        "HIGH": [
            "IV Oseltamivir (Tamiflu IV)",
            "IV Fluids (Normal Saline, Ringer's Lactate)",
            "IV Paracetamol (Perfalgan, Ofirmev)",
            "Oxygen Support",
            "IV Methylprednisolone (Solu-Medrol)",
            "Hospitalization Required",
            "ICU if respiratory distress",
            "Mechanical Ventilation if needed"
        ]
    },
    "Typhoid Fever": {
        "LOW": [
            "Azithromycin 500mg (Azithral, Zithromax, Azee)",
            "Ciprofloxacin 500mg (Ciplox, Cifran, Ciprobay)",
            "Paracetamol 650mg (Crocin Advance, Dolo 650)",
            "ORS - Oral Rehydration Solution (Electral, Jeevani)",
            "Probiotics (Econorm, VSL#3, Bifilac, Sporlac)",
            "Vitamin B Complex (Becosules, Neurobion)",
            "Soft Diet (Rice, Banana, Toast)",
            "Adequate Rest and Hydration",
            "Avoid Spicy and Oily Foods"
        ],
        "MEDIUM": [
            "Ceftriaxone 1g (Monocef, Rocephin, Intacef)",
            "Azithromycin 500mg (Azithral, Zithromax)",
            "IV Fluids (Normal Saline, Ringer's Lactate)",
            "Paracetamol 1000mg (Crocin, Dolo)",
            "Ondansetron 8mg (Emeset, Zofran, Ondem)",
            "Electrolyte Replacement (Electral, Jeevani)",
            "Blood Culture and Sensitivity",
            "Widal Test Monitoring",
            "Hospitalization may be required"
        ],
        "HIGH": [
            "IV Ceftriaxone 2g (Monocef, Rocephin)",
            "IV Ciprofloxacin 400mg (Ciplox IV)",
            "IV Fluid Resuscitation",
            "IV Dexamethasone (for complications)",
            "Hospitalization Required",
            "ICU if complications (perforation, bleeding)",
            "Blood Transfusion if severe anemia",
            "Surgery if intestinal perforation",
            "Intensive Monitoring"
        ]
    },
    "Food Poisoning": {
        "LOW": [
            "ORS - Oral Rehydration Solution (Electral, Jeevani)",
            "Loperamide 2mg (Eldoper, Imodium, Lopamide)",
            "Probiotics (Econorm, Enterogermina, Bifilac)",
            "Simethicone 40mg (Gas-X, Digene, Gelusil)",
            "Domperidone 10mg (Domstal, Motilium, Vomistop)",
            "BRAT Diet (Banana, Rice, Apple, Toast)",
            "Ginger Tea for Nausea",
            "Avoid Dairy and Fatty Foods",
            "Rest and Hydration"
        ],
        "MEDIUM": [
            "Ciprofloxacin 500mg (Ciplox, Cifran, Ciprobay)",
            "Ondansetron 8mg (Emeset, Zofran, Ondem)",
            "Metronidazole 400mg (Flagyl, Metrogyl)",
            "IV Fluids (Outpatient - Normal Saline)",
            "Electrolyte Replacement (Electral, Jeevani)",
            "Pantoprazole 40mg (Pantop, Protonix)",
            "Racecadotril 100mg (Hidrasec, Redotil)",
            "Stool Examination",
            "Monitor for dehydration"
        ],
        "HIGH": [
            "IV Antibiotics (Ceftriaxone, Ciprofloxacin)",
            "IV Antiemetics (Ondansetron, Metoclopramide)",
            "IV Fluid Resuscitation",
            "IV Pantoprazole 40mg (Pantop IV)",
            "Hospitalization Required",
            "Monitor Electrolytes and Kidney Function",
            "Stool Culture and Sensitivity",
            "Blood Tests (CBC, Electrolytes)"
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

# Real Hospital Recommendations by Severity - Updated for Indian Context
HOSPITAL_DATABASE = {
    "LOW": [
        "Primary Health Centre (PHC)",
        "Community Health Center",
        "Local Clinic",
        "General Practitioner",
        "Dispensary"
    ],
    "MEDIUM": [
        "District Hospital",
        "Sub-District Hospital",
        "Nursing Home",
        "Multi-Specialty Clinic",
        "City Hospital"
    ],
    "HIGH": [
        "Medical College Hospital - Emergency Department",
        "Super Specialty Hospital - ICU",
        "Tertiary Care Hospital",
        "Government Medical College",
        "Corporate Hospital - Emergency Care"
    ]
}

# Doctor advice by severity
DOCTOR_ADVICE = {
    "LOW 🟢": "Monitor symptoms at home. Stay hydrated and get adequate rest. Consult a doctor if symptoms worsen or persist for more than 3 days.",
    "MEDIUM 🟡": "Consult a doctor within 24 hours. Follow prescribed medications strictly and monitor your condition closely. Seek immediate care if symptoms worsen.",
    "HIGH 🔴": "Seek immediate medical attention. Visit the emergency department or call an ambulance. This condition requires urgent professional medical care."
}
