# 🏗️ System Architecture

## Overview

The Professional Healthcare System is a full-stack web application with AI-powered disease prediction capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Login/     │  │   Patient    │  │   Doctor     │                  │
│  │   Signup     │  │  Dashboard   │  │  Dashboard   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Symptom    │  │   Result     │  │   Medical    │                  │
│  │   Entry      │  │   Display    │  │   History    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER (Flask)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Route Handlers                               │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  • Authentication Routes (signup, login, logout)                  │  │
│  │  • Patient Routes (dashboard, symptom-entry, predict, history)   │  │
│  │  • Doctor Routes (dashboard, analytics-data)                     │  │
│  │  • Utility Routes (download PDF)                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Business Logic                                 │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  • User Management (Flask-Login)                                 │  │
│  │  • Role-Based Access Control                                     │  │
│  │  • Session Management                                            │  │
│  │  • Password Hashing (Werkzeug)                                   │  │
│  │  • Risk Calculation                                              │  │
│  │  • PDF Generation (ReportLab)                                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ML MODEL LAYER     │  │   DATA LAYER     │  │  STORAGE LAYER   │
├──────────────────────┤  ├──────────────────┤  ├──────────────────┤
│                      │  │                  │  │                  │
│  ┌────────────────┐ │  │  ┌────────────┐ │  │  ┌────────────┐ │
│  │ Random Forest  │ │  │  │  SQLite    │ │  │  │    PDF     │ │
│  │  Classifier    │ │  │  │  Database  │ │  │  │  Reports   │ │
│  └────────────────┘ │  │  └────────────┘ │  │  └────────────┘ │
│         │            │  │        │        │  │        │        │
│  ┌────────────────┐ │  │  ┌────────────┐ │  │  ┌────────────┐ │
│  │  14 Symptom    │ │  │  │   Users    │ │  │  │  Hospital  │ │
│  │   Features     │ │  │  │   Table    │ │  │  │    Logo    │ │
│  └────────────────┘ │  │  └────────────┘ │  │  └────────────┘ │
│         │            │  │        │        │  │                  │
│  ┌────────────────┐ │  │  ┌────────────┐ │  │                  │
│  │   Disease      │ │  │  │Predictions │ │  │                  │
│  │   Prediction   │ │  │  │   Table    │ │  │                  │
│  └────────────────┘ │  │  └────────────┘ │  │                  │
│         │            │  │                  │  │                  │
│  ┌────────────────┐ │  │                  │  │                  │
│  │ Probability    │ │  │                  │  │                  │
│  │  Calculation   │ │  │                  │  │                  │
│  └────────────────┘ │  │                  │  │                  │
│                      │  │                  │  │                  │
└──────────────────────┘  └──────────────────┘  └──────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL RESOURCES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Medicine    │  │   Hospital   │  │  Training    │                  │
│  │  Database    │  │   Database   │  │    Data      │                  │
│  │ (100+ meds)  │  │ (12+ hosps)  │  │ (Health.csv) │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### Frontend Technologies
- **HTML5**: Structure and content
- **CSS3**: Styling and animations
- **Bootstrap 5**: Responsive UI framework
- **JavaScript**: Client-side interactivity
- **Chart.js**: Data visualization
- **Font Awesome**: Icons

#### Pages (8)
1. **Login Page**: User authentication
2. **Signup Page**: User registration
3. **Patient Dashboard**: Patient home page
4. **Symptom Entry**: Symptom checker interface
5. **Result Page**: Diagnosis results display
6. **History Page**: Medical history timeline
7. **Doctor Dashboard**: Analytics and statistics
8. **Base Template**: Common layout and navigation

### 2. Application Layer (Flask)

#### Core Components

**Authentication System**
```python
Flask-Login
├── User Class (UserMixin)
├── Login Manager
├── Password Hashing (Werkzeug)
└── Session Management
```

