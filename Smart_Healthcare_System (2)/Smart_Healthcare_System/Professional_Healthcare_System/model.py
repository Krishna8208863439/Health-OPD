import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def train_model():
    """Train the disease prediction model"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "Health.csv")
    
    data = pd.read_csv(csv_path)
    
    X = data[['bodypain','Hollow','cold and cough','cough','fever',
              'chest pain','breathing problem','Throat pain','head pain',
              'stomach pain','diarrhea','omitting','back pain','Swollen feet']]
    y = data['PID']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    disease_map = dict(
        data.groupby(['PID', 'Problem']).first().index
    )
    
    accuracy = model.score(X_test, y_test)
    print(f"[OK] Model trained successfully with accuracy: {accuracy:.2%}")
    
    return model, disease_map, accuracy
