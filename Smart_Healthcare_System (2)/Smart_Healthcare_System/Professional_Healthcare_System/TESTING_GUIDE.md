# 🧪 Testing Guide

## How to Test All Features

### 1. Test Sign Up & Login

#### Sign Up as Patient
1. Run the application: `python app.py`
2. Open browser: http://localhost:5002
3. Click "Sign Up Here"
4. Fill in the form:
   ```
   Full Name: John Smith
   Username: johnsmith
   Email: john@test.com
   Password: test123
   Age: 35
   Gender: Male
   Role: Patient
   Contact: +1-555-0123
   Address: 123 Main St, City
   ```
5. Click "Create Account"
6. ✅ Should see success message
7. Login with john@test.com / test123
8. ✅ Should redirect to Patient Dashboard

#### Sign Up as Doctor
1. Click "Sign Up Here"
2. Fill in form with Role: **Doctor**
   ```
   Full Name: Dr. Sarah Johnson
   Username: drjohnson
   Email: doctor@test.com
   Password: doctor123
   Age: 42
   Gender: Female
   Role: Doctor
   ```
3. ✅ Should create doctor account

### 2. Test Patient Dashboard

1. Login as patient (john@test.com)
2. ✅ Check if patient name is displayed: "Welcome, John Smith!"
3. ✅ Check if age is shown: "Age: 35 years"
4. ✅ Check if Patient ID is shown: "PT-000001"
5. ✅ Verify two action cards: "Check Symptoms" and "Medical History"
6. ✅ Recent diagnoses section should be empty initially

### 3. Test Symptom Entry

1. Click "Check Symptoms" button
2. ✅ Verify patient name is shown: "John Smith"
3. ✅ Verify patient age is shown: "35 years"
4. ✅ Check all symptom groups are displayed:
   - General Symptoms (Fever, Body Pain, Headache, Back Pain)
   - Respiratory Symptoms (Cough, Cold & Cough, Breathing Problem, Throat Pain)
   - Chest & Heart Symptoms (Chest Pain, Hollow Feeling)
   - Digestive Symptoms (Stomach Pain, Diarrhea, Vomiting, Swollen Feet)

#### Test Case 1: Stomach Infection
1. Select symptoms:
   - ✅ Stomach Pain
   - ✅ Diarrhea
   - ✅ Vomiting
   - ✅ Fever
2. Click "Analyze Symptoms & Predict Disease"
3. ✅ Should predict stomach-related disease

#### Test Case 2: Respiratory Issue
1. Go back to symptom entry
2. Select symptoms:
   - ✅ Cough
   - ✅ Fever
   - ✅ Breathing Problem
   - ✅ Chest Pain
3. Click "Analyze Symptoms"
4. ✅ Should predict respiratory disease (Pneumonia/Bronchitis)

### 4. Test Result Page

After prediction, verify:

1. ✅ Patient name displayed: "John Smith"
2. ✅ Patient age displayed: "35 years"
3. ✅ Patient ID shown: "PT-000001"
4. ✅ Predicted disease name shown
5. ✅ Risk percentage displayed (e.g., 75.5%)
6. ✅ Severity level with icon (🟢 LOW / 🟡 MEDIUM / 🔴 HIGH)
7. ✅ Color-coded severity box (Green/Orange/Red)

#### Check Medicine Recommendations
✅ Should show real medicine names like:
- Omeprazole 20mg (Prilosec)
- Ciprofloxacin 500mg
- Metronidazole 400mg (Flagyl)
- Oral Rehydration Solution (ORS)

#### Check Hospital Recommendations
✅ Should show real hospitals like:
- City General Hospital
- Regional Medical Center
- Multi-Specialty Hospital

#### Check Doctor's Advice
✅ Should show appropriate advice based on severity:
- LOW: "Monitor symptoms at home..."
- MEDIUM: "Consult a doctor within 24 hours..."
- HIGH: "Seek immediate medical attention..."

#### Test PDF Download
1. Click "Download PDF Report" button
2. ✅ PDF should download automatically
3. Open the PDF and verify:
   - ✅ Hospital logo in header
   - ✅ Hospital name: "HealthCare Plus Medical Center"
   - ✅ Blue header background
   - ✅ Patient name: "John Smith"
   - ✅ Patient age: "35 years"
   - ✅ Patient contact information
   - ✅ Report ID and date
   - ✅ Predicted disease
   - ✅ Risk percentage
   - ✅ Severity level (color-coded)
   - ✅ Medicine list
   - ✅ Hospital recommendations
   - ✅ Doctor's advice
   - ✅ Professional footer with contact info

### 5. Test Medical History

1. Click "View History" or "History" in navigation
2. ✅ Patient name shown: "John Smith"
3. ✅ Patient age shown: "35 years"
4. ✅ Patient ID shown: "PT-000001"
5. ✅ Total records count displayed
6. ✅ All past diagnoses listed
7. ✅ Each record shows:
   - Disease name
   - Timestamp
   - Severity badge (color-coded)
   - Risk percentage
   - Medicines (truncated)
   - Hospitals (truncated)
   - Doctor's advice (truncated)
   - Download PDF button

#### Test Multiple Diagnoses
1. Go back to symptom entry
2. Enter different symptoms
3. Get new prediction
4. Go to history
5. ✅ Should show 2 records now
6. ✅ Records sorted by newest first
7. ✅ Each record has unique timestamp

#### Test PDF Download from History
1. Click "Download PDF" on any record
2. ✅ PDF should download
3. ✅ PDF should match that specific diagnosis

### 6. Test Doctor Dashboard

1. Logout from patient account
2. Login as doctor (doctor@test.com / doctor123)
3. ✅ Should redirect to Doctor Dashboard

