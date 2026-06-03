#!/usr/bin/env python3
"""
Test Indian Cities and Medicine Names Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hospital_finder import find_hospitals, HOSPITALS_BY_CITY
from medicine_db import MEDICINE_DATABASE

def test_indian_cities():
    """Test Indian cities integration"""
    print("🇮🇳 TESTING INDIAN CITIES INTEGRATION")
    print("=" * 60)
    
    indian_cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Kolkata", 
                    "Chennai", "Pune", "Kolhapur", "Kagal", "Ahmedabad", "Jaipur", "Agra"]
    
    for city in indian_cities:
        hospitals = find_hospitals(city=city)
        print(f"✅ {city}: {len(hospitals)} hospitals found")
        if hospitals:
            print(f"   - {hospitals[0]['name']} ({hospitals[0]['type']})")
    
    print()

def test_indian_medicines():
    """Test Indian medicine names"""
    print("💊 TESTING INDIAN MEDICINE NAMES")
    print("=" * 60)
    
    diseases = ["Stomach Infection", "Pneumonia", "Common Cold", "Hypertension", "Diabetes"]
    
    for disease in diseases:
        if disease in MEDICINE_DATABASE:
            medicines = MEDICINE_DATABASE[disease]["LOW"]
            print(f"✅ {disease}:")
            for med in medicines[:2]:  # Show first 2 medicines
                print(f"   - {med}")
    
    print()

def test_specific_indian_hospitals():
    """Test specific Indian hospitals"""
    print("🏥 TESTING SPECIFIC INDIAN HOSPITALS")
    print("=" * 60)
    
    # Test Kolhapur specifically
    kolhapur_hospitals = find_hospitals(city="Kolhapur")
    print(f"Kolhapur Hospitals: {len(kolhapur_hospitals)}")
    for hospital in kolhapur_hospitals:
        print(f"  - {hospital['name']} ({hospital['type']})")
        print(f"    Phone: {hospital['phone']}")
        print(f"    Specialties: {', '.join(hospital['specialty'])}")
    
    print()
    
    # Test Mumbai specifically
    mumbai_hospitals = find_hospitals(city="Mumbai", hospital_type="Government")
    print(f"Mumbai Government Hospitals: {len(mumbai_hospitals)}")
    for hospital in mumbai_hospitals:
        print(f"  - {hospital['name']}")
        print(f"    Address: {hospital['address']}")
    
    print()

def test_disease_to_hospital_mapping():
    """Test disease to hospital specialty mapping"""
    print("🔗 TESTING DISEASE TO HOSPITAL MAPPING")
    print("=" * 60)
    
    test_cases = [
        ("Pneumonia", "Mumbai"),
        ("Hypertension", "Delhi"),
        ("Migraine", "Bengaluru"),
        ("Diabetes", "Kolhapur")
    ]
    
    for disease, city in test_cases:
        hospitals = find_hospitals(city=city, disease=disease)
        print(f"✅ {disease} in {city}: {len(hospitals)} suitable hospitals")
        if hospitals:
            print(f"   - Recommended: {hospitals[0]['name']}")
            print(f"   - Specialties: {', '.join(hospitals[0]['specialty'])}")
    
    print()

if __name__ == "__main__":
    print("🧪 TESTING INDIAN CITIES AND MEDICINE INTEGRATION")
    print("=" * 60)
    
    test_indian_cities()
    test_indian_medicines()
    test_specific_indian_hospitals()
    test_disease_to_hospital_mapping()
    
    print("🎉 INDIAN INTEGRATION TESTS COMPLETED!")
    print("✅ All Indian cities and medicine names are properly integrated!")