**Route Structure**
```
/                       → Home (role-based redirect)
/signup                 → User registration
/login                  → User authentication
/logout                 → User logout
/patient-dashboard      → Patient home
/symptom-entry          → Symptom checker
/predict                → Disease prediction
/result                 → Diagnosis results
/history                → Medical history
/doctor-dashboard       → Doctor analytics
/analytics-data         → Chart data API
/download/<filename>    → PDF download
```

**Business Logic**
- User management and authentication
- Role-based access control (Patient/Doctor)
- Session management (2-hour timeout)
- Password hashing and verification
- Risk calculation (Low/Medium/High)
- PDF generation with hospital branding
- Database operations (CRUD)
- Error handling and validation

### 3. Machine Learning Layer

#### Model Architecture
```
Input: 14 Symptoms
    ↓
Random Forest Classifier
├── n_estimators: 100
├── random_state: 42
└── train_test_split: 80-20
    ↓
Output: Disease Prediction + Probability
```

#### Features (14 Symptoms)
1. Body Pain
2. Hollow Feeling
3. Cold & Cough
4. Cough
5. Fever
6. Chest Pain
7. Breathing Problem
8. Throat Pain
9. Head Pain
10. Stomach Pain
11. Diarrhea
12. Vomiting
13. Back Pain
14. Swollen Feet

#### Prediction Process
```
User Symptoms → DataFrame → Model.predict() → Disease ID
                                    ↓
                          Model.predict_proba() → Probability
                                    ↓
                          Risk Calculation → Low/Medium/High
                                    ↓
                          Medicine Lookup → Recommendations
                                    ↓
                          Hospital Lookup → Recommendations
```

### 4. Data Layer

#### Database Schema

**Users Table**
```sql
users
├── id (PRIMARY KEY)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── full_name
├── age
├── gender
├── contact
├── address
├── role (patient/doctor)
└── created_at
```

**Predictions Table**
```sql
predictions
├── id (PRIMARY KEY)
├── patient_id (FOREIGN KEY → users.id)
├── patient_name
├── patient_age
├── disease
├── risk_percentage
├── severity
├── probability
├── symptoms
├── medicines
├── hospitals
├── doctor_advice
├── pdf_path
└── timestamp
```

#### Database Operations
- **Create**: User registration, prediction storage
- **Read**: User authentication, history retrieval, analytics
- **Update**: Session management
- **Delete**: Not implemented (data retention)

### 5. Storage Layer

#### File Storage Structure
```
static/
├── assets/
│   └── hospital_logo.png       # Hospital branding
└── reports/
    └── Medical_Report_*.pdf    # Generated reports
```

#### PDF Generation Process
```
Prediction Data
    ↓
ReportLab Canvas
    ↓
Add Hospital Logo
    ↓
Add Patient Information
    ↓
Add Diagnosis Results
    ↓
Add Medicine Recommendations
    ↓
Add Hospital Recommendations
    ↓
Add Doctor's Advice
    ↓
Add Professional Footer
    ↓
Save to static/reports/
    ↓
Return filename for download
```

### 6. External Resources

#### Medicine Database
```python
MEDICINE_DATABASE = {
    "Disease": {
        "LOW": ["Medicine1", "Medicine2", ...],
        "MEDIUM": ["Medicine3", "Medicine4", ...],
        "HIGH": ["Medicine5", "Medicine6", ...]
    }
}
```
- 10+ diseases covered
- 100+ real medicines
- Dosage information included
- Brand names provided

#### Hospital Database
```python
HOSPITAL_DATABASE = {
    "LOW": ["Primary Care Clinic", ...],
    "MEDIUM": ["Regional Medical Center", ...],
    "HIGH": ["Tertiary Care Hospital", ...]
}
```
- 12+ hospital types
- Severity-based recommendations
- Emergency care options

## Data Flow

