# 🚀 Quick Start Guide - New Features

## What's New?

### 1. Health Risk Score (0-100) 🎯
Every patient now gets a comprehensive health risk score based on:
- Age
- Number of symptoms
- Disease severity
- Past medical history
- Lifestyle (smoking, blood pressure, blood sugar)

### 2. Hospital Finder with Google Maps 🏥
- Find nearby hospitals based on your disease
- Filter by Government/Private
- Filter by distance
- Get directions via Google Maps
- View hospital details (phone, address, rating)

### 3. Admin Analytics Dashboard 📊
Doctors can now see:
- Most common diseases
- Daily patient count
- High-risk patients list
- Age-wise disease distribution
- Interactive charts and graphs

---

## How to Use New Features

### For Patients

#### Step 1: Sign Up with Lifestyle Info
```
1. Go to Signup page
2. Fill in your details
3. NEW: Select your city (New York, LA, Chicago, Houston, or Other)
4. NEW: Add lifestyle information (optional but recommended):
   - Do you smoke?
   - Blood pressure status
   - Blood sugar status
5. Create account
```

#### Step 2: Enter Symptoms with Hospital Preferences
```
1. Login and click "New Symptom Assessment"
2. Select all your symptoms
3. NEW: Set hospital preferences:
   - Hospital Type: Government or Private (or leave blank for all)
   - Maximum Distance: e.g., 10 km (or leave blank for all)
4. Click "Analyze Symptoms"
```

#### Step 3: View Your Results
```
You'll now see:
✅ Your Health Risk Score (0-100) with color indicator
✅ Risk Category (Low/Moderate/High/Critical)
✅ Personalized health recommendations
✅ Predicted disease with severity
✅ Recommended medicines
✅ Nearby hospitals with:
   - Type (Government/Private)
   - Specialties
   - Distance from you
   - Phone number
   - Rating
   - "View on Maps" button
   - "Get Directions" button
✅ Download PDF report
```

### For Doctors/Admins

#### Access Enhanced Dashboard
```
1. Login with doctor account
2. You'll see the new Analytics Dashboard with:

📊 Key Metrics:
   - Total Patients
   - Today's Patients
   - High Risk Cases
   - Average Risk Score

📈 Charts:
   - Most Common Diseases (Bar Chart)
   - Severity Distribution (Pie Chart)
   - Age-wise Distribution (Bar Chart)
   - Daily Patient Trend (Line Chart)

⚠️ High-Risk Patients Table:
   - All patients with risk score ≥ 60
   - Sorted by risk level
   - Shows name, age, disease, score, category

📋 Age-wise Disease Distribution:
   - See which diseases affect which age groups
```

---

## Examples

### Example 1: High-Risk Patient

**Patient Profile:**
- Age: 65
- Symptoms: 7 (fever, cough, chest pain, breathing problem, body pain, head pain, throat pain)
- Disease: Pneumonia (HIGH severity)
- Past History: 3 previous visits
- Lifestyle: Smoker, High BP, High Blood Sugar

**Health Risk Score Calculation:**
- Age (60+): 25 points
- Symptoms (7+): 20 points
- Severity (HIGH): 30 points
- History (3 visits): 10 points
- Lifestyle (smoking + high BP + high sugar): 10 points
- **Total: 95/100 - CRITICAL RISK 🚨**

**Recommendations:**
- 🆘 IMMEDIATE MEDICAL ATTENTION REQUIRED
- 🆘 Visit emergency room or call ambulance
- 🆘 Do not delay treatment

**Hospitals Shown:**
- Mount Sinai Hospital (Private, 2.5 km, Emergency)
- NYC Health + Hospitals/Bellevue (Government, 4.1 km, Emergency)
- With Google Maps links for directions

---

### Example 2: Low-Risk Patient

**Patient Profile:**
- Age: 25
- Symptoms: 2 (cold and cough, throat pain)
- Disease: Common Cold (LOW severity)
- Past History: 0 visits
- Lifestyle: Non-smoker, Normal BP, Normal Sugar

**Health Risk Score Calculation:**
- Age (18-39): 10 points
- Symptoms (1-2): 5 points
- Severity (LOW): 10 points
- History (0): 0 points
- Lifestyle (all normal): 0 points
- **Total: 25/100 - LOW RISK 🟢**

**Recommendations:**
- ✓ Continue healthy lifestyle habits
- ✓ Regular health checkups recommended
- ✓ Stay hydrated and maintain good sleep

**Hospitals Shown:**
- Primary Care Clinic (Government, 1.5 km)
- Community Health Center (Government, 2.0 km)

---

## Testing the Features

### Test Scenario 1: Complete Patient Journey
```
1. Sign up as new patient
   - Name: John Doe
   - Age: 45
   - City: New York
   - Smoking: No
   - BP: High
   - Sugar: Normal

2. Enter symptoms:
   - Fever ✓
   - Cough ✓
   - Chest Pain ✓
   - Breathing Problem ✓

3. Set hospital filters:
   - Type: Private
   - Distance: 5 km

4. View results:
   - Risk Score: ~55 (Moderate Risk)
   - Disease: Pneumonia
   - Hospitals: Mount Sinai, Lenox Hill
   - Click "View on Maps" for Mount Sinai
   - Click "Get Directions"
```

### Test Scenario 2: Doctor Dashboard
```
1. Sign up as doctor
   - Role: Doctor

2. Login and view dashboard
   - See all statistics
   - View charts
   - Check high-risk patients
   - Review age-wise distribution
```

---

## Tips for Best Results

### For Accurate Risk Scores:
1. ✅ Provide accurate age
2. ✅ Select ALL symptoms you're experiencing
3. ✅ Fill in lifestyle information during signup
4. ✅ Update your profile if lifestyle changes

### For Better Hospital Recommendations:
1. ✅ Select your correct city during signup
2. ✅ Use filters to narrow down options
3. ✅ Check hospital ratings and distance
4. ✅ Call hospital before visiting

### For Doctors:
1. ✅ Check dashboard daily
2. ✅ Prioritize high-risk patients (score ≥ 60)
3. ✅ Monitor disease trends
4. ✅ Use age-wise data for preventive care

---

## Troubleshooting

### No hospitals showing?
- Try removing filters (hospital type, distance)
- Check if your city is set correctly
- Default hospitals will show if city not found

### Risk score seems wrong?
- Verify all symptoms are selected
- Check lifestyle information in profile
- Past history affects score (more visits = higher score)

### Charts not loading?
- Refresh the page
- Check internet connection (Chart.js needs to load)
- Clear browser cache

---

## Quick Reference

### Risk Score Ranges:
- 🟢 0-29: Low Risk
- 🟡 30-59: Moderate Risk
- 🔴 60-79: High Risk
- 🚨 80-100: Critical Risk

### Hospital Types:
- Government: Public hospitals, usually lower cost
- Private: Private hospitals, often more amenities

### Supported Cities:
- New York (4 hospitals)
- Los Angeles (3 hospitals)
- Chicago (2 hospitals)
- Houston (2 hospitals)
- Other cities (default hospitals)

---

## Need Help?

Refer to:
- `NEW_FEATURES.md` - Detailed feature documentation
- `README.md` - General system documentation
- `TESTING_GUIDE.md` - Testing procedures

---

**Enjoy the new features! 🎉**
