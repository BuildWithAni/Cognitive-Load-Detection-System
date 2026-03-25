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
    # blink_rate: 5-12, typing_speed: 30-50, error_rate: 0.02-0.08, mouse_movement: 10-30
    X_low = np.random.rand(n_samples//3, 4)
    X_low[:,0] = np.random.uniform(5, 12, n_samples//3)
    X_low[:,1] = np.random.uniform(30, 50, n_samples//3)
    X_low[:,2] = np.random.uniform(0.02, 0.08, n_samples//3)
    X_low[:,3] = np.random.uniform(10, 30, n_samples//3)
    X.append(X_low)
    y.extend([0]*(n_samples//3))
    
    # Medium load (1)
    X_med = np.random.rand(n_samples//3, 4)
    X_med[:,0] = np.random.uniform(12, 20, n_samples//3)
    X_med[:,1] = np.random.uniform(50, 70, n_samples//3)
    X_med[:,2] = np.random.uniform(0.08, 0.15, n_samples//3)
    X_med[:,3] = np.random.uniform(30, 60, n_samples//3)
    X.append(X_med)
    y.extend([1]*(n_samples//3))
    
    # High load (2)
    X_high = np.random.rand(n_samples - 2*(n_samples//3), 4)
    X_high[:,0] = np.random.uniform(20, 35, n_samples - 2*(n_samples//3))
    X_high[:,1] = np.random.uniform(70, 100, n_samples - 2*(n_samples//3))
    X_high[:,2] = np.random.uniform(0.15, 0.30, n_samples - 2*(n_samples//3))
    X_high[:,3] = np.random.uniform(60, 100, n_samples - 2*(n_samples//3))
    X.append(X_high)
    y.extend([2]*(n_samples - 2*(n_samples//3)))
    
    X = np.vstack(X)
    y = np.array(y)
    return X, y

def train_model():
    X, y = generate_synthetic_data()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    # Save model and scaler
    with open('model.pkl', 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler}, f)
    print("Model trained and saved as model.pkl")

def load_model():
    with open('model.pkl', 'rb') as f:
        data = pickle.load(f)
    return data['model'], data['scaler']

if __name__ == '__main__':
    train_model()