"""FastAPI serving layer for the spam classifier. Loads both model.pkl
and vectorizer.pkl at startup — text has to be vectorized the same way
it was during training before the model can predict on it.
"""
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="spam-service")
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


class TextInput(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "spam-service"}


@app.post("/predict")
def predict(input: TextInput):
    vec = vectorizer.transform([input.text])
    prediction = model.predict(vec)[0]
    probability = model.predict_proba(vec)[0][1]  # P(spam)
    return {
        "prediction": "spam" if prediction == 1 else "ham",
        "spam_probability": round(float(probability), 4),
    }
