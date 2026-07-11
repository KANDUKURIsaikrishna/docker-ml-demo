"""Flask frontend. Serves the webcam-capture UI and proxies prediction
requests server-side to the gateway, so the browser only ever talks to
this one origin — no CORS, no exposing internal service DNS names to
the client.
"""
import os

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:8000")
REQUEST_TIMEOUT = 5.0


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/predict/<model_name>")
def predict(model_name):
    image = request.files.get("image")
    if image is None:
        return jsonify({"detail": "no image uploaded"}), 400

    try:
        response = requests.post(
            f"{GATEWAY_URL}/predict/{model_name}",
            files={"image": (image.filename, image.stream, image.mimetype)},
            timeout=REQUEST_TIMEOUT,
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as exc:
        return jsonify({"detail": f"gateway unreachable: {exc}"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
