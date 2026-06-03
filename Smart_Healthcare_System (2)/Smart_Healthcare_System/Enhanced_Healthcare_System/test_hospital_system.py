#!/usr/bin/env python3
"""
Test hospital recommendation system
"""

from hospital_finder import find_hospitals, get_google_maps_url, get_directions_url

def test_hospital_recommendations():
    print("Testing Hospital Recommendation System")
    print("=" * 50)
    
    # Test different scenarios
    test_cases = [
        {
            'name': 'Mumbai - Stomach Infection - All hospitals',
            'city': 'Mumbai',
            'disease': 'Stomach Infection',
            'hospital_type': None,
            'max_distance': None
        },
        {
            'name': 'Mumbai - Seasonal Influenza - Government only',
            'city': 'Mumbai', 
            'disease': 'Seasonal Influenza',
            'hospital_type': 'Government',
            'max_distance': None
        },
        {
            'name': 'Delhi - Typhoid Fever - Within 5km',
            'city': 'Delhi',
            'disease': 'Typhoid Fever', 
            'hospital_type': None,
            'max_distance': 5.0
        },
        {
            'name': 'Kolhapur - Food Poisoning - Private only',
            'city': 'Kolhapur',
            'disease': 'Food Poisoning',
            'hospital_type': 'Private',
            'max_distance': None
        },
        {
            'name': 'Unknown City - Default hospitals',
            'city': 'UnknownCity',
            'disease': 'Stomach Infection',
            'hospital_type': None,
            'max_distance': None
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print("-" * len(test_case['name']))
        
        hospitals = find_hospitals(
            city=test_case['city'],
            disease=test_case['disease'],
            hospital_type=test_case['hospital_type'],
            max_distance=test_case['max_distance']
        )
        
        print(f"Found {len(hospitals)} hospitals")
        
        if hospitals:
            for i, hospital in enumerate(hospitals[:3], 1):  # Show top 3
                print(f"\n{i}. {hospital['name']}")
                print(f"   Type: {hospital['type']}")
                print(f"   Distance: {hospital['distance']}km")
                print(f"   Rating: {hospital['rating']}/5.0")
                print(f"   Specialties: {', '.join(hospital['specialty'][:3])}")
                print(f"   Address: {hospital['address']}")
                print(f"   Phone: {hospital['phone']}")
                
                # Test Google Maps URLs
                maps_url = get_google_maps_url(hospital)
                directions_url = get_directions_url(hospital)
                
                print(f"   Maps URL: {maps_url[:50]}...")
                print(f"   Directions URL: {directions_url[:50]}...")
        else:
            print("   No hospitals found matching criteria")
    
    print(f"\n{'='*50}")
    print("Hospital recommendation system test completed!")

def test_filtering():
    print("\n\nTesting Hospital Filtering")
    print("=" * 30)
    
    city = 'Mumbai'
    disease = 'Stomach Infection'
    
    # Test all hospitals
    all_hospitals = find_hospitals(city=city, disease=disease)
    print(f"All hospitals in {city}: {len(all_hospitals)}")
    
    # Test government only
    gov_hospitals = find_hospitals(city=city, disease=disease, hospital_type='Government')
    print(f"Government hospitals: {len(gov_hospitals)}")
    
    # Test private only  
    private_hospitals = find_hospitals(city=city, disease=disease, hospital_type='Private')
    print(f"Private hospitals: {len(private_hospitals)}")
    
    # Test distance filter
    nearby_hospitals = find_hospitals(city=city, disease=disease, max_distance=3.0)
    print(f"Hospitals within 3km: {len(nearby_hospitals)}")
    
    # Verify filtering works
    assert len(gov_hospitals) + len(private_hospitals) == len(all_hospitals), "Type filtering error"
    assert all(h['distance'] <= 3.0 for h in nearby_hospitals), "Distance filtering error"
    
    print("✓ All filtering tests passed!")

if __name__ == "__main__":
    test_hospital_recommendations()
    test_filtering()