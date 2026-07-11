"""API gateway: receives /predict/{model} from the frontend and routes
to the right model microservice by name. Service addresses come from
env vars, defaulting to docker-compose service names — the same code
runs unmodified against Kubernetes Service DNS names.
"""
import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_URLS = {
    "iris": os.getenv("IRIS_SERVICE_URL", "http://iris-service:8000"),
    "diabetes": os.getenv("DIABETES_SERVICE_URL", "http://diabetes-service:8000"),
    "spam": os.getenv("SPAM_SERVICE_URL", "http://spam-service:8000"),
}

REQUEST_TIMEOUT = 5.0


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway", "routes": list(SERVICE_URLS)}


@app.post("/predict/{model_name}")
async def predict(model_name: str, payload: dict[str, Any]):
    base_url = SERVICE_URLS.get(model_name)
    if base_url is None:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model_name}'")

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(f"{base_url}/predict", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail=f"{model_name} service timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"{model_name} service unavailable")
