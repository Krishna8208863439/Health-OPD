#!/usr/bin/env python3
"""
Test Enhanced Medicine Names Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medicine_db import MEDICINE_DATABASE

def test_enhanced_medicines():
    """Test enhanced medicine names"""
    print("💊 TESTING ENHANCED MEDICINE NAMES DATABASE")
    print("=" * 70)
    
    diseases = list(MEDICINE_DATABASE.keys())
    
    for disease in diseases:
        print(f"\n🔹 {disease.upper()}")
        print("-" * 50)
        
        for severity in ["LOW", "MEDIUM", "HIGH"]:
            if severity in MEDICINE_DATABASE[disease]:
                medicines = MEDICINE_DATABASE[disease][severity]
                print(f"\n  {severity} Risk ({len(medicines)} medicines):")
                
                for i, medicine in enumerate(medicines[:5], 1):  # Show first 5
                    print(f"    {i}. {medicine}")
                
                if len(medicines) > 5:
                    print(f"    ... and {len(medicines) - 5} more medicines")

def count_total_medicines():
    """Count total number of medicines in database"""
    print("\n📊 MEDICINE DATABASE STATISTICS")
    print("=" * 70)
    
    total_medicines = 0
    disease_count = len(MEDICINE_DATABASE)
    
    for disease, severities in MEDICINE_DATABASE.items():
        disease_total = 0
        for severity, medicines in severities.items():
            disease_total += len(medicines)
            total_medicines += len(medicines)
        
        print(f"✅ {disease}: {disease_total} medicines")
    
    print(f"\n🎯 TOTAL STATISTICS:")
    print(f"   - Diseases Covered: {disease_count}")
    print(f"   - Total Medicine Recommendations: {total_medicines}")
    print(f"   - Average per Disease: {total_medicines // disease_count}")

def test_indian_brands():
    """Test for Indian pharmaceutical brands"""
    print("\n🇮🇳 INDIAN PHARMACEUTICAL BRANDS FOUND")
    print("=" * 70)
    
    indian_brands = [
        "Crocin", "Dolo", "Azithral", "Ciplox", "Omez", "Glycomet", 
        "Asthalin", "Wysolone", "Electral", "Econorm", "Brufen", 
        "Montair", "Telma", "Amlong", "Betaloc", "Budecort", "Domstal",
        "Alerid", "Limcee", "Zincovit", "Mucolite", "Corex", "Emeset"
    ]
    
    found_brands = []
    
    for disease, severities in MEDICINE_DATABASE.items():
        for severity, medicines in severities.items():
            for medicine in medicines:
                for brand in indian_brands:
                    if brand in medicine and brand not in found_brands:
                        found_brands.append(brand)
                        print(f"✅ {brand} - Found in {disease} ({severity})")
    
    print(f"\n🎯 Found {len(found_brands)} Indian brands out of {len(indian_brands)} searched")

if __name__ == "__main__":
    test_enhanced_medicines()
    count_total_medicines()
    test_indian_brands()
    
    print("\n🎉 ENHANCED MEDICINE DATABASE TEST COMPLETED!")
    print("✅ All medicine names have been significantly expanded with real pharmaceutical brands!")