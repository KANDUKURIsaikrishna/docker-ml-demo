"""FastAPI serving layer for eyes-open/closed detection.

Heuristic: OpenCV's eye cascade is trained on open-eye images, so it
reliably fails to match closed eyes. No match in the eye region after
a face is found is read as "eyes closed" rather than "detector missed
it" — a known limitation of this classic trick, acceptable for a demo.
"""
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="eyes-service")

CASCADE_DIR = cv2.data.haarcascades
face_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_eye.xml")


@app.get("/health")
def health():
    return {"status": "ok", "service": "eyes-service"}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    contents = await image.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "could not decode image"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return {"face_detected": False, "eyes_open": False, "eyes_detected": 0}

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    # Eyes sit in the upper ~60% of the face — restricting the search
    # region cuts false positives from nostrils/mouth.
    upper_face = gray[y : y + int(h * 0.6), x : x + w]

    eyes = eye_cascade.detectMultiScale(upper_face, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))

    # Requiring both eyes detected is too strict in practice — head angle,
    # glare, or hair routinely leaves only one eye cleanly matched even
    # when both are open. Since this cascade only matches open eyes at
    # all (see module docstring), a single detection is already strong
    # evidence of "open," not just a partial result.
    return {"face_detected": True, "eyes_open": len(eyes) >= 1, "eyes_detected": len(eyes)}
