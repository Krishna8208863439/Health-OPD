import pandas as pd
from model import train_model

# Train the model
model, disease_map, accuracy = train_model()

# Test with CORRECTED conversion: checked=1 (has symptom), unchecked=2 (no symptom)
test_cases = [
    {
        'name': 'Stomach Infection (stomach pain, diarrhea, vomiting)',
        'symptoms': [2, 2, 2, 2, 98, 2, 2, 2, 2, 1, 1, 1, 2, 2]  # stomach=1, diarrhea=1, omitting=1
    },
    {
        'name': 'Dengue (fever, body pain, headache)',
        'symptoms': [1, 2, 2, 2, 102, 2, 2, 2, 1, 2, 2, 2, 2, 2]  # bodypain=1, fever=102, headpain=1
    },
    {
        'name': 'Pneumonia (cough, fever, chest pain, breathing)',
        'symptoms': [2, 1, 2, 1, 102, 1, 1, 2, 2, 2, 2, 2, 2, 2]  # cough=1, fever=102, chest=1, breathing=1, Hollow=1
    },
    {
        'name': 'Kidney Infection (back pain, swollen feet, fever)',
        'symptoms': [2, 2, 2, 2, 102, 2, 2, 2, 2, 2, 2, 2, 1, 1]  # back=1, swollen=1, fever=102
    },
]

column_names = ['bodypain', 'Hollow', 'cold and cough', 'cough', 'fever',
               'chest pain', 'breathing problem', 'Throat pain', 'head pain',
               'stomach pain', 'diarrhea', 'omitting', 'back pain', 'Swollen feet']

for test in test_cases:
    df = pd.DataFrame([test['symptoms']], columns=column_names)
    pid = model.predict(df)[0]
    proba = model.predict_proba(df)[0]
    max_prob = max(proba)
    
    print(f"{test['name']}:")
    print(f"  Input: {test['symptoms']}")
    print(f"  Predicted: {disease_map[pid]}")
    print(f"  Probability: {max_prob:.2%}")
    print()
