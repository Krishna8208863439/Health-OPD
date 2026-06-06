import pandas as pd
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache.pkl")

def train_model():
    """Train the disease prediction model, with caching to speed up startup."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "Health.csv")

    # ── Load from cache if available ──────────────────────────────────────────
    if os.path.exists(MODEL_CACHE):
        try:
            with open(MODEL_CACHE, "rb") as f:
                cached = pickle.load(f)
            print(f"Model loaded from cache (accuracy: {cached['accuracy']:.2%})")
            return cached["model"], cached["disease_map"], cached["accuracy"]
        except Exception:
            pass  # Cache corrupt – retrain

    # ── Train fresh ───────────────────────────────────────────────────────────
    data = pd.read_csv(csv_path)

    X = data[['bodypain', 'Hollow', 'cold and cough', 'cough', 'fever',
              'chest pain', 'breathing problem', 'Throat pain', 'head pain',
              'stomach pain', 'diarrhea', 'omitting', 'back pain', 'Swollen feet']]
    y = data['PID']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    disease_map = dict(data.groupby(['PID', 'Problem']).first().index)
    accuracy = model.score(X_test, y_test)
    print(f"Model trained with accuracy: {accuracy:.2%}")

    # ── Save to cache ─────────────────────────────────────────────────────────
    try:
        with open(MODEL_CACHE, "wb") as f:
            pickle.dump({"model": model, "disease_map": disease_map, "accuracy": accuracy}, f)
        print("Model cached to disk.")
    except Exception as e:
        print(f"Cache save failed (non-critical): {e}")

    return model, disease_map, accuracy
