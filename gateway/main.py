"""API gateway: receives /predict/{model} from the frontend and routes
to the right model microservice by name. Service addresses come from
env vars, defaulting to docker-compose service names — the same code
runs unmodified against Kubernetes Service DNS names.

Payload is a webcam-captured image (multipart), not JSON — the gateway
just streams the uploaded bytes on to whichever model service owns
that name, unchanged.
"""
import os

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_URLS = {
    "smile": os.getenv("SMILE_SERVICE_URL", "http://smile-service:8000"),
    "glasses": os.getenv("GLASSES_SERVICE_URL", "http://glasses-service:8000"),
    "eyes": os.getenv("EYES_SERVICE_URL", "http://eyes-service:8000"),
}

REQUEST_TIMEOUT = 5.0


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway", "routes": list(SERVICE_URLS)}


@app.post("/predict/{model_name}")
async def predict(model_name: str, image: UploadFile = File(...)):
    base_url = SERVICE_URLS.get(model_name)
    if base_url is None:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model_name}'")

    contents = await image.read()
    files = {"image": (image.filename or "frame.jpg", contents, image.content_type or "image/jpeg")}

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(f"{base_url}/predict", files=files)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail=f"{model_name} service timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"{model_name} service unavailable")