### Patient Diagnosis Flow
```
1. Patient Login
        ↓
2. Navigate to Symptom Entry
        ↓
3. Select Symptoms (14 checkboxes)
        ↓
4. Submit Form → POST /predict
        ↓
5. Create DataFrame from symptoms
        ↓
6. ML Model Prediction
        ↓
7. Calculate Risk & Severity
        ↓
8. Lookup Medicines & Hospitals
        ↓
9. Generate PDF Report
        ↓
10. Save to Database
        ↓
11. Display Results
        ↓
12. Download PDF (optional)
```

### Doctor Analytics Flow
```
1. Doctor Login
        ↓
2. Navigate to Dashboard
        ↓
3. Fetch Statistics from Database
        ↓
4. Calculate Metrics
        ↓
5. Render Dashboard
        ↓
6. Load Chart.js
        ↓
7. Fetch Analytics Data → GET /analytics-data
        ↓
8. Query Database for:
   - Disease distribution
   - Severity analysis
   - Monthly trends
        ↓
9. Return JSON data
        ↓
10. Render Charts
```

## Security Architecture

### Authentication Flow
```
User Registration
    ↓
Password → Werkzeug Hash → Store in Database
    ↓
User Login
    ↓
Email + Password → Verify Hash → Create Session
    ↓
Flask-Login → User Object → Session Cookie
    ↓
Protected Routes → @login_required → Verify Session
    ↓
Role Check → @role_required → Verify User Role
```

### Security Features
- Password hashing (Werkzeug)
- Session management (Flask-Login)
- Role-based access control
- SQL injection prevention (parameterized queries)
- CSRF protection (Flask built-in)
- Secure session cookies

## Performance Considerations

### Optimization Strategies
1. **Database Indexing**: Primary keys and foreign keys
2. **Session Management**: 2-hour timeout
3. **Static File Caching**: Browser caching for CSS/JS
4. **Lazy Loading**: Charts load after page render
5. **Efficient Queries**: Limit results, use indexes

### Scalability
- **Horizontal**: Multiple Flask instances with load balancer
- **Vertical**: Increase server resources
- **Database**: Migrate to PostgreSQL for production
- **File Storage**: Use cloud storage (S3, Azure Blob)
- **Caching**: Implement Redis for session storage

## Technology Stack Summary

### Backend
- **Flask 3.0.0**: Web framework
- **Flask-Login 0.6.3**: Authentication
- **SQLite**: Database (development)
- **Pandas 2.1.4**: Data processing
- **Scikit-learn 1.3.2**: Machine learning
- **ReportLab 4.0.7**: PDF generation
- **Pillow 10.1.0**: Image processing
- **Werkzeug 3.0.1**: Security utilities

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling
- **Bootstrap 5.3.0**: UI framework
- **JavaScript ES6**: Interactivity
- **Chart.js 4.4.0**: Data visualization
- **Font Awesome 6.4.0**: Icons

### Machine Learning
- **Random Forest Classifier**: Disease prediction
- **Scikit-learn**: Model training and evaluation
- **Pandas**: Data preprocessing

## Deployment Architecture

### Development
```
Local Machine
    ↓
Python 3.8+
    ↓
Flask Development Server
    ↓
SQLite Database
    ↓
http://localhost:5002
```

### Production
```
Cloud Server (AWS/Azure/Heroku)
    ↓
Gunicorn/Waitress (WSGI Server)
    ↓
Flask Application
    ↓
PostgreSQL Database
    ↓
Nginx (Reverse Proxy)
    ↓
HTTPS (SSL Certificate)
    ↓
https://yourdomain.com
```

## Monitoring & Logging

### Application Monitoring
- Error logging to file
- Performance metrics
- User activity tracking
- Database query monitoring

### Health Checks
- `/health` endpoint
- Database connectivity
- File system access
- ML model availability

---

**Architecture Status**: ✅ Production Ready
**Scalability**: ⭐⭐⭐⭐ High
**Security**: 🔒 Secure
**Performance**: ⚡ Optimized
