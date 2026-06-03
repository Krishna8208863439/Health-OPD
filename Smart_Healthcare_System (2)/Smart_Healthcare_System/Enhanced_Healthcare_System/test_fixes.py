#!/usr/bin/env python3
"""
Test script to verify hospital finder and new diseases
"""

from hospital_finder import find_hospitals
from medicine_db import MEDICINE_DATABASE

def test_hospital_finder():
    print("Testing hospital finder...")
    
    # Test different cities
    cities = ['Mumbai', 'Delhi', 'Kolhapur', 'Default']
    diseases = ['Stomach Infection', 'Seasonal Influenza', 'Typhoid Fever', 'Food Poisoning']
    
    for city in cities:
        print(f"\n--- Testing {city} ---")
        for disease in diseases:
            hospitals = find_hospitals(city=city, disease=disease)
            print(f"{disease}: Found {len(hospitals)} hospitals")
            if hospitals:
                for h in hospitals[:2]:  # Show first 2
                    print(f"  - {h['name']} ({h['type']}) - {h['distance']}km")

def test_medicine_database():
    print("\n\nTesting medicine database...")
    
    new_diseases = ['Seasonal Influenza', 'Typhoid Fever', 'Food Poisoning']
    
    for disease in new_diseases:
        if disease in MEDICINE_DATABASE:
            print(f"✓ {disease} found in medicine database")
            print(f"  LOW severity medicines: {len(MEDICINE_DATABASE[disease]['LOW'])}")
            print(f"  MEDIUM severity medicines: {len(MEDICINE_DATABASE[disease]['MEDIUM'])}")
            print(f"  HIGH severity medicines: {len(MEDICINE_DATABASE[disease]['HIGH'])}")
        else:
            print(f"✗ {disease} NOT found in medicine database")

def test_model_data():
    print("\n\nTesting model data...")
    import pandas as pd
    
    try:
        df = pd.read_csv('Health.csv')
        print(f"Total records: {len(df)}")
        print("Unique diseases:")
        diseases = df['Problem'].unique()
        for disease in diseases:
            count = len(df[df['Problem'] == disease])
            print(f"  {disease}: {count} records")
        
        # Check for new diseases
        new_diseases = ['Seasonal Influenza', 'Typhoid Fever', 'Food Poisoning']
        for disease in new_diseases:
            if disease in diseases:
                print(f"✓ {disease} found in training data")
            else:
                print(f"✗ {disease} NOT found in training data")
                
    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    test_hospital_finder()
    test_medicine_database()
    test_model_data()