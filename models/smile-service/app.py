"""FastAPI serving layer for smile detection. No training, no model.pkl —
uses OpenCV's pretrained Haar cascades, which ship inside the opencv
package itself (cv2.data.haarcascades). This service loads two
cascades at startup and never touches disk again after that.
"""
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="smile-service")

CASCADE_DIR = cv2.data.haarcascades
face_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_smile.xml")


@app.get("/health")
def health():
    return {"status": "ok", "service": "smile-service"}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    contents = await image.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "could not decode image"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return {"face_detected": False, "smiling": False}

    # Largest face = the one closest to camera, most likely the subject.
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y : y + h, x : x + w]

    # Scope the search to the mouth/chin region only. Running the smile
    # cascade over the whole face (eyes, forehead included) makes a high
    # minNeighbors threshold nearly impossible to satisfy even for a real
    # smile — the mouth pattern is a small fraction of a noisy full-face
    # search area. Scoping it first lets a moderate minNeighbors still
    # filter false positives without starving real smiles of matches.
    mouth_roi = face_roi[int(h * 0.5) :, :]
    smiles = smile_cascade.detectMultiScale(mouth_roi, scaleFactor=1.7, minNeighbors=15, minSize=(25, 25))

    return {"face_detected": True, "smiling": len(smiles) > 0}
