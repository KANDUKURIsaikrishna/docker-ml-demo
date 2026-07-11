# 02 — Build the Docker images

Five images total: `frontend`, `gateway`, `smile-service`, `glasses-service`, `eyes-service`. Each has its own `Dockerfile` in its own directory — one image, one job.

> **Docker beginners:** a `Dockerfile` is a recipe. `docker build` reads it top to bottom and produces an *image* — a frozen filesystem + startup command. Nothing runs yet; `build` just assembles the image. Running it is the next step (`docker run`, or `docker-compose up` in step 3).

Open `models/smile-service/Dockerfile` and read it — all three model Dockerfiles in this repo follow the same shape:

```dockerfile
FROM python:3.11-slim      # base image: minimal Python, not full OS
WORKDIR /app                 # everything below happens in /app inside the image

COPY requirements.txt .      # copy ONLY the dependency list first...
RUN pip install --no-cache-dir -r requirements.txt   # ...and install here

COPY app.py .                 # code copied AFTER deps are installed

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Notice there's no `COPY model.pkl` here — nothing to copy. The Haar cascades this service needs are already inside `opencv-python-headless`, installed by the `pip install` line above. The image is self-contained after that one `RUN` line.

**Why `requirements.txt` is copied before the code:** Docker caches each instruction as a layer. If you edit `app.py` and rebuild, Docker sees `requirements.txt` is unchanged and reuses the cached `pip install` layer instead of reinstalling every dependency from scratch. Reorder those two `COPY` lines and every code change forces a full reinstall — try it and time the difference. This matters more here than it might elsewhere: `opencv-python-headless` is a meaningfully large dependency, so a cached layer saves real time.

Build one image by hand to see it work:

```bash
cd models/smile-service
docker build -t smile-service:local .
cd ../..
```

Watch the output — each `COPY`/`RUN` line becomes a numbered step. Run it again without changing anything and notice the `CACHED` steps fly by.

You don't need to build all five by hand — `docker-compose` builds all five in one command:

```bash
docker-compose up --build
```

Open http://localhost:5000 — pick a model from the dropdown, click **Start camera**, allow browser camera access, then **Capture & Predict**. This is your fast inner loop: change code, `docker-compose up --build` again, refresh the browser. No Kubernetes yet, no registry push yet — just confirming the app works as five containers talking to each other.

Stop it with `Ctrl+C`, then `docker-compose down`.

**What just happened, container-to-container:** `frontend` (port 5000, the only one exposed to your machine) called `gateway` over the Docker Compose network using the service name `gateway:8000`. `gateway` in turn called `smile-service:8000` / `glasses-service:8000` / `eyes-service:8000` the same way, forwarding the captured JPEG frame as a multipart upload. Compose creates a private network per project and gives every service a DNS name matching its name in `docker-compose.yml` — that's the exact mechanism Kubernetes Services provide too, which is why the gateway's code doesn't need to change in step 5.

Next: [03 — Push to Docker Hub](03-push-dockerhub.md)
