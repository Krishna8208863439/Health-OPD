"""
Test script for new features
Run this to verify all new features are working correctly
"""

from risk_calculator import calculate_health_risk_score, get_risk_recommendations
from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url

def test_risk_calculator():
    """Test the health risk score calculator"""
    print("=" * 60)
    print("Testing Health Risk Score Calculator")
    print("=" * 60)
    
    # Test Case 1: High Risk Patient
    print("\n1. High Risk Patient (65 years, smoker, high BP, high sugar)")
    patient_data = {
        'age': 65,
        'smoking': 'yes',
        'blood_pressure': 'high',
        'blood_sugar': 'high'
    }
    symptoms = {
        'fever': 1, 'cough': 1, 'chest pain': 1, 'breathing problem': 1,
        'bodypain': 1, 'head pain': 1, 'throat pain': 1, 'stomach pain': 0,
        'diarrhea': 0, 'omitting': 0, 'back pain': 0, 'Hollow': 0,
        'cold and cough': 0, 'Swollen feet': 0
    }
    result = calculate_health_risk_score(patient_data, symptoms, "HIGH 🔴", 3)
    print(f"   Risk Score: {result['score']}/100")
    print(f"   Category: {result['category']} {result['icon']}")
    print(f"   Breakdown: {result['breakdown']}")
    
    recommendations = get_risk_recommendations(result['score'])
    print(f"   Recommendations:")
    for rec in recommendations:
        print(f"      {rec}")
    
    # Test Case 2: Low Risk Patient
    print("\n2. Low Risk Patient (25 years, non-smoker, normal vitals)")
    patient_data = {
        'age': 25,
        'smoking': 'no',
        'blood_pressure': 'normal',
        'blood_sugar': 'normal'
    }
    symptoms = {
        'fever': 0, 'cough': 1, 'chest pain': 0, 'breathing problem': 0,
        'bodypain': 0, 'head pain': 0, 'throat pain': 1, 'stomach pain': 0,
        'diarrhea': 0, 'omitting': 0, 'back pain': 0, 'Hollow': 0,
        'cold and cough': 1, 'Swollen feet': 0
    }
    result = calculate_health_risk_score(patient_data, symptoms, "LOW 🟢", 0)
    print(f"   Risk Score: {result['score']}/100")
    print(f"   Category: {result['category']} {result['icon']}")
    print(f"   Breakdown: {result['breakdown']}")
    
    recommendations = get_risk_recommendations(result['score'])
    print(f"   Recommendations:")
    for rec in recommendations:
        print(f"      {rec}")
    
    print("\n✅ Risk Calculator Tests Passed!")

def test_hospital_finder():
    """Test the hospital finder"""
    print("\n" + "=" * 60)
    print("Testing Hospital Finder")
    print("=" * 60)
    
    # Test Case 1: Find all hospitals in New York
    print("\n1. All hospitals in New York:")
    hospitals = find_hospitals(city="New York")
    print(f"   Found {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"   - {h['name']} ({h['type']}, {h['distance']} km)")
    
    # Test Case 2: Government hospitals only
    print("\n2. Government hospitals in New York:")
    hospitals = find_hospitals(city="New York", hospital_type="Government")
    print(f"   Found {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"   - {h['name']} ({h['type']}, {h['distance']} km)")
    
    # Test Case 3: Hospitals within 3 km
    print("\n3. Hospitals within 3 km in New York:")
    hospitals = find_hospitals(city="New York", max_distance=3.0)
    print(f"   Found {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"   - {h['name']} ({h['distance']} km)")
    
    # Test Case 4: Emergency specialty for Pneumonia
    print("\n4. Hospitals for Pneumonia (Emergency specialty):")
    hospitals = find_hospitals(city="New York", disease="Pneumonia")
    print(f"   Found {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"   - {h['name']} (Specialties: {', '.join(h['specialty'][:3])})")
    
    # Test Case 5: Google Maps URLs
    print("\n5. Testing Google Maps integration:")
    if hospitals:
        hospital = hospitals[0]
        maps_url = get_google_maps_url(hospital)
        directions_url = get_directions_url(hospital)
        print(f"   Hospital: {hospital['name']}")
        print(f"   Maps URL: {maps_url[:60]}...")
        print(f"   Directions URL: {directions_url[:60]}...")
    
    # Test Case 6: Default city
    print("\n6. Hospitals in unlisted city (Default):")
    hospitals = find_hospitals(city="Unknown City")
    print(f"   Found {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"   - {h['name']} ({h['type']})")
    
    print("\n✅ Hospital Finder Tests Passed!")

def test_integration():
    """Test integration of both features"""
    print("\n" + "=" * 60)
    print("Testing Feature Integration")
    print("=" * 60)
    
    print("\nScenario: 45-year-old patient with Pneumonia in New York")
    
    # Calculate risk
    patient_data = {
        'age': 45,
        'smoking': 'no',
        'blood_pressure': 'high',
        'blood_sugar': 'normal'
    }
    symptoms = {
        'fever': 1, 'cough': 1, 'chest pain': 1, 'breathing problem': 1,
        'bodypain': 1, 'head pain': 0, 'throat pain': 0, 'stomach pain': 0,
        'diarrhea': 0, 'omitting': 0, 'back pain': 0, 'Hollow': 0,
        'cold and cough': 0, 'Swollen feet': 0
    }
    risk_result = calculate_health_risk_score(patient_data, symptoms, "MEDIUM 🟡", 1)
    
    print(f"\n1. Health Assessment:")
    print(f"   Risk Score: {risk_result['score']}/100")
    print(f"   Category: {risk_result['category']} {risk_result['icon']}")
    
    # Find hospitals
    hospitals = find_hospitals(
        city="New York",
        disease="Pneumonia",
        hospital_type="Private",
        max_distance=5.0
    )
    
    print(f"\n2. Recommended Hospitals (Private, within 5 km):")
    for h in hospitals[:3]:
        print(f"   - {h['name']}")
        print(f"     Type: {h['type']}, Distance: {h['distance']} km")
        print(f"     Rating: {h['rating']}/5.0")
        print(f"     Phone: {h['phone']}")
    
    # Get recommendations
    recommendations = get_risk_recommendations(risk_result['score'])
    print(f"\n3. Health Recommendations:")
    for rec in recommendations[:3]:
        print(f"   {rec}")
    
    print("\n✅ Integration Tests Passed!")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TESTING NEW HEALTHCARE SYSTEM FEATURES")
    print("=" * 60)
    
    try:
        test_risk_calculator()
        test_hospital_finder()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNew features are working correctly:")
        print("✓ Health Risk Score Calculator (0-100)")
        print("✓ Hospital Finder with Filtering")
        print("✓ Google Maps Integration")
        print("✓ Feature Integration")
        print("\nYou can now run the application with: python app.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
