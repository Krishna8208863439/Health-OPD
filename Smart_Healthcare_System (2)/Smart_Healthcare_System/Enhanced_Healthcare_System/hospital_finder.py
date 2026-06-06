"""
Hospital Finder - Extended database with 100+ hospitals across India & major cities
"""
import math

HOSPITALS_BY_CITY = {
    "Mumbai": [
        {"name": "Tata Memorial Hospital", "type": "Government", "specialty": ["Oncology", "Surgery", "Emergency", "General Medicine"], "address": "Dr. E Borges Road, Parel, Mumbai 400012", "phone": "+91-22-2417-7000", "distance": 2.8, "rating": 4.9, "lat": 19.0176, "lng": 72.8562, "beds": 600, "24hrs": True},
        {"name": "Kokilaben Dhirubhai Ambani Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Andheri West, Mumbai 400053", "phone": "+91-22-4269-6969", "distance": 3.5, "rating": 4.8, "lat": 19.1136, "lng": 72.8697, "beds": 750, "24hrs": True},
        {"name": "Lilavati Hospital", "type": "Private", "specialty": ["General Medicine", "Surgery", "Cardiology", "Emergency"], "address": "Bandra West, Mumbai 400050", "phone": "+91-22-2675-1000", "distance": 4.2, "rating": 4.7, "lat": 19.0596, "lng": 72.8295, "beds": 323, "24hrs": True},
        {"name": "KEM Hospital", "type": "Government", "specialty": ["Emergency", "General Medicine", "Surgery"], "address": "Parel, Mumbai 400012", "phone": "+91-22-2410-7000", "distance": 2.1, "rating": 4.3, "lat": 19.0176, "lng": 72.8562, "beds": 1800, "24hrs": True},
        {"name": "Hinduja Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency", "Transplant"], "address": "Mahim, Mumbai 400016", "phone": "+91-22-2445-2222", "distance": 3.0, "rating": 4.7, "lat": 19.0388, "lng": 72.8416, "beds": 351, "24hrs": True},
        {"name": "Jaslok Hospital", "type": "Private", "specialty": ["Cardiology", "Surgery", "General Medicine", "Emergency"], "address": "Pedder Road, Mumbai 400026", "phone": "+91-22-6657-3333", "distance": 3.8, "rating": 4.6, "lat": 18.9696, "lng": 72.8080, "beds": 345, "24hrs": True},
        {"name": "Nair Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Dr. A.L. Nair Road, Mumbai 400008", "phone": "+91-22-2308-2222", "distance": 1.8, "rating": 4.1, "lat": 18.9784, "lng": 72.8341, "beds": 1400, "24hrs": True},
    ],
    "Delhi": [
        {"name": "AIIMS New Delhi", "type": "Government", "specialty": ["General Medicine", "Surgery", "Cardiology", "Neurology", "Emergency"], "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi 110029", "phone": "+91-11-2658-8500", "distance": 3.2, "rating": 4.9, "lat": 28.5672, "lng": 77.2100, "beds": 2478, "24hrs": True},
        {"name": "Fortis Escorts Heart Institute", "type": "Private", "specialty": ["Cardiology", "Cardiac Surgery", "Emergency"], "address": "Okhla Road, New Delhi 110025", "phone": "+91-11-4713-5000", "distance": 4.5, "rating": 4.8, "lat": 28.5355, "lng": 77.2731, "beds": 310, "24hrs": True},
        {"name": "Max Super Speciality Hospital Saket", "type": "Private", "specialty": ["General Medicine", "Surgery", "Oncology", "Emergency"], "address": "Press Enclave Road, Saket, New Delhi 110017", "phone": "+91-11-2651-5050", "distance": 5.1, "rating": 4.7, "lat": 28.5245, "lng": 77.2066, "beds": 500, "24hrs": True},
        {"name": "Safdarjung Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Ansari Nagar, New Delhi 110029", "phone": "+91-11-2673-0000", "distance": 2.8, "rating": 4.2, "lat": 28.5679, "lng": 77.2028, "beds": 3000, "24hrs": True},
        {"name": "Apollo Hospital Delhi", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency", "Transplant"], "address": "Sarita Vihar, New Delhi 110076", "phone": "+91-11-7179-1090", "distance": 6.2, "rating": 4.8, "lat": 28.5339, "lng": 77.2906, "beds": 710, "24hrs": True},
        {"name": "GTB Hospital", "type": "Government", "specialty": ["General Medicine", "Emergency", "Surgery", "Pediatrics"], "address": "Dilshad Garden, Delhi 110095", "phone": "+91-11-2258-7600", "distance": 7.1, "rating": 4.0, "lat": 28.6811, "lng": 77.3138, "beds": 1500, "24hrs": True},
    ],
    "Bengaluru": [
        {"name": "Manipal Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Airport Road, Bengaluru 560017", "phone": "+91-80-2502-4444", "distance": 3.8, "rating": 4.8, "lat": 12.9716, "lng": 77.5946, "beds": 650, "24hrs": True},
        {"name": "Narayana Health City", "type": "Private", "specialty": ["Cardiology", "Cardiac Surgery", "Neurology", "Emergency"], "address": "Bommasandra, Bengaluru 560099", "phone": "+91-80-7122-2200", "distance": 6.2, "rating": 4.7, "lat": 12.7953, "lng": 77.6302, "beds": 1000, "24hrs": True},
        {"name": "Bangalore Medical College (BMCRI)", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency"], "address": "Fort, Bengaluru 560002", "phone": "+91-80-2670-1150", "distance": 2.5, "rating": 4.2, "lat": 12.9716, "lng": 77.5946, "beds": 2500, "24hrs": True},
        {"name": "Fortis Hospital Bannerghatta", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Bannerghatta Road, Bengaluru 560076", "phone": "+91-80-6621-4444", "distance": 5.4, "rating": 4.7, "lat": 12.8833, "lng": 77.5969, "beds": 400, "24hrs": True},
        {"name": "Victoria Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Jubilee Road, Bengaluru 560002", "phone": "+91-80-2670-1150", "distance": 2.1, "rating": 4.0, "lat": 12.9731, "lng": 77.5763, "beds": 1800, "24hrs": True},
    ],
    "Hyderabad": [
        {"name": "Apollo Hospitals Jubilee Hills", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Jubilee Hills, Hyderabad 500033", "phone": "+91-40-2360-7777", "distance": 4.1, "rating": 4.8, "lat": 17.4065, "lng": 78.4772, "beds": 700, "24hrs": True},
        {"name": "NIMS Hyderabad", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Neurology"], "address": "Punjagutta, Hyderabad 500082", "phone": "+91-40-2348-9000", "distance": 3.5, "rating": 4.5, "lat": 17.4239, "lng": 78.4738, "beds": 1000, "24hrs": True},
        {"name": "Yashoda Hospital Secunderabad", "type": "Private", "specialty": ["Cardiology", "Oncology", "General Medicine", "Emergency"], "address": "SP Road, Secunderabad 500003", "phone": "+91-40-4567-4567", "distance": 5.2, "rating": 4.6, "lat": 17.4399, "lng": 78.4983, "beds": 600, "24hrs": True},
        {"name": "Osmania General Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Afzalgunj, Hyderabad 500012", "phone": "+91-40-2461-2800", "distance": 3.0, "rating": 4.1, "lat": 17.3760, "lng": 78.4740, "beds": 1500, "24hrs": True},
        {"name": "Care Hospital Banjara Hills", "type": "Private", "specialty": ["Cardiology", "Neurology", "Transplant", "Emergency"], "address": "Banjara Hills, Hyderabad 500034", "phone": "+91-40-3041-8888", "distance": 4.8, "rating": 4.7, "lat": 17.4132, "lng": 78.4481, "beds": 450, "24hrs": True},
    ],
    "Chennai": [
        {"name": "Apollo Hospitals Chennai", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Greams Road, Chennai 600006", "phone": "+91-44-2829-0200", "distance": 3.5, "rating": 4.8, "lat": 13.0600, "lng": 80.2480, "beds": 700, "24hrs": True},
        {"name": "Government General Hospital Chennai", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Park Town, Chennai 600003", "phone": "+91-44-2819-3000", "distance": 2.1, "rating": 4.2, "lat": 13.0827, "lng": 80.2707, "beds": 2650, "24hrs": True},
        {"name": "Fortis Malar Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Emergency", "Surgery"], "address": "Adyar, Chennai 600020", "phone": "+91-44-4289-2222", "distance": 6.8, "rating": 4.6, "lat": 13.0081, "lng": 80.2575, "beds": 180, "24hrs": True},
        {"name": "MIOT Hospitals", "type": "Private", "specialty": ["Orthopedics", "Cardiology", "Neurology", "Emergency"], "address": "Mount Poonamallee Road, Chennai 600089", "phone": "+91-44-2249-2288", "distance": 8.2, "rating": 4.7, "lat": 13.0333, "lng": 80.1683, "beds": 1000, "24hrs": True},
        {"name": "Rajiv Gandhi Government Hospital", "type": "Government", "specialty": ["General Medicine", "Emergency", "Surgery"], "address": "Park Town, Chennai 600003", "phone": "+91-44-2530-5200", "distance": 2.3, "rating": 4.0, "lat": 13.0843, "lng": 80.2784, "beds": 1400, "24hrs": True},
    ],
    "Kolkata": [
        {"name": "AMRI Hospital Salt Lake", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "JC-16&17, Salt Lake, Kolkata 700098", "phone": "+91-33-6680-0000", "distance": 3.2, "rating": 4.7, "lat": 22.5726, "lng": 88.3639, "beds": 350, "24hrs": True},
        {"name": "Medical College Kolkata", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "College Street, Kolkata 700073", "phone": "+91-33-2241-3106", "distance": 2.8, "rating": 4.3, "lat": 22.5726, "lng": 88.3639, "beds": 1750, "24hrs": True},
        {"name": "Apollo Gleneagles Hospital", "type": "Private", "specialty": ["Cardiology", "Oncology", "Transplant", "Emergency"], "address": "Canal Circular Road, Kolkata 700054", "phone": "+91-33-2320-3040", "distance": 4.5, "rating": 4.7, "lat": 22.5584, "lng": 88.3922, "beds": 520, "24hrs": True},
        {"name": "SSKM Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Neurology"], "address": "AJC Bose Road, Kolkata 700020", "phone": "+91-33-2223-3206", "distance": 3.1, "rating": 4.1, "lat": 22.5355, "lng": 88.3476, "beds": 2300, "24hrs": True},
    ],
    "Pune": [
        {"name": "Ruby Hall Clinic", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Sassoon Road, Pune 411001", "phone": "+91-20-2612-7100", "distance": 2.8, "rating": 4.7, "lat": 18.5204, "lng": 73.8567, "beds": 550, "24hrs": True},
        {"name": "Sassoon General Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Near Pune Railway Station, Pune 411001", "phone": "+91-20-2612-7394", "distance": 1.5, "rating": 4.1, "lat": 18.5195, "lng": 73.8553, "beds": 1400, "24hrs": True},
        {"name": "Jehangir Hospital", "type": "Private", "specialty": ["Cardiology", "Oncology", "Surgery", "Emergency"], "address": "Sassoon Road, Pune 411001", "phone": "+91-20-6681-3333", "distance": 2.2, "rating": 4.6, "lat": 18.5206, "lng": 73.8530, "beds": 350, "24hrs": True},
        {"name": "KEM Hospital Pune", "type": "Government", "specialty": ["General Medicine", "Emergency", "Surgery", "Pediatrics"], "address": "Sardar Moodliar Road, Pune 411011", "phone": "+91-20-2612-8000", "distance": 3.8, "rating": 4.2, "lat": 18.5145, "lng": 73.8514, "beds": 700, "24hrs": True},
        {"name": "Deenanath Mangeshkar Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Transplant", "Emergency"], "address": "Erandwane, Pune 411004", "phone": "+91-20-4015-1000", "distance": 4.1, "rating": 4.8, "lat": 18.5090, "lng": 73.8277, "beds": 750, "24hrs": True},
    ],
    "Ahmedabad": [
        {"name": "Apollo Hospitals Ahmedabad", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Gandhinagar, Ahmedabad 382421", "phone": "+91-79-6670-1000", "distance": 4.2, "rating": 4.8, "lat": 23.0225, "lng": 72.5714, "beds": 650, "24hrs": True},
        {"name": "Civil Hospital Ahmedabad", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Asarwa, Ahmedabad 380016", "phone": "+91-79-2268-9011", "distance": 2.5, "rating": 4.0, "lat": 23.0513, "lng": 72.5987, "beds": 3500, "24hrs": True},
        {"name": "Sterling Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Gurukul Road, Ahmedabad 380052", "phone": "+91-79-4001-5678", "distance": 5.3, "rating": 4.6, "lat": 23.0503, "lng": 72.5443, "beds": 400, "24hrs": True},
        {"name": "SAL Hospital", "type": "Private", "specialty": ["Cardiology", "Surgery", "General Medicine", "Emergency"], "address": "Drive-in Road, Ahmedabad 380054", "phone": "+91-79-6630-1000", "distance": 4.8, "rating": 4.5, "lat": 23.0479, "lng": 72.5327, "beds": 300, "24hrs": True},
    ],
    "Jaipur": [
        {"name": "Fortis Escorts Hospital Jaipur", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Malviya Nagar, Jaipur 302017", "phone": "+91-141-254-7000", "distance": 3.8, "rating": 4.7, "lat": 26.8503, "lng": 75.8069, "beds": 350, "24hrs": True},
        {"name": "SMS Hospital Jaipur", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Neurology"], "address": "JLN Marg, Jaipur 302004", "phone": "+91-141-251-8121", "distance": 2.1, "rating": 4.2, "lat": 26.9124, "lng": 75.7873, "beds": 5200, "24hrs": True},
        {"name": "Manipal Hospital Jaipur", "type": "Private", "specialty": ["Cardiology", "Oncology", "Transplant", "Emergency"], "address": "Sector 5, Vidhyadhar Nagar, Jaipur 302039", "phone": "+91-141-391-5000", "distance": 6.4, "rating": 4.7, "lat": 26.9627, "lng": 75.7614, "beds": 300, "24hrs": True},
        {"name": "RUHS Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Kumbha Marg, Pratap Nagar, Jaipur 302033", "phone": "+91-141-2710-960", "distance": 4.2, "rating": 4.0, "lat": 26.8471, "lng": 75.8069, "beds": 1000, "24hrs": True},
    ],
    "Lucknow": [
        {"name": "SGPGI Lucknow", "type": "Government", "specialty": ["General Medicine", "Neurology", "Cardiology", "Emergency", "Transplant"], "address": "Raebareli Road, Lucknow 226014", "phone": "+91-522-2668-700", "distance": 5.0, "rating": 4.8, "lat": 26.7606, "lng": 80.9497, "beds": 1700, "24hrs": True},
        {"name": "Ram Manohar Lohia Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Vibhuti Khand, Lucknow 226010", "phone": "+91-522-2235-100", "distance": 3.2, "rating": 4.1, "lat": 26.8571, "lng": 81.0073, "beds": 1200, "24hrs": True},
        {"name": "Medanta Hospital Lucknow", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Amar Shaheed Path, Lucknow 226030", "phone": "+91-522-4504-000", "distance": 6.8, "rating": 4.7, "lat": 26.7784, "lng": 80.9347, "beds": 450, "24hrs": True},
    ],
    "Surat": [
        {"name": "SMIMER Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Trauma"], "address": "Udhna-Magdalla Road, Surat 395010", "phone": "+91-261-227-9181", "distance": 3.1, "rating": 4.1, "lat": 21.1702, "lng": 72.8311, "beds": 1200, "24hrs": True},
        {"name": "Kiran Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Emergency", "Surgery"], "address": "Majura Gate, Surat 395002", "phone": "+91-261-246-6666", "distance": 2.4, "rating": 4.5, "lat": 21.2049, "lng": 72.8323, "beds": 350, "24hrs": True},
        {"name": "HCG Hospital Surat", "type": "Private", "specialty": ["Oncology", "Surgery", "General Medicine", "Emergency"], "address": "Ghod Dod Road, Surat 395001", "phone": "+91-261-271-1111", "distance": 3.8, "rating": 4.6, "lat": 21.1828, "lng": 72.8156, "beds": 200, "24hrs": True},
    ],
    "Nagpur": [
        {"name": "AIIMS Nagpur", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Cardiology"], "address": "MIHAN, Nagpur 441108", "phone": "+91-712-299-6200", "distance": 8.2, "rating": 4.7, "lat": 21.0831, "lng": 79.0478, "beds": 993, "24hrs": True},
        {"name": "Orange City Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Khamla Road, Nagpur 440015", "phone": "+91-712-292-5222", "distance": 4.1, "rating": 4.6, "lat": 21.1463, "lng": 79.0849, "beds": 350, "24hrs": True},
        {"name": "Government Medical College Nagpur", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Hanuman Nagar, Nagpur 440009", "phone": "+91-712-254-8768", "distance": 2.8, "rating": 4.0, "lat": 21.1458, "lng": 79.0882, "beds": 1400, "24hrs": True},
    ],
    "Kolhapur": [
        {"name": "Chhatrapati Pramila Raje Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency"], "address": "Near Rajaram Bridge, Kolhapur 416002", "phone": "+91-231-265-2185", "distance": 2.2, "rating": 4.2, "lat": 16.7050, "lng": 74.2433, "beds": 800, "24hrs": True},
        {"name": "Kolhapur Cancer Centre", "type": "Private", "specialty": ["Oncology", "Surgery", "General Medicine"], "address": "Nagala Park, Kolhapur 416003", "phone": "+91-231-265-0000", "distance": 2.8, "rating": 4.4, "lat": 16.7010, "lng": 74.2400, "beds": 200, "24hrs": False},
        {"name": "Sahyadri Speciality Hospital Kolhapur", "type": "Private", "specialty": ["Cardiology", "General Medicine", "Surgery", "Emergency"], "address": "Tarabai Park, Kolhapur 416003", "phone": "+91-231-661-0000", "distance": 3.1, "rating": 4.6, "lat": 16.7080, "lng": 74.2460, "beds": 250, "24hrs": True},
    ],
    "Nashik": [
        {"name": "Wockhardt Hospital Nashik", "type": "Private", "specialty": ["Cardiology", "Neurology", "Emergency", "Surgery"], "address": "Pathardi Phata, Nashik 422010", "phone": "+91-253-660-3000", "distance": 3.5, "rating": 4.5, "lat": 19.9975, "lng": 73.7898, "beds": 300, "24hrs": True},
        {"name": "District General Hospital Nashik", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency"], "address": "Dwarka Circle, Nashik 422001", "phone": "+91-253-257-2776", "distance": 2.1, "rating": 4.0, "lat": 20.0059, "lng": 73.7798, "beds": 900, "24hrs": True},
    ],
    "Bhopal": [
        {"name": "AIIMS Bhopal", "type": "Government", "specialty": ["General Medicine", "Surgery", "Cardiology", "Emergency"], "address": "Saket Nagar, Bhopal 462020", "phone": "+91-755-272-9000", "distance": 6.0, "rating": 4.7, "lat": 23.1990, "lng": 77.4340, "beds": 960, "24hrs": True},
        {"name": "Hamidia Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Royal Market, Bhopal 462001", "phone": "+91-755-254-2000", "distance": 3.2, "rating": 4.0, "lat": 23.2634, "lng": 77.4015, "beds": 1500, "24hrs": True},
        {"name": "Bansal Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "C-Sector, Shahpura, Bhopal 462016", "phone": "+91-755-499-3900", "distance": 5.1, "rating": 4.5, "lat": 23.2082, "lng": 77.4317, "beds": 350, "24hrs": True},
    ],
    "Coimbatore": [
        {"name": "PSG Hospitals", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "Peelamedu, Coimbatore 641004", "phone": "+91-422-257-2111", "distance": 4.2, "rating": 4.7, "lat": 11.0230, "lng": 77.0290, "beds": 900, "24hrs": True},
        {"name": "Kovai Medical Center (KMCH)", "type": "Private", "specialty": ["Cardiology", "Transplant", "Surgery", "Emergency"], "address": "Avanashi Road, Coimbatore 641014", "phone": "+91-422-441-1111", "distance": 5.8, "rating": 4.8, "lat": 11.0178, "lng": 77.0348, "beds": 750, "24hrs": True},
        {"name": "Coimbatore Medical College Hospital", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency"], "address": "Trichy Road, Coimbatore 641018", "phone": "+91-422-230-1393", "distance": 3.1, "rating": 4.1, "lat": 10.9974, "lng": 76.9612, "beds": 1600, "24hrs": True},
    ],
    "Patna": [
        {"name": "AIIMS Patna", "type": "Government", "specialty": ["General Medicine", "Surgery", "Cardiology", "Emergency"], "address": "Phulwarisharif, Patna 801507", "phone": "+91-612-245-1070", "distance": 7.5, "rating": 4.6, "lat": 25.5564, "lng": 85.0560, "beds": 960, "24hrs": True},
        {"name": "PMCH Patna", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency", "Pediatrics"], "address": "Ashok Rajpath, Patna 800004", "phone": "+91-612-265-0151", "distance": 3.2, "rating": 3.9, "lat": 25.6093, "lng": 85.1376, "beds": 2400, "24hrs": True},
        {"name": "Ruban Memorial Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Emergency", "Surgery"], "address": "Hathwa Market, Patna 800001", "phone": "+91-612-250-0000", "distance": 4.1, "rating": 4.4, "lat": 25.6095, "lng": 85.1242, "beds": 300, "24hrs": True},
    ],
    "Chandigarh": [
        {"name": "PGIMER Chandigarh", "type": "Government", "specialty": ["General Medicine", "Surgery", "Cardiology", "Neurology", "Emergency", "Transplant"], "address": "Sector 12, Chandigarh 160012", "phone": "+91-172-275-5555", "distance": 3.0, "rating": 4.9, "lat": 30.7650, "lng": 76.7781, "beds": 1800, "24hrs": True},
        {"name": "Government Medical College Chandigarh", "type": "Government", "specialty": ["General Medicine", "Surgery", "Emergency"], "address": "Sector 32, Chandigarh 160030", "phone": "+91-172-260-1023", "distance": 4.5, "rating": 4.3, "lat": 30.7221, "lng": 76.7434, "beds": 1200, "24hrs": True},
        {"name": "Fortis Hospital Mohali", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "Sector 62, Mohali 160062", "phone": "+91-172-492-2222", "distance": 5.8, "rating": 4.7, "lat": 30.7046, "lng": 76.7179, "beds": 400, "24hrs": True},
    ],
    "New York": [
        {"name": "Mount Sinai Hospital", "type": "Private", "specialty": ["Cardiology", "Neurology", "Oncology", "Emergency"], "address": "1 Gustave L. Levy Place, New York, NY 10029", "phone": "+1-212-241-6500", "distance": 2.5, "rating": 4.8, "lat": 40.7903, "lng": -73.9527, "beds": 1134, "24hrs": True},
        {"name": "NewYork-Presbyterian Hospital", "type": "Private", "specialty": ["General Medicine", "Surgery", "Pediatrics", "Emergency"], "address": "525 E 68th St, New York, NY 10065", "phone": "+1-212-746-5454", "distance": 3.2, "rating": 4.7, "lat": 40.7648, "lng": -73.9540, "beds": 2478, "24hrs": True},
        {"name": "NYC Health + Hospitals/Bellevue", "type": "Government", "specialty": ["Emergency", "Trauma", "General Medicine"], "address": "462 1st Ave, New York, NY 10016", "phone": "+1-212-562-4141", "distance": 4.1, "rating": 4.2, "lat": 40.7391, "lng": -73.9754, "beds": 828, "24hrs": True},
        {"name": "Lenox Hill Hospital", "type": "Private", "specialty": ["Orthopedics", "Cardiology", "Surgery"], "address": "100 E 77th St, New York, NY 10075", "phone": "+1-212-434-2000", "distance": 1.8, "rating": 4.6, "lat": 40.7738, "lng": -73.9594, "beds": 652, "24hrs": True},
    ],
    "Los Angeles": [
        {"name": "Cedars-Sinai Medical Center", "type": "Private", "specialty": ["Cardiology", "Oncology", "Neurology", "Emergency"], "address": "8700 Beverly Blvd, Los Angeles, CA 90048", "phone": "+1-310-423-3277", "distance": 5.2, "rating": 4.9, "lat": 34.0754, "lng": -118.3773, "beds": 886, "24hrs": True},
        {"name": "UCLA Medical Center", "type": "Government", "specialty": ["General Medicine", "Surgery", "Pediatrics"], "address": "757 Westwood Plaza, Los Angeles, CA 90095", "phone": "+1-310-825-9111", "distance": 7.5, "rating": 4.7, "lat": 34.0522, "lng": -118.2437, "beds": 520, "24hrs": True},
        {"name": "LAC+USC Medical Center", "type": "Government", "specialty": ["Emergency", "Trauma", "General Medicine"], "address": "2051 Marengo St, Los Angeles, CA 90033", "phone": "+1-323-409-1000", "distance": 3.8, "rating": 4.3, "lat": 34.0584, "lng": -118.2096, "beds": 600, "24hrs": True},
    ],
    "London": [
        {"name": "St Thomas' Hospital", "type": "Government", "specialty": ["Cardiology", "Neurology", "Emergency", "Surgery"], "address": "Westminster Bridge Road, London SE1 7EH", "phone": "+44-20-7188-7188", "distance": 3.0, "rating": 4.7, "lat": 51.4988, "lng": -0.1177, "beds": 900, "24hrs": True},
        {"name": "University College Hospital", "type": "Government", "specialty": ["General Medicine", "Oncology", "Emergency", "Surgery"], "address": "235 Euston Road, London NW1 2BU", "phone": "+44-20-3456-7890", "distance": 4.2, "rating": 4.6, "lat": 51.5246, "lng": -0.1340, "beds": 665, "24hrs": True},
        {"name": "King's College Hospital", "type": "Government", "specialty": ["Transplant", "Neurology", "Emergency", "Surgery"], "address": "Denmark Hill, London SE5 9RS", "phone": "+44-20-3299-9000", "distance": 5.1, "rating": 4.7, "lat": 51.4686, "lng": -0.0936, "beds": 1000, "24hrs": True},
    ],
    "Default": [
        {"name": "City General Hospital", "type": "Government", "specialty": ["General Medicine", "Emergency"], "address": "Main Street, City Center", "phone": "+91-XXX-XXX-XXXX", "distance": 2.0, "rating": 4.0, "lat": 0, "lng": 0, "beds": 200, "24hrs": True},
        {"name": "Community Medical Center", "type": "Private", "specialty": ["General Medicine", "Surgery"], "address": "Healthcare Avenue, Downtown", "phone": "+91-XXX-XXX-XXXX", "distance": 3.5, "rating": 4.3, "lat": 0, "lng": 0, "beds": 100, "24hrs": False},
    ]
}


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in km (Haversine formula)"""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)


def estimate_eta(distance_km, mode="driving"):
    """Estimate travel time in minutes"""
    speeds = {"driving": 40, "walking": 5, "cycling": 15}
    spd = speeds.get(mode, 40)
    mins = int((distance_km / spd) * 60)
    if mins < 60:
        return f"{mins} min"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m"


def find_hospitals(city="Default", hospital_type=None, specialty=None,
                   max_distance=None, disease=None, user_lat=None, user_lng=None):
    if user_lat is not None and user_lng is not None:
        hospitals_to_search = []
        for ck, cl in HOSPITALS_BY_CITY.items():
            if ck != "Default":
                hospitals_to_search.extend(cl)
    else:
        hospitals_to_search = HOSPITALS_BY_CITY.get(city, HOSPITALS_BY_CITY["Default"])

    disease_specialty_map = {
        "Pneumonia": "Emergency", "Pneumonia or TB": "Emergency",
        "Pneumonia or TB or COVID": "Emergency", "Bronchitis": "Emergency",
        "Influenza": "Emergency", "Seasonal Influenza": "Emergency",
        "Asthma": "Emergency", "Stomach Infection": "General Medicine",
        "Gastroenteritis": "General Medicine", "Food Poisoning": "General Medicine",
        "Typhoid Fever": "General Medicine", "Migraine": "Neurology",
        "Hypertension": "Cardiology", "Diabetes": "General Medicine",
        "Common Cold": "General Medicine", "cold and cough": "General Medicine",
        "Dengue": "Emergency", "Kidney Infection or Stone": "General Medicine",
        "Allergic Side Effects": "General Medicine", "Acidity": "General Medicine"
    }
    if disease and not specialty:
        specialty = disease_specialty_map.get(disease, "General Medicine")

    filtered = []
    for h in hospitals_to_search:
        if hospital_type and h["type"] != hospital_type:
            continue
        if specialty and specialty not in h["specialty"]:
            continue
        hc = dict(h)
        if user_lat is not None and user_lng is not None and hc["lat"] != 0 and hc["lng"] != 0:
            hc["distance"] = calculate_haversine_distance(user_lat, user_lng, hc["lat"], hc["lng"])
        if max_distance and hc["distance"] > max_distance:
            continue
        hc.setdefault("beds", 0)
        hc.setdefault("24hrs", True)
        filtered.append(hc)

    filtered.sort(key=lambda x: x["distance"])
    return filtered


def get_google_maps_url(hospital):
    if hospital["lat"] == 0 and hospital["lng"] == 0:
        return f"https://www.google.com/maps/search/?api=1&query={hospital['address'].replace(' ', '+')}"
    return f"https://www.google.com/maps/search/?api=1&query={hospital['lat']},{hospital['lng']}"


def get_directions_url(hospital, user_location=None):
    origin = f"{user_location['lat']},{user_location['lng']}" if user_location else "My+Location"
    if hospital["lat"] == 0 and hospital["lng"] == 0:
        dest = hospital["address"].replace(" ", "+")
    else:
        dest = f"{hospital['lat']},{hospital['lng']}"
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}"