#### Check Statistics Cards
✅ Verify 4 stat cards:
1. Total Patients (with blue icon)
2. Total Diagnoses (with green icon)
3. High Risk Cases (with red icon)
4. Critical Rate % (with orange icon)

#### Check Analytics Charts
✅ Verify 3 charts are displayed:
1. **Disease Distribution** (Doughnut Chart)
   - Shows different diseases
   - Color-coded slices
   - Legend at bottom

2. **Severity Analysis** (Bar Chart)
   - Three bars: Low Risk, Medium Risk, High Risk
   - Color-coded (Green, Orange, Red)
   - Y-axis shows count

3. **Monthly Trends** (Line Chart)
   - Shows diagnoses over months
   - Blue line with gradient fill
   - X-axis shows months

#### Check Recent Cases
✅ Verify recent cases section shows:
- Patient name and age
- Disease name
- Severity badge (color-coded)
- Risk percentage
- Timestamp
- Color-coded left border (Green/Orange/Red)

### 7. Test Hospital Theme Colors

Verify colors throughout the application:

✅ **Primary Blue (#1E3A8A)**: 
- Navigation bar
- Headers
- Section titles

✅ **Accent Blue (#3B82F6)**:
- Buttons
- Links
- Highlights

✅ **Success Green (#10B981)**:
- Low severity indicators
- Success messages
- Positive actions

✅ **Warning Orange (#F59E0B)**:
- Medium severity indicators
- Warning messages

✅ **Danger Red (#EF4444)**:
- High severity indicators
- Critical alerts
- Logout button

### 8. Test Professional UI Elements

#### Navigation Bar
✅ Check:
- Hospital logo/icon
- "HealthCare Plus" branding
- Navigation links
- User name display
- Logout button
- Responsive collapse on mobile

#### Cards and Shadows
✅ Verify:
- Rounded corners (15px-20px)
- Box shadows on cards
- Hover effects (translateY)
- Smooth transitions

#### Buttons
✅ Check:
- Consistent styling
- Hover effects
- Icon integration
- Color coding by action type

#### Forms
✅ Verify:
- Clean input fields
- Proper labels with icons
- Focus states
- Validation messages

#### Footer
✅ Check:
- Blue background
- Hospital name
- Contact information
- Copyright notice

### 9. Test Responsive Design

1. Resize browser window
2. ✅ Layout should adapt to smaller screens
3. ✅ Navigation should collapse to hamburger menu
4. ✅ Cards should stack vertically on mobile
5. ✅ Charts should remain readable
6. ✅ Tables should be scrollable

### 10. Test Security Features

#### Password Hashing
1. Check database file: healthcare_system.db
2. ✅ Passwords should be hashed (not plain text)

#### Role-Based Access
1. Login as patient
2. Try to access: http://localhost:5002/doctor-dashboard
3. ✅ Should be denied with error message
4. ✅ Should redirect to patient dashboard

#### Session Management
1. Login
2. Close browser
3. Reopen and go to http://localhost:5002
4. ✅ Should still be logged in (within 2 hours)

### 11. Test Edge Cases

#### Empty Symptoms
1. Go to symptom entry
2. Don't select any symptoms
3. Click "Analyze Symptoms"
4. ✅ Should still make prediction (all zeros)

#### Duplicate Email
1. Try to sign up with existing email
2. ✅ Should show error: "Email or username already exists!"

#### Invalid Login
1. Try to login with wrong password
2. ✅ Should show error: "Invalid email or password!"

#### No History
1. Create new patient account
2. Go to history page
3. ✅ Should show empty state with message

### 12. Test PDF Features

Create multiple diagnoses and check PDFs:

✅ **Low Severity PDF**:
- Green severity indicator
- Basic medicines
- Primary care recommendations

✅ **Medium Severity PDF**:
- Orange severity indicator
- Moderate medicines
- Regional hospital recommendations

✅ **High Severity PDF**:
- Red severity indicator
- Strong medicines/IV medications
- Tertiary care/ICU recommendations

### 13. Performance Testing

1. Create 10+ patient accounts
2. Generate 20+ diagnoses
3. ✅ Doctor dashboard should load quickly
4. ✅ Charts should render smoothly
5. ✅ History page should handle multiple records

## ✅ Complete Testing Checklist

- [ ] Sign up as patient works
- [ ] Sign up as doctor works
- [ ] Login works for both roles
- [ ] Patient name shown on all pages
- [ ] Patient age shown on all pages
- [ ] Symptom entry page displays correctly
- [ ] All 14 symptoms are selectable
- [ ] Disease prediction works
- [ ] Risk calculation is accurate
- [ ] Real medicine names are shown
- [ ] Real hospital names are shown
- [ ] Doctor's advice is appropriate
- [ ] PDF generates automatically
- [ ] PDF contains hospital logo
- [ ] PDF has all required information
- [ ] PDF downloads successfully
- [ ] Medical history displays all records
- [ ] History shows correct timestamps
- [ ] Download from history works
- [ ] Doctor dashboard shows statistics
- [ ] Disease distribution chart works
- [ ] Severity analysis chart works
- [ ] Monthly trends chart works
- [ ] Recent cases display correctly
- [ ] Hospital theme colors are consistent
- [ ] UI is professional and clean
- [ ] Responsive design works
- [ ] Role-based access control works
- [ ] Password hashing works
- [ ] Session management works
- [ ] Error messages display correctly
- [ ] Success messages display correctly

## 🎯 Expected Results

After completing all tests:
- ✅ All features working perfectly
- ✅ Professional hospital-style UI
- ✅ Real medicines and hospitals
- ✅ PDF generation with logo
- ✅ Analytics and graphs
- ✅ Complete patient history
- ✅ Doctor dashboard functional
- ✅ Security features active

---

**Testing Complete! 🎉**
All features verified and working as expected.
