"""FastAPI serving layer for eyeglasses detection.

No cascade classifies "wearing glasses" directly, so this uses a
classic heuristic instead: glasses frames create a dense horizontal
band of edges across the nose bridge, between the eyes, that bare skin
doesn't. Detect the face, locate the eye line, run a Canny edge
detector on the strip between the eyes, and threshold on edge density.

Good enough for a live demo, not a production classifier — lighting
and head angle both affect it.
"""
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="glasses-service")

CASCADE_DIR = cv2.data.haarcascades
face_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_frontalface_default.xml")
# The plain eye cascade is trained on bare eyes and reliably fails to
# match when eyeglasses are worn — which is exactly the population this
# service needs to locate accurately. The eye_tree_eyeglasses variant is
# trained to detect eyes whether or not glasses are present, so the eye
# line (and therefore the nose-bridge strip below) lands in the right
# place regardless of what we're trying to detect.
eye_cascade = cv2.CascadeClassifier(CASCADE_DIR + "haarcascade_eye_tree_eyeglasses.xml")

# Calibrated from real captures (one user, one webcam, one lighting
# setup): no-glasses measured 0.0731, with-glasses measured 0.1411.
# Threshold is the midpoint. This is two data points, not a validated
# dataset — expect to retune per-camera/lighting if it misfires.
EDGE_DENSITY_THRESHOLD = 0.1071


@app.get("/health")
def health():
    return {"status": "ok", "service": "glasses-service"}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    contents = await image.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "could not decode image"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return {"face_detected": False, "wearing_glasses": False}

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y : y + h, x : x + w]

    eyes = eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))

    if len(eyes) >= 2:
        # Eye line = average vertical center of detected eyes.
        eye_y = int(np.mean([ey + eh / 2 for (_, ey, _, eh) in eyes]))
    else:
        # Fallback: eyes sit roughly 40% down a frontal face.
        eye_y = int(h * 0.4)

    # Narrow horizontal strip across the nose bridge, centered on the eye line.
    strip_h = max(int(h * 0.12), 6)
    top = max(eye_y - strip_h // 2, 0)
    bottom = min(eye_y + strip_h // 2, h)
    strip = face_roi[top:bottom, :]

    edges = cv2.Canny(strip, 60, 150)
    edge_density = float(np.count_nonzero(edges)) / edges.size if edges.size else 0.0

    return {
        "face_detected": True,
        "wearing_glasses": edge_density > EDGE_DENSITY_THRESHOLD,
        "edge_density": round(edge_density, 4),
    }
