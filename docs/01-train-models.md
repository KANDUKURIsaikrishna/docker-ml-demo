# 01 — How the models work (no training required)

> **Docker beginners:** skip ahead to nothing here — this step is plain Python, no Docker yet. That's intentional: understanding what a model needs to run happens *before* Docker enters the picture. The container's only job is to *serve* the model, not train one.

All 3 model services (`smile-service`, `glasses-service`, `eyes-service`) use **OpenCV Haar cascades** — pretrained classifiers that ship *inside* the `opencv-python-headless` package itself. There's no `train.py`, no `.pkl` file, no dataset to download. `pip install opencv-python-headless` gives every service everything it needs.

```python
import cv2
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
```

That line alone gives you a working face detector. Each service loads 1-2 of these cascades at startup and never touches disk again.

## What each service does

- **`models/smile-service/app.py`** — finds the largest face in the frame, crops to the mouth/chin region, then runs a smile cascade on just that area. Scoping the search to the mouth (instead of the whole face) is what makes a strict `minNeighbors` threshold actually reliable — searching the whole face for a small mouth-shaped pattern starves real smiles of matches.
- **`models/glasses-service/app.py`** — no cascade classifies "wearing glasses" directly. Instead it locates the eye line using `haarcascade_eye_tree_eyeglasses.xml` (trained to detect eyes whether or not glasses are worn — the plain eye cascade fails specifically on glasses-wearers, which would break this for exactly the case we care about), crops the nose-bridge strip between the eyes, and measures edge density there with a Canny edge detector. Glasses frames create a dense band of edges that bare skin doesn't.
- **`models/eyes-service/app.py`** — the eye cascade is trained on *open*-eye images, so it reliably fails to match closed eyes. A single eye detection is enough to call it "open" — requiring both eyes is too strict in practice, since head angle or glare routinely hides one eye even when both are open.

None of these are production-grade classifiers — lighting and head angle affect all three. That's an acceptable tradeoff here: the lesson is Docker/Kubernetes, not model accuracy, and all three are honest about their limits in code comments.

## Try it without Docker first

```bash
cd models/smile-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -c "import cv2; print(cv2.data.haarcascades)"   # confirms cascades are installed
uvicorn app:app --reload
deactivate
```

**Windows (PowerShell):** replace the venv line with `python -m venv venv; venv\Scripts\Activate.ps1` — everything else is identical. Full Windows setup: [docs/windows-setup.md](windows-setup.md).

Open http://localhost:8000/docs — FastAPI's built-in UI. Use "Try it out" on `/predict`, upload any photo with a face in it, see the JSON response. This confirms the model logic works before Docker adds another layer to debug through.

Repeat for `glasses-service` and `eyes-service` if you want to poke at all three before containerizing.

Next: [02 — Build the images](02-build-images.md)
