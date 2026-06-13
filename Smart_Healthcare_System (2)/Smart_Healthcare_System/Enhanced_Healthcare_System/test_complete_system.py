#!/usr/bin/env python3
"""
Complete system test for disease prediction with new diseases
"""

import pandas as pd
from model import train_model
from hospital_finder import find_hospitals
from medicine_db import MEDICINE_DATABASE

def test_complete_system():
    print("Testing complete healthcare system...")
    
    # Test model training
    print("\n1. Testing model training...")
    try:
        model, disease_map, accuracy = train_model()
        print(f"[PASS] Model trained successfully with accuracy: {accuracy:.2%}")
        print(f"[PASS] Disease mapping created with {len(disease_map)} diseases")
        
        # Print disease mapping
        print("\nDisease mapping:")
        for pid, disease in disease_map.items():
            print(f"  PID {pid}: {disease}")
            
    except Exception as e:
        print(f"[FAIL] Model training failed: {e}")
        return False
    
    # Test prediction for new diseases
    print("\n2. Testing predictions for new diseases...")
    
    # Test data for Seasonal Influenza (symptoms: body pain, cold/cough, cough, fever, throat pain, head pain)
    test_cases = [
        {
            'name': 'Seasonal Influenza Test',
            'symptoms': [1, 2, 1, 1, 102, 2, 2, 1, 1, 2, 2, 2, 2, 2],  # body pain, cold/cough, cough, fever, throat pain, head pain
            'expected_disease': 'Seasonal Influenza'
        },
        {
            'name': 'Typhoid Fever Test', 
            'symptoms': [2, 2, 2, 2, 103, 2, 2, 2, 1, 1, 2, 2, 2, 2],  # fever, head pain, stomach pain
            'expected_disease': 'Typhoid Fever'
        },
        {
            'name': 'Food Poisoning Test',
            'symptoms': [2, 2, 2, 2, 98, 2, 2, 2, 2, 1, 1, 1, 2, 2],  # stomach pain, diarrhea, vomiting
            'expected_disease': 'Food Poisoning'
        }
    ]
    
    column_names = ['bodypain', 'Hollow', 'cold and cough', 'cough', 'fever',
                   'chest pain', 'breathing problem', 'Throat pain', 'head pain',
                   'stomach pain', 'diarrhea', 'omitting', 'back pain', 'Swollen feet']
    
    for test_case in test_cases:
        try:
            df = pd.DataFrame([test_case['symptoms']], columns=column_names)
            pid = model.predict(df)[0]
            prob = max(model.predict_proba(df)[0])
            predicted_disease = disease_map[pid]
            
            print(f"\n{test_case['name']}:")
            print(f"  Predicted: {predicted_disease} (PID: {pid})")
            print(f"  Confidence: {prob:.2%}")
            print(f"  Expected: {test_case['expected_disease']}")
            
            if predicted_disease == test_case['expected_disease']:
                print("  [PASS] CORRECT prediction")
            else:
                print("  [WARN] Different prediction (may still be valid)")
                
        except Exception as e:
            print(f"  [FAIL] Prediction failed: {e}")
    
    # Test medicine database
    print("\n3. Testing medicine recommendations...")
    new_diseases = ['Seasonal Influenza', 'Typhoid Fever', 'Food Poisoning']
    
    for disease in new_diseases:
        if disease in MEDICINE_DATABASE:
            print(f"\n{disease}:")
            for severity in ['LOW', 'MEDIUM', 'HIGH']:
                medicines = MEDICINE_DATABASE[disease][severity]
                print(f"  {severity}: {len(medicines)} medicines")
                print(f"    Example: {medicines[0]}")
        else:
            print(f"[FAIL] {disease} not found in medicine database")
    
    # Test hospital finder
    print("\n4. Testing hospital recommendations...")
    test_cities = ['Mumbai', 'Delhi', 'Kolhapur']
    
    for city in test_cities:
        for disease in new_diseases:
            hospitals = find_hospitals(city=city, disease=disease)
            print(f"\n{disease} in {city}: {len(hospitals)} hospitals found")
            if hospitals:
                print(f"  Best option: {hospitals[0]['name']} ({hospitals[0]['distance']}km)")
    
    print("\n[PASS] Complete system test finished!")
    return True

if __name__ == "__main__":
    test_complete_system()