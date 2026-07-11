# ML Docker Deployment Demo — Design

**Date:** 2026-07-11
**Purpose:** Teaching demo/repo for mentoring students on dockerizing and deploying ML models in a real-world pattern — from trained model to running Kubernetes service.

## Goal

Build a small multi-model ML web app where a user picks a model from a dropdown and gets a prediction. The app itself is secondary — the real deliverable is the pipeline and docs walking students through:

```
Train model → Save model.pkl → Build API → Write Dockerfile →
docker build → Docker Image → Push to Docker Hub →
Deploy to Kubernetes (local kind/minikube) → Users send prediction requests
```

## Architecture

5 containers, microservice pattern:

- **frontend** — Flask app serving a static page with a model-selection dropdown. Plain HTML/JS, no build step. Calls the gateway via `fetch()`.
- **gateway** — FastAPI service. Receives `/predict/{model}` requests from the frontend, routes to the correct model microservice by name, returns the response.
- **iris-service** — FastAPI + `model.pkl` (RandomForest classifier, iris dataset).
- **diabetes-service** — FastAPI + `model.pkl` (regression, diabetes dataset).
- **spam-service** — FastAPI + `model.pkl` + `vectorizer.pkl` (TF-IDF + LogisticRegression, SMS spam dataset).

All three model services share the same framework (scikit-learn) but differ in task type (classification / regression / text classification), so students see the Docker/K8s pattern repeat 3 times across genuinely different problems rather than 3 copies of the same thing.

### Data flow

```
Browser → frontend (dropdown, POST) → gateway
        → routes by model name → {iris,diabetes,spam}-service
        → model loads .pkl at container startup → predict()
        → response bubbles back: service → gateway → frontend → user
```

Service addressing uses plain service-name DNS (`iris-service:8000`, etc.) — identical names in `docker-compose.yml` and in Kubernetes `Service` objects, so the same gateway code works unmodified in both environments. This is the concrete lesson: containers don't change between compose and k8s, only orchestration does.

## Repo layout

```
ml-docker-demo/
  frontend/
    app.py                Flask, serves static/index.html
    static/index.html     dropdown + fetch() to gateway
    Dockerfile
  gateway/
    main.py                FastAPI, /predict/{model} router
    Dockerfile
  models/
    iris-service/
      train.py              trains + saves model.pkl
      model.pkl
      app.py                 FastAPI, loads model.pkl, /predict
      Dockerfile
      requirements.txt
    diabetes-service/         same shape as iris-service
    spam-service/
      train.py               also saves vectorizer.pkl
      model.pkl
      vectorizer.pkl
      app.py
      Dockerfile
      requirements.txt
  k8s/
    namespace.yaml            ml-demo namespace
    frontend-deployment.yaml
    gateway-deployment.yaml
    iris-deployment.yaml
    diabetes-deployment.yaml
    spam-deployment.yaml
    (each pairs a Deployment + ClusterIP Service; frontend gets NodePort)
  .github/workflows/
    build-and-push.yml        bonus: mirrors manual build/tag/push commands
  docs/
    01-train-models.md
    02-build-images.md
    03-push-dockerhub.md
    04-local-k8s-setup.md
    05-deploy-k8s.md
    06-test-app.md
    07-bonus-cicd.md
  docker-compose.yml           fast local inner loop before k8s
```

## Docker strategy

Each model service uses `python:3.11-slim` as base. `requirements.txt` is `COPY`'d and installed before the rest of the source is copied in, so students see Docker's layer cache in action (code changes don't force a dependency reinstall). Dependencies are small (scikit-learn, fastapi, uvicorn, joblib) so a multi-stage build isn't needed — this keeps the lesson focused on layering/caching rather than multi-stage complexity.

Frontend is a single thin image, no build step (plain HTML/JS).

## Kubernetes

- Namespace: `ml-demo`.
- Each component gets a `Deployment` + `ClusterIP Service`, except frontend which gets a `NodePort` (or `kubectl port-forward`) for direct access — ingress is called out as an optional stretch step, not required for the core demo.
- Target: local cluster via `kind` or `minikube`. Manifests are plain Kubernetes YAML with no cloud-specific fields, so they carry over to a real EKS cluster unchanged aside from image registry auth.
- Docs walk: `kubectl apply -f k8s/`, `kubectl get pods -n ml-demo`, `kubectl logs`, `kubectl port-forward`.

## Registry

Docker Hub (free, no cloud account required). Students `docker login`, tag images as `<their-dockerhub-username>/<service-name>:v1`, and push. K8s manifests reference the image name via a placeholder students substitute with their own username — this makes the push step observably matter, since their build produces the pod that actually runs.

## Verification loop

1. `docker-compose up` — validates the full app (frontend → gateway → 3 services) locally, fast iteration, no k8s yet.
2. `kind create cluster`, `kubectl apply -f k8s/`, `port-forward`, re-test the same requests.
3. Comparing steps 1 and 2 is itself the lesson: identical containers, different orchestration.

## Bonus: CI/CD

One GitHub Actions workflow (`.github/workflows/build-and-push.yml`) automates the same `docker build` / `tag` / `push` sequence on push to `main`. The doc for this step maps each manual command 1:1 to its line in the workflow YAML, so it reads as "the same thing, automated" rather than a new concept.

## Docs / audience

Docs are tiered: Docker-101 explanations (what a layer is, what `EXPOSE` does, why `.dockerignore` matters) are called out in separate boxes/asides so students who already know Docker basics can skim past them, while beginners get the full explanation inline. Same applies to Kubernetes docs — one flow, explanatory asides layered in rather than a separate beginner track.

## Out of scope

- Real AWS EKS deployment (noted as a natural next step using the same manifests, not built out).
- Ingress / TLS / autoscaling — mentioned as stretch ideas, not implemented.
- Authentication on the API — demo is unauthenticated by design, kept simple for the teaching context.
- Model monitoring/retraining pipelines — out of scope, this demo stops at "prediction requests work."
