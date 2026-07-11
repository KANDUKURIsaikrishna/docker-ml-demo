"""Trains a GradientBoostingRegressor on the diabetes dataset and saves
model.pkl. Regression, not classification — the API and metrics differ
from iris-service even though the Docker pattern is identical.
"""
import joblib
from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

mse = mean_squared_error(y_test, model.predict(X_test))
print(f"Test MSE: {mse:.2f}")

joblib.dump(model, "model.pkl")
print("Saved model.pkl")
