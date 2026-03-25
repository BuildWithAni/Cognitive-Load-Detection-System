import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    # Features: [blink_rate, typing_speed, error_rate, mouse_movement]
    # Labels: 0 = Low, 1 = Medium, 2 = High
    X = []
    y = []
    
    # Low load (0)
    # blink_rate: 0-12, typing_speed: 0-50, error_rate: 0.00-0.08, mouse_movement: 0-30
    X_low = np.random.rand(n_samples//3, 4)
    X_low[:,0] = np.random.uniform(0, 12, n_samples//3)
    X_low[:,1] = np.random.uniform(0, 50, n_samples//3)
    X_low[:,2] = np.random.uniform(0.00, 0.08, n_samples//3)
    X_low[:,3] = np.random.uniform(0, 30, n_samples//3)
    X.append(X_low)
    y.extend([0]*(n_samples//3))
    
    # Medium load (1)
    X_med = np.random.rand(n_samples//3, 4)
    X_med[:,0] = np.random.uniform(12, 25, n_samples//3)
    X_med[:,1] = np.random.uniform(50, 75, n_samples//3)
    X_med[:,2] = np.random.uniform(0.08, 0.15, n_samples//3)
    X_med[:,3] = np.random.uniform(30, 60, n_samples//3)
    X.append(X_med)
    y.extend([1]*(n_samples//3))
    
    # High load (2)
    X_high = np.random.rand(n_samples - 2*(n_samples//3), 4)
    X_high[:,0] = np.random.uniform(25, 200, n_samples - 2*(n_samples//3))
    X_high[:,1] = np.random.uniform(75, 150, n_samples - 2*(n_samples//3))
    X_high[:,2] = np.random.uniform(0.15, 0.50, n_samples - 2*(n_samples//3))
    X_high[:,3] = np.random.uniform(60, 120, n_samples - 2*(n_samples//3))
    X.append(X_high)
    y.extend([2]*(n_samples - 2*(n_samples//3)))
    
    X = np.vstack(X)
    y = np.array(y)
    return X, y

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')

def train_model():
    X, y = generate_synthetic_data()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    # Save model and scaler
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler}, f)
    print(f"Model trained and saved to {MODEL_PATH}")

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_model()
    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)
    return data['model'], data['scaler']

if __name__ == '__main__':
    train_model()