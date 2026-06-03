import pandas as pd

data = pd.read_csv('Health.csv')

# Show patterns for each disease
diseases = ['Stomach Infection', 'Dengue', 'Pneumonia or TB', 'Kidney Infection or Stone']

for disease in diseases:
    print(f"\n{'='*60}")
    print(f"{disease}")
    print('='*60)
    disease_data = data[data['Problem'] == disease]
    
    # Show average values for each symptom
    symptom_cols = ['bodypain','Hollow','cold and cough','cough','fever',
                   'chest pain','breathing problem','Throat pain','head pain',
                   'stomach pain','diarrhea','omitting','back pain','Swollen feet']
    
    print("\nAverage symptom values (1=no, 2=yes):")
    for col in symptom_cols:
        avg = disease_data[col].mean()
        print(f"  {col:20s}: {avg:.2f}")
    
    # Show a few sample rows
    print("\nSample rows:")
    print(disease_data[symptom_cols].head(3).to_string())
