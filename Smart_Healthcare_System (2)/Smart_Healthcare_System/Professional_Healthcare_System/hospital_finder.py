"""
Hospital Finder with filtering and Google Maps integration
"""

# Comprehensive Hospital Database (City-wise)
HOSPITALS_BY_CITY = {
    "New York": [
        {
            "name": "Mount Sinai Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "1 Gustave L. Levy Place, New York, NY 10029",
            "phone": "+1-212-241-6500",
            "distance": 2.5,
            "rating": 4.8,
            "lat": 40.7903,
            "lng": -73.9527
        },
        {
            "name": "NewYork-Presbyterian Hospital",
            "type": "Private",
            "specialty": ["General Medicine", "Surgery", "Pediatrics", "Emergency"],
            "address": "525 E 68th St, New York, NY 10065",
            "phone": "+1-212-746-5454",
            "distance": 3.2,
            "rating": 4.7,
            "lat": 40.7648,
            "lng": -73.9540
        },
        {
            "name": "NYC Health + Hospitals/Bellevue",
            "type": "Government",
            "specialty": ["Emergency", "Trauma", "General Medicine"],
            "address": "462 1st Ave, New York, NY 10016",
            "phone": "+1-212-562-4141",
            "distance": 4.1,
            "rating": 4.2,
            "lat": 40.7391,
            "lng": -73.9754
        },
        {
            "name": "Lenox Hill Hospital",
            "type": "Private",
            "specialty": ["Orthopedics", "Cardiology", "Surgery"],
            "address": "100 E 77th St, New York, NY 10075",
            "phone": "+1-212-434-2000",
            "distance": 1.8,
            "rating": 4.6,
            "lat": 40.7738,
            "lng": -73.9594
        }
    ],
    "Los Angeles": [
        {
            "name": "Cedars-Sinai Medical Center",
            "type": "Private",
            "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"],
            "address": "8700 Beverly Blvd, Los Angeles, CA 90048",
            "phone": "+1-310-423-3277",
            "distance": 5.2,
            "rating": 4.9,
            "lat": 34.0754,
            "lng": -118.3773
        },
        {
            "name": "UCLA Medical Center",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Pediatrics"],
            "address": "757 Westwood Plaza, Los Angeles, CA 90095",
            "phone": "+1-310-825-9111",
            "distance": 7.5,
            "rating": 4.7,
            "lat": 34.0522,
            "lng": -118.2437
        },
        {
            "name": "LAC+USC Medical Center",
            "type": "Government",
            "specialty": ["Emergency", "Trauma", "General Medicine"],
            "address": "2051 Marengo St, Los Angeles, CA 90033",
            "phone": "+1-323-409-1000",
            "distance": 3.8,
            "rating": 4.3,
            "lat": 34.0584,
            "lng": -118.2096
        }
    ],
    "Chicago": [
        {
            "name": "Northwestern Memorial Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology"],
            "address": "251 E Huron St, Chicago, IL 60611",
            "phone": "+1-312-926-2000",
            "distance": 2.1,
            "rating": 4.8,
            "lat": 41.8955,
            "lng": -87.6217
        },
        {
            "name": "Cook County Health",
            "type": "Government",
            "specialty": ["Emergency", "General Medicine", "Trauma"],
            "address": "1969 W Ogden Ave, Chicago, IL 60612",
            "phone": "+1-312-864-6000",
            "distance": 4.5,
            "rating": 4.1,
            "lat": 41.8781,
            "lng": -87.6298
        }
    ],
    "Houston": [
        {
            "name": "Houston Methodist Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Oncology", "Neurology"],
            "address": "6565 Fannin St, Houston, TX 77030",
            "phone": "+1-713-790-3311",
            "distance": 3.7,
            "rating": 4.8,
            "lat": 29.7096,
            "lng": -95.3984
        },
        {
            "name": "Ben Taub Hospital",
            "type": "Government",
            "specialty": ["Emergency", "Trauma", "General Medicine"],
            "address": "1504 Taub Loop, Houston, TX 77030",
            "phone": "+1-713-873-2000",
            "distance": 4.2,
            "rating": 4.2,
            "lat": 29.7074,
            "lng": -95.3978
        }
    ],
    "Default": [
        {
            "name": "City General Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Emergency"],
            "address": "Main Street, City Center",
            "phone": "+1-800-HOSPITAL",
            "distance": 2.0,
            "rating": 4.0,
            "lat": 0,
            "lng": 0
        },
        {
            "name": "Community Medical Center",
            "type": "Private",
            "specialty": ["General Medicine", "Surgery"],
            "address": "Healthcare Avenue, Downtown",
            "phone": "+1-800-MEDICAL",
            "distance": 3.5,
            "rating": 4.3,
            "lat": 0,
            "lng": 0
        }
    ]
}


def find_hospitals(city="Default", hospital_type=None, specialty=None, max_distance=None, disease=None):
    """
    Find hospitals based on filters
    
    Args:
        city: City name
        hospital_type: "Government" or "Private" or None (all)
        specialty: Required specialty or None (all)
        max_distance: Maximum distance in km or None (all)
        disease: Disease name to match specialty
    
    Returns:
        List of matching hospitals
    """
    # Get hospitals for city
    hospitals = HOSPITALS_BY_CITY.get(city, HOSPITALS_BY_CITY["Default"])
    
    # Map diseases to specialties
    disease_specialty_map = {
        "Pneumonia": "Emergency",
        "Bronchitis": "Emergency",
        "Influenza": "Emergency",
        "Asthma": "Emergency",
        "Stomach Infection": "General Medicine",
        "Gastroenteritis": "General Medicine",
        "Migraine": "Neurology",
        "Hypertension": "Cardiology",
        "Diabetes": "General Medicine",
        "Common Cold": "General Medicine"
    }
    
    # Auto-detect specialty from disease
    if disease and not specialty:
        specialty = disease_specialty_map.get(disease, "General Medicine")
    
    # Apply filters
    filtered = []
    for hospital in hospitals:
        # Type filter
        if hospital_type and hospital["type"] != hospital_type:
            continue
        
        # Specialty filter
        if specialty and specialty not in hospital["specialty"]:
            continue
        
        # Distance filter
        if max_distance and hospital["distance"] > max_distance:
            continue
        
        filtered.append(hospital)
    
    # Sort by distance
    filtered.sort(key=lambda x: x["distance"])
    
    return filtered


def get_google_maps_url(hospital):
    """Generate Google Maps URL for hospital"""
    if hospital["lat"] == 0 and hospital["lng"] == 0:
        # Use address-based search
        address = hospital["address"].replace(" ", "+")
        return f"https://www.google.com/maps/search/?api=1&query={address}"
    else:
        # Use coordinates
        return f"https://www.google.com/maps/search/?api=1&query={hospital['lat']},{hospital['lng']}"


def get_directions_url(hospital, user_location=None):
    """Generate Google Maps directions URL"""
    if user_location:
        origin = f"{user_location['lat']},{user_location['lng']}"
    else:
        origin = "My+Location"
    
    if hospital["lat"] == 0 and hospital["lng"] == 0:
        destination = hospital["address"].replace(" ", "+")
    else:
        destination = f"{hospital['lat']},{hospital['lng']}"
    
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
