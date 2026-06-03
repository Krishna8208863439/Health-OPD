# Design Document

## Overview

This design document outlines the enhancements to the Smart Healthcare System to fix the hospital recommendation functionality and expand disease prediction capabilities. The system will be enhanced to support three new diseases (Seasonal Influenza, Typhoid Fever, Food Poisoning) while maintaining the existing architecture and improving the hospital finder module.

The enhancements focus on data-driven improvements to the machine learning model, comprehensive medicine database updates, and robust hospital recommendation logic that properly maps diseases to medical specialties.

## Architecture

The existing Flask-based architecture will be maintained with enhancements to the following components:

### Core Components
- **Disease Prediction Engine** (`model.py`): Enhanced ML model with expanded training dataset
- **Hospital Finder Service** (`hospital_finder.py`): Improved recommendation logic with better specialty mapping
- **Medicine Database** (`medicine_db.py`): Expanded medication recommendations for new diseases
- **PDF Report Generator** (`app.py`): Updated to handle new disease types
- **Web Interface** (`templates/`): Enhanced UI for better hospital filtering and display

### Data Flow
1. User enters symptoms through web interface
2. Symptoms are processed and fed to the enhanced ML model
3. Disease prediction is made with confidence scoring
4. Hospital recommendations are generated based on disease-specialty mapping
5. Medicine recommendations are retrieved from expanded database
6. Comprehensive PDF report is generated with all recommendations

## Components and Interfaces

### Enhanced Disease Prediction Model

**Input Interface:**
```python
def predict_disease(symptom_profile: Dict[str, int]) -> PredictionResult:
    """
    Predicts disease based on symptom profile
    
    Args:
        symptom_profile: Dictionary mapping symptom names to values (1=present, 2=absent)
    
    Returns:
        PredictionResult containing disease, confidence, and risk assessment
    """
```

**Training Data Enhancement:**
- Expand Health.csv with 200+ samples per new disease
- Maintain balanced dataset across all disease categories
- Include symptom patterns specific to new diseases

### Hospital Finder Service Enhancement

**Core Interface:**
```python
def find_hospitals(
    city: str,
    disease: str,
    hospital_type: Optional[str] = None,
    max_distance: Optional[float] = None,
    specialty_required: bool = True
) -> List[HospitalRecommendation]:
    """
    Enhanced hospital finder with improved disease-specialty mapping
    """
```

**Disease-Specialty Mapping:**
```python
ENHANCED_DISEASE_SPECIALTY_MAP = {
    "Seasonal Influenza": ["Emergency", "General Medicine", "Internal Medicine"],
    "Typhoid Fever": ["Infectious Disease", "General Medicine", "Emergency"],
    "Food Poisoning": ["Emergency", "Gastroenterology", "General Medicine"],
    "Pneumonia": ["Emergency", "Pulmonology", "General Medicine"],
    "Dengue": ["Emergency", "General Medicine", "Infectious Disease"],
    # ... existing mappings
}
```

**Fallback Logic:**
- If no specialty hospitals found, recommend general hospitals
- Sort by distance and rating
- Provide clear messaging about hospital capabilities

### Medicine Database Enhancement

**New Disease Medications:**
```python
ENHANCED_MEDICINE_DATABASE = {
    "Seasonal Influenza": {
        "LOW": ["Paracetamol 500mg", "Rest and fluids", "Throat lozenges"],
        "MEDIUM": ["Oseltamivir 75mg", "Paracetamol 500mg", "Decongestants"],
        "HIGH": ["Oseltamivir 75mg", "IV fluids", "Hospitalization recommended"]
    },
    "Typhoid Fever": {
        "LOW": ["Azithromycin 500mg", "ORS", "Probiotics"],
        "MEDIUM": ["Ceftriaxone 1g IV", "Azithromycin 500mg", "IV fluids"],
        "HIGH": ["Ceftriaxone 2g IV", "ICU monitoring", "Blood culture guided therapy"]
    },
    "Food Poisoning": {
        "LOW": ["ORS", "Probiotics", "BRAT diet"],
        "MEDIUM": ["Loperamide", "ORS", "Electrolyte replacement"],
        "HIGH": ["IV fluids", "Antiemetics", "Hospitalization recommended"]
    }
}
```

## Data Models

### Enhanced Training Dataset Structure

**New Disease Symptom Patterns:**

**Seasonal Influenza:**
- High fever (102-104°F): Present
- Body pain: Present
- Cough: Present (dry, non-productive)
- Throat pain: Present
- Head pain: Present
- Breathing problems: Sometimes present
- Stomach symptoms: Rare (mainly in children)

**Typhoid Fever:**
- Gradual fever onset: Present
- Stomach pain: Present
- Head pain: Present
- Body pain: Present
- Diarrhea: Sometimes present
- Back pain: Present
- Hollow feeling: Present

**Food Poisoning:**
- Stomach pain: Present
- Diarrhea: Present
- Vomiting: Present
- Fever: Sometimes present
- Body pain: Sometimes present
- Dehydration symptoms: Present

### Database Schema Updates

**Predictions Table Enhancement:**
```sql
ALTER TABLE predictions ADD COLUMN symptom_severity_score INTEGER DEFAULT 0;
ALTER TABLE predictions ADD COLUMN treatment_recommendations TEXT;
ALTER TABLE predictions ADD COLUMN hospital_specialty_match BOOLEAN DEFAULT FALSE;
```

