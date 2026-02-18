"""Train and save the ML model. Run once to generate model.pkl."""
import pickle
from pathlib import Path

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load data and train
X, y = load_iris(return_X_y=True)
X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Save to app directory for Docker build
Path("app/model.pkl").parent.mkdir(parents=True, exist_ok=True)
with open("app/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved to app/model.pkl")
