import pandas as pd
from model import train_model

# Train the model
model, disease_map, accuracy = train_model()

print("Disease Map:")
print(disease_map)
print("\n" + "="*60 + "\n")

# Test different symptom combinations
test_cases = [
    {
        'name': 'Stomach Infection Test',
        'symptoms': [1, 1, 1, 1, 98, 1, 1, 1, 1, 2, 2, 2, 1, 1]  # stomach pain, diarrhea, vomiting
    },
    {
        'name': 'Dengue Test',
        'symptoms': [2, 1, 1, 1, 102, 1, 1, 1, 2, 1, 1, 1, 2, 1]  # fever, body pain, headache, back pain
    },
    {
        'name': 'Pneumonia Test',
        'symptoms': [1, 1, 1, 2, 102, 2, 2, 1, 1, 1, 1, 1, 1, 1]  # cough, fever, chest pain, breathing
    },
    {
        'name': 'Kidney Infection Test',
        'symptoms': [1, 1, 1, 1, 102, 1, 1, 1, 1, 1, 1, 1, 2, 2]  # fever, back pain, swollen feet
    },
    {
        'name': 'All Symptoms',
        'symptoms': [2, 2, 2, 2, 102, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # all symptoms
    },
    {
        'name': 'No Symptoms',
        'symptoms': [1, 1, 1, 1, 98, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # no symptoms
    }
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
    print(f"  Predicted PID: {pid}")
    print(f"  Disease: {disease_map[pid]}")
    print(f"  Probability: {max_prob:.2%}")
    print(f"  All probabilities: {proba}")
    print()
