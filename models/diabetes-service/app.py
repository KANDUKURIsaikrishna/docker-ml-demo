"""FastAPI serving layer for the diabetes regression model."""
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, conlist

app = FastAPI(title="diabetes-service")
model = joblib.load("model.pkl")


class DiabetesInput(BaseModel):
    # 10 baseline features from sklearn's diabetes dataset, already
    # mean-centered/scaled by sklearn's loader.
    features: conlist(float, min_length=10, max_length=10)  # type: ignore[valid-type]


@app.get("/health")
def health():
    return {"status": "ok", "service": "diabetes-service"}


@app.post("/predict")
def predict(input: DiabetesInput):
    prediction = model.predict([input.features])[0]
    return {"prediction": round(float(prediction), 2)}
