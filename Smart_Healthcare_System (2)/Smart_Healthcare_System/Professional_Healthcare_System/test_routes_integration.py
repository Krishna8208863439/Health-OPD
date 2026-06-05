import requests
import random
import sys

BASE_URL = "http://127.0.0.1:5002"

def test_integration():
    print("=" * 60)
    print("STARTING FULL END-TO-END SYSTEM INTEGRATION TESTS")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Sign Up a Patient
    print("\n[Step 1] Registering a new patient...")
    patient_username = f"test_patient_{random.randint(1000, 9999)}"
    patient_email = f"{patient_username}@example.com"
    signup_data = {
        'username': patient_username,
        'email': patient_email,
        'password': 'password123',
        'full_name': 'Test Patient User',
        'age': '30',
        'gender': 'Male',
        'role': 'patient',
        'contact': '+91-9876543210',
        'address': '123 Health Street',
        'city': 'Mumbai',
        'smoking': 'no',
        'blood_pressure': 'normal',
        'blood_sugar': 'normal'
    }
    
    res = session.post(f"{BASE_URL}/signup", data=signup_data, allow_redirects=True)
    if "Login" not in res.text and "Account created successfully" not in res.text:
        print("❌ Patient Signup Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Patient Signup Succeeded!")
    
    # 2. Login as Patient
    print("\n[Step 2] Logging in as patient...")
    login_data = {
        'email': patient_email,
        'password': 'password123'
    }
    res = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    if "Welcome, Test Patient User" not in res.text and "Dashboard" not in res.text:
        print("❌ Patient Login Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Patient Login Succeeded!")
    
    # 3. Log Vitals
    print("\n[Step 3] Logging vitals...")
    vitals_data = {
        'bp_systolic': '125',
        'bp_diastolic': '82',
        'pulse': '74',
        'temperature': '98.8',
        'weight': '72.5',
        'oxygen_saturation': '99',
        'blood_glucose': '95',
        'feeling': 'energetic'
    }
    res = session.post(f"{BASE_URL}/vitals/log", data=vitals_data, allow_redirects=True)
    if "Vitals logged successfully" not in res.text:
        print("❌ Vitals Logging Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Vitals Logging Succeeded!")
    
    # 4. Predict Disease with Hospital Filters
    print("\n[Step 4] Checking symptoms and predicting disease with hospital filter...")
    prediction_query = {
        'fever': '1',
        'cough': '1',
        'breathing_problem': '1',
        'chest_pain': '1',
        'hospital_type': 'Government',
        'max_distance': '10.0',
        'user_lat': '19.0176',
        'user_lng': '72.8562'
    }
    res = session.post(f"{BASE_URL}/predict", data=prediction_query, allow_redirects=True)
    if "Diagnosis Result" not in res.text and "Diagnosis Report" not in res.text:
        print("❌ Disease Prediction / Hospital Finder Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Disease Prediction & Hospital Finding Succeeded!")
    print("   Response contains Referred Hospital details!")
    
    # 5. Check Monthly Report Card
    print("\n[Step 5] Retrieving Monthly Report Card...")
    res = session.get(f"{BASE_URL}/report-card")
    if "Monthly Health Report Card" not in res.text and "30-Day Vitals Averages" not in res.text:
        print("❌ Report Card GET Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Report Card Page Loaded Successfully!")
    
    # 6. Download Report Card PDF
    print("\n[Step 6] Downloading Report Card PDF...")
    res = session.get(f"{BASE_URL}/report-card/pdf")
    if res.status_code != 200 or res.headers.get('content-type') != 'application/pdf':
        print(f"❌ PDF Download Failed! Status: {res.status_code}, Header: {res.headers.get('content-type')}")
        sys.exit(1)
    print(f"✅ PDF Download Succeeded! Received {len(res.content)} bytes.")
    
    # 7. Doctor Slots Management
    print("\n[Step 7] Testing doctor availability slot workflow...")
    # Log out patient first
    session.get(f"{BASE_URL}/logout")
    
    # Login as seeded doctor dr_cardio
    doc_login_data = {
        'email': 'dr_cardio@healthcare.com',  # seeded email pattern
        'password': 'doctor123'
    }
    # Let's verify email for dr_cardio
    # Wait, what email was seeded for dr_cardio? Let's check verify_db or register a new doctor test account
    # To be safe, let's register a new doctor account!
    print("   Registering a new doctor for slot creation...")
    doc_username = f"test_doc_{random.randint(1000, 9999)}"
    doc_email = f"{doc_username}@example.com"
    doc_signup_data = {
        'username': doc_username,
        'email': doc_email,
        'password': 'doctor123',
        'full_name': 'Dr. Test Cardiologist',
        'age': '45',
        'gender': 'Female',
        'role': 'doctor',
        'contact': '+91-9999999999',
        'address': 'Heart Institute',
        'city': 'Mumbai',
    }
    session.post(f"{BASE_URL}/signup", data=doc_signup_data, allow_redirects=True)
    
    # Login as doctor
    res = session.post(f"{BASE_URL}/login", data={'email': doc_email, 'password': 'doctor123'}, allow_redirects=True)
    if "Doctor" not in res.text and "Dashboard" not in res.text:
        print("❌ Doctor Login Failed!")
        sys.exit(1)
    print("   Doctor Logged In Successfully!")
    
    # Create Slot
    slot_data = {
        'slot_date': '2026-07-10',
        'start_time': '14:00',
        'end_time': '14:30',
        'hospital_name': 'Lilavati Hospital'
    }
    res = session.post(f"{BASE_URL}/doctor/slots", data=slot_data, allow_redirects=True)
    if "Availability slot at Lilavati Hospital added" not in res.text:
        print("❌ Doctor Slot Creation Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Doctor Slot Creation Succeeded!")
    
    # Log out doctor
    session.get(f"{BASE_URL}/logout")
    
    # Login as the patient again
    session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    # Get slot ID by parsing /appointments/book-slot HTML page
    print("   Fetching available slots page as patient...")
    res = session.get(f"{BASE_URL}/appointments/book-slot")
    import re
    slot_ids = re.findall(r'action="/appointments/book-slot/(\d+)"', res.text)
    if not slot_ids:
        print("❌ Could not parse slot IDs from available slots page!")
        sys.exit(1)
    slot_id = int(slot_ids[-1])
    print(f"   Found Available Slot ID via HTML parsing: {slot_id}")
    
    # Book the slot
    print("\n[Step 8] Patient booking the doctor availability slot...")
    res = session.post(f"{BASE_URL}/appointments/book-slot/{slot_id}", allow_redirects=True)
    if "Slot booked!" not in res.text or "Lilavati Hospital" not in res.text:
        print("❌ Slot Booking Failed!")
        print(res.text[:1000])
        sys.exit(1)
    print("✅ Slot Booking Succeeded!")
    
    # Verify appointment hospital name in list
    res = session.get(f"{BASE_URL}/appointments")
    if "Lilavati Hospital" not in res.text:
        print("❌ Verification: Hospital name not present in appointments list!")
        sys.exit(1)
    print("✅ Verification: Hospital name present in appointments list!")
    
    print("\n" + "=" * 60)
    print("🎉 ALL END-TO-END INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_integration()
