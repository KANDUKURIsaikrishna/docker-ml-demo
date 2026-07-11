# ML Docker Deployment Demo

A teaching repo: dockerize and deploy 3 ML models + a gateway + a dropdown frontend, from trained model to running Kubernetes service.

```
Train model → Save model.pkl → Build FastAPI/Flask app → Write Dockerfile →
docker build → Docker Image → Push to Docker Hub →
Deploy to Kubernetes (local kind/minikube) → Users send prediction requests
```

## Prerequisites

Clone, then check what's missing:

```bash
./scripts/check-prereqs.sh
```

Needs: Python 3, a running Docker engine (Docker Desktop, colima, or Rancher Desktop — any of them work, `docker login` is only required later for pushing images), `docker-compose`. `kubectl` + `kind` only if you're going past docs/03 into Kubernetes.

## What's here

- **`frontend/`** — Flask app, dropdown UI, proxies requests to the gateway.
- **`gateway/`** — FastAPI, routes `/predict/{model}` to the right model microservice.
- **`models/iris-service/`** — RandomForest classifier (iris dataset).
- **`models/diabetes-service/`** — GradientBoostingRegressor (diabetes dataset).
- **`models/spam-service/`** — TF-IDF + LogisticRegression spam classifier (2 artifacts: model + vectorizer).
- **`k8s/`** — Deployment + Service manifests for all 5 components.
- **`docker-compose.yml`** — fast local run of all 5 containers, no Kubernetes needed.
- **`.github/workflows/`** — bonus: automates the manual build/push steps.
- **`docs/`** — numbered, step-by-step tutorial. **Start here:** [docs/01-train-models.md](docs/01-train-models.md).
- **`scripts/check-prereqs.sh`** — run after cloning, tells you what's missing.
- **[`DEMO.md`](DEMO.md)** — script for live-presenting the app to students (what to click, what to say, how to break it on purpose).

## Full design

See [docs/superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md](docs/superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md) for the full design doc — architecture, decisions, and what's intentionally out of scope.

## Quickest path to seeing it work

```bash
# 1. train all 3 models (see docs/01)
# 2. run everything locally, no k8s:
docker-compose up --build
# open http://localhost:5000
```

Full path including Kubernetes: follow `docs/01` through `docs/07` in order.