**New Symptom Tracking:**
```python
SYMPTOM_SEVERITY_WEIGHTS = {
    "fever": {"high": 3, "medium": 2, "low": 1},
    "stomach_pain": {"severe": 3, "moderate": 2, "mild": 1},
    "diarrhea": {"bloody": 3, "watery": 2, "mild": 1},
    # ... additional severity mappings
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Now I need to analyze the acceptance criteria to determine which ones are testable as properties. Let me use the prework tool:

### Converting EARS to Properties

Based on the prework analysis, I've identified the testable acceptance criteria and consolidated redundant properties. Here are the key correctness properties:

**Property 1: Hospital Relevance Filtering**
*For any* disease prediction and filter combination, all returned hospitals should have specialties relevant to the predicted disease and match the specified filters (type, distance)
**Validates: Requirements 1.1, 1.2, 1.6**

**Property 2: Hospital Information Completeness**
*For any* hospital recommendation, the result should contain all required fields: name, type, distance, contact information, specialties, and valid Google Maps URLs
**Validates: Requirements 1.4, 1.5**

**Property 3: Hospital Fallback Behavior**
*For any* query that returns no specialty hospitals, the system should return the nearest general hospitals sorted by distance with appropriate messaging
**Validates: Requirements 1.3, 1.7, 6.5**

**Property 4: New Disease Prediction Accuracy**
*For any* symptom pattern characteristic of Seasonal Influenza, Typhoid Fever, or Food Poisoning, the Disease_Predictor should correctly identify the corresponding disease with appropriate confidence
**Validates: Requirements 2.1, 3.1, 4.1**

**Property 5: Disease Classification Accuracy**
*For any* symptom pattern that could overlap between similar diseases, the Disease_Predictor should correctly distinguish between diseases (e.g., influenza vs other respiratory conditions, typhoid vs other fever conditions, food poisoning vs other GI conditions)
**Validates: Requirements 2.5, 3.5, 4.5, 7.5**

**Property 6: Dataset Completeness and Balance**
*For any* disease in the system including new diseases, the training dataset should contain sufficient representative samples (minimum 200 per disease) to ensure reliable predictions and maintain balanced representation
**Validates: Requirements 2.2, 3.2, 4.2, 7.1, 7.4**

**Property 7: Medication Recommendation Appropriateness**
*For any* disease prediction and severity level, the system should recommend medically appropriate medications with correct classification (OTC vs prescription) and include dosage guidelines and precautions
**Validates: Requirements 2.3, 3.3, 4.3, 5.1, 5.2, 5.3, 5.4, 5.5**

**Property 8: Disease-Specific Medical Advice**
*For any* new disease prediction, the system should provide disease-specific medical advice including appropriate isolation recommendations for typhoid and hydration/dietary recommendations for food poisoning
**Validates: Requirements 2.4, 3.4, 4.4**

**Property 9: Hospital Specialty Prioritization**
*For any* disease prediction, hospitals with relevant specialties should be prioritized in recommendations (Emergency/General Medicine for influenza, Infectious Disease/General Medicine for typhoid, Emergency/Gastroenterology for food poisoning)
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

**Property 10: Model Performance Standards**
*For any* disease in the system, the prediction accuracy should maintain above 85% and validation should correctly identify accurate predictions against known symptom patterns
**Validates: Requirements 7.2, 7.3**

**Property 11: PDF Report Completeness**
*For any* new disease prediction, the generated PDF should contain disease-specific information, appropriate medical advice, relevant medication recommendations, and disease-appropriate hospital recommendations while maintaining consistent formatting
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

## Error Handling

### Hospital Finder Error Scenarios
- **No hospitals in city**: Return default hospitals with clear messaging
- **No specialty hospitals**: Fall back to general hospitals with explanation
- **Invalid coordinates**: Use address-based Google Maps search
- **Network failures**: Provide cached hospital data where possible

### Disease Prediction Error Scenarios
- **Insufficient symptoms**: Request additional symptom information
- **Low confidence predictions**: Provide multiple possible diagnoses with confidence scores
- **Model training failures**: Fall back to rule-based classification
- **Data corruption**: Validate training data integrity before model training

### Medicine Database Error Scenarios
- **Missing medication data**: Provide general treatment advice
- **Drug interaction warnings**: Include appropriate precautions
- **Dosage calculation errors**: Default to "Consult physician" recommendations

## Testing Strategy

### Dual Testing Approach
The system will employ both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests** will focus on:
- Specific disease prediction examples with known symptom patterns
- Hospital filtering edge cases (empty results, invalid filters)
- PDF generation for each disease type
- Medicine database lookup for specific disease-severity combinations
- Google Maps URL generation for various hospital data formats

**Property-Based Tests** will verify:
- Universal properties across all diseases and hospitals (Properties 1-11)
- Model accuracy across randomly generated symptom combinations
- Hospital recommendation consistency across all cities and filter combinations
- PDF generation completeness for all disease types
- Medicine recommendation appropriateness across all severity levels

### Property-Based Testing Configuration
- **Testing Framework**: Use Hypothesis for Python property-based testing
- **Test Iterations**: Minimum 100 iterations per property test
- **Test Tagging**: Each property test tagged with format: **Feature: healthcare-system-enhancements, Property {number}: {property_text}**
- **Data Generation**: Smart generators that create medically realistic symptom patterns and hospital data

### Integration Testing
- **End-to-end workflows**: Complete patient journey from symptom entry to PDF report
- **Database integration**: Verify all database operations maintain data integrity
- **External service integration**: Test Google Maps URL generation and validation
- **Performance testing**: Ensure response times remain acceptable with expanded dataset

### Validation Testing
- **Medical accuracy validation**: Review medication recommendations with medical professionals
- **Hospital data validation**: Verify hospital information accuracy and specialty mappings
- **Model performance validation**: Cross-validation with holdout test sets for each disease
- **User acceptance testing**: Validate UI improvements and hospital recommendation display