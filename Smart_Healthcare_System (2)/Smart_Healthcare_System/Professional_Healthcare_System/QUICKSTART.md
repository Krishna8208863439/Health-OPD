# 🚀 Quick Start Guide

## Installation (3 Simple Steps)

### Step 1: Install Dependencies
```bash
cd Professional_Healthcare_System
pip install -r requirements.txt
```

### Step 2: Create Hospital Logo
```bash
python create_logo.py
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Open Browser
```
http://localhost:5002
```

## First Time Setup

### Create Patient Account
1. Go to http://localhost:5002
2. Click "Sign Up Here"
3. Fill in details:
   - Full Name: John Doe
   - Username: johndoe
   - Email: john@example.com
   - Password: password123
   - Age: 30
   - Gender: Male
   - Role: **Patient**
4. Click "Create Account"
5. Login with your credentials

### Create Doctor Account
1. Click "Sign Up Here"
2. Fill in details with Role: **Doctor**
3. Login to access Doctor Dashboard

## Test the System

### As Patient:
1. Login as patient
2. Click "Check Symptoms"
3. Select symptoms (e.g., Fever, Cough, Body Pain)
4. Click "Analyze Symptoms"
5. View results and download PDF
6. Check "History" to see all records

### As Doctor:
1. Login as doctor
2. View analytics dashboard
3. See charts and statistics
4. Review recent cases

## Features to Try

✅ Sign Up & Login
✅ Enter symptoms
✅ Get AI prediction
✅ Download PDF report
✅ View medical history
✅ Doctor dashboard
✅ Analytics charts

## Troubleshooting

**Port already in use?**
Change port in app.py:
```python
app.run(debug=True, port=5003)  # Change to any available port
```

**Missing dependencies?**
```bash
pip install Flask Flask-Login pandas scikit-learn reportlab Pillow
```

**Database issues?**
Delete `healthcare_system.db` and restart the app.

## Default Test Accounts

You can create these for testing:

**Patient:**
- Email: patient@test.com
- Password: patient123

**Doctor:**
- Email: doctor@test.com
- Password: doctor123

---

**Ready to go! 🎉**
