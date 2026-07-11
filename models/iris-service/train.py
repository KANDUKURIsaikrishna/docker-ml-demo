"""Trains a RandomForest classifier on the iris dataset and saves model.pkl.

Run this once, locally, before building the Docker image — the image just
serves the artifact it doesn't train it. That split (train offline, serve
in a container) is the pattern the whole demo is built around.
"""
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Test accuracy: {accuracy:.3f}")

joblib.dump(model, "model.pkl")
print("Saved model.pkl")
