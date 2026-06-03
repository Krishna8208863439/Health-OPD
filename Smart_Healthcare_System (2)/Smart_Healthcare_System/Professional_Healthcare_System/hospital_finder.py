"""
Hospital Finder with filtering and Google Maps integration
"""

# Comprehensive Hospital Database (City-wise) - Updated with Indian Cities
HOSPITALS_BY_CITY = {
    "Mumbai": [
        {
            "name": "Tata Memorial Hospital",
            "type": "Government",
            "specialty": ["Oncology", "Surgery", "Emergency", "General Medicine"],
            "address": "Dr. E Borges Road, Parel, Mumbai, Maharashtra 400012",
            "phone": "+91-22-2417-7000",
            "distance": 2.8,
            "rating": 4.9,
            "lat": 19.0176,
            "lng": 72.8562
        },
        {
            "name": "Kokilaben Dhirubhai Ambani Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bunglows, Andheri West, Mumbai 400053",
            "phone": "+91-22-4269-6969",
            "distance": 3.5,
            "rating": 4.8,
            "lat": 19.1136,
            "lng": 72.8697
        },
        {
            "name": "Lilavati Hospital",
            "type": "Private",
            "specialty": ["General Medicine", "Surgery", "Cardiology", "Emergency"],
            "address": "A-791, Bandra Reclamation, Bandra West, Mumbai 400050",
            "phone": "+91-22-2675-1000",
            "distance": 4.2,
            "rating": 4.7,
            "lat": 19.0596,
            "lng": 72.8295
        },
        {
            "name": "KEM Hospital",
            "type": "Government",
            "specialty": ["Emergency", "General Medicine", "Surgery"],
            "address": "489, Rasta Peth, Sardar Moodliar Road, Parel, Mumbai 400012",
            "phone": "+91-22-2410-7000",
            "distance": 2.1,
            "rating": 4.3,
            "lat": 19.0176,
            "lng": 72.8562
        }
    ],
    "Delhi": [
        {
            "name": "All India Institute of Medical Sciences (AIIMS)",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Cardiology", "Neurology", "Emergency"],
            "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi 110029",
            "phone": "+91-11-2658-8500",
            "distance": 3.2,
            "rating": 4.9,
            "lat": 28.5672,
            "lng": 77.2100
        },
        {
            "name": "Fortis Escorts Heart Institute",
            "type": "Private",
            "specialty": ["Cardiology", "Cardiac Surgery", "Emergency"],
            "address": "Okhla Road, New Delhi 110025",
            "phone": "+91-11-4713-5000",
            "distance": 4.5,
            "rating": 4.8,
            "lat": 28.5355,
            "lng": 77.2731
        },
        {
            "name": "Max Super Speciality Hospital",
            "type": "Private",
            "specialty": ["General Medicine", "Surgery", "Oncology", "Emergency"],
            "address": "1, Press Enclave Road, Saket, New Delhi 110017",
            "phone": "+91-11-2651-5050",
            "distance": 5.1,
            "rating": 4.7,
            "lat": 28.5245,
            "lng": 77.2066
        }
    ],
    "Bengaluru": [
        {
            "name": "Manipal Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "98, Rustum Bagh, Airport Road, Bengaluru 560017",
            "phone": "+91-80-2502-4444",
            "distance": 3.8,
            "rating": 4.8,
            "lat": 12.9716,
            "lng": 77.5946
        },
        {
            "name": "Narayana Health City",
            "type": "Private",
            "specialty": ["Cardiology", "Cardiac Surgery", "Neurology", "Emergency"],
            "address": "258/A, Bommasandra Industrial Area, Anekal Taluk, Bengaluru 560099",
            "phone": "+91-80-7122-2200",
            "distance": 6.2,
            "rating": 4.7,
            "lat": 12.7953,
            "lng": 77.6302
        },
        {
            "name": "Bangalore Medical College and Research Institute",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "Fort, Bengaluru, Karnataka 560002",
            "phone": "+91-80-2670-1150",
            "distance": 2.5,
            "rating": 4.2,
            "lat": 12.9716,
            "lng": 77.5946
        }
    ],
    "Hyderabad": [
        {
            "name": "Apollo Hospitals",
            "type": "Private",
            "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"],
            "address": "Jubilee Hills, Hyderabad, Telangana 500033",
            "phone": "+91-40-2360-7777",
            "distance": 4.1,
            "rating": 4.8,
            "lat": 17.4065,
            "lng": 78.4772
        },
        {
            "name": "Nizam's Institute of Medical Sciences (NIMS)",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "Punjagutta, Hyderabad, Telangana 500082",
            "phone": "+91-40-2348-9000",
            "distance": 3.5,
            "rating": 4.5,
            "lat": 17.4239,
            "lng": 78.4738
        }
    ],
    "Kolkata": [
        {
            "name": "AMRI Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "P-4 & 5, CIT Scheme LXXII, Near Rabindra Sarobar Metro, Kolkata 700029",
            "phone": "+91-33-6680-0000",
            "distance": 3.2,
            "rating": 4.7,
            "lat": 22.5726,
            "lng": 88.3639
        },
        {
            "name": "Medical College and Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "88, College Street, Kolkata, West Bengal 700073",
            "phone": "+91-33-2241-3106",
            "distance": 2.8,
            "rating": 4.3,
            "lat": 22.5726,
            "lng": 88.3639
        }
    ],
    "Chennai": [
        {
            "name": "Apollo Hospitals",
            "type": "Private",
            "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"],
            "address": "21, Greams Lane, Off Greams Road, Chennai 600006",
            "phone": "+91-44-2829-0200",
            "distance": 3.5,
            "rating": 4.8,
            "lat": 13.0827,
            "lng": 80.2707
        },
        {
            "name": "Government General Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "EVR Periyar Salai, Park Town, Chennai 600003",
            "phone": "+91-44-2819-3000",
            "distance": 2.1,
            "rating": 4.2,
            "lat": 13.0827,
            "lng": 80.2707
        }
    ],
    "Pune": [
        {
            "name": "Ruby Hall Clinic",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "40, Sassoon Road, Pune, Maharashtra 411001",
            "phone": "+91-20-2612-7100",
            "distance": 2.8,
            "rating": 4.7,
            "lat": 18.5204,
            "lng": 73.8567
        },
        {
            "name": "Sassoon General Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "Near Pune Railway Station, Pune, Maharashtra 411001",
            "phone": "+91-20-2612-7394",
            "distance": 1.5,
            "rating": 4.1,
            "lat": 18.5204,
            "lng": 73.8567
        }
    ],
    "Kolhapur": [
        {
            "name": "Chhatrapati Pramila Raje Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "Near Rajaram Bridge, Kolhapur, Maharashtra 416002",
            "phone": "+91-231-265-2185",
            "distance": 2.2,
            "rating": 4.2,
            "lat": 16.7050,
            "lng": 74.2433
        },
        {
            "name": "Kolhapur Institute of Orthopaedics and Trauma",
            "type": "Private",
            "specialty": ["Orthopedics", "Surgery", "Emergency"],
            "address": "1158 E, Shahupuri, Kolhapur, Maharashtra 416001",
            "phone": "+91-231-265-4321",
            "distance": 1.8,
            "rating": 4.5,
            "lat": 16.7050,
            "lng": 74.2433
        },
        {
            "name": "Sahyadri Speciality Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "General Medicine", "Surgery"],
            "address": "Tarabai Park, Kolhapur, Maharashtra 416003",
            "phone": "+91-231-661-0000",
            "distance": 3.1,
            "rating": 4.6,
            "lat": 16.7050,
            "lng": 74.2433
        }
    ],
    "Kagal": [
        {
            "name": "Kagal Primary Health Centre",
            "type": "Government",
            "specialty": ["General Medicine", "Emergency"],
            "address": "Main Road, Kagal, Maharashtra 416216",
            "phone": "+91-231-123-4567",
            "distance": 1.0,
            "rating": 3.8,
            "lat": 16.5833,
            "lng": 74.3167
        },
        {
            "name": "Shree Hospital Kagal",
            "type": "Private",
            "specialty": ["General Medicine", "Surgery"],
            "address": "Station Road, Kagal, Maharashtra 416216",
            "phone": "+91-231-234-5678",
            "distance": 1.5,
            "rating": 4.0,
            "lat": 16.5833,
            "lng": 74.3167
        }
    ],
    "Ahmedabad": [
        {
            "name": "Apollo Hospitals",
            "type": "Private",
            "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"],
            "address": "Plot No 1A, Bhat GIDC Information Technology Park, Khoraj, Gandhinagar 382421",
            "phone": "+91-79-6670-1000",
            "distance": 4.2,
            "rating": 4.8,
            "lat": 23.0225,
            "lng": 72.5714
        },
        {
            "name": "Civil Hospital Ahmedabad",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "Asarwa, Ahmedabad, Gujarat 380016",
            "phone": "+91-79-2268-9011",
            "distance": 2.5,
            "rating": 4.0,
            "lat": 23.0225,
            "lng": 72.5714
        }
    ],
    "Jaipur": [
        {
            "name": "Fortis Escorts Hospital",
            "type": "Private",
            "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"],
            "address": "Jawahar Lal Nehru Marg, Malviya Nagar, Jaipur 302017",
            "phone": "+91-141-254-7000",
            "distance": 3.8,
            "rating": 4.7,
            "lat": 26.9124,
            "lng": 75.7873
        },
        {
            "name": "SMS Medical College Hospital",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "JLN Marg, Jaipur, Rajasthan 302004",
            "phone": "+91-141-251-8121",
            "distance": 2.1,
            "rating": 4.2,
            "lat": 26.9124,
            "lng": 75.7873
        }
    ],
    "Agra": [
        {
            "name": "Pushpanjali Medical Centre",
            "type": "Private",
            "specialty": ["Cardiology", "General Medicine", "Surgery"],
            "address": "A-1, Pushpanjali, Fatehabad Road, Agra 282001",
            "phone": "+91-562-406-0100",
            "distance": 3.2,
            "rating": 4.5,
            "lat": 27.1767,
            "lng": 78.0081
        },
        {
            "name": "District Hospital Agra",
            "type": "Government",
            "specialty": ["General Medicine", "Surgery", "Emergency"],
            "address": "MG Road, Agra, Uttar Pradesh 282010",
            "phone": "+91-562-246-3048",
            "distance": 2.5,
            "rating": 3.9,
            "lat": 27.1767,
            "lng": 78.0081
        }
    ],
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
            "phone": "+91-XXX-XXX-XXXX",
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
            "phone": "+91-XXX-XXX-XXXX",
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
        "Pneumonia or TB": "Emergency", 
        "Pneumonia or TB or COVID": "Emergency",
        "Bronchitis": "Emergency",
        "Influenza": "Emergency",
        "Seasonal Influenza": "Emergency",
        "Asthma": "Emergency",
        "Stomach Infection": "General Medicine",
        "Gastroenteritis": "General Medicine",
        "Food Poisoning": "General Medicine",
        "Typhoid Fever": "General Medicine",
        "Migraine": "Neurology",
        "Hypertension": "Cardiology",
        "Diabetes": "General Medicine",
        "Common Cold": "General Medicine",
        "cold and cough": "General Medicine",
        "Dengue": "Emergency",
        "Kidney Infection or Stone": "General Medicine",
        "Allergic Side Effects": "General Medicine",
        "Acidity": "General Medicine"
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
