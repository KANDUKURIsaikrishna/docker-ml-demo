"""FastAPI serving layer for the iris model. Loads model.pkl once at
startup and answers /predict requests — no training happens here.
"""
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, conlist

app = FastAPI(title="iris-service")
model = joblib.load("model.pkl")

CLASS_NAMES = ["setosa", "versicolor", "virginica"]


class IrisInput(BaseModel):
    features: conlist(float, min_length=4, max_length=4)  # type: ignore[valid-type]
    # order: sepal_length, sepal_width, petal_length, petal_width


@app.get("/health")
def health():
    return {"status": "ok", "service": "iris-service"}


@app.post("/predict")
def predict(input: IrisInput):
    prediction = model.predict([input.features])[0]
    probabilities = model.predict_proba([input.features])[0]
    return {
        "prediction": CLASS_NAMES[prediction],
        "confidence": round(float(max(probabilities)), 4),
    }
