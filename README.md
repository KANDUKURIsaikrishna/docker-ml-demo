# ML Docker Deployment Demo

A teaching repo: dockerize and deploy 3 webcam-based ML models + a gateway + a dropdown frontend, from model code to a running Kubernetes service.

```
Write model code → Build FastAPI/Flask app → Write Dockerfile →
docker build → Docker Image → Push to Docker Hub →
Deploy to Kubernetes (local kind/minikube) → Users send prediction requests
```

## Prerequisites

Needs Python 3 first (one manual install — see below), then everything else is checked for you:

```bash
python3 scripts/check_prereqs.py            # macOS/Linux
python scripts\check_prereqs.py             # Windows
```

Add `--install` to have it install missing tools automatically (Homebrew on macOS, winget on Windows).

Needs: Python 3, a running Docker engine (Docker Desktop, colima, or Rancher Desktop — any of them work, `docker login` is only required later for pushing images), `docker-compose`. `kubectl` + `kind` only if you're going past docs/03 into Kubernetes.

**Windows:** see [docs/windows-setup.md](docs/windows-setup.md) — required installs and the WSL2/Docker Desktop gotchas.

## What's here

- **`frontend/`** — Flask app, webcam-capture UI, proxies requests to the gateway.
- **`gateway/`** — FastAPI, routes `/predict/{model}` to the right model microservice.
- **`models/smile-service/`** — smile detector (OpenCV Haar cascade, face + smile).
- **`models/glasses-service/`** — eyeglasses detector (edge-density heuristic on the nose bridge).
- **`models/eyes-service/`** — eyes open/closed detector (OpenCV eye cascade).
- **`k8s/`** — Deployment + Service manifests for all 5 components.
- **`docker-compose.yml`** — fast local run of all 5 containers, no Kubernetes needed.
- **`.github/workflows/`** — bonus: automates the manual build/push steps.
- **`docs/`** — numbered, step-by-step tutorial. **Start here:** [docs/01-train-models.md](docs/01-train-models.md).
- **[`docs/kind-deployment.md`](docs/kind-deployment.md)** — the kind deployment (docs 04-06) as one file, plus a Docker-Hub-free shortcut for local testing.
- **`scripts/check_prereqs.py`** — run after cloning, tells you what's missing. Same script on macOS/Linux/Windows.
- **`scripts/push_to_dockerhub.py`** — builds, tags, pushes all 5 images, and updates `k8s/*.yaml` for you (automates docs/03).
- **[`DEMO.md`](DEMO.md)** / **[`DEMO-windows.md`](DEMO-windows.md)** — Docker Compose live-demo script (what to click, what to say, how to break it on purpose).
- **[`DEMO-kind.md`](DEMO-kind.md)** / **[`DEMO-kind-windows.md`](DEMO-kind-windows.md)** — Kubernetes live-demo script (pods, service discovery, self-heal).

All 3 models use pretrained OpenCV Haar cascades — no training step, no dataset, no `.pkl` file. See [docs/01-train-models.md](docs/01-train-models.md) for how that works.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system diagram, request lifecycle, why 5 services instead of 1, Docker/K8s strategy, and "why not kustomize."

## Design history

See [docs/superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md](docs/superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md) for how this repo got here — decisions and what's intentionally out of scope.

## Quickest path to seeing it work

```bash
docker-compose up --build
# open http://localhost:5000, click "Start camera", then "Capture & Predict"
```

Full path including Kubernetes: follow `docs/01` through `docs/07` in order.